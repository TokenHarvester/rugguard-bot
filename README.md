# RUGGUARD X Bot
A Twitter/X bot for analyzing user trustworthiness in response to specific triggers.

This bot monitors for replies containing a specific phrase, analyzes the original
author's account for trust signals, and posts a trust report in response.

![Bot Workflow](https://via.placeholder.com/600x400?text=RUGGUARD+Bot+Workflow) *(Replace with actual workflow diagram)*

## Table of Contents
- [Features](#features)
- [Setup](#setup)
- [Prerequisites](#prerequisites)
- [Twitter API Configuration](#twitter-api-configuration)
- [Installation](#installation)
- [Running the Bot](#running-the-bot)
- [Trusted Accounts System](#trusted-accounts-system)
- [Rate Limit Handling](#rate-limit-handling)
- [Environment Variables](#environment-variables)
- [Monitoring Process](#monitoring-process)
- [Troubleshooting](#troubleshooting)

## Features
- 🔍 Detects replies to @projectrugguard containing "riddle me this"
- 📊 Analyzes:
  - Account age (days)
  - Follower/Following ratio
  - Bio length
  - Average tweet likes
  - Trusted connections (from `trusted.txt`)
- 🤖 Auto-replies with analysis report
- ⏲️ Built-in rate limit handling

## Setup

### Prerequisites
- Python 3.8+
- Twitter Developer Account (Essential Access tier)
- `.env` file with API keys

### Twitter API Configuration
1. Apply for developer access at [developer.twitter.com](https://developer.twitter.com)
2. Create a new Project → App
3. Generate these credentials:
   - API Key
   - API Secret
   - Bearer Token
   - Access Token
   - Access Token Secret
4. Required permissions:
   - Read + Write (for posting replies)
   - Tweet read (for analysis)

### Installation
1. Clone repository:
   ```bash
   git clone https://github.com/TokenHarvester/rugguard-bot.git
   cd rugguard-bot

2. Install dependencies:
```bash   
pip install -r requirements.txt
```
3. Create .env file:
```bash   
API_KEY=your_api_key

API_SECRET=your_api_secret

BEARER_TOKEN=your_bearer_token

ACCESS_TOKEN=your_access_token

ACCESS_SECRET=your_access_secret
```
### Running the Bot

**Local Execution**
python main.py

**Expected Behavior**

- 🔍 RUGGUARD-Bot is listening for triggers...
- Checking for new replies...
- 🚨 Trigger detected! Tweet ID: 123456789
- 👤 Original author: 987654321
- ✅ Replied to 123456789

### Trusted Accounts System
The bot checks if analyzed accounts are followed by at least 3 accounts from trusted.txt:

TRUSTED_ACCOUNTS = [
    "JupiterExchange",
    "RaydiumProtocol",
    "orca_so",
    # ... 50+ trusted accounts
]

**Updating Trusted Accounts**
1. Edit trusted.txt

2. Add/remove usernames (one per line)

3. No @ symbols needed

4. Bot checks first 3 accounts to avoid rate limits
   
### Rate Limit Handling
The bot implements multiple protections:

- 5-minute initial delay between checks

- 60-second delay between processing replies

- Automatic 15-minute wait when rate limited

- Reduced API calls (checks only 3 trusted accounts)

### Environment Variables

| Variable        | Required | Description          |
|-----------------|----------|----------------------|
| API_KEY         | Yes      | Twitter API Key      |
| API_SECRET      | Yes      | Twitter API Secret   |
| BEARER_TOKEN    | Yes      | For search endpoints |
| ACCESS_TOKEN    | Yes      | User access token    |
| ACCESS_SECRET   | Yes      | User access secret   |

### Monitoring Process
- Checks every 5 minutes for new replies

- Searches for: to:projectrugguard "riddle me this" is:reply

- Processes up to 10 recent replies per cycle

- Tracks processed tweets to avoid duplicates

### Troubleshooting
| Error               | Solution                        |
|---------------------|---------------------------------|
| Missing .env file   | Copy .env.example → .env        | 
| Rate limit errors   | Wait 15-30 minutes              | 
| "No user data"      | Verify API permissions          |
| Reply failures      | Check Twitter app permissions   |
| Trusted check fails | Verify usernames in trusted.txt |

**Code Structure**



**Key Functions**
- monitor_replies(): Main listening loop

- process_trigger(): Handles tweet parsing

- analyze_user(): Generates trust report

- check_trusted_followers(): Verifies trusted connections

- post_reply(): Posts analysis response

**Note:** The bot is optimized for Replit deployment with built-in rate limit handling. For production use, consider adding:

- Error logging

- Database for processed tweets

- Enhanced metrics analysis
