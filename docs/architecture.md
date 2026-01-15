# Smart ATS Architecture

## System Overview

Smart ATS is a serverless, cloud-native Applicant Tracking System built on AWS. The system automates the process of CV screening, candidate ranking, and recruiter management.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER                             │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Flask Application (Docker Container)                       │    │
│  │  - User Interface for Recruiters                           │    │
│  │  - CV Upload                                                │    │
│  │  - Candidate Dashboard                                      │    │
│  └────────────────────────────────────────────────────────────┘    │
│                              ▲                                       │
│                              │ AWS Cognito Authentication           │
│                              ├──────────────────┐                   │
│                              │                  ▼                   │
│                    ┌─────────────────┐  ┌──────────────┐           │
│                    │  Elastic        │  │   Cognito    │           │
│                    │  Beanstalk      │  │  User Pool   │           │
│                    └─────────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API & STORAGE LAYER                          │
│  ┌───────────────┐     ┌─────────────┐     ┌─────────────────┐    │
│  │  API Gateway  │────▶│   S3 Bucket │────▶│  S3 Event       │    │
│  │   REST API    │     │   CV Files  │     │  Notification   │    │
│  └───────────────┘     └─────────────┘     └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                                      │
                                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ASYNC PROCESSING LAYER                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  SQS Queue (Buffer)                                          │   │
│  │  - Decouples upload from processing                          │   │
│  │  - Dead Letter Queue for failed messages                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Lambda Function (CV Processor Worker)                       │   │
│  │  ┌───────────────┐  ┌────────────────┐  ┌────────────────┐ │   │
│  │  │  CV Parser    │─▶│ Ranking Engine │─▶│ DynamoDB Write │ │   │
│  │  │  - PDF/DOCX   │  │ - Score calc   │  │ - Store result │ │   │
│  │  │  - Extract    │  │ - Skills match │  │                │ │   │
│  │  └───────────────┘  └────────────────┘  └────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                               │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  DynamoDB Table (smart-ats-candidates)                       │   │
│  │  - Candidate Information                                     │   │
│  │  - Ranking Scores                                            │   │
│  │  - Skills & Experience                                       │   │
│  │  - GSI: JobPositionRankingIndex                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer

**Technology**: Flask (Python), Docker, AWS Elastic Beanstalk

**Responsibilities**:
- Recruit authentication via Cognito
- CV upload interface
- Candidate dashboard with rankings
- Real-time status updates

**Key Features**:
- JWT-based authentication
- Responsive UI with modern CSS
- AJAX file uploads
- Session management

### 2. Authentication

**Technology**: AWS Cognito User Pool

**Features**:
- Username/password authentication
- JWT token generation
- Admin-managed user creation
- Secure password policies

### 3. Storage Layer

**Technology**: AWS S3

**Features**:
- Versioned CV storage
- Event notifications to SQS
- Lifecycle policies for old versions
- Private bucket with encryption

### 4. API Layer

**Technology**: AWS API Gateway (REST)

**Endpoints**:
- `GET /health` - Health check (no auth)
- Future: Additional management endpoints

**Features**:
- Cognito authorizer integration
- CORS configuration
- Request/response transformation

### 5. Async Processing

**Technology**: AWS SQS

**Queue Configuration**:
- Visibility timeout: 15 minutes
- Message retention: 14 days
- Long polling enabled
- Dead Letter Queue for failed processing

**Flow**:
1. S3 sends notification when CV is uploaded
2. Message queued in SQS
3. Lambda polls SQS and processes in batches
4. Automatic retries on failure (max 3 attempts)

### 6. Processing Layer

**Technology**: AWS Lambda (Python 3.9)

**Components**:

#### CV Parser (`utils/cv_parser.py`)
- Extracts text from PDF/DOCX files
- Parses: name, email, phone, skills, experience, education
- Pattern matching for contact info
- Keyword extraction for skills

#### Ranking Engine (`utils/ranking_engine.py`)
- Job-specific scoring criteria
- Weighted algorithm:
  - Skills match: 50%
  - Experience: 30%
  - Education: 20% (configurable)
- Outputs: score (0-100) and skills matched ratio

#### Handler (`handler.py`)
- SQS event processing
- Orchestrates parsing and ranking
- Writes results to DynamoDB
- Error handling and logging

### 7. Database Layer

**Technology**: AWS DynamoDB

**Table Schema**:
```
Primary Key: candidate_id (String)

Attributes:
- candidate_name
- email
- phone
- job_position
- ranking_score (Number)
- skills_matched
- experience_years
- education
- skills (List)
- s3_bucket, s3_key
- status
- upload_date
- uploaded_by

GSI: JobPositionRankingIndex
- Partition Key: job_position
- Sort Key: ranking_score (allows efficient ranking queries)
```

## Data Flow

### Upload Flow
1. Recruiter logs in via Cognito
2. Uploads CV through Flask UI
3. File stored in S3 with metadata
4. S3 triggers event → SQS queue
5. Lambda polls SQS (batch of up to 10)
6. Lambda downloads CV from S3
7. Parser extracts structured data
8. Ranking engine calculates score
9. Results stored in DynamoDB
10. Dashboard refreshes to show new candidate

### Query Flow
1. Recruiter accesses dashboard
2. Flask queries DynamoDB table
3. Results sorted by ranking_score (DESC)
4. Rendered in UI with color-coded scores

## Infrastructure as Code

All infrastructure is defined in `infrastructure/template.yaml` using AWS SAM:

- **Resources**: S3, SQS, Lambda, DynamoDB, API Gateway, Cognito
- **IAM Policies**: Least-privilege access for each service
- **Event Mappings**: S3 → SQS, SQS → Lambda
- **Outputs**: Exports for use in other stacks

## Deployment

See [README.md](../README.md) for deployment instructions.

## Security Considerations

1. **Authentication**: Cognito-based with strong password policies
2. **Authorization**: API Gateway with Cognito authorizer
3. **Encryption**: S3 server-side encryption, DynamoDB encryption at rest
4. **Network**: S3 bucket is private, Lambda in VPC (optional)
5. **IAM**: Minimal permissions per service
6. **Secrets**: Environment variables for sensitive data

## Scalability

- **Serverless**: Auto-scaling Lambda and DynamoDB
- **Queue**: SQS buffers load spikes
- **Batch Processing**: Lambda processes up to 10 CVs concurrently
- **Caching**: Future: CloudFront for static assets

## Monitoring

- **CloudWatch Logs**: Lambda execution logs
- **CloudWatch Metrics**: Lambda invocations, SQS queue depth
- **DynamoDB Metrics**: Read/write capacity
- **X-Ray**: Distributed tracing (optional)

## Cost Optimization

- **Pay-per-use**: Serverless architecture
- **DynamoDB**: On-demand billing
- **S3**: Lifecycle policies to delete old versions
- **Lambda**: Right-sized memory allocation

## Future Enhancements

1. **CI/CD Pipeline**: CodePipeline + CodeBuild
2. **Email Notifications**: SES integration for recruiter alerts
3. **Advanced ML**: Comprehend for sentiment analysis
4. **Resume Templates**: Standardized CV generation
5. **Interview Scheduling**: Calendar integration
