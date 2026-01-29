# 🎯 Smart ATS - Applicant Tracking System

[![CI/CD Pipeline](https://github.com/salvlea/Sistemi_Cloud/actions/workflows/deploy.yml/badge.svg)](https://github.com/salvlea/Sistemi_Cloud/actions)
[![AWS](https://img.shields.io/badge/AWS-Deployed-orange)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-22%20passed-success)](https://github.com/salvlea/Sistemi_Cloud/actions)

Sistema **Cloud-Native Serverless** per l'automazione della selezione dei candidati basato su architettura **AWS Event-Driven**, con ranking intelligente dei CV e pipeline CI/CD completa.

---

## Panoramica

Smart ATS automatizza il processo di screening CV utilizzando:
- ⚡ **Processing asincrono** con Lambda & SQS
- 🤖 **Ranking automatico** basato su skills, experience, education
- 🔐 **Autenticazione** con AWS Cognito
- 📊 **Dashboard web** per recruiter (Flask)
- 🚀 **Deploy automatico** con GitHub Actions

**Stack Tecnologico**: AWS (S3, SQS, Lambda, DynamoDB, Cognito, API Gateway), Python, Flask, SAM

---

##  Architettura

```
┌─────────────┐         ┌─────┐         ┌─────┐         ┌────────┐         ┌──────────┐
│   Frontend  │────────▶│ S3  │────────▶│ SQS │────────▶│ Lambda │────────▶│ DynamoDB │
│   (Flask)   │  upload │ CVs │  event  │Queue│ trigger │   CV   │  store  │ Rankings │
└─────────────┘         └─────┘         └─────┘         │Processor│        └──────────┘
      │                                                   ────────┘             │
      │ auth            ┌──────────┐                          │                 │
      └────────────────▶│ Cognito  │                     ┌────┴────┐            │
                        └──────────┘                     │PyPDF2   │            │
                                                         │python   │            │
                                                         │-docx    │            │
                                                         └─────────┘            │
                                                                                │
                        ┌──────────┐◀──────────────────────────────────────────-┘
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



##  Setup & Installation

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




