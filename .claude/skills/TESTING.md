# Testing the heroku-deploy Skill

## Prerequisites Checklist

Before testing the deployment skill, verify:

- [x] Heroku CLI installed (`heroku --version`)
- [x] Logged into Heroku (`heroku auth:whoami`)
- [x] Git remote configured (`git remote -v` shows heroku)
- [x] AppLink connections exist (`heroku applink:connections --app credit-scoring-compute`)
- [x] API spec directory exists with required files

## Test Scenarios

### 1. Full Deployment (Push + Publish)

**Command:** "deploy app"

**Expected Flow:**
1. Check git status
2. Push to Heroku: `git push heroku main`
3. Wait for build completion
4. List connections: prod-org, agentforce-org
5. Ask user which connection to publish to
6. Publish API spec to selected org
7. Report success with app URL

### 2. Deployment with Specified Org

**Command:** "deploy app to prod-org"

**Expected Flow:**
1. Check git status
2. Push to Heroku
3. Directly publish to prod-org (no prompt)
4. Report success

### 3. Heroku Only (No Publish)

**Command:** "push to heroku but don't publish"

**Expected Flow:**
1. Check git status
2. Push to Heroku
3. Skip AppLink publishing
4. Report deployment success

### 4. With Uncommitted Changes

**Scenario:** Modify a file without committing

**Expected Flow:**
1. Detect uncommitted changes via `git status --porcelain`
2. Ask user: "You have uncommitted changes. Deploy anyway?"
3. If yes, continue with deployment
4. If no, abort and suggest committing first

## Manual Testing Commands

```bash
# Test git status check
git status --porcelain

# Test Heroku push (dry-run not available, use with caution)
# git push heroku main

# Test connection listing
heroku applink:connections --app credit-scoring-compute

# Test publish command (replace connection-name)
heroku salesforce:publish force-app/main/default/computeExtensions/CreditScoring \
  --app credit-scoring-compute \
  --connection-name prod-org \
  --client-name CreditScoringAPI

# Check app status
heroku ps --app credit-scoring-compute

# View recent logs
heroku logs --tail --num 50 --app credit-scoring-compute
```

## Verification

After deployment:

1. **Check Heroku Dashboard**
   - Visit: https://dashboard.heroku.com/apps/credit-scoring-compute
   - Verify latest dyno is running
   - Check build was successful

2. **Check AppLink in Salesforce**
   - Navigate to Setup → Custom Code → Compute Extensions
   - Verify CreditScoring extension appears
   - Check last published timestamp

3. **Test API Endpoint**
   ```bash
   curl https://credit-scoring-compute.herokuapp.com/api/credit-scoring/ \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"accountId": "test"}'
   ```

## Expected Outcomes

✅ **Success Indicators:**
- Git push completes without errors
- Build log shows "Build succeeded"
- Dyno starts successfully
- AppLink publish completes
- Salesforce org shows updated API spec

❌ **Failure Indicators:**
- Authentication errors → Run `heroku login`
- Build failures → Check `heroku logs`
- Publish errors → Verify connection with `heroku applink:info`
- App crashes → Check application logs

## Rollback

If deployment fails:

```bash
# Roll back to previous release
heroku rollback --app credit-scoring-compute

# Check release history
heroku releases --app credit-scoring-compute

# View specific release
heroku releases:info v123 --app credit-scoring-compute
```
