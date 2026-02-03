# CI/CD Implementatione

##  Implementazione Completata

###  File Creati

#### 1. **GitHub Actions Workflow**
- `.github/workflows/deploy.yml` - Pipeline completa con 5 jobs

#### 2. **Unit Tests**
- `lambda/cv_processor/tests/test_cv_parser.py` - 12 test per CV Parser
- `lambda/cv_processor/tests/test_ranking_engine.py` - 18 test per Ranking Engine
- `lambda/cv_processor/tests/__init__.py` - Package marker

#### 3. **Integration Tests**
- `tests/integration/test_aws_integration.py` - Test end-to-end su AWS
- `tests/integration/__init__.py` - Package marker
- `tests/__init__.py` - Package marker

#### 4. **Documentazione**
- `.github/workflows/README.md` - Guida all'uso della pipeline

---

##  Pipeline Jobs

### 1. **Test** (Ad ogni push)
```yaml
- Checkout code
- Setup Python 3.13
- Install dependencies
- Run pytest with coverage
- Lint with flake8
```


### 2. **Validate** (Runs on: ogni push/PR)
```yaml
- Checkout code
- Install SAM CLI
- Validate CloudFormation template
```



### 3. **Deploy to Development** (Trigger: push su `develop`)
```yaml
- Configure AWS credentials (dev)
- SAM Build with Docker
- SAM Deploy to smart-ats-stack-dev
- Get stack outputs
- Run integration tests
```



### 4. **Deploy to Production** (Trigger: push su `main`)
```yaml
- Configure AWS credentials (prod)
- SAM Build with Docker
- SAM Deploy to smart-ats-stack-prod
- Smoke tests (API health check)
- Create GitHub Release
```


### 5. **Security Scan** (Runs on: ogni push/PR)
```yaml
- Run Checkov (IaC security)
- Run Bandit (Python security)     
- Upload security reports
```



### Unit Tests (30 test)

#### CV Parser (12 test):
- ✅ Email extraction
- ✅ Phone extraction
- ✅ Skills matching (case-insensitive)
- ✅ Experience years calculation
- ✅ Education level detection
- ✅ Complete CV parsing

#### Ranking Engine (18 test):
- ✅ Score calculation (perfect match)
- ✅ Score calculation (partial match)
- ✅ Different job positions
- ✅ Skills score (case-insensitive)
- ✅ Experience score (various scenarios)
- ✅ Education score (PhD, Master's, Bachelor's)

### Integration Tests (7 test):
- ✅ S3 bucket exists and versioning enabled
- ✅ DynamoDB table active with GSI
- ✅ SQS queue configured correctly
- ✅ Lambda function deployed
- ✅ **End-to-end CV processing** (upload → process → verify)

---






