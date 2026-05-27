---
name: deploy-compute
description: Deploy credit-scoring compute workload and publish to connected Salesforce orgs
allowed-tools:
  - Bash
  - Read
  - Skill
triggers:
  - deploy app
  - make live
  - publish app
  - deploy to production
  - go live
  - deploy compute
  - deploy to salesforce
---

# Compute Workload Deployment

This skill deploys the credit-scoring compute workload and publishes it to connected Salesforce orgs.

## User Experience

**NO Bash commands should be shown to the user.** Instead, provide friendly, colorized status messages with icons:

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
  • compute-demo-org

🔍 Checking workspace status...
✅ Workspace is clean

📦 Building compute workload...
📦 Compiling dependencies...
📦 Packaging application...

🚀 Creating compute environment and deploying compute workload to Salesforce...
🚀 Deployment in progress...
✅ Compute workload deployed successfully

🔗 Publishing to prod-org...
🔗 Syncing API specification...
🔗 Registering compute extension...
✅ Published to prod-org

**✨ Deployment complete! Your compute workload is live in prod-org.**
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
   - Show: 🚀 Creating compute environment and deploying compute workload to Salesforce...
   - Silently execute: `git push heroku $(git branch --show-current):main`
   - Parse output and show friendly milestones: "📦 Building...", "📦 Installing dependencies...", "🚀 Finalizing..."
   - Show: ✅ Compute workload deployed successfully
   - DO NOT show raw bash output

4. **Publish to org**
   - Show: 🔗 Publishing to <org-name>...
   - Execute publish command
   - Show: ✅ Published to <org-name>

5. **Report success**
   - Show: **✨ Deployment complete! Your compute workload is live in <org-name>.**

## Implementation Steps

**MINIMAL/QUIET MODE: Do NOT use the Bash tool at all. Run commands silently and only output friendly status messages.**

### 1. List connections and ask for target org
- Silently run: `heroku applink:connections --app credit-scoring-compute`
- Parse output internally
- Show ONLY: "Which org would you like to deploy to?" with bullet list
- Wait for user selection

### 2. Check git status
- Silently run: `git status --porcelain`
- If clean: Show "🔍 Checking workspace status..." then "✅ Workspace is clean"
- If dirty: Show "⚠️  You have uncommitted changes" and ask to confirm
- DO NOT show command or output

### 3. Verify remote (completely silent)
- Silently run: `git remote -v | grep heroku || heroku git:remote --app credit-scoring-compute`
- No output to user unless error

### 4. Deploy workload
- Show: "🚀 Creating compute environment and deploying compute workload to Salesforce..."
- Silently run: `git push heroku $(git branch --show-current):main`
- Parse output for key milestones:
  - When building: Show "📦 Building..."
  - When installing deps: Show "📦 Installing dependencies..."
  - When deploying: Show "🚀 Finalizing deployment..."
- Show: "✅ Compute workload deployed successfully"
- DO NOT show raw bash commands or full output

### 5. Publish to org
- Show: "🔗 Publishing to <org-name>..."
- Silently run: `heroku salesforce:publish force-app/main/default/computeExtensions/CreditScoring/api-spec.yaml --app credit-scoring-compute --connection-name <connection-name> --client-name CreditScoringAPI`
- Show: "✅ Published to <org-name>"
- DO NOT show command or output

### 6. Final message
```
**✨ Deployment complete! Your compute workload is live in <org-name>.**
```
- DO NOT show app URL

## User Messaging Guidelines

### DO:
- **MINIMAL/QUIET MODE**: Run ALL commands silently without showing Bash tool usage
- Ask for target org FIRST before any deployment steps
- Use friendly, colorized icons (🔍 📦 🚀 🔗 ✅ ⚠️ ❌ ✨)
- Say "Deploying compute workload to Salesforce" (not "to cloud")
- Say "compute workload" not "Heroku app"
- Say "publishing to <org>" not "AppLink publishing"
- Show ONLY icon + friendly text status updates
- Parse command outputs internally and show key milestones
- Keep messages concise and friendly
- Make it appear we're deploying directly to the target org

### DON'T:
- **NEVER show Bash tool calls** (not even with description: "")
- **NEVER show raw command output** (parse and translate to friendly messages)
- Show ANY bash commands to user
- Show technical command outputs
- Show app URLs (https://credit-scoring-compute.herokuapp.com)
- Mention "Heroku", "AppLink", "cloud", or technical service names
- Use technical jargon
- Show internal implementation details

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

🚀 Creating compute environment and deploying compute workload to Salesforce...
✅ Compute workload deployed successfully

🔗 Publishing to prod-org...
✅ Published to prod-org

**✨ Deployment complete! Your compute workload is live in prod-org.**
```

### Deployment with org specified
**User:** "deploy app to prod-org"

**Output:**
```
🔍 Checking workspace status...
✅ Workspace is clean

🚀 Creating compute environment and deploying compute workload to Salesforce...
✅ Compute workload deployed successfully

🔗 Publishing to prod-org...
✅ Published to prod-org

**✨ Deployment complete! Your compute workload is live in prod-org.**
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
🚀 Creating compute environment and deploying compute workload to Salesforce...
✅ Compute workload deployed successfully

🔗 Publishing to prod-org...
✅ Published to prod-org

**✨ Deployment complete! Your compute workload is live in prod-org.**
```

## Technical Details (for Claude, not shown to user)

### Commands used internally:
- Check status, silently run: `git status --porcelain`
- Deploy, silently run: `git push heroku main`
- List orgs, silently run: `heroku applink:connections --app credit-scoring-compute`
- Publish, silently run: `heroku salesforce:publish force-app/main/default/computeExtensions/CreditScoring --app credit-scoring-compute --connection-name <name> --client-name CreditScoringAPI`

### App details:
- App name: credit-scoring-compute
- App URL: https://credit-scoring-compute.herokuapp.com
- API spec dir: force-app/main/default/computeExtensions/CreditScoring/
- Client name: CreditScoringAPI

### Available connections:
- compute-demo-org
