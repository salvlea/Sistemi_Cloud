#!/usr/bin/env python3
"""
Test script to upload a sample CV to S3 bucket
"""

import boto3
import os
import sys
from datetime import datetime

def upload_test_cv():
    # Get bucket name from environment or command line
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    if not bucket_name and len(sys.argv) > 1:
        bucket_name = sys.argv[1]
    
    if not bucket_name:
        print("Error: Please provide S3 bucket name")
        print("Usage: python test_upload.py <bucket-name>")
        print("   OR: Set S3_BUCKET_NAME environment variable")
        sys.exit(1)
    
    # Create sample CV content
    sample_cv = """
JOHN DOE
Software Engineer

Email: john.doe@email.com
Phone: +1-555-0123

EDUCATION
Bachelor's Degree in Computer Science
University of Technology, 2018-2022

EXPERIENCE
Software Engineer at Tech Company
2022 - Present
- Developed web applications using Python and JavaScript
- Worked with AWS services including Lambda and DynamoDB
- Implemented CI/CD pipelines with Docker

SKILLS
Python, JavaScript, React, Node.js, AWS, Docker, Git, SQL, Agile
    """
    
    # Upload to S3
    s3_client = boto3.client('s3')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    s3_key = f"cvs/test_{timestamp}_john_doe.txt"
    
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=sample_cv.encode('utf-8'),
            Metadata={
                'job_position': 'Software Engineer',
                'uploaded_by': 'test_script'
            }
        )
        
        print(f"✓ Successfully uploaded test CV to: s3://{bucket_name}/{s3_key}")
        print(f"✓ The Lambda function should process this CV automatically")
        print(f"✓ Check DynamoDB table for results in a few seconds")
        
    except Exception as e:
        print(f"✗ Error uploading CV: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    upload_test_cv()
