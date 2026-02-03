# Presentazione Progetto Smart ATS - Sistema Cloud-Native su AWS

**Studente**: Salvatore Leanza  
**Corso**: Sistemi Cloud  
**Anno Accademico**: 2025/2026

---


## 1. Introduzione al Progetto 

### Il Problema

Le aziende ricevono centinaia di CV per ogni posizione aperta. Il processo manuale di screening è:
- **Lento**: Un recruiter impiega 5-10 minuti per CV
- **Inconsistente**: Valutazioni soggettive
- **Non scalabile**: Impossibile gestire grandi volumi

### La Soluzione: Smart ATS

Un **Applicant Tracking System intelligente** che:
- **Automatizza** il parsing dei CV (PDF, DOCX)
- **Analizza** competenze, esperienza ed educazione
- **Classifica** i candidati con uno score oggettivo
- **Scala automaticamente** grazie all'architettura serverless

---

## 2. Architettura Cloud-Native 

### Diagramma Architettura

```
┌─────────────┐
│   Browser   │ Recruiter accede via web
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│           AWS Cognito User Pool                     │
│  - Autenticazione JWT                               │
│  - User: admin@smartats.com                         │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│        Flask Application (Docker + Gunicorn)        │
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

### Principi Architetturali

#### **1. Event-Driven Architecture**
- Ogni upload CV genera un evento S3
- Eventi processati in modo **asincrono** tramite SQS
- **Disaccoppiamento** tra componenti

#### **2. Serverless-First**
- **Zero gestione server**: AWS gestisce infrastruttura
- **Auto-scaling**: Scala automaticamente con il carico
- **Pay-per-use**: Costi solo quando in uso

#### **3. Microservices Pattern**
- Ogni componente ha una **singola responsabilità**
- Componenti **indipendentemente scalabili**
- Facile manutenzione e testing

---

## 3. Tecnologie AWS Utilizzate 

### 3.1 AWS S3 (Simple Storage Service)

**Ruolo**: Storage per i file CV caricati

**Configurazione**:
```yaml
CVStorageBucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketName: !Sub smart-ats-cvs-${Environment}-${AWS::AccountId}
    VersioningConfiguration:
      Status: Enabled  
    PublicAccessBlockConfiguration:
      BlockPublicAcls: true
      BlockPublicPolicy: true
      IgnorePublicAcls: true
      RestrictPublicBuckets: true 
```

**Funzionalità Implementate**:
1. **Event Notifications**: Invia eventi a SQS quando un file viene caricato
2. **Versioning**: Mantiene storico modifiche
4. **Encryption**: Dati cifrati at-rest (AES-256)

**Perché S3?**
- ✅ Scalabilità illimitata
- ✅ Storage economico 
- ✅ Integrazione nativa con altri servizi AWS

---

### 3.2 AWS SQS (Simple Queue Service)

**Ruolo**: Coda messaggi per processing asincrono

**Configurazione**:
```yaml
CVProcessingQueue:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: !Sub smart-ats-cv-queue-${Environment}
    VisibilityTimeout: 900  # 15 minuti
    MessageRetentionPeriod: 1209600  # 14 giorni
    ReceiveMessageWaitTimeSeconds: 20  # Long polling
    RedrivePolicy:
      deadLetterTargetArn: !GetAtt CVProcessingDLQ.Arn
      maxReceiveCount: 3  # Dopo 3 fallimenti → DLQ
```


**Vantaggi SQS**:
- ✅ **Buffering**: Assorbe picchi di traffico
- ✅ **Retry automatico**: Riprova messaggi falliti
- ✅ **At-least-once delivery**: Garantisce elaborazione
- ✅ **Long polling**: Riduce costi (meno richieste API)

**Flusso Messaggi**:
```python
# S3 invia messaggio quando CV caricato
{
  "Records": [{
    "s3": {
      "bucket": {"name": "smart-ats-cvs-dev-*"},
      "object": {"key": "cvs/john_doe_20260116.pdf"}
    }
  }]
}
```

---

### 3.3 AWS Lambda

**Ruolo**: Serverless compute per processare CV

**Configurazione**:
```yaml
CVProcessorFunction:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName: !Sub smart-ats-cv-processor-${Environment}
    Runtime: python3.13
    Handler: handler.lambda_handler
    MemorySize: 512  
    Timeout: 300     
    Environment:
      Variables:
        DYNAMODB_TABLE: !Ref CandidatesTable
        S3_BUCKET: !Ref CVStorageBucket
    Events:
      SQSEvent:
        Type: SQS
        Properties:
          Queue: !GetAtt CVProcessingQueue.Arn
          BatchSize: 10  # Processa fino a 10 CV alla volta
