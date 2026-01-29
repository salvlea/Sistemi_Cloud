"""
Integration tests for Smart ATS AWS deployment
"""
import boto3
import pytest
import os
import time
from datetime import datetime


class TestAWSIntegration:
    """Integration tests for deployed AWS resources."""
    
    @pytest.fixture(scope="class")
    def aws_config(self):
        """AWS configuration fixture."""
        return {
            'region': os.environ.get('AWS_REGION', 'us-east-1'),
            'stack_name': 'smart-ats-stack-dev',
            's3_bucket': None,  # Will be fetched from stack
            'dynamodb_table': None,
            'sqs_queue_url': None
        }
    
    @pytest.fixture(scope="class", autouse=True)
    def fetch_stack_outputs(self, aws_config):
        """Fetch stack outputs before running tests."""
        cf_client = boto3.client('cloudformation', region_name=aws_config['region'])
        
        try:
            response = cf_client.describe_stacks(StackName=aws_config['stack_name'])
            outputs = response['Stacks'][0]['Outputs']
            
            for output in outputs:
                if output['OutputKey'] == 'S3BucketName':
                    aws_config['s3_bucket'] = output['OutputValue']
                elif output['OutputKey'] == 'DynamoDBTableName':
                    aws_config['dynamodb_table'] = output['OutputValue']
                elif output['OutputKey'] == 'SQSQueueURL':
                    aws_config['sqs_queue_url'] = output['OutputValue']
        except Exception as e:
            pytest.skip(f"Stack not deployed or not accessible: {e}")
    
    def test_s3_bucket_exists(self, aws_config):
        """Test S3 bucket exists and is accessible."""
        s3 = boto3.client('s3', region_name=aws_config['region'])
        
        # Check bucket exists
        response = s3.list_buckets()
        bucket_names = [b['Name'] for b in response['Buckets']]
        
        assert aws_config['s3_bucket'] in bucket_names
    
    def test_s3_bucket_versioning(self, aws_config):
        """Test S3 bucket has versioning enabled."""
        s3 = boto3.client('s3', region_name=aws_config['region'])
        
        response = s3.get_bucket_versioning(Bucket=aws_config['s3_bucket'])
        
        assert response.get('Status') == 'Enabled'
    
    def test_dynamodb_table_exists(self, aws_config):
        """Test DynamoDB table exists and is active."""
        dynamodb = boto3.client('dynamodb', region_name=aws_config['region'])
        
        response = dynamodb.describe_table(TableName=aws_config['dynamodb_table'])
        
        assert response['Table']['TableStatus'] == 'ACTIVE'
    
    def test_dynamodb_table_gsi(self, aws_config):
        """Test DynamoDB table has required GSI."""
        dynamodb = boto3.client('dynamodb', region_name=aws_config['region'])
        
        response = dynamodb.describe_table(TableName=aws_config['dynamodb_table'])
        
        gsi_names = [gsi['IndexName'] for gsi in response['Table'].get('GlobalSecondaryIndexes', [])]
        
        assert 'JobPositionRankingIndex' in gsi_names
    
    def test_sqs_queue_exists(self, aws_config):
        """Test SQS queue exists and is accessible."""
        sqs = boto3.client('sqs', region_name=aws_config['region'])
        
        response = sqs.get_queue_attributes(
            QueueUrl=aws_config['sqs_queue_url'],
            AttributeNames=['QueueArn', 'VisibilityTimeout']
        )
        
        assert 'QueueArn' in response['Attributes']
        assert int(response['Attributes']['VisibilityTimeout']) == 900
    
    def test_lambda_function_exists(self, aws_config):
        """Test Lambda function exists and is configured correctly."""
        lambda_client = boto3.client('lambda', region_name=aws_config['region'])
        
        function_name = 'smart-ats-cv-processor-dev'
        
        try:
            response = lambda_client.get_function(FunctionName=function_name)
            
            assert response['Configuration']['Runtime'] == 'python3.13'
            assert response['Configuration']['MemorySize'] == 512
            assert response['Configuration']['Timeout'] == 300
        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.fail(f"Lambda function {function_name} not found")
    
    def test_end_to_end_cv_processing(self, aws_config):
        """
        Integration test: Upload CV → Process → Verify in DynamoDB
        """
        s3 = boto3.client('s3', region_name=aws_config['region'])
        dynamodb = boto3.resource('dynamodb', region_name=aws_config['region'])
        
        # Create test CV content
        test_cv_content = """
        CURRICULUM VITAE
        
        Name: Integration Test User
        Email: integration@test.com
        Phone: +39 333 9999999
        
        SKILLS: Python, AWS, Docker, Kubernetes
        
        EXPERIENCE:
        Senior Engineer (2020-present)
        
        EDUCATION: Master's Degree in Computer Science
        """
        
        # Upload to S3
        test_filename = f"cvs/integration_test_{datetime.now().timestamp()}.txt"
        s3.put_object(
            Bucket=aws_config['s3_bucket'],
            Key=test_filename,
            Body=test_cv_content.encode('utf-8'),
            Metadata={
                'job_position': 'Software Engineer',
                'uploaded_by': 'integration_test'
            }
        )
        
        # Wait for Lambda processing (max 30 seconds)
        table = dynamodb.Table(aws_config['dynamodb_table'])
        
        for _ in range(6):  # 6 attempts × 5 seconds = 30 seconds
            time.sleep(5)
            
            # Query DynamoDB for the processed candidate
            response = table.scan(
                FilterExpression='contains(candidate_name, :name)',
                ExpressionAttributeValues={':name': 'Integration Test'}
            )
            
            if response['Items']:
                # Candidate found!
                candidate = response['Items'][0]
                
                # Verify processing
                assert 'ranking_score' in candidate
                assert float(candidate['ranking_score']) > 0
                assert candidate['status'] == 'processed'
                
                # Cleanup
                table.delete_item(Key={'candidate_id': candidate['candidate_id']})
                s3.delete_object(Bucket=aws_config['s3_bucket'], Key=test_filename)
                
                return
        
        # If we reach here, test failed
        pytest.fail("CV not processed within 30 seconds")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
