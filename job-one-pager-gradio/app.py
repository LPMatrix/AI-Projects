import os
from pathlib import Path
import gradio as gr
from dotenv import load_dotenv
from one_pager import stream_one_pager

# Load environment variables
load_dotenv(override=True)

if not os.getenv("OPENROUTER_API_KEY"):
    print("Set OPENROUTER_API_KEY in .env (repo root or this folder).")
else:
    print("OPENROUTER_API_KEY loaded.")

# OpenRouter model choices (model id -> label)
MODELS = [
    ("openai/gpt-4o-mini", "GPT-4o Mini (OpenAI)"),
    ("openai/gpt-4o", "GPT-4o (OpenAI)"),
    ("anthropic/claude-3.5-sonnet", "Claude 3.5 Sonnet (Anthropic)"),
    ("anthropic/claude-3-haiku", "Claude 3 Haiku (Anthropic)"),
    ("google/gemini-2.0-flash-001", "Gemini 2.0 Flash (Google)"),
    ("meta-llama/llama-3.1-70b-instruct", "Llama 3.1 70B (Meta)"),
]
DEFAULT_MODEL_ID = "openai/gpt-4o-mini"


def stream_one_pager_accumulated(url_or_text: str, model_id: str):
    """Yield accumulated text so Gradio can stream into the textbox."""
    if not url_or_text or not url_or_text.strip():
        yield "Paste a job URL or full job description above, then click Generate."
        return
    acc = ""
    for chunk in stream_one_pager(url_or_text.strip(), model=model_id):
        acc += chunk
        yield acc


def save_as_md(content: str) -> str:
    """Write content to job_one_pager.md. Returns status message."""
    if not content or content.startswith("Error:") or content.startswith("Paste a job"):
        return "Nothing to save. Generate a one-pager first."
    path = Path.cwd() / "job_one_pager.md"
    try:
        path.write_text(content, encoding="utf-8")
        return f"Saved to {path.name}"
    except Exception as e:
        return f"Save failed: {e}"


with gr.Blocks(title="Job one-pager") as demo:
    gr.Markdown(
        """
        # Job posting → one-pager
        Paste a **job URL** (e.g. company careers page) or the **full job description** (e.g. from LinkedIn).  
        Pick a model, then click **Generate** to stream a one-pager: role summary, requirements, cover letter bullets, resume keywords.
        """
    )
    with gr.Row():
        model_dropdown = gr.Dropdown(
            label="Model",
            choices=[(label, id_) for id_, label in MODELS],
            value=DEFAULT_MODEL_ID,
            allow_custom_value=False,
        )
    url_or_text = gr.Textbox(
        label="Job URL or pasted description",
        placeholder="https://company.com/careers/role  or  Senior Engineer – Backend\nCompany X – Remote\nRequirements: 5+ years Python...",
        lines=8,
        max_lines=20,
    )
    with gr.Row():
        generate_btn = gr.Button("Generate one-pager", variant="primary")
    output = gr.Textbox(
        label="One-pager (markdown)",
        lines=20,
        max_lines=40,
    )
    with gr.Row():
        save_btn = gr.Button("Save as .md")
    status = gr.Textbox(label="Status", interactive=False)

    generate_btn.click(
        fn=stream_one_pager_accumulated,
        inputs=[url_or_text, model_dropdown],
        outputs=output,
    )
    save_btn.click(
        fn=save_as_md,
        inputs=output,
        outputs=status,
    )

if __name__ == "__main__":
    demo.launch()
