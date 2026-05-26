# Credit Scoring Compute - Deployment Guide

This repository includes a Claude skill for automated deployment to Heroku and publishing via AppLink.

## Quick Deploy

Simply say to Claude:

```
deploy app
```

Or with a specific target:

```
deploy app to prod-org
```

## What Happens

1. **Git Check** - Verifies working directory status
2. **Heroku Push** - Deploys code to Heroku app `credit-scoring-compute`
3. **Build Monitor** - Watches build logs for completion
4. **Connection List** - Shows available Salesforce org connections
5. **AppLink Publish** - Publishes API spec to selected org

## Available Connections

- `prod-org` - Production Salesforce org
- `agentforce-org` - Agentforce demo org

## Manual Commands

If you prefer manual control:

### Deploy to Heroku
```bash
git push heroku main
```

### Check Build Status
```bash
heroku logs --tail --app credit-scoring-compute
```

### List Connections
```bash
heroku applink:connections --app credit-scoring-compute
```

### Publish to Org
```bash
heroku salesforce:publish force-app/main/default/computeExtensions/CreditScoring \
  --app credit-scoring-compute \
  --connection-name prod-org \
  --client-name CreditScoringAPI
```

### Check App Status
```bash
heroku ps --app credit-scoring-compute
```

## App Details

- **Heroku App:** credit-scoring-compute
- **App URL:** https://credit-scoring-compute.herokuapp.com
- **API Spec:** `force-app/main/default/computeExtensions/CreditScoring/api-spec.yaml`
- **Process Type:** web (Python/FastAPI with AppLink service mesh)

## Rollback

If something goes wrong:

```bash
# View releases
heroku releases --app credit-scoring-compute

# Rollback to previous version
heroku rollback --app credit-scoring-compute
```

## Troubleshooting

### Authentication Issues
```bash
heroku login
heroku auth:whoami
```

### Build Failures
```bash
heroku logs --tail --app credit-scoring-compute
```

### AppLink Issues
```bash
heroku applink:info --app credit-scoring-compute
```

### Connection Problems
Re-authenticate the connection in the Heroku dashboard or Salesforce Setup.

## Files Deployed

The AppLink publish command deploys from:
```
force-app/main/default/computeExtensions/CreditScoring/
├── api-spec.yaml              # OpenAPI 3.0 specification
├── main.py                    # Python application
├── requirements.txt           # Python dependencies
├── Procfile                   # Process definition
├── CreditScoring.computeExtension  # Salesforce metadata
└── tests/                     # Test files
```

## Environment Variables

Set via Heroku dashboard or CLI:
- `SCORING_METHOD` - Algorithm selection (altman_z or logistic_regression)
- `APP_PORT` - Application port (default: 3000)

```bash
heroku config:set SCORING_METHOD=altman_z --app credit-scoring-compute
```

## More Information

- [Heroku AppLink Documentation](https://devcenter.heroku.com/articles/heroku-applink)
- [Heroku AppLink CLI](https://devcenter.heroku.com/articles/heroku-applink-cli)
- Skill Documentation: `.claude/skills/README.md`
