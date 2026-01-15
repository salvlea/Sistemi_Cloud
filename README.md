# Smart ATS - Applicant Tracking System

Sistema Cloud-Native serverless per l'automazione della selezione dei candidati, basato su architettura AWS.

## 🏗️ Architettura

```
┌─────────────┐
│   Recruiter │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Flask Frontend │ ◄──► AWS Cognito (Auth)
│   (Beanstalk)   │
└────────┬────────┘
         │
         ▼
    ┌────────────┐
    │ API Gateway│
    └─────┬──────┘
          │
          ▼
      ┌───────┐
      │  SQS  │
      │ Queue │
      └───┬───┘
          │
          ▼
    ┌──────────┐         ┌─────────────┐
    │  Lambda  │────────►│  DynamoDB   │
    │ Worker   │         │  (Rankings) │
    └─────┬────┘         └─────────────┘
          │
          ▼
      ┌───────┐
      │   S3  │
      │  CVs  │
      └───────┘
```

## 📦 Componenti

- **Frontend**: Flask app containerizzata su Elastic Beanstalk
- **Autenticazione**: AWS Cognito User Pool
- **Storage**: S3 per CV caricati
- **API**: API Gateway REST
- **Queue**: SQS per elaborazione asincrona
- **Processing**: Lambda function per analisi CV
- **Database**: DynamoDB per ranking candidati
- **IaC**: AWS SAM per gestione infrastruttura
- **CI/CD**: GitHub → CodeBuild → CodePipeline

## 🚀 Setup Locale

### Prerequisiti
- Python 3.9+
- Docker
- AWS CLI configurato
- AWS SAM CLI
- Git

### Installazione

```bash
# Clone repository
git clone https://github.com/salvlea/Sistemi_Cloud.git
cd Sistemi_Cloud

# Install frontend dependencies
cd frontend
pip install -r requirements.txt

# Install Lambda dependencies
cd ../lambda/cv_processor
pip install -r requirements.txt
```

## 🔧 Deploy

### 1. Deploy Infrastructure (SAM)

```bash
cd infrastructure
sam build
sam deploy --guided
```

### 2. Build & Push Docker Image

```bash
cd frontend
docker build -t smart-ats-frontend .
# Push to ECR (see deploy script)
```

### 3. Deploy Frontend to Beanstalk

```bash
./scripts/deploy.sh
```

## 📚 Struttura Progetto

```
├── frontend/              # Flask application
├── lambda/                # Lambda functions
├── infrastructure/        # SAM templates
├── scripts/               # Utility scripts
└── docs/                  # Documentation
```

## 🧪 Testing

```bash
# Test S3 upload
python scripts/test_upload.py

# Test Lambda locally
cd lambda/cv_processor
sam local invoke
```

## 📖 Documentation

- [Architecture Details](docs/architecture.md)
- [API Specifications](docs/api_specs.md)

## 👨‍💻 Autore

Salvatore Leanza - Progetto Sistemi Cloud