# Claude Skills for Credit Scoring Compute

## Available Skills

### deploy-compute

Deploys the credit-scoring compute workload and publishes it to connected Salesforce orgs.

**Triggers:**
- "deploy app"
- "make live"
- "publish app"
- "deploy to production"
- "go live"
- "deploy compute"

**Connected Orgs:**
- `prod-org` - Production Salesforce org
- `agentforce-org` - Agentforce demo org

**Example Usage:**
```
User: deploy app
Claude: Provides friendly status updates with icons, asks which org to publish to

User: make live on prod-org
Claude: Deploys and publishes directly to prod-org with friendly messages

User: deploy compute
Claude: Deploys workload with colorized progress indicators
```

**User Experience:**
- ✅ No CLI commands shown
- ✅ Friendly, colorized status messages
- ✅ Icons for each step (🔍 📦 🚀 🔗 ✅)
- ✅ Clean, modern output
- ✅ Progress indicators

**What Users See:**
```
Which org would you like to deploy to?
  • prod-org
  • agentforce-org

(User selects prod-org)

🔍 Checking workspace status...
✅ Workspace is clean

🚀 Deploying compute workload to Salesforce...
✅ Compute workload deployed successfully

🔗 Publishing to prod-org...
✅ Published to prod-org

✨ Deployment complete! Your compute workload is live in prod-org.
```

## Prerequisites

- Heroku CLI installed ✓
- Logged into Heroku ✓
- Git remote configured ✓
- AppLink connections established ✓
