#  Smart ATS 

Sistema **Cloud-Native Serverless** per l'automazione della selezione dei candidati basato su architettura **AWS Event-Driven**, con ranking intelligente dei CV e pipeline CI/CD completa.

per informazioni più dettagliate consultare - `doc/README_spiegazione_progetto.md`
--- 

## Panoramica

Smart ATS automatizza il processo di screening CV utilizzando:        
-  **Processing asincrono** con Lambda & SQS
-  **Ranking automatico** basato su skills, experience, education
-  **Autenticazione** con AWS Cognito
-  **Dashboard web** per recruiter (Flask)
-  **Deploy automatico** con GitHub Actions


---

##  Architettura

```
┌─────────────┐
│   Browser   │ Recruiter accede via web
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│           AWS Cognito User Pool                     │
│  - Autenticazione                                   │
│  - User: admin@smartats.com                         |
|  - Password: SmartATS2026!                          |                           
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│        Flask Application                            │
│  - Dashboard per upload CV                          │
│  - Visualizzazione ranking candidati                │
└──────┬──────────────────────────┬───────────────────┘
       │                          │
       │ Upload CV                │ Query candidati
       ▼                          ▼
┌──────────────┐          ┌──────────────────┐
│  AWS S3      │          │   DynamoDB       │
│  Bucket      │          │   Table          │
│              │          │                  │
│ smart-ats-   │◄─────────│ Candidati        │
│ cvs-dev-*    │  Legge   │ processati       │
└──────┬───────┘          └──────▲───────────┘
       │                         │
       │ S3 Event                │ Scrive
       │ Notification            │ risultati
       ▼                         │
┌──────────────┐                 │
│  AWS SQS     │                 │
│  Queue       │                 │
│              │                 │
│ cv-queue-dev │                 │
└──────┬───────┘                 │
       │                         │
       │ Trigger                 │
       ▼                         │
┌──────────────────────────────┐ │
│   AWS Lambda Function        │ │
│   smart-ats-cv-processor     │─┘
│                              │
│  1. Download CV da S3        │
│  2. Parse PDF/DOCX           │
│  3. Extract info (skills...) │
│  4. Calculate ranking score  │
│  5. Write to DynamoDB        │
└──────────────────────────────┘
```

### Event-Driven Flow

1. **Upload** → Recruiter carica CV su S3 via dashboard
2. **Trigger** → notifica del evento S3 → coda SQS 
3. **Process** → SQS triggera Lambda function
4. **Parse** → Lambda estrae: nome, email, skills, esperienza, formazione
5. **Rank** → Algoritmo calcola score pesato (skills 60%, esperienza 30%, formazione 10%)
6. **Store** → Risultati salvati in DynamoDB
7. **Display** → Dashboard mostra candidati 

---

##  Servizi AWS (7 integrati)

| Servizio | Utilizzo | 
| **S3** | Storage CV | 
| **SQS** | Event Queue | 
| **Lambda** | CV Processing | 
| **DynamoDB** | Database Rankings | 
| **Cognito** | Authentication | 
| **API Gateway** | REST API | 
| **CloudWatch** | Monitoring |

---


 
##  Setup & Installatione


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




##  Struttura Progetto

```
.
├── .github/
│   └── workflows/
│       ├── deploy.yml          # Pipeline CI/CD
│       └── README.md           
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
├── infrastructure/             # AWS 
│   ├── template.yaml           
│   ├── samconfig.toml
│   └── parameters.json
├── lambda/                   
│   └── cv_processor/
│       ├── handler.py
│       ├── utils/
│       │   ├── cv_parser.py
│       │   └── ranking_engine.py
│       ├── tests/              # Unit tests
│       └── requirements.txt
├── scripts/                    
│   ├── deploy.sh
│   ├── test_upload.py
│   └── seed_dynamodb.py
└── tests/                      
    └── integration/
        └── test_aws_integration.py
```

---





##  Come Iniziare

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




