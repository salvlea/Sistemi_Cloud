import json
import boto3
import os
from datetime import datetime
from utils.cv_parser import CVParser
from utils.ranking_engine import RankingEngine

# AWS Clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'smart-ats-candidates')

def lambda_handler(event, context):
    """
    Lambda handler triggered by SQS messages.
    Processes CV files from S3, extracts information, and stores rankings in DynamoDB.
    """
    print(f"Received event: {json.dumps(event)}")
    
    # Process each SQS message
    for record in event['Records']:
        try:
            # Parse SQS message
            message_body = json.loads(record['body'])
            
            # Handle S3 event notification (if message comes from S3)
            if 'Records' in message_body:
                s3_event = message_body['Records'][0]
                bucket = s3_event['s3']['bucket']['name']
                key = s3_event['s3']['object']['key']
            else:
                # Direct message format
                bucket = message_body.get('s3_bucket')
                key = message_body.get('s3_key')
                
            print(f"Processing CV from S3: s3://{bucket}/{key}")
            
            # Download CV from S3
            response = s3_client.get_object(Bucket=bucket, Key=key)
            cv_content = response['Body'].read()
            
            # Get metadata
            metadata = response.get('Metadata', {})
            job_position = metadata.get('job_position', 'General')
            uploaded_by = metadata.get('uploaded_by', 'unknown')
            
            # Parse CV
            parser = CVParser()
            cv_data = parser.parse(cv_content, key)
            
            # Calculate ranking
            ranker = RankingEngine()
            ranking_score, skills_matched = ranker.calculate_score(cv_data, job_position)
            
            # Store in DynamoDB
            table = dynamodb.Table(DYNAMODB_TABLE)
            item = {
                'candidate_id': f"{cv_data['name']}_{datetime.now().timestamp()}",
                'candidate_name': cv_data['name'],
                'email': cv_data.get('email', 'N/A'),
                'phone': cv_data.get('phone', 'N/A'),
                'job_position': job_position,
                'ranking_score': ranking_score,
                'skills_matched': skills_matched,
                'experience_years': cv_data.get('experience_years', 0),
                'education': cv_data.get('education', 'N/A'),
                'skills': cv_data.get('skills', []),
                's3_bucket': bucket,
                's3_key': key,
                'status': 'processed',
                'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'uploaded_by': uploaded_by
            }
            
            table.put_item(Item=item)
            
            print(f"Successfully processed candidate: {cv_data['name']} with score: {ranking_score}")
            
        except Exception as e:
            print(f"Error processing record: {str(e)}")
            # Don't raise exception to avoid retrying failed messages infinitely
            continue
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Processing completed'})
    }
