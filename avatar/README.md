---
title: avatar
app_file: app.py
sdk: gradio
---

# Avatar — Week 1 Lab 4 (OpenRouter + local tools)

**Avatar** lives in `1_foundations/community_contributions/avatar`. It is a Week 1 `1_foundations/4_lab4` style contribution that keeps the same ideas:

- persona chat from your `linkedin.pdf` + `summary.txt`
- function tool calling (`record_user_details`, `record_unknown_question`)
- multi-turn tool loop until the model returns a normal assistant message

But it changes two things:

1. Uses **OpenRouter** via OpenAI-compatible API
2. Logs tool outputs to **local JSONL files** instead of push notifications

## Files

- `app.py` - Gradio chat app + tool-calling loop
- `me/linkedin.pdf` - your exported LinkedIn PDF (you add this)
- `me/summary.txt` - short profile summary (you add/edit)
- `data/leads.jsonl` - generated when lead tool is called
- `data/unknown_questions.jsonl` - generated when unknown-question tool is called

## Environment variables

Required:

- `OPENROUTER_API_KEY`

Optional:

- `OPENROUTER_MODEL` (default: `openai/gpt-4o-mini`)
- `OPENROUTER_BASE_URL` (default: `https://openrouter.ai/api/v1`)
- `OPENROUTER_SITE_URL` (optional OpenRouter header)
- `OPENROUTER_APP_NAME` (optional OpenRouter header)
- `AGENT_NAME` (default: `Your Name`)
- `PROFILE_DIR` (default: local `me/` folder)

## Quick start

From this folder:

```bash
uv venv
uv pip install -r requirements.txt
```

Create `.env` in project root with at least:

```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
AGENT_NAME=Your Name
```

Add your profile files:

- `me/linkedin.pdf`
- `me/summary.txt`

Run:

```bash
uv run app.py
```

## Notes

- This keeps Week 1 tool-calling behavior and local side effects.
- JSONL logs are append-only for easy review and import.
- **Gradio:** use `gradio>=5.22.0` (see `requirements.txt`). The app does not pass `type="messages"` to `ChatInterface` so older Gradio versions do not error; history is normalized from tuple pairs or message dicts in code.
