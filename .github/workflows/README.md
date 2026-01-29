# CI/CD Pipeline - Smart ATS

Questa directory contiene la configurazione della pipeline CI/CD per il progetto Smart ATS.

## 🔄 Pipeline Overview

La pipeline automatizza:
- **Testing**: Unit test e integration test
- **Validation**: Lint e security scan
- **Deployment**: Deploy automatico su AWS (dev/prod)
- **Monitoring**: Smoke tests post-deployment

## 📋 Workflow Jobs

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

## 🔐 Secrets Richiesti

Configurare in **Settings → Secrets and variables → Actions**:

### Development
- `AWS_ACCESS_KEY_ID`: Access key per account AWS dev
- `AWS_SECRET_ACCESS_KEY`: Secret key per account AWS dev

### Production
- `AWS_ACCESS_KEY_ID_PROD`: Access key per account AWS prod
- `AWS_SECRET_ACCESS_KEY_PROD`: Secret key per account AWS prod

## 🚀 Come Usare

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

## 📊 Monitoring

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

## 🧪 Test Locali

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

## 🛡️ Environments

### Development
- **Branch**: `develop`
- **Stack**: `smart-ats-stack-dev`
- **Protection**: None (auto-deploy)

### Production
- **Branch**: `main`
- **Stack**: `smart-ats-stack-prod`
- **Protection**: Manual approval richiesta

Per configurare protection rules:
`Settings → Environments → production → Required reviewers`

## 📈 Best Practices

1. **Feature Branches**: Crea branch da `develop` per nuove feature
2. **Pull Requests**: Sempre via PR per merge su `develop` o `main`
3. **Code Review**: Almeno 1 approvazione prima del merge
4. **Semantic Versioning**: Usa conventional commits (`feat:`, `fix:`, `docs:`)
5. **Rollback**: Se deploy fallisce, pipeline fa rollback automatico

## 🔧 Troubleshooting

### Pipeline fallisce sui test
```bash
# Esegui test localmente
pytest tests/ -v
```

### Deploy fallisce
```bash
# Verifica stack AWS
aws cloudformation describe-stacks --stack-name smart-ats-stack-dev

# Verifica stack events
aws cloudformation describe-stack-events --stack-name smart-ats-stack-dev
```

### Security scan warnings
- Controllare artifact "security-reports"
- Risolvere issue critici prima del merge

## 📚 Risorse

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-command-reference.html)
- [Pytest Documentation](https://docs.pytest.org/)
