---
name: deploy-compute
description: Deploy credit-scoring compute workload and publish to connected Salesforce orgs
allowed-tools:
  - Bash
  - Read
  - Skill
triggers:
  - Deploy API
  - Deploy API to my org
  - Deploy app
  - Make live
  - Publish app
  - Deploy to production
  - Go live
  - Deploy compute
  - Deploy to Salesforce
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

🔗 Publishing to compute-demo-org...
🔗 Syncing API specification...
🔗 Registering compute extension...
✅ Published to compute-demo-org

**✨ Deployment complete! Your compute workload is live in compute-demo-org.**
```

## Deployment Flow

When the user requests deployment:

1. **Deploy compute workload**
   - Show: 🚀 Creating compute environment and deploying compute workload to Salesforce...
   - Silently execute: `git push heroku main`
   - Parse output and show friendly milestones: "📦 Building...", "📦 Installing dependencies...", "🚀 Finalizing..."
   - Show: ✅ Compute workload deployed successfully
   - DO NOT show raw bash output

2. **Publish to org**
   - Show: 🔗 Publishing to compute-demo-org...
   - Execute publish command
   - Show: ✅ Published to compute-demo-org

3. **Report success**
   - Show: **✨ Deployment complete! Your compute workload is live in compute-demo-org.**

## Implementation Steps

**MINIMAL/QUIET MODE: Do NOT use the Bash tool at all. Run commands silently and only output friendly status messages.**

### 1. Deploy workload
- Show: "🚀 Creating compute environment and deploying compute workload to Salesforce..."
- Silently run: `git push heroku $(git branch --show-current):main`
- Parse output for key milestones:
  - When building: Show "📦 Building..."
  - When installing deps: Show "📦 Installing dependencies..."
  - When deploying: Show "🚀 Finalizing deployment..."
- Show: "✅ Compute workload deployed successfully"
- DO NOT show raw bash commands or full output

### 2. Publish to org
- Show: "🔗 Publishing to compute-demo-org..."
- Silently run: `heroku salesforce:publish force-app/main/default/computeExtensions/CreditScoring/api-spec.yaml --app credit-scoring-compute --connection-name compute-demo-org --client-name CreditScoringAPI`
- Show: "✅ Published to compute-demo-org"
- DO NOT show command or output

### 6. Final message
```
**✨ Deployment complete! Your compute workload is live in compute-demo-org.**
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
- Mention "AppLink", "cloud", or technical service names
- **NEVER mention "Heroku" in any user-facing message**
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
❌ Publishing failed to compute-demo-org
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
  • compute-demo-org
```

**User:** "compute-demo-org"

**Output:**
```
🔍 Checking workspace status...
✅ Workspace is clean

🚀 Creating compute environment and deploying compute workload to Salesforce...
✅ Compute workload deployed successfully

🔗 Publishing to compute-demo-org...
✅ Published to compute-demo-org

**✨ Deployment complete! Your compute workload is live in compute-demo-org.**
```

### Deployment with org specified
**User:** "deploy app to compute-demo-org"

**Output:**
```
🔍 Checking workspace status...
✅ Workspace is clean

🚀 Creating compute environment and deploying compute workload to Salesforce...
✅ Compute workload deployed successfully

🔗 Publishing to compute-demo-org...
✅ Published to compute-demo-org

**✨ Deployment complete! Your compute workload is live in compute-demo-org.**
```

### With uncommitted changes
**User:** "make live"

**Output:**
```
Which org would you like to deploy to?
  • compute-demo-org
```

**User:** "compute-demo-org"

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

🔗 Publishing to compute-demo-org...
✅ Published to compute-demo-org

**✨ Deployment complete! Your compute workload is live in compute-demo-org.**
```

## Technical Details (for Claude, not shown to user)

**IMPORTANT: These technical details contain "Heroku" references for implementation only. NEVER mention "Heroku" in any user-facing output.**

### Commands used internally:
- Publish, silently run: `heroku salesforce:publish force-app/main/default/computeExtensions/CreditScoring --app credit-scoring-compute --connection-name compute-demo-org --client-name CreditScoringAPI`

### App details:
- App name: credit-scoring-compute
- API spec dir: force-app/main/default/computeExtensions/CreditScoring/
- Client name: CreditScoringAPI

### Available connections:
- compute-demo-org

**REMINDER: The word "Heroku" should NEVER appear in any message shown to the user.**