```



**Vantaggi Lambda**:
- ✅ **Zero gestione server**: AWS gestisce OS, patching, scaling
- ✅ **Scaling automatico**: Da 0 a 1000+ istanze in secondi
- ✅ **Costo**: Solo per tempo di esecuzione effettivo
- ✅ **Integrazione nativa**: Con SQS, S3, DynamoDB


---

### 3.4 AWS DynamoDB

**Ruolo**: Database NoSQL per memorizzare candidati e ranking

**Configurazione**:
```yaml
CandidatesTable:
  Type: AWS::DynamoDB::Table
  Properties:
    TableName: !Sub smart-ats-candidates-${Environment}
    BillingMode: PAY_PER_REQUEST  
    AttributeDefinitions:
      - AttributeName: candidate_id
        AttributeType: S  
      - AttributeName: job_position
        AttributeType: S
      - AttributeName: ranking_score
        AttributeType: N 
    KeySchema:
      - AttributeName: candidate_id
        KeyType: HASH
    GlobalSecondaryIndexes:
      - IndexName: JobPositionRankingIndex
        KeySchema:
          - AttributeName: job_position
            KeyType: HASH
          - AttributeName: ranking_score
            KeyType: RANGE 
        Projection:
          ProjectionType: ALL
```

**Schema Item**:
```json
{
  "candidate_id": "John Doe_1768587600.576779",
  "candidate_name": "John Doe",
  "email": "john.doe@email.com",
  "phone": "+39 333 1234567",
  "job_position": "Software Engineer",
  "ranking_score": 87.5,
  "skills": ["Python", "AWS", "Docker", "JavaScript"],
  "experience_years": 5,
  "education": "Master's Degree",
  "status": "processed",
  "upload_date": "2026-01-20 17:00:00"
}
```

**Query Ottimizzate con GSI**:
```python
# Query candidati per posizione, ordinati per score 
response = table.query(
    IndexName='JobPositionRankingIndex',
    KeyConditionExpression='job_position = :pos',
    ExpressionAttributeValues={':pos': 'Software Engineer'},
    ScanIndexForward=False  # Ordine decrescente
)
```

**Vantaggi DynamoDB**:
- ✅ **Performance**: pochissima latenza anche con milioni di record
- ✅ **Auto-scaling**: Scala read/write capacity automaticamente
- ✅ **Global Tables**: Multi-region replication
- ✅ **No maintenance**: Full managed

---

### 3.5 AWS Cognito

**Ruolo**: Autenticazione e gestione utenti

**Configurazione**:
```yaml
UserPool:
  Type: AWS::Cognito::UserPool
  Properties:
    UserPoolName: !Sub smart-ats-users-${Environment}
    AutoVerifiedAttributes:
      - email
    UsernameAttributes:
      - email  # Login con email invece di username
    Policies:
      PasswordPolicy:
        MinimumLength: 8
        RequireUppercase: true
        RequireLowercase: true
        RequireNumbers: true
    AdminCreateUserConfig:
      AllowAdminCreateUserOnly: true  # Solo admin crea utenti
```



**Vantaggi Cognito**:
- ✅ **Sicurezza**: Password hashing,
- ✅ **Scalabilità**: Gestisce milioni di utenti
- ✅ **Integrazione**: Con API Gateway, Lambda

---

### 3.6 AWS API Gateway

**Ruolo**: REST API endpoint (attualmente usato minimamente, espandibile)

**Configurazione**:
```yaml
SmartATSApi:
  Type: AWS::Serverless::Api
  Properties:
    Name: !Sub smart-ats-api-${Environment}
    StageName: !Ref Environment
    Auth:
      DefaultAuthorizer: CognitoAuthorizer
      Authorizers:
        CognitoAuthorizer:
          UserPoolArn: !GetAtt UserPool.Arn
    Cors:
      AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
      AllowHeaders: "'Content-Type,Authorization'"
      AllowOrigin: "'*'"
```


---

### 3.7 AWS SAM (Serverless Application Model)

**Ruolo**: Infrastructure as Code

**Template SAM** (`template.yaml`):
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Smart ATS - Serverless Applicant Tracking System

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

Globals:
  Function:
    Timeout: 300
    MemorySize: 512
    Runtime: python3.13
    Environment:
      Variables:
        ENVIRONMENT: !Ref Environment

Resources:
  # S3, SQS, Lambda, DynamoDB, Cognito, API Gateway...
  # (come visto nelle sezioni precedenti)

Outputs:
  S3BucketName:
    Value: !Ref CVStorageBucket
  ApiEndpoint:
    Value: !Sub https://${SmartATSApi}.execute-api.${AWS::Region}.amazonaws.com/${Environment}
  UserPoolId:
    Value: !Ref UserPool
```


**Vantaggi SAM**:
- ✅ **Reproducibilità**: Stessa infrastruttura in dev/staging/prod
- ✅ **Versioning**: Template in Git
- ✅ **Rollback automatico**: Se deploy fallisce
- ✅ **Local testing**: `sam local invoke` per test locali

---

