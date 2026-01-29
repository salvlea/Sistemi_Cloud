# 🎯 Smart ATS - Applicant Tracking System

[![CI/CD Pipeline](https://github.com/salvlea/Sistemi_Cloud/actions/workflows/deploy.yml/badge.svg)](https://github.com/salvlea/Sistemi_Cloud/actions)
[![AWS](https://img.shields.io/badge/AWS-Deployed-orange)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-22%20passed-success)](https://github.com/salvlea/Sistemi_Cloud/actions)

Sistema **Cloud-Native Serverless** per l'automazione della selezione dei candidati basato su architettura **AWS Event-Driven**, con ranking intelligente dei CV e pipeline CI/CD completa.

---

## 📋 Panoramica

Smart ATS automatizza il processo di screening CV utilizzando:
- ⚡ **Processing asincrono** con Lambda & SQS
- 🤖 **Ranking automatico** basato su skills, experience, education
- 🔐 **Autenticazione** con AWS Cognito
- 📊 **Dashboard web** per recruiter (Flask)
- 🚀 **Deploy automatico** con GitHub Actions

**Stack Tecnologico**: AWS (S3, SQS, Lambda, DynamoDB, Cognito, API Gateway), Python, Flask, SAM

---

## 🏗️ Architettura

```
┌─────────────┐         ┌─────┐         ┌─────┐         ┌────────┐         ┌──────────┐
│   Frontend  │────────▶│ S3  │────────▶│ SQS │────────▶│ Lambda │────────▶│ DynamoDB │
│   (Flask)   │  upload │ CVs │  event  │Queue│ trigger │   CV   │  store  │ Rankings │
└─────────────┘         └─────┘         └─────┘         │Processor│         └──────────┘
      │                                                   └────────┘              │
      │ auth            ┌──────────┐                          │                  │
      └────────────────▶│ Cognito  │                     ┌────┴────┐            │
                        └──────────┘                     │PyPDF2   │            │
                                                         │python   │            │
                                                         │-docx    │            │
                                                         └─────────┘            │
                                                                                │
                        ┌──────────┐◀──────────────────────────────────────────┘
                        │   API    │           query
                        │ Gateway  │
                        └──────────┘
```

### Event-Driven Flow

1. **Upload** → Recruiter carica CV su S3 via dashboard
2. **Trigger** → S3 event notification → SQS queue
3. **Process** → SQS triggera Lambda function
4. **Parse** → Lambda estrae: nome, email, skills, experience, education
5. **Rank** → Algoritmo calcola score pesato (skills 60%, experience 30%, education 10%)
6. **Store** → Risultati salvati in DynamoDB
7. **Display** → Dashboard mostra candidati ranked

---

## ☁️ Servizi AWS (7 integrati)

| Servizio | Utilizzo | Configurazione |
|----------|----------|----------------|
| **S3** | Storage CV | Versioning + Encryption + Event Notifications |
| **SQS** | Event Queue | Standard Queue + DLQ, Visibility 15min |
| **Lambda** | CV Processing | Python 3.13, 512MB, Timeout 5min |
| **DynamoDB** | Database Rankings | GSI per job position, Encryption at-rest |
| **Cognito** | Authentication | User Pool per recruiter |
| **API Gateway** | REST API | Lambda proxy integration |
| **CloudWatch** | Monitoring | Logs + Metrics |

---

## 🚀 Deployment Status

### ✅ Production Environment

| Risorsa | Status | Region |
|---------|--------|--------|
| **Stack** | ✅ DEPLOYED | us-east-1 |
| **Lambda** | ✅ ACTIVE | - |
| **DynamoDB** | ✅ ACTIVE | - |
| **S3 Bucket** | ✅ ACTIVE | - |
| **CI/CD Pipeline** | ✅ SUCCESS | - |

**Ultimo Deploy**: 29 Gennaio 2026  
**Stack Name**: `smart-ats-stack-prod`  
**Account**: 055316374175

---

## 🔄 CI/CD Pipeline

### GitHub Actions - Pipeline Completa

**File**: `.github/workflows/deploy.yml`  
**Trigger**: Push su `main`  
**Status**: ✅ [**SUCCESS**](https://github.com/salvlea/Sistemi_Cloud/actions)

#### 4 Jobs Automatici

| Job | Tempo | Descrizione |
|-----|-------|-------------|
| **Run Tests** | ~22s | 22 unit tests, coverage 62%, lint flake8 |
| **Validate SAM** | ~36s | Validazione template CloudFormation |
| **Deploy Production** | ~1m14s | SAM build + deploy su AWS |
| **Security Scan** | ~23s | Checkov (IaC) + Bandit (Python) |

**Totale Execution Time**: ~2m 23s

---

## 🧪 Test Automation

### Test Results

```bash
============================= test summary ==============================
22 passed, 3 skipped, 1 warning in 0.57s
========================== test coverage ================================
TOTAL                            277    104    62%
=========================================================================
```

### Test Suite

**Unit Tests** (`lambda/cv_processor/tests/`):
- ✅ `test_cv_parser.py` - Parsing PDF/DOCX, extraction (email, phone, skills, education)
- ✅ `test_ranking_engine.py` - Score calculation, job-specific requirements

**Integration Tests** (`tests/integration/`):
- ✅ `test_aws_integration.py` - End-to-end S3→Lambda→DynamoDB flow

---

## 📦 Setup & Installation

### Prerequisiti

- Python 3.12+
- AWS CLI configurato
- AWS SAM CLI
- Git
- Docker (per SAM build)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/salvlea/Sistemi_Cloud.git
cd Sistemi_Cloud

# 2. Deploy Infrastructure
cd infrastructure
sam build --use-container
sam deploy --guided

# 3. Configure Frontend
cd ../frontend
cp .env.example .env
# Edit .env con output dello stack

# 4. Run Frontend Locally
python3 app.py
# Apri http://localhost:8080
```

### Deployment Automatico (CI/CD)

```bash
# Push su main triggera automaticamente la pipeline
git add .
git commit -m "feat: new feature"
git push origin main

# Monitora su: https://github.com/salvlea/Sistemi_Cloud/actions
```

---

## 🛠️ Infrastructure as Code

### AWS SAM Template

**File**: `infrastructure/template.yaml` (500+ lines)

**Risorse definite**:
- S3 Bucket con policy & notifications
- SQS Queue + DLQ
- Lambda Function con event source mapping
- DynamoDB Table con GSI
- Cognito User Pool
- API Gateway REST API
- IAM Roles & Policies

**Parametri**:
- `Environment` (dev/prod)
- `CognitoUserEmail`

---

## 💻 Codice

### Backend (Lambda)

**Handler** (`lambda/cv_processor/handler.py`):
- Entry point: `lambda_handler(event, context)`
- Input: SQS batch messages
- Processing: Download S3 → Parse → Rank → Store DynamoDB
- Error handling: DLQ per fallimenti

**Utilities**:
- `utils/cv_parser.py` - Parsing PDF (PyPDF2) & DOCX (python-docx)
- `utils/ranking_engine.py` - Weighted scoring algorithm

### Frontend (Flask)

**Routes** (`frontend/app.py`):
- `/` - Landing page
- `/login` - Cognito authentication
- `/dashboard` - Upload CV + view rankings
- `/logout` - Session cleanup

**Templates**:
- `templates/index.html`
- `templates/login.html`
- `templates/dashboard.html`

---

## 🔐 Sicurezza

### Implementazioni

- ✅ **Autenticazione**: AWS Cognito User Pool con JWT
- ✅ **Encryption at-rest**: DynamoDB & S3
- ✅ **Encryption in-transit**: HTTPS (API Gateway)
- ✅ **IAM**: Least privilege policies
- ✅ **Secrets**: GitHub Secrets per AWS credentials
- ✅ **Security Scanning**: Checkov + Bandit in pipeline

### Security Scan Results

10 warnings (non bloccanti) - best practices enterprise tipo:
- API Gateway logging
- Lambda concurrency limits
- Lambda environment encryption

**Nota**: Accettabili per progetto dimostrativo

---

## 📊 Statistiche Progetto

| Metrica | Valore |
|---------|--------|
| Servizi AWS | 7 |
| Linee di codice | ~1,500 |
| Test automatici | 25 (22 passed) |
| Test coverage | 62% |
| Pipeline jobs | 4 |
| Tempo deploy | ~2m 23s |
| Commits | 15+ |
| Documentazione | 7 file |

---

## 📚 Documentazione

- [**Presentazione Professore**](docs/PRESENTAZIONE_PROFESSORE.md) - Overview completo per presentazione
- [**Architecture**](docs/architecture.md) - Dettagli architettura sistema
- [**API Specs**](docs/api_specs.md) - Specifiche endpoint REST
- [**CI/CD Implementation**](docs/CI_CD_IMPLEMENTATION.md) - Documentazione pipeline
- [**Quick Start**](docs/QUICKSTART.md) - Guida deployment rapido

---

## 📂 Struttura Progetto

```
.
├── .github/
│   └── workflows/
│       ├── deploy.yml          # Pipeline CI/CD
│       └── README.md           # Docs pipeline
├── docs/                       # Documentazione
│   ├── architecture.md
│   ├── api_specs.md
│   ├── CI_CD_IMPLEMENTATION.md
│   └── PRESENTAZIONE_PROFESSORE.md
├── frontend/                   # Flask application
│   ├── app.py
│   ├── templates/
│   ├── static/
│   ├── Dockerfile
│   └── requirements.txt
├── infrastructure/             # AWS SAM
│   ├── template.yaml           # CloudFormation
│   ├── samconfig.toml
│   └── parameters.json
├── lambda/                     # Lambda functions
│   └── cv_processor/
│       ├── handler.py
│       ├── utils/
│       │   ├── cv_parser.py
│       │   └── ranking_engine.py
│       ├── tests/              # Unit tests
│       └── requirements.txt
├── scripts/                    # Utility scripts
│   ├── deploy.sh
│   ├── test_upload.py
│   └── seed_dynamodb.py
└── tests/                      # Integration tests
    └── integration/
        └── test_aws_integration.py
```

---

## 🧪 Testing

### Run Tests Locally

```bash
# Unit tests
cd lambda/cv_processor
pytest tests/ -v --cov

# Integration tests (richiede stack deployato)
export AWS_REGION=us-east-1
pytest tests/integration/ -v
```

### Lint

```bash
flake8 lambda/cv_processor --max-line-length=127
```

---

## 🎯 Features Implementate

### Core Functionality
- ✅ Upload CV (PDF, DOCX, TXT)
- ✅ Processing asincrono event-driven
- ✅ Parsing automatico CV (nome, email, phone, skills, experience, education)
- ✅ Ranking intelligente pesato per job position
- ✅ Dashboard visualizzazione candidati
- ✅ Autenticazione recruiter

### DevOps
- ✅ Infrastructure as Code (AWS SAM)
- ✅ CI/CD pipeline (GitHub Actions)
- ✅ Test automation (25 tests)
- ✅ Security scanning
- ✅ Automated deployment

### Monitoring
- ✅ CloudWatch Logs
- ✅ Lambda metrics
- ✅ Error tracking
- ✅ DLQ per failed messages

---

## 🔮 Possibili Evoluzioni

- 🤖 **ML Integration**: SageMaker per ranking basato su ML
- 📧 **Notifications**: SES per email ai candidati
- 📱 **Mobile App**: React Native frontend
- 🌍 **Multi-tenancy**: Support multiple companies
- 📊 **Analytics**: QuickSight dashboards
- 🔗 **Integrations**: Slack, Teams, external ATS APIs

---

## 🚦 Come Iniziare

### 1. Testa Localmente

```bash
# Clona e configura
git clone https://github.com/salvlea/Sistemi_Cloud.git
cd Sistemi_Cloud

# Deploy su AWS
cd infrastructure && sam deploy --guided

# Avvia frontend
cd ../frontend && python3 app.py
```

### 2. Verifica su GitHub

- [View Pipeline](https://github.com/salvlea/Sistemi_Cloud/actions) - Status CI/CD
- [View Code](https://github.com/salvlea/Sistemi_Cloud) - Repository

### 3. Verifica su AWS

```bash
# Stack status
aws cloudformation describe-stacks --stack-name smart-ats-stack-prod

# Lambda logs
aws logs tail /aws/lambda/smart-ats-cv-processor-dev --follow

# DynamoDB data
aws dynamodb scan --table-name smart-ats-candidates-dev
```

---

## 📞 Supporto

Per domande o supporto, consulta la [documentazione completa](docs/) o apri una issue su GitHub.

---

## 👨‍💻 Autore

**Salvatore Leanza**  
Progetto Sistemi Cloud - Magistrale  
Università degli Studi

---

## 📄 License

Questo progetto è stato sviluppato per scopi didattici.

---

## 🎓 Competenze Dimostrate

- ✅ Cloud-Native Architecture (AWS)
- ✅ Event-Driven Design
- ✅ Serverless Computing
- ✅ Infrastructure as Code (SAM)
- ✅ CI/CD Pipeline (GitHub Actions)
- ✅ Test Automation (pytest)
- ✅ Security Best Practices
- ✅ Python Development
- ✅ Web Development (Flask)
- ✅ DevOps Practices

---

**Made with ☁️ on AWS**
