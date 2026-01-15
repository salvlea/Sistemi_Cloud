#!/usr/bin/env python3
"""
Seed DynamoDB table with sample candidate data
"""

import boto3
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

def seed_dynamodb():
    # Get table name
    table_name = os.environ.get('DYNAMODB_TABLE', 'smart-ats-candidates-dev')
    if len(sys.argv) > 1:
        table_name = sys.argv[1]
    
    print(f"Seeding table: {table_name}")
    
    # Sample candidates
    candidates = [
        {
            'candidate_id': 'alice_2026010001',
            'candidate_name': 'Alice Johnson',
            'email': 'alice.j@email.com',
            'phone': '+1-555-0101',
            'job_position': 'Software Engineer',
            'ranking_score': Decimal('87.5'),
            'skills_matched': '4/5',
            'experience_years': 5,
            'education': "Master's Degree",
            'skills': ['Python', 'Java', 'AWS', 'Docker'],
            's3_bucket': 'sample-bucket',
            's3_key': 'cvs/alice_cv.pdf',
            'status': 'processed',
            'upload_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'uploaded_by': 'admin'
        },
        {
            'candidate_id': 'bob_2026010002',
            'candidate_name': 'Bob Smith',
            'email': 'bob.smith@email.com',
            'phone': '+1-555-0102',
            'job_position': 'Cloud Engineer',
            'ranking_score': Decimal('92.3'),
            'skills_matched': '5/5',
            'experience_years': 7,
            'education': "Bachelor's Degree",
            'skills': ['AWS', 'Docker', 'Kubernetes', 'Terraform', 'DevOps'],
            's3_bucket': 'sample-bucket',
            's3_key': 'cvs/bob_cv.pdf',
            'status': 'processed',
            'upload_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'uploaded_by': 'admin'
        },
        {
            'candidate_id': 'carol_2026010003',
            'candidate_name': 'Carol Williams',
            'email': 'carol.w@email.com',
            'phone': '+1-555-0103',
            'job_position': 'Data Scientist',
            'ranking_score': Decimal('78.9'),
            'skills_matched': '3/4',
            'experience_years': 3,
            'education': 'PhD',
            'skills': ['Python', 'Machine Learning', 'SQL'],
            's3_bucket': 'sample-bucket',
            's3_key': 'cvs/carol_cv.pdf',
            'status': 'processed',
            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'uploaded_by': 'admin'
        }
    ]
    
    # Insert into DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    try:
        for candidate in candidates:
            table.put_item(Item=candidate)
            print(f"✓ Added: {candidate['candidate_name']}")
        
        print(f"\n✓ Successfully seeded {len(candidates)} candidates")
        
    except Exception as e:
        print(f"✗ Error seeding data: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    seed_dynamodb()
