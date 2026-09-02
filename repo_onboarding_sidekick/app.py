import hashlib
import os
import subprocess
import tempfile
from pathlib import Path

import gradio as gr

from repo_onboarding_sidekick import (
    DEFAULT_SUCCESS_CRITERIA,
    RepoOnboardingSidekick,
    openrouter_model_label,
)

# Local default repo path — only used when running standalone on a dev machine.
# Set SIDEKICK_DEFAULT_REPO to override; leave empty on a hosted/public deployment
# so users must supply a public Git URL instead.
_LOCAL_DEFAULT = os.getenv("SIDEKICK_DEFAULT_REPO", "").strip()
_CLONE_CACHE: dict[str, str] = {}


def _looks_like_git_url(value: str) -> bool:
    return value.startswith(("http://", "https://", "git@", "ssh://"))


def _materialize_repo(repo_path: str) -> str:
    """Turn user input into a local directory path.

    Accepts either a local path (dev use) or a public Git URL, which is
    shallow-cloned into a temp dir and cached for the process lifetime.
    """
    value = (repo_path or "").strip() or _LOCAL_DEFAULT
    if not value:
        raise ValueError(
            "Paste a public Git URL (e.g. https://github.com/owner/repo) to begin."
        )

    if _looks_like_git_url(value):
        key = hashlib.sha256(value.encode()).hexdigest()[:16]
        cached = _CLONE_CACHE.get(key)
        if cached and Path(cached).is_dir():
            return cached
        dest = Path(tempfile.gettempdir()) / f"sidekick_repo_{key}"
        if not dest.is_dir():
            subprocess.run(
                ["git", "clone", "--depth", "1", "--", value, str(dest)],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
        _CLONE_CACHE[key] = str(dest)
        return str(dest)

    path = Path(value).expanduser()
    if not path.is_dir():
        raise ValueError(f"Not a directory: {path}")
    return str(path)


async def setup(repo_path: str):
    try:
        root = _materialize_repo(repo_path)
    except (ValueError, subprocess.SubprocessError) as e:
        return None, f"⚠️ {e}"
    sidekick = RepoOnboardingSidekick()
    await sidekick.setup(root)
    return sidekick, f"**OpenRouter** · `{openrouter_model_label()}` · **Repo:** `{root}`"


async def process_message(sidekick, message, success_criteria, repo_path, history):
    root = _materialize_repo(repo_path)
    if sidekick is None or getattr(sidekick, "repo_root", None) != root:
        sidekick = RepoOnboardingSidekick()
        await sidekick.setup(root)
    results = await sidekick.run_superstep(message, success_criteria, history)
    return results, sidekick


async def reset(repo_path: str):
    try:
        root = _materialize_repo(repo_path)
    except (ValueError, subprocess.SubprocessError) as e:
        return "", DEFAULT_SUCCESS_CRITERIA, None, None, f"⚠️ {e}"
    agent = RepoOnboardingSidekick()
    await agent.setup(root)
    return "", DEFAULT_SUCCESS_CRITERIA, None, agent, f"Reset · **OpenRouter** · `{openrouter_model_label()}` · **Repo:** `{root}`"


def free_resources(sidekick):
    try:
        if sidekick:
            sidekick.cleanup()
    except Exception as e:
        print(f"Cleanup: {e}")


with gr.Blocks(title="Repo onboarding Sidekick", theme=gr.themes.Default(primary_hue="teal")) as ui:
    gr.Markdown(
        "## Repo onboarding Sidekick\n"
        "Paste a **public Git URL** (or a local path when running this app yourself). "
        "It shallow-clones the repo, explores it with read-only tools, then answers "
        "onboarding questions.\n\n"
        "Uses **OpenRouter** (`OPENROUTER_API_KEY`). Large repos may be slow to search."
    )
    sidekick = gr.State(delete_callback=free_resources)
    status = gr.Markdown(value="")

    repo_path = gr.Textbox(
        label="Public Git URL or local path",
        value=_LOCAL_DEFAULT,
        placeholder="https://github.com/owner/repo",
    )

    with gr.Row():
        chatbot = gr.Chatbot(label="Chat", height=380, type="messages")
    with gr.Group():
        with gr.Row():
            message = gr.Textbox(
                show_label=False,
                placeholder="e.g. Where should I start if I want to add a new Sidekick tool?",
            )
        with gr.Row():
            success_criteria = gr.Textbox(
                label="Success criteria (optional)",
                value=DEFAULT_SUCCESS_CRITERIA,
                lines=6,
            )
    with gr.Row():
        reset_button = gr.Button("Reset", variant="stop")
        go_button = gr.Button("Go", variant="primary")

    ui.load(setup, [repo_path], [sidekick, status])
    message.submit(
        process_message,
        [sidekick, message, success_criteria, repo_path, chatbot],
        [chatbot, sidekick],
    )
    go_button.click(
        process_message,
        [sidekick, message, success_criteria, repo_path, chatbot],
        [chatbot, sidekick],
    )
    reset_button.click(
        reset,
        [repo_path],
        [message, success_criteria, chatbot, sidekick, status],
    )


if __name__ == "__main__":
    ui.launch(inbrowser=True)
