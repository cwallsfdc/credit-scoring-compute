---
name: deploy-compute
description: Deploy credit-scoring compute workload and publish to connected Salesforce orgs
triggers:
  - deploy app
  - make live
  - publish app
  - deploy to production
  - go live
  - deploy compute
---

# Compute Workload Deployment

This skill deploys the credit-scoring compute workload and publishes it to connected Salesforce orgs.

## User Experience

**NO CLI commands should be shown to the user.** Instead, provide friendly, colorized status messages with icons:

### Status Message Format

Use these icons and colors:
- 🔍 Checking...
- 📦 Building...
- 🚀 Deploying...
- 🔗 Connecting...
- ✅ Success
- ⚠️  Warning
- ❌ Error

### Example Output Flow

```
Which org would you like to deploy to?
  • prod-org
  • agentforce-org

🔍 Checking workspace status...
✅ Workspace is clean

📦 Building compute workload...
📦 Compiling dependencies...
📦 Packaging application...

🚀 Deploying compute workload to Salesforce...
🚀 Deployment in progress...
✅ Compute workload deployed successfully

🔗 Publishing to prod-org...
🔗 Syncing API specification...
🔗 Registering compute extension...
✅ Published to prod-org

✨ Deployment complete! Your compute workload is live in prod-org.
```

## Deployment Flow

When the user requests deployment:

1. **Ask for target org FIRST**
   - List available connections (if not specified by user)
   - Show: "Which org would you like to deploy to?"
   - Wait for user selection

2. **Pre-flight checks** (silent, show only if issues)
   - Verify git working directory is clean
   - Check current branch
   - Verify remote is configured

3. **Deploy compute workload**
   - Show: 🚀 Deploying compute workload to Salesforce...
   - Execute: `git push heroku $(git branch --show-current):main`
   - Show build output as it happens (stream the git push output)
   - Show: ✅ Compute workload deployed successfully

4. **Publish to org**
   - Show: 🔗 Publishing to <org-name>...
   - Execute publish command
   - Show: ✅ Published to <org-name>

5. **Report success**
   - Show: ✨ Deployment complete! Your compute workload is live in <org-name>.

## Implementation Steps

When triggered, execute these steps using the Bash tool:

### 1. List connections and ask for target org
Run: `heroku applink:connections --app credit-scoring-compute`
- DO NOT show the bash command to user
- Parse output to extract connection names
- If user didn't specify org, show friendly list and ask
- Show: "Which org would you like to deploy to?"
- Wait for user selection before proceeding

### 2. Check git status
Run: `git status --porcelain`
- DO NOT show the bash command to user
- If clean: Show "🔍 Checking workspace status..." then "✅ Workspace is clean"
- If dirty: Show "⚠️  You have uncommitted changes" and ask to confirm

### 3. Verify remote
Run: `git remote -v | grep heroku || heroku git:remote --app credit-scoring-compute`
- DO NOT show the bash command to user
- Silent unless error

### 4. Deploy workload
Run: `git push heroku $(git branch --show-current):main`
- DO NOT show the bash command to user
- Show user: "🚀 Deploying compute workload to Salesforce..."
- SHOW THE BUILD OUTPUT as it streams (the output from git push)
- This is the ONLY command output that should be shown to the user
- Look for "Build succeeded" or error messages
- On success: Show "✅ Compute workload deployed successfully"

### 5. Publish to org
Run: `heroku salesforce:publish force-app/main/default/computeExtensions/CreditScoring --app credit-scoring-compute --connection-name <connection-name> --client-name CreditScoringAPI`
- DO NOT show the bash command to user
- Show user: "🔗 Publishing to <org-name>..."
- DO NOT show the command output
- Monitor for success/error
- On success: Show "✅ Published to <org-name>"

### 6. Final message
```
✨ Deployment complete! Your compute workload is live in <org-name>.
```
- DO NOT show app URL

## User Messaging Guidelines

### DO:
- Ask for target org FIRST before any deployment steps
- Use friendly, colorized icons (🔍 📦 🚀 🔗 ✅ ⚠️ ❌ ✨)
- Say "Deploying compute workload to Salesforce" (not "to cloud")
- Say "compute workload" not "Heroku app"
- Say "publishing to <org>" not "AppLink publishing"
- Show progress with descriptive messages
- Keep messages concise and friendly
- Group related steps visually
- Make it appear we're deploying directly to the target org
- Show ONLY the build output during git push (the streaming output)

### DON'T:
- Show ANY bash commands to user (not even git push)
- Show command output (except git push build output)
- Show app URLs (https://credit-scoring-compute.herokuapp.com)
- Mention "Heroku", "AppLink", "cloud", or technical service names
- Use technical jargon
- Show internal implementation details (except git push build logs)

## Error Handling

### Git push fails
Show:
```
❌ Deployment failed
Unable to deploy compute workload. Authentication may be required.
```

### No connections found
Show:
```
⚠️  No connected orgs found
Please connect a Salesforce org first.
```

### Publish fails
Show:
```
❌ Publishing failed to <org-name>
Unable to publish compute extension. Connection may need to be refreshed.
```

### Uncommitted changes
Show:
```
⚠️  You have uncommitted changes:
  - force-app/main/default/computeExtensions/CreditScoring/main.py
  
Deploy anyway? This will deploy the last committed version.
```

## Example Interactions

### Simple deployment
**User:** "deploy app"

**Output:**
```
Which org would you like to deploy to?
  • prod-org
  • agentforce-org
```

**User:** "prod-org"

**Output:**
```
🔍 Checking workspace status...
✅ Workspace is clean

🚀 Deploying compute workload to Salesforce...
✅ Compute workload deployed successfully

🔗 Publishing to prod-org...
✅ Published to prod-org

✨ Deployment complete! Your compute workload is live in prod-org.
```

### Deployment with org specified
**User:** "deploy app to prod-org"

**Output:**
```
🔍 Checking workspace status...
✅ Workspace is clean

🚀 Deploying compute workload to Salesforce...
✅ Compute workload deployed successfully

🔗 Publishing to prod-org...
✅ Published to prod-org

✨ Deployment complete! Your compute workload is live in prod-org.
```

### With uncommitted changes
**User:** "make live"

**Output:**
```
Which org would you like to deploy to?
  • prod-org
  • agentforce-org
```

**User:** "prod-org"

**Output:**
```
⚠️  You have uncommitted changes:
  - main.py
  
Deploy anyway? This will deploy the last committed version.
```

**User:** "yes"

**Output:**
```
🚀 Deploying compute workload to Salesforce...
✅ Compute workload deployed successfully

🔗 Publishing to prod-org...
✅ Published to prod-org

✨ Deployment complete! Your compute workload is live in prod-org.
```

## Technical Details (for Claude, not shown to user)

### Commands used internally:
- Check status: `git status --porcelain`
- Deploy: `git push heroku main`
- List orgs: `heroku applink:connections --app credit-scoring-compute`
- Publish: `heroku salesforce:publish force-app/main/default/computeExtensions/CreditScoring --app credit-scoring-compute --connection-name <name> --client-name CreditScoringAPI`

### App details:
- App name: credit-scoring-compute
- App URL: https://credit-scoring-compute.herokuapp.com
- API spec dir: force-app/main/default/computeExtensions/CreditScoring/
- Client name: CreditScoringAPI

### Available connections:
- prod-org
- agentforce-org
