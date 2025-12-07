# Payment News Discord Bot - Complete Setup Guide

**👋 Welcome!** This guide will walk you through setting up your Payment News Discord Bot from scratch, even if you've never worked with bots, APIs, or cloud hosting before.

**Time Required:** 45-60 minutes for first-time setup

**What You'll Build:** A Discord bot that automatically fetches payment industry news, summarizes it using AI, and posts daily digests to your Discord channel.

---

## Table of Contents
1. [Prerequisites & Tools](#1-prerequisites--tools)
2. [Local Development Setup](#2-local-development-setup)
3. [Version Control with Git & GitHub](#3-version-control-with-git--github)
4. [Cloud Deployment on Railway](#4-cloud-deployment-on-railway)
5. [Maintenance & Updates](#5-maintenance--updates)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Prerequisites & Tools

### What You Need to Install

#### 1.1 Python (The Programming Language)

**What is Python?** Python is the programming language this bot is written in. Think of it like the language the computer understands to run your bot.

**Installation:**

**For macOS:**
```bash
# Check if Python is already installed
python3 --version

# If not installed, download from python.org or use Homebrew:
brew install python@3.9
```

**For Windows:**
1. Download Python 3.9 or higher from [python.org](https://www.python.org/downloads/)
2. **Important:** Check "Add Python to PATH" during installation
3. Click "Install Now"

**Verify Installation:**
```bash
python3 --version
# Should show: Python 3.9.x or higher
```

---

#### 1.2 Git (Version Control System)

**What is Git?** Git tracks changes to your code over time, like a super-powered "undo" button. It lets you save different versions of your project and collaborate with others.

**Installation:**

**For macOS:**
```bash
# Check if Git is already installed
git --version

# If not installed:
brew install git
```

**For Windows:**
1. Download Git from [git-scm.com](https://git-scm.com/download/win)
2. Use default settings during installation
3. Select "Git from the command line and also from 3rd-party software"

**Verify Installation:**
```bash
git --version
# Should show: git version 2.x.x
```

---

#### 1.3 Code Editor (VS Code Recommended)

**What is a Code Editor?** A specialized text editor designed for writing code, with helpful features like syntax highlighting and error detection.

**Installation:**
1. Download [Visual Studio Code](https://code.visualstudio.com/)
2. Install with default settings
3. (Optional) Install Python extension: Open VS Code → Extensions (left sidebar) → Search "Python" → Install

**Alternative:** You can use any text editor (Sublime Text, Atom, etc.) or even your system's default terminal.

---

#### 1.4 Discord Account & Server

**What is Discord?** A communication platform where your bot will post news updates.

**Setup Steps:**

1. **Create Discord Account** (if you don't have one)
   - Go to [discord.com](https://discord.com)
   - Click "Register"
   - Follow the signup process

2. **Create a Discord Server** (or use an existing one)
   - Open Discord
   - Click the "+" button on the left sidebar
   - Choose "Create My Own"
   - Name your server (e.g., "Payment News Test")

3. **Create a Channel for News**
   - Right-click your server name
   - Select "Create Channel"
   - Name it (e.g., "payment-news")
   - Click "Create Channel"

---

### Getting API Keys

API keys are like passwords that let your bot access external services. You'll need two of them.

#### 1.5 Discord Bot Token

**What is a Bot Token?** A secret key that lets your program control a Discord bot account.

**Steps to Get Your Discord Bot Token:**

1. **Go to Discord Developer Portal**
   - Visit [discord.com/developers/applications](https://discord.com/developers/applications)
   - Click "New Application"
   - Name it (e.g., "Payment News Bot")
   - Click "Create"

2. **Create the Bot**
   - Click "Bot" in the left sidebar
   - Click "Add Bot"
   - Click "Yes, do it!"

3. **Get the Token**
   - Under "TOKEN" section, click "Reset Token"
   - Click "Copy" and save it somewhere safe
   - ⚠️ **Never share this token publicly!**

4. **Enable Message Content Intent**
   - Scroll down to "Privileged Gateway Intents"
   - Enable "Message Content Intent"
   - Click "Save Changes"

5. **Invite Bot to Your Server**
   - Click "OAuth2" → "URL Generator" in left sidebar
   - Under "SCOPES", check `bot`
   - Under "BOT PERMISSIONS", check:
     - ✅ Send Messages
     - ✅ Send Messages in Threads
     - ✅ Embed Links
     - ✅ Read Message History
     - ✅ Add Reactions
   - Copy the generated URL at the bottom
   - Paste it in your browser
   - Select your server and click "Authorize"

6. **Get Your Channel ID**
   - In Discord, go to User Settings → Advanced
   - Enable "Developer Mode"
   - Right-click the channel where you want news posted
   - Click "Copy ID"
   - Save this ID

---

#### 1.6 Anthropic API Key

**What is Anthropic?** A company that provides AI models (Claude) that will summarize news articles for your bot.

**Steps to Get Your Anthropic API Key:**

1. **Create Anthropic Account**
   - Go to [console.anthropic.com](https://console.anthropic.com/)
   - Click "Sign Up"
   - Complete the signup process

2. **Get API Key**
   - Once logged in, go to "API Keys" section
   - Click "Create Key"
   - Name it (e.g., "Payment News Bot")
   - Click "Create Key"
   - Copy the key (starts with `sk-ant-`)
   - ⚠️ **Save it immediately - you can't see it again!**

3. **Add Credits** (if needed)
   - Anthropic requires credits to use the API
   - Go to "Billing" section
   - Add a payment method and purchase credits ($5-10 is enough to start)

---

## 2. Local Development Setup

### 2.1 Download the Project

**Option A: Clone from GitHub (Recommended)**

Open your terminal (Terminal on macOS, Command Prompt or Git Bash on Windows):

```bash
# Navigate to where you want to store the project
cd ~/Documents/Projects

# Clone the repository
git clone https://github.com/ratanon97/PaymentNewsDiscordBot.git

# Enter the project folder
cd PaymentNewsDiscordBot
```

**Option B: Download ZIP**

1. Go to [github.com/ratanon97/PaymentNewsDiscordBot](https://github.com/ratanon97/PaymentNewsDiscordBot)
2. Click green "Code" button → "Download ZIP"
3. Extract the ZIP file
4. Open terminal and navigate to the extracted folder

---

### 2.2 Understanding Project Structure

Here's what each file does:

```
PaymentNewsBot/
├── bot.py                      # 🤖 Main Discord bot logic and commands
├── news_fetcher.py             # 📰 Fetches RSS feeds and processes with AI
├── database.py                 # 💾 Stores articles in SQLite database
├── scheduler.py                # ⏰ Handles daily digest scheduling
├── config.py                   # ⚙️ Configuration settings
├── requirements.txt            # 📦 List of Python packages needed
├── Procfile                    # 🚂 Tells Railway how to run the bot
├── runtime.txt                 # 🐍 Specifies Python version for Railway
├── .env                        # 🔐 YOUR secrets (you'll create this)
├── .env.example               # 📝 Template for .env file
├── .gitignore                 # 🚫 Files Git should ignore
├── README.md                  # 📖 Project overview
├── REQUIREMENTS.md            # 📋 Technical requirements
├── SECURITY_IMPROVEMENTS.md   # 🔒 Security documentation
└── SETUP_GUIDE.md            # 📚 This guide!
```

**Key Files You'll Work With:**
- `.env` - Contains your secret API keys
- `config.py` - Customize RSS feeds, schedule, etc.
- `requirements.txt` - Python packages to install

---

### 2.3 Set Up Python Virtual Environment

**What is a Virtual Environment?** An isolated space for your project's Python packages, so they don't conflict with other Python projects on your computer.

**Create Virtual Environment:**

```bash
# Make sure you're in the project folder
cd PaymentNewsDiscordBot

# Create virtual environment (creates a 'venv' folder)
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**You'll know it's activated when you see `(venv)` at the start of your terminal prompt:**
```
(venv) username@computer:~/PaymentNewsBot$
```

---

### 2.4 Install Dependencies

**What are Dependencies?** External Python packages this project needs to work (like Discord.py, feedparser, etc.)

**Install All Dependencies:**

```bash
# Make sure virtual environment is activated (you see 'venv')
pip install -r requirements.txt
```

**What's being installed:**
- `discord.py` - Interact with Discord API
- `feedparser` - Parse RSS feeds
- `anthropic` - Use Claude AI for summarization
- `beautifulsoup4` - Clean HTML from articles
- `python-dotenv` - Load environment variables
- `pytz` - Handle Bangkok timezone
- `schedule` - Schedule daily digests

**Verification:**
```bash
pip list
# Should show all the packages installed
```

---

### 2.5 Create Your .env File

**What is .env?** A file that stores your secret API keys and configuration. It's excluded from Git so secrets don't get shared publicly.

**Create the File:**

```bash
# Copy the example file
cp .env.example .env

# Open it in your text editor
# On macOS:
open .env

# On Windows:
notepad .env

# Or open the folder in VS Code:
code .
```

**Edit .env and add your actual values:**

```env
# Your Discord bot token from step 1.5
DISCORD_TOKEN=your_discord_bot_token_here

# Your Discord channel ID from step 1.5
DISCORD_CHANNEL_ID=your_channel_id_here

# Your Anthropic API key from step 1.6
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

**⚠️ Important:**
- Replace the example values with YOUR actual tokens
- Don't add quotes around the values
- Don't commit this file to Git (it's already in .gitignore)
- Keep this file secret!

---

### 2.6 Run the Bot Locally

**Two Ways to Run:**

#### Option 1: Bot Only (Manual Commands Only)

```bash
# Make sure you're in project folder with venv activated
python3 bot.py
```

**You should see:**
```
[2025-12-07 10:30:15] [INFO    ] Configuration loaded:
[2025-12-07 10:30:15] [INFO    ] Bot has connected to Discord!
[2025-12-07 10:30:15] [INFO    ] Bot is in 1 guild(s)
```

#### Option 2: With Scheduler (Automatic Daily Digests)

```bash
# This runs the bot AND the daily scheduler
python3 scheduler.py
```

**You should see:**
```
[2025-12-07 10:30:15] [INFO    ] Configuration loaded:
[2025-12-07 10:30:15] [INFO    ] Bot has connected to Discord!
[2025-12-07 10:30:15] [INFO    ] Scheduler started, waiting for 08:00 Asia/Bangkok
```

---

### 2.7 Test Your Bot

**Go to your Discord channel and try these commands:**

1. **Test the !latest command:**
   ```
   !latest
   ```
   - Should show the last 5 articles in the database
   - If database is empty, it will say "No articles found"

2. **Test the !digest command:**
   ```
   !digest
   ```
   - Fetches new articles from RSS feeds
   - Processes them with AI
   - Displays unsent articles
   - First time: Will process ~50+ articles (takes 2-3 minutes)
   - Second time: Will show "No new articles to report"

**Expected Output:**
- Bot responds with "Fetching and processing latest news..."
- Shows articles as Discord embeds with:
  - 🇹🇭 Thailand-specific news
  - 🌏 Global news
  - Each article has reactions: 📌 💬 🔗

---

### 2.8 Stop the Bot

**To stop the bot:**
- Press `Ctrl + C` in the terminal

**To deactivate virtual environment:**
```bash
deactivate
```

---

## 3. Version Control with Git & GitHub

### 3.1 What is Git and Why Use It?

**Git** is a version control system that:
- Tracks every change you make to your code
- Lets you revert to previous versions if something breaks
- Enables collaboration with other developers
- Acts as a backup of your project

**GitHub** is a website where you store your Git repositories online.

**Analogy:** Think of Git like a save game feature in video games, and GitHub like cloud storage for those saves.

---

### 3.2 Create a GitHub Account

1. Go to [github.com](https://github.com)
2. Click "Sign up"
3. Follow the registration process
4. Verify your email address

---

### 3.3 Create a New Repository

**Option A: Use the Existing Repository (Fork)**

If you want to contribute back or track updates from the original project:

1. Go to [github.com/ratanon97/PaymentNewsDiscordBot](https://github.com/ratanon97/PaymentNewsDiscordBot)
2. Click "Fork" (top right)
3. This creates a copy under your account

**Option B: Create Your Own Repository**

If you want a completely independent copy:

1. Go to GitHub and click the "+" icon → "New repository"
2. Name it (e.g., "PaymentNewsBot")
3. Choose "Private" or "Public"
4. **Don't** initialize with README (we already have one)
5. Click "Create repository"

---

### 3.4 Understanding Basic Git Commands

Here are the Git commands you'll use most often:

**Check Status:**
```bash
git status
# Shows which files have changed
```

**Stage Files:**
```bash
# Stage specific file
git add filename.py

# Stage all changed files
git add .
```

**Commit Changes:**
```bash
git commit -m "Description of what you changed"
# Creates a save point with a message
```

**Push to GitHub:**
```bash
git push origin main
# Uploads your commits to GitHub
```

**Pull from GitHub:**
```bash
git pull origin main
# Downloads changes from GitHub
```

---

### 3.5 Connect Local Project to GitHub

**If you cloned the repository (Option A in 2.1):**

Your project is already connected to GitHub. Skip to the next section.

**If you downloaded as ZIP or created your own repo:**

```bash
# Initialize Git in your project folder
cd PaymentNewsDiscordBot
git init

# Stage all files
git add .

# Create first commit
git commit -m "Initial commit: Payment News Bot"

# Connect to your GitHub repository
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/PaymentNewsBot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**You'll be prompted for credentials:**
- Username: Your GitHub username
- Password: Use a **Personal Access Token** (not your GitHub password)

**To create a Personal Access Token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Select scope: `repo`
4. Copy the token and use as password

---

### 3.6 Understanding .gitignore

**What is .gitignore?** A file that tells Git which files to ignore and never commit.

**Why is this important?** We don't want to commit:
- `.env` (contains secret API keys)
- `*.db` (database files that can be regenerated)
- `venv/` (virtual environment - too large, can be recreated)
- `__pycache__/` (temporary Python files)

**Your .gitignore already includes:**
```
# Environment variables (secrets!)
.env

# Database (can be regenerated)
*.db
*.db-shm
*.db-wal

# Python cache files
__pycache__/
*.pyc

# Virtual environment
venv/
env/
```

**⚠️ Never commit .env to Git!** If you accidentally do:
```bash
# Remove from Git (but keep local copy)
git rm --cached .env
git commit -m "Remove .env from version control"
git push
```

---

### 3.7 Making Changes and Pushing to GitHub

**Typical Workflow:**

1. **Make Changes** (edit files in VS Code)

2. **Check What Changed:**
   ```bash
   git status
   git diff
   ```

3. **Stage Your Changes:**
   ```bash
   git add .
   ```

4. **Commit with Message:**
   ```bash
   git commit -m "Add new RSS feed source"
   ```

5. **Push to GitHub:**
   ```bash
   git push origin main
   ```

**Good Commit Message Examples:**
- ✅ "Fix Discord embed color for Thailand articles"
- ✅ "Add PaymentsSource.com to RSS feeds"
- ✅ "Update digest time to 9 AM"
- ❌ "Fixed stuff"
- ❌ "Updates"
- ❌ "asdf"

---

## 4. Cloud Deployment on Railway

### 4.1 Why Cloud Hosting?

**Problem:** If you run the bot on your laptop and close it, the bot stops working.

**Solution:** Deploy to Railway (cloud hosting) so the bot runs 24/7, even when your computer is off.

**Railway Benefits:**
- Runs continuously
- Auto-restarts if it crashes
- Easy deployment from GitHub
- $5/month free credit (enough for this bot)

---

### 4.2 Create Railway Account

1. Go to [railway.app](https://railway.app/)
2. Click "Login" or "Start a New Project"
3. Choose "Login with GitHub" (easiest option)
4. Authorize Railway to access your GitHub

**Why use GitHub login?** It automatically connects Railway to your GitHub repositories, making deployment seamless.

---

### 4.3 Deploy from GitHub

**Step-by-Step:**

1. **Create New Project**
   - Click "New Project" in Railway dashboard
   - Select "Deploy from GitHub repo"

2. **Select Repository**
   - You'll see a list of your GitHub repositories
   - Click "PaymentNewsBot" (or whatever you named it)
   - Railway will start analyzing the repository

3. **Railway Auto-Detection**
   - Railway automatically detects:
     - `Procfile` (knows to run `python3 scheduler.py`)
     - `runtime.txt` (knows to use Python 3.9)
     - `requirements.txt` (installs dependencies)

4. **Wait for Initial Deploy**
   - Railway will try to deploy
   - **This will FAIL** because we haven't set environment variables yet
   - That's expected! Continue to next section.

---

### 4.4 Configure Environment Variables

**Why?** Railway needs your Discord token, channel ID, and Anthropic API key to run the bot.

**Steps:**

1. **Click on Your Service**
   - In Railway dashboard, click on your deployed service

2. **Go to Variables Tab**
   - Click "Variables" at the top

3. **Add Environment Variables**

   Click "+ New Variable" and add each of these:

   **Variable 1:**
   ```
   Name:  DISCORD_TOKEN
   Value: (paste your Discord bot token from .env file)
   ```

   **Variable 2:**
   ```
   Name:  DISCORD_CHANNEL_ID
   Value: (paste your Discord channel ID from .env file)
   ```

   **Variable 3:**
   ```
   Name:  ANTHROPIC_API_KEY
   Value: (paste your Anthropic API key from .env file)
   ```

4. **Save**
   - Railway automatically saves as you type
   - After adding all three, Railway will **automatically redeploy**

---

### 4.5 Monitor Deployment

**Check Deployment Status:**

1. **Go to Deployments Tab**
   - Click "Deployments" in your Railway project

2. **View Logs**
   - Click on the latest deployment
   - Click "View Logs" or "Deploy Logs"

**Successful Deployment Logs Should Show:**
```
[INFO] Configuration loaded:
[INFO] Discord Token: ✓ Set
[INFO] Discord Channel ID: 1446903334123339857
[INFO] Anthropic API Key: ✓ Set
[INFO] Bot has connected to Discord!
[INFO] Bot is in 1 guild(s)
[INFO] Scheduler started, waiting for 08:00 Asia/Bangkok
```

**If you see these logs, congratulations! Your bot is live! 🎉**

---

### 4.6 Verify Bot is Running

**Test in Discord:**

1. Go to your Discord channel
2. Type: `!latest`
3. Bot should respond with articles

**Check Railway Dashboard:**
- "Deployments" tab should show "Success" in green
- "Metrics" tab shows CPU/Memory usage (should be low)

---

### 4.7 Understanding Railway Procfile

**What is Procfile?** A file that tells Railway how to run your application.

**Your Procfile:**
```
worker: python3 scheduler.py
```

**Breakdown:**
- `worker:` - Type of process (not a web server)
- `python3 scheduler.py` - Command to run

**Why scheduler.py?** Because it:
- Starts the Discord bot
- Starts the daily digest scheduler
- Runs continuously

---

## 5. Maintenance & Updates

### 5.1 Making Code Changes

**Scenario:** You want to add a new RSS feed.

**Step-by-Step:**

1. **Pull Latest Changes** (if working with team)
   ```bash
   git pull origin main
   ```

2. **Edit config.py Locally**
   ```python
   RSS_FEEDS = [
       {
           'name': 'Finextra Payments',
           'url': 'https://www.finextra.com/rss/channel.aspx?channel=payments'
       },
       {
           'name': 'Payments Dive',
           'url': 'https://www.paymentsdive.com/feeds/news/'
       },
       {
           'name': 'PaymentsSource',  # NEW FEED
           'url': 'https://www.paymentssource.com/feed'
       }
   ]
   ```

3. **Test Locally**
   ```bash
   python3 scheduler.py
   # Test with !digest command in Discord
   # Press Ctrl+C to stop
   ```

4. **Commit Changes**
   ```bash
   git add config.py
   git commit -m "Add PaymentsSource to RSS feeds"
   git push origin main
   ```

5. **Railway Auto-Deploys**
   - Railway detects the GitHub push
   - Automatically redeploys with new code
   - Check deployment logs to verify

---

### 5.2 Checking if Bot is Running

**Method 1: Test in Discord**
```
!latest
```
If bot responds, it's running.

**Method 2: Check Railway Logs**
1. Railway Dashboard → Your Project
2. Click "Deployments"
3. Latest deployment should show "Success"
4. Click "View Logs" - should show recent activity

**Method 3: Check Railway Metrics**
- Metrics tab shows CPU/Memory usage
- If both are 0%, bot might be crashed

---

### 5.3 Reading Logs for Errors

**Where to Find Logs:**
- Railway Dashboard → Deployments → View Logs

**Common Log Messages:**

**✅ Good Logs:**
```
[INFO] Bot has connected to Discord!
[INFO] Scheduler started
[INFO] Processed 10 new articles
[INFO] Digest sent!
```

**❌ Error Logs:**

**API Errors:**
```
[ERROR] Invalid or missing DISCORD_TOKEN
[ERROR] Anthropic API error: Invalid API key
```
**Fix:** Check environment variables in Railway

**Feed Errors:**
```
[ERROR] Error fetching from Finextra: 404
```
**Fix:** RSS feed URL might have changed

**Discord Errors:**
```
[ERROR] Missing permissions in channel
```
**Fix:** Check bot permissions in Discord server settings

---

### 5.4 Restarting the Bot

**When to Restart:**
- After changing environment variables
- If bot seems stuck/unresponsive
- After Railway deployment (happens automatically)

**How to Restart on Railway:**
1. Railway Dashboard → Your Service
2. Settings tab
3. Click "Restart"

**Or trigger via new deployment:**
```bash
git commit --allow-empty -m "Trigger redeploy"
git push origin main
```

---

### 5.5 Updating Dependencies

**Scenario:** A new version of discord.py is released.

**Step-by-Step:**

1. **Update requirements.txt**
   ```txt
   discord.py>=2.4.0  # Changed from 2.3.2
   ```

2. **Test Locally**
   ```bash
   # Activate venv
   source venv/bin/activate

   # Update packages
   pip install -r requirements.txt --upgrade

   # Test the bot
   python3 bot.py
   ```

3. **If Tests Pass, Deploy**
   ```bash
   git add requirements.txt
   git commit -m "Update discord.py to 2.4.0"
   git push origin main
   ```

4. **Railway Auto-Installs**
   - Railway reads updated requirements.txt
   - Installs new package versions
   - Redeploys automatically

---

### 5.6 Monitoring Costs

**Railway Costs:**
- $5 free credit per month
- This bot typically uses $3-5/month
- If you exceed, you'll be charged

**Check Usage:**
1. Railway Dashboard → Settings → Usage
2. See resource consumption
3. Set up billing alerts

**Anthropic Costs:**
1. console.anthropic.com → Billing
2. Check credit balance
3. ~50 articles = ~$0.10-0.20

**Optimization Tips:**
- Reduce `MAX_ARTICLES_LATEST` in config.py
- Limit number of RSS feeds
- Increase `API_REQUEST_TIMEOUT` to avoid retries

---

## 6. Troubleshooting

### Common Issues and Solutions

#### Issue 1: Bot Not Responding to Commands

**Symptoms:**
- Type `!digest` or `!latest` in Discord
- No response from bot

**Possible Causes & Fixes:**

**Cause 1: Message Content Intent Not Enabled**
```
Solution:
1. Discord Developer Portal → Your App → Bot
2. Enable "Message Content Intent"
3. Save changes
4. Restart bot (Railway or locally)
```

**Cause 2: Bot Not in Server**
```
Solution:
1. Check if bot appears in member list
2. If not, re-invite using OAuth2 URL (see section 1.5)
```

**Cause 3: Bot Offline**
```
Solution:
1. Check Railway logs for errors
2. Check Railway deployment status
3. Restart the service
```

**Cause 4: Wrong Channel**
```
Solution:
1. Verify DISCORD_CHANNEL_ID in .env or Railway variables
2. Should match channel where you're testing
```

---

#### Issue 2: "Invalid Discord Token" Error

**Symptoms:**
```
[ERROR] Invalid or missing DISCORD_TOKEN
discord.errors.LoginFailure: Improper token has been passed
```

**Solution:**
1. Go to Discord Developer Portal
2. Bot section → Reset Token
3. Copy new token
4. Update in Railway Variables or .env file
5. Redeploy/restart

---

#### Issue 3: "No Articles Found"

**Symptoms:**
- `!latest` returns "No articles found in the database"
- `!digest` returns "No new articles to report"

**Cause 1: Fresh Database**
```
Solution:
Run !digest for the first time - it will fetch and process articles
(takes 2-3 minutes for initial fetch)
```

**Cause 2: RSS Feeds Down**
```
Solution:
1. Check logs for "Error fetching from [feed name]"
2. Test RSS feed URLs in browser
3. Update feed URLs in config.py if changed
```

---

#### Issue 4: Anthropic API Errors

**Symptoms:**
```
[ERROR] Anthropic API error: Invalid API key
[ERROR] Anthropic API error: Insufficient credits
```

**Solution:**
1. console.anthropic.com → API Keys
2. Verify key is active
3. Check billing → Add credits if needed
4. Update API key in Railway/env if regenerated

---

#### Issue 5: Railway Deployment Failed

**Symptoms:**
- Railway shows "Failed" deployment status
- Red X on deployment

**Solution:**
1. Click deployment → View Logs
2. Look for error messages
3. Common fixes:
   - Missing environment variables → Add in Variables tab
   - Wrong Python version → Check runtime.txt
   - Syntax errors → Fix code and push again

---

#### Issue 6: Bot Works Locally but Not on Railway

**Symptoms:**
- `python3 scheduler.py` works on your computer
- Railway deployment fails or bot doesn't respond

**Checklist:**
- [ ] All 3 environment variables set in Railway?
- [ ] Railway logs show "Bot has connected"?
- [ ] Procfile exists and correct?
- [ ] runtime.txt specifies Python 3.9+?
- [ ] requirements.txt includes all dependencies?

---

#### Issue 7: Database Locked Error

**Symptoms:**
```
[ERROR] database is locked
```

**Cause:** Multiple instances of bot trying to access database

**Solution:**
1. Stop local bot (`Ctrl+C`)
2. Only run on Railway OR locally, not both
3. If on Railway, restart the service

---

#### Issue 8: Daily Digest Not Sending

**Symptoms:**
- Bot is running
- Manual `!digest` works
- But no automatic digest at 8 AM Bangkok time

**Checklist:**
- [ ] Using `scheduler.py` not `bot.py`?
- [ ] Railway Procfile says `worker: python3 scheduler.py`?
- [ ] Check logs at 8 AM Bangkok time for errors?
- [ ] Timezone set correctly in config.py (`Asia/Bangkok`)?

**Quick Test:**
Change `DIGEST_TIME = '08:00'` to a few minutes from now in config.py, deploy, and wait.

---

#### Issue 9: Git Push Rejected

**Symptoms:**
```
error: failed to push some refs to 'https://github.com/...'
```

**Solution:**
```bash
# Pull remote changes first
git pull origin main

# If conflicts, resolve them in files
# Then commit and push again
git add .
git commit -m "Merge and resolve conflicts"
git push origin main
```

---

#### Issue 10: Pip Install Fails

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement
```

**Solution:**
```bash
# Update pip first
pip install --upgrade pip

# Try installing again
pip install -r requirements.txt

# If still fails, install packages one by one:
pip install discord.py
pip install feedparser
pip install anthropic
# ... etc
```

---

### Getting Help

**If you're still stuck:**

1. **Check Logs**
   - Railway: Deployments → View Logs
   - Local: Read terminal output carefully

2. **Search Error Messages**
   - Copy exact error message
   - Google it: "discord.py [error message]"

3. **GitHub Issues**
   - Check existing issues: github.com/ratanon97/PaymentNewsDiscordBot/issues
   - Create new issue with:
     - What you tried to do
     - What happened instead
     - Error logs (remove sensitive data!)
     - Your environment (Python version, OS, etc.)

4. **Discord/Anthropic Support**
   - Discord Developer Discord: discord.gg/discord-developers
   - Anthropic Support: support@anthropic.com

---

## Appendix: Quick Reference

### Essential Commands Cheat Sheet

**Git:**
```bash
git status                     # Check what changed
git add .                      # Stage all changes
git commit -m "message"        # Save changes
git push origin main           # Upload to GitHub
git pull origin main           # Download from GitHub
```

**Python:**
```bash
python3 --version              # Check Python version
python3 -m venv venv          # Create virtual environment
source venv/bin/activate      # Activate venv (Mac/Linux)
venv\Scripts\activate         # Activate venv (Windows)
deactivate                     # Deactivate venv
pip install -r requirements.txt  # Install dependencies
pip list                       # List installed packages
```

**Running Bot:**
```bash
python3 bot.py                # Bot only (no scheduler)
python3 scheduler.py          # Bot + daily scheduler
```

**Discord Commands:**
```
!digest                        # Fetch and send new articles
!latest                        # Show last 5 articles
```

---

### File Quick Reference

| File | Purpose | Edit? |
|------|---------|-------|
| `.env` | Your secret keys | ✅ Yes, keep updated |
| `config.py` | Settings (feeds, time, etc.) | ✅ Yes, customize |
| `bot.py` | Discord bot logic | ⚠️ Advanced users |
| `scheduler.py` | Scheduling logic | ⚠️ Advanced users |
| `news_fetcher.py` | RSS & AI processing | ⚠️ Advanced users |
| `database.py` | Database operations | ⚠️ Advanced users |
| `requirements.txt` | Python packages | ⚠️ When upgrading |
| `Procfile` | Railway run command | ⚠️ Rarely |
| `runtime.txt` | Python version | ⚠️ Rarely |
| `.gitignore` | Files to ignore | ⚠️ Rarely |

---

### Environment Variables Reference

| Variable | Where to Get | Example |
|----------|--------------|---------|
| `DISCORD_TOKEN` | Discord Developer Portal → Bot → Token | `MTQ0Njg5...` |
| `DISCORD_CHANNEL_ID` | Discord → Right-click channel → Copy ID | `1446903334123339857` |
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys | `sk-ant-api03...` |

---

### Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| GitHub | [github.com](https://github.com) | Code hosting |
| Railway | [railway.app](https://railway.app/) | Cloud hosting |
| Discord Dev Portal | [discord.com/developers](https://discord.com/developers/applications) | Bot setup |
| Anthropic Console | [console.anthropic.com](https://console.anthropic.com/) | AI API keys |
| Project Repo | [github.com/ratanon97/PaymentNewsDiscordBot](https://github.com/ratanon97/PaymentNewsDiscordBot) | Source code |

---

## Congratulations! 🎉

You've successfully:
- ✅ Installed all necessary tools
- ✅ Set up a Discord bot
- ✅ Run the bot locally
- ✅ Learned Git basics
- ✅ Deployed to Railway for 24/7 hosting
- ✅ Know how to maintain and update

**Your bot is now:**
- Running 24/7 in the cloud
- Fetching payment industry news automatically
- Sending daily digests at 8 AM Bangkok time
- Responding to manual commands

**Next Steps:**
- Monitor your bot's performance
- Customize RSS feeds in `config.py`
- Experiment with different digest times
- Share with your team!

**Questions?** Create an issue on GitHub or check the troubleshooting section.

Happy bot building! 🤖
