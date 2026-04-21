# LinkedIn Post Generator

Fetches fresh AI news, generates a LinkedIn post in your voice via Claude, and emails it to you — automatically, 3x/week.

## What it does

1. Pulls AI news from Perplexity (sonar-small-online)
2. Fetches TLDR AI and AI Report NL via Jina.ai reader (no API key needed)
3. Calls Claude Sonnet with `web_search` enabled to generate the post
4. Emails the result to you every Tuesday, Thursday, and Saturday at 8 AM Berlin time

---

## Setup (Python script)

### 1. Install dependencies

```bash
cd Projects/linkedin_post_generator
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your keys
```

**Keys you need:**
- `ANTHROPIC_API_KEY` — [console.anthropic.com](https://console.anthropic.com)
- `PERPLEXITY_API_KEY` — [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)
- `GMAIL_ADDRESS` — your Gmail address
- `GMAIL_APP_PASSWORD` — generate at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (requires 2FA enabled)
- `RECIPIENT_EMAIL` — where to send the post (can be same as `GMAIL_ADDRESS`)

### 3. Run manually

```bash
python linkedin_post_generator.py
```

### 4. Schedule via cron (Tue/Thu/Sat 8 AM Berlin)

```bash
crontab -e
```

Add this line (adjust path):

```
0 8 * * 2,4,6 TZ=Europe/Berlin /usr/bin/python3 /path/to/linkedin_post_generator.py >> /tmp/linkedin_post.log 2>&1
```

### 5. Schedule via GitHub Actions

Create `.github/workflows/linkedin_post.yml` with:

```yaml
name: LinkedIn Post Generator
on:
  schedule:
    - cron: '0 7 * * 2,4,6'  # 7 AM UTC = 8 AM Berlin (CET); adjust for CEST offset in summer
  workflow_dispatch:
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r Projects/linkedin_post_generator/requirements.txt
      - run: python Projects/linkedin_post_generator/linkedin_post_generator.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          PERPLEXITY_API_KEY: ${{ secrets.PERPLEXITY_API_KEY }}
          GMAIL_ADDRESS: ${{ secrets.GMAIL_ADDRESS }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          RECIPIENT_EMAIL: ${{ secrets.RECIPIENT_EMAIL }}
```

---

## Setup (n8n workflow)

### 1. Import the workflow

- Open n8n → Workflows → Import from file
- Select `n8n_workflow.json`

### 2. Configure credentials

- **Gmail OAuth2** node: connect your Gmail account via OAuth in n8n credentials
- **Environment variables** in n8n: set `ANTHROPIC_API_KEY`, `PERPLEXITY_API_KEY`, `GMAIL_ADDRESS`, `RECIPIENT_EMAIL` under Settings → Environment Variables (or replace the `$env.*` expressions with literal values in each node)

### 3. Activate the workflow

- Toggle the workflow to **Active**
- It will fire every Tuesday, Thursday, Saturday at 08:00 Europe/Berlin

### 4. Test it

- Click **Execute Workflow** manually to verify each node passes before waiting for the schedule

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Gmail refuses login | Use App Password, not your main password. 2FA must be on. |
| Perplexity returns 401 | Check your API key — free tier requires credit card on file |
| Jina.ai times out | Retry — it occasionally has latency spikes; the script continues if it fails |
| Claude returns `overloaded_error` | The script will raise — re-run manually; the n8n workflow will retry on next schedule |
| Email arrives but post is empty | Check Claude API logs — likely a tool_use loop that didn't resolve |

---

## Cost estimate (per run)

| Service | Cost |
|---|---|
| Claude Sonnet 4 (~1k tokens in, ~300 out) | ~$0.004 |
| Perplexity sonar-small-online | ~$0.001 |
| Jina.ai | Free |
| Gmail SMTP | Free |
| **Per month (3x/week = ~13 runs)** | **< $0.10** |
