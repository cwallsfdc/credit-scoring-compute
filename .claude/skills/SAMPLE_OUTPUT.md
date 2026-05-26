# Sample Output: Deploy App

This document shows exactly what users will see when they use the `deploy-compute` skill.

---

## Scenario 1: Simple Deployment

**User Input:**
```
deploy app
```

**Claude Output:**
```
Which org would you like to deploy to?
  • prod-org
  • agentforce-org
```

**User:** `prod-org`

**Claude Output:**
```
🔍 Checking workspace status...
✅ Workspace is clean

🚀 Deploying compute workload to Salesforce...

Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 324 bytes | 324.00 KiB/s, done.
Total 3 (delta 2), reused 0 (delta 0), pack-reused 0
remote: Compressing source files... done.
remote: Building source:
remote: -----> Building on the Heroku-22 stack
remote: -----> Using buildpack: heroku/python
remote: -----> Python app detected
remote: -----> Installing python-3.11.4
remote: -----> Installing pip 23.1.2, setuptools 67.8.0 and wheel 0.40.0
remote: -----> Installing requirements with pip
remote:        Collecting fastapi==0.109.0
remote:        Collecting uvicorn==0.27.0
remote:        Successfully installed fastapi uvicorn pydantic
remote: -----> Discovering process types
remote:        Procfile declares types -> web
remote: -----> Compressing...
remote: -----> Launching...
remote:        Released v42
remote:        https://credit-scoring-compute.herokuapp.com/ deployed to Heroku

✅ Compute workload deployed successfully

🔗 Publishing to prod-org...
✅ Published to prod-org

✨ Deployment complete! Your compute workload is live in prod-org.
```

---

## Scenario 2: Deployment with Specified Org

**User Input:**
```
deploy app to prod-org
```

**Claude Output:**
```
🔍 Checking workspace status...
✅ Workspace is clean

🚀 Deploying compute workload to Salesforce...
✅ Compute workload deployed successfully

🔗 Publishing to prod-org...
✅ Published to prod-org

✨ Deployment complete! Your compute workload is live in prod-org.
```

---

## Scenario 3: Deployment with Uncommitted Changes

**User Input:**
```
make live
```

**Claude Output:**
```
Which org would you like to deploy to?
  • prod-org
  • agentforce-org
```

**User:** `agentforce-org`

**Claude Output:**
```
⚠️  You have uncommitted changes:
  • main.py
  • api-spec.yaml

Deploy anyway? This will deploy the last committed version, not your current changes.
```

**User:** `yes, deploy anyway`

**Claude Output:**
```
🚀 Deploying compute workload to Salesforce...
✅ Compute workload deployed successfully

🔗 Publishing to agentforce-org...
✅ Published to agentforce-org

✨ Deployment complete! Your compute workload is live in agentforce-org.
```

---

## Scenario 4: Deployment Error

**User Input:**
```
deploy app to prod-org
```

**Claude Output:**
```
🔍 Checking workspace status...
✅ Workspace is clean

🚀 Deploying compute workload to Salesforce...
❌ Deployment failed

Unable to deploy compute workload. Authentication may be required.
Please check your credentials and try again.
```

---

## Scenario 5: Publishing Error

**User Input:**
```
go live on prod-org
```

**Claude Output:**
```
🔍 Checking workspace status...
✅ Workspace is clean

🚀 Deploying compute workload to Salesforce...
✅ Compute workload deployed successfully

🔗 Publishing to prod-org...
❌ Publishing failed to prod-org

Unable to publish compute extension. The connection may need to be refreshed.
```

---

## Scenario 6: Multiple Steps Visible

**User Input:**
```
deploy compute
```

**Claude Output:**
```
Which org would you like to deploy to?
  • prod-org
  • agentforce-org
```

**User:** `prod-org`

**Claude Output:**
```
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

---

## Key Characteristics

### ✅ What Users See:
- Org selection prompt FIRST
- Friendly icons (🔍 📦 🚀 🔗 ✅ ⚠️ ❌ ✨)
- "Deploying compute workload to Salesforce" (not "to cloud")
- Clear status messages
- Progress indicators
- Clean, readable output
- Appears to deploy directly to target org

### ❌ What Users DON'T See:
- CLI commands (`git push`, `heroku publish`)
- App URLs (https://credit-scoring-compute.herokuapp.com)
- Raw build logs
- Technical service names ("Heroku", "AppLink", "cloud")
- Error stack traces
- Implementation details

### 🎨 Design Principles:
- **Ask First**: Get target org before starting deployment
- **Conversational**: Feels like talking to a helpful assistant
- **Visual**: Icons make status immediately clear
- **Progressive**: Shows what's happening in real-time
- **Forgiving**: Clear error messages with suggested fixes
- **Concise**: No unnecessary verbosity
- **Salesforce-Native**: Appears to deploy directly to Salesforce org
