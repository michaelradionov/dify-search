# Configuration

## Setup

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Fill in your credentials:
```bash
DIFY_BASE_URL=https://your-dify-instance.com
DIFY_API_TOKEN=app-your-token-here
```

## Credentials

### DIFY_BASE_URL
Base URL of your Dify instance (without trailing slash).

### DIFY_API_TOKEN
API token for your Dify workflow.

Get it from: Dify → App Settings → API Access → API Key

## Security

**NEVER commit `.env` to git!**

The `.env` file contains sensitive credentials and is ignored by git.
