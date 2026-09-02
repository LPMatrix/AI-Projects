---
title: AI Projects Playground
emoji: 🧪
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 6.7.0
app_file: launcher.py
pinned: false
short_description: A tabbed playground across a few small AI apps.
---

# AI Projects — Playground

One Gradio app ([`launcher.py`](launcher.py)) that tabs across the sub-projects in
this repo:

| Tab | Folder | What it does |
|---|---|---|
| Digital Avatar | [`avatar/`](avatar/) | Chat with an LLM persona built from a summary + LinkedIn PDF. |
| Bank Statement | [`bank_statement/`](bank_statement/) | Upload a PDF/CSV/XLSX statement and ask questions about the transactions. |
| Job One-Pager | [`job-one-pager-gradio/`](job-one-pager-gradio/) | Paste a job URL or description; streams a role summary, requirements, cover-letter bullets, and resume keywords. |
| Repo Sidekick | [`repo_onboarding_sidekick/`](repo_onboarding_sidekick/) | Paste a public Git URL; it shallow-clones and answers onboarding questions with read-only tools. |

Not in the playground: [`notion-mcp/`](notion-mcp/) is a CLI research/fact-check tool that
writes to your Notion via MCP — no web UI, and not something to expose to public input.

Each sub-project still runs on its own (`python <folder>/app.py`); the launcher
just imports each one's top-level Gradio `Blocks` and wraps them in a
`TabbedInterface`. If a tab fails to import, it renders a placeholder with the
error instead of taking the whole app down.

## Configuration (environment variables / Space secrets)

| Variable | Needed for | Notes |
|---|---|---|
| `OPENROUTER_API_KEY` | all tabs | Required. Public traffic spends this key — keep models cheap. |
| `OPENROUTER_MODEL` | all tabs | Defaults to `openai/gpt-4o-mini`. |
| `AGENT_NAME`, `PROFILE_DIR`, `WELCOME_MESSAGE` | Digital Avatar | Persona name + where `summary.txt` / `linkedin.pdf` live (defaults to `avatar/me/`). |
| `SIDEKICK_DEFAULT_REPO` | Repo Sidekick | Optional local path prefilled in the box; leave unset on a public deploy. |
| `GRADIO_CONCURRENCY` | launcher | Shared queue width across all tabs (default `4`). |
| `PLAYGROUND_USER` / `PLAYGROUND_PASSWORD` | launcher (local run only) | If both set, `launch()` gets HTTP basic auth. |

## Run locally

```bash
pip install -r requirements.txt
python launcher.py            # http://127.0.0.1:7860
```

## Deploy to Hugging Face Spaces

1. Create a new **Gradio** Space.
2. Add `OPENROUTER_API_KEY` (and any others above) under **Settings → Secrets**.
3. Push this repo to the Space remote:

   ```bash
   git remote add space https://huggingface.co/spaces/<user>/<space-name>
   git push space main
   ```

The Space runs `launcher.py`. Link it from your portfolio directly
(`https://huggingface.co/spaces/<user>/<space-name>`) or embed it:

```html
<script type="module" src="https://gradio.s3-us-west-2.amazonaws.com/6.7.0/gradio.js"></script>
<gradio-app src="https://<user>-<space-name>.hf.space"></gradio-app>
```

### Notes for a public deployment

- **Cost:** every tab calls OpenRouter with your key. Pin cheap models and keep
  `GRADIO_CONCURRENCY` modest.
- **Bank statements:** uploads are processed in-memory per session and not
  persisted by the app; the tab says so. Free Spaces still have ephemeral disk —
  don't treat it as private.
- **Repo Sidekick:** clones go to the container's temp dir and disappear on
  restart. Only public repos work (no credentials are used).
- **Sleep:** free Spaces sleep after ~48h idle and cold-start (~30s) on the next
  visit.
