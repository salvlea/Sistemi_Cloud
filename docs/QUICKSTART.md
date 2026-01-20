# Smart ATS - Quick Start Guide

## Prerequisites

Before deploying Smart ATS, ensure you have:

- ✅ **AWS Account** with appropriate permissions
- ✅ **AWS CLI** installed and configured (`aws configure`)
- ✅ **SAM CLI** installed ([Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))
- ✅ **Docker** installed and running
- ✅ **Python 3.9+** installed
- ✅ **Git** for version control

## Deployment Steps

### 1. Clone Repository

```bash
git clone https://github.com/salvlea/Sistemi_Cloud.git
cd Sistemi_Cloud
```

### 2. Deploy Infrastructure

Run the automated deployment script:

```bash
./scripts/deploy.sh dev us-east-1
```

This will:
- Build Lambda functions
- Deploy SAM stack (S3, SQS, Lambda, DynamoDB, API Gateway, Cognito)
- Create `.env` file with AWS resource IDs

**Note**: First deployment takes 5-10 minutes.

### 3. Set Cognito User Password

After deployment, set a password for the admin user:

```bash
# Get User Pool ID from stack outputs
USER_POOL_ID=$(aws cloudformation describe-stacks \
  --stack-name smart-ats-stack-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
  --output text)

# Set password
aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username admin@smartats.com \
  --password 'MySecurePassword123!' \
  --permanent
```

### 4. Test the System

#### Option A: Seed Sample Data

```bash
cd scripts
python seed_dynamodb.py smart-ats-candidates-dev
```

#### Option B: Upload Test CV

```bash
# Get S3 bucket name
S3_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name smart-ats-stack-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
  --output text)

# Upload test CV
python test_upload.py $S3_BUCKET
```

Wait ~10 seconds for processing, then check DynamoDB:

```bash
aws dynamodb scan --table-name smart-ats-candidates-dev
```

### 5. Run Flask Frontend Locally

```bash
cd frontend

# Install dependencies
pip install -r requirements.txt

# Run app
python app.py
```

Open browser: **http://localhost:8080**

Login with:
- **Username**: `admin@smartats.com`
- **Password**: `MySecurePassword123!` (or what you set)

## Project Structure Overview

```
Sistemi_Cloud/
├── frontend/              # Flask web application
│   ├── app.py            # Main Flask app
│   ├── Dockerfile        # Container definition
│   └── templates/        # HTML templates
├── lambda/               # Lambda functions
│   └── cv_processor/     # CV processing worker
│       ├── handler.py    # Lambda entry point
│       └── utils/        # Parser & ranking
├── infrastructure/       # AWS SAM templates
│   └── template.yaml     # Infrastructure as Code
├── scripts/              # Deployment & testing
│   ├── deploy.sh         # Main deployment script
│   ├── test_upload.py    # Test CV upload
│   └── seed_dynamodb.py  # Seed sample data
└── docs/                 # Documentation
    ├── architecture.md   # System architecture
    └── api_specs.md      # API documentation
```

## Next Steps

### Deploy to Elastic Beanstalk (Production)

1. **Create Elastic Beanstalk Application**:
   ```bash
   eb init -p docker smart-ats-frontend --region us-east-1
   ```

2. **Create Environment**:
   ```bash
   eb create smart-ats-prod
   ```

3. **Deploy**:
   ```bash
   eb deploy
   ```

### Set Up CI/CD Pipeline

Create AWS CodePipeline:
- **Source**: GitHub repository
- **Build**: CodeBuild (build Docker image)
- **Deploy**: Elastic Beanstalk

### Monitor & Logs

- **Lambda Logs**: CloudWatch Logs → `/aws/lambda/smart-ats-cv-processor-dev`
- **SQS Queue**: Monitor queue depth in CloudWatch
- **DynamoDB**: Check table metrics

## Common Issues

### Issue: SAM build fails

**Solution**: Ensure Docker is running:
```bash
docker ps
```

### Issue: Cannot login to Cognito

**Solution**: Verify user password was set:
```bash
aws cognito-idp admin-get-user \
  --user-pool-id $USER_POOL_ID \
  --username admin@smartats.com
```

### Issue: Lambda not processing CVs

**Solution**: Check SQS queue and Lambda logs:
```bash
# Check queue
aws sqs get-queue-attributes \
  --queue-url $(aws sqs get-queue-url --queue-name smart-ats-cv-queue-dev --query QueueUrl --output text) \
  --attribute-names All

# Check Lambda logs
aws logs tail /aws/lambda/smart-ats-cv-processor-dev --follow
```

## Cleanup (Delete Resources)

To delete all AWS resources:

```bash
aws cloudformation delete-stack --stack-name smart-ats-stack-dev

# Manually delete ECR repository if created
aws ecr delete-repository --repository-name smart-ats-frontend --force
```

## Support

For questions or issues:
- 📧 Email: salvatore.leanza@example.com
- 📁 GitHub: https://github.com/salvlea/Sistemi_Cloud
- 📖 Docs: See `docs/` folder

---

**Congratulations! Your Smart ATS system is now deployed! 🎉**
