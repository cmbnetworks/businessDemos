# KW AI Demo Chatbot — Python/FastAPI

Live AI chatbot demos for Key West local businesses.
Built with Python, FastAPI, and the Anthropic Claude API.
Deploy to Render.com in under 10 minutes.

---

## What This Does

A single web app hosting AI chatbot demos for multiple Key West businesses.
Each business has its own knowledge base (tours, prices, FAQs, policies).

Send prospects a direct link:
```
https://your-app.onrender.com/?biz=danger-charters
https://your-app.onrender.com/?biz=fishmonster
https://your-app.onrender.com/?biz=gulfstream
```

---

## Project Structure

```
kw-demo-python/
├── main.py                    # FastAPI server — edit this to add features
├── requirements.txt           # Python dependencies
├── render.yaml                # Render.com deployment config
├── .env.example               # Copy to .env and add your API key
├── .gitignore
├── README.md
├── businesses/
│   ├── danger-charters.json   # Danger Charters knowledge base
│   ├── fishmonster.json       # FishMonster & IslandJane knowledge base
│   └── gulfstream.json        # Gulfstream Fishing knowledge base
└── public/
    └── index.html             # Chat UI (no changes needed)
```

---

## Local Setup (Your Python IDE)

```bash
# 1. Clone or unzip the project and open in PyCharm/VS Code

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up your API key
cp .env.example .env
# Open .env and add your ANTHROPIC_API_KEY
# Get it from: https://console.anthropic.com

# 6. Run the server
python main.py
# OR
uvicorn main:app --reload --port 3000

# 7. Open http://localhost:3000
```

---

## Deploy to Render.com

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "KW AI demo chatbot - Python/FastAPI"
git branch -M main
git remote add origin https://github.com/YOURUSERNAME/kw-demo-python.git
git push -u origin main
```

### Step 2 — Create Render Web Service
1. Go to https://render.com → New → Web Service
2. Connect your GitHub repository
3. Render reads `render.yaml` automatically
4. It detects Python and uses the correct build/start commands

### Step 3 — Add API Key
1. Render dashboard → your service → Environment tab
2. Add: `ANTHROPIC_API_KEY` = your key from console.anthropic.com
3. Save Changes → auto-deploys

Your live URL: `https://kw-ai-demo-chatbot.onrender.com`

---

## Adding a New Business (5 minutes)

1. Copy `businesses/danger-charters.json` as a template
2. Fill in: `id`, `name`, `tagline`, `phone`, `address`, `website`,
   `booking_url`, `theme` colors, `logo_emoji`, and `system_prompt`
3. Add starter questions in `public/index.html` under `starterQuestions`
4. Git push — Render auto-deploys in ~2 minutes

### system_prompt Tips
- Be specific about tours, prices, durations, what's included
- Include the real FAQ questions customers ask
- Set the personality/tone (warm, nautical, laid-back, etc.)
- Always include phone number and booking URL to fall back on
- Tell it what NOT to do (don't make up prices, don't promise availability)

---

## API Endpoints

FastAPI auto-generates interactive docs at:
`http://localhost:3000/docs`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/businesses` | List all businesses |
| GET | `/api/business/{id}` | Get single business config |
| POST | `/api/chat/{id}` | Streaming chat (SSE) |

---

## Modifying main.py

The server is intentionally simple and well-commented. Common modifications:

**Change the AI model:**
```python
model="claude-sonnet-4-20250514"  # Change this line in the chat() function
```

**Change max response length:**
```python
max_tokens=600  # Increase for longer responses
```

**Add conversation logging:**
```python
# After the stream completes, add:
with open(f"logs/{business_id}.txt", "a") as f:
    f.write(f"{messages}\n---\n")
```

**Rate limiting** — add `slowapi` to requirements.txt and decorate the chat endpoint.

---

## Cost

- **Render.com**: Free tier works. $7/mo Starter keeps it always-on (no sleep).
- **Anthropic API**: ~$0.003 per demo conversation. 100 demos = ~$0.30.
- **Total**: Under $10/month to run all your demos.

---

## The Pitch Email Line

Once deployed, send this:

> "I've built a live demo of what this would look like for your business.
> Try it here: [your-url]/?biz=danger-charters
> Ask it anything a customer would ask — it's running on your actual tours
> and FAQ. Takes 2 minutes to see what it can do."
