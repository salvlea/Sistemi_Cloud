# CI/CD Pipeline - Smart ATS

Questa directory contiene la configurazione della pipeline 

##  Pipeline Overview

La pipeline automatizza:
- **Testing**: Unit test e integration test
- **Validation**: Lint e security scan
- **Deployment**: Deploy automatico su AWS (dev/prod)
- **Monitoring**: Smoke tests post-deployment

##  Workflow 

### 1. Test (`test`)
- Esegue unit tests con pytest
- Genera coverage report
- Lint con flake8

### 2. Validate (`validate`)
- Valida template SAM
- Verifica sintassi CloudFormation

### 3. Deploy to Development (`deploy-dev`)
- **Trigger**: Push su branch `develop`
- Deploy automatico su environment `dev`
- Esegue integration tests

### 4. Deploy to Production (`deploy-prod`)
- **Trigger**: Push su branch `main`
- Deploy su environment `prod` con protezione
- Smoke tests
- Crea GitHub Release automatica

### 5. Security Scan (`security-scan`)
- Scansione IaC con Checkov
- Scansione Python con Bandit
- Upload report come artifact

##  Credenziali Richieste

Configurare in **Settings → Secrets and variables → Actions**:

### Development
- `AWS_ACCESS_KEY_ID`: Access key per account AWS dev
- `AWS_SECRET_ACCESS_KEY`: Secret key per account AWS dev

### Production
- `AWS_ACCESS_KEY_ID_PROD`: Access key per account AWS prod
- `AWS_SECRET_ACCESS_KEY_PROD`: Secret key per account AWS prod

## Come Usare

### Deploy manuale
```bash
# Trigger workflow manualmente
gh workflow run deploy.yml
```

### Deploy automatico

**Development**:
```bash
git checkout develop
git add .
git commit -m "feat: new feature"
git push origin develop
# → Pipeline deploya automaticamente su dev
```

**Production**:
```bash
git checkout main
git merge develop
git push origin main
# → Pipeline deploya automaticamente su prod
```

## Monitoraggio 

### Visualizzare Workflow
```bash
# Lista workflow runs
gh run list

# Visualizza dettagli run
gh run view <run-id>

# Visualizza logs
gh run view <run-id> --log
```

### Dashboard GitHub Actions
Vai su: https://github.com/salvlea/Sistemi_Cloud/actions

##  Test Locali

### Unit Tests
```bash
cd lambda/cv_processor
pip install -r requirements.txt
pip install pytest pytest-cov
pytest tests/ -v --cov
```

### Integration Tests
```bash
export AWS_REGION=us-east-1
pytest tests/integration/ -v
```
