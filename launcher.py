"""AI Projects playground — one Gradio app that tabs across the sub-projects.

Run locally:      python launcher.py
Hugging Face:     set as `app_file: launcher.py` in README.md (sdk: gradio)

Each sub-project keeps its own folder, its own `app.py`, and its own bare
imports (`processor`, `repo_onboarding_sidekick`, ...). We load each one under a
unique module name with its folder on `sys.path` so those imports resolve
without turning the folders into packages.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import traceback
from pathlib import Path

import gradio as gr

ROOT = Path(__file__).resolve().parent


def _load(module_name: str, rel_file: str, deps_dirs: list[str]) -> object:
    """Import ROOT/rel_file as `module_name`, with deps_dirs added to sys.path."""
    for d in deps_dirs:
        p = str((ROOT / d).resolve())
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location(module_name, ROOT / rel_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot build import spec for {rel_file}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _placeholder(title: str, err: Exception) -> gr.Blocks:
    detail = "".join(traceback.format_exception_only(type(err), err)).strip()
    with gr.Blocks() as block:
        gr.Markdown(f"### {title} unavailable\n\nThis tab failed to load:\n\n```\n{detail}\n```")
    return block


# (tab label, module name, app.py path, folders its internal imports need)
SPECS = [
    ("Digital Avatar", "avatar_app", "avatar/app.py", ["avatar"]),
    ("Bank Statement", "bank_app", "bank_statement/app.py", ["bank_statement"]),
    ("Job One-Pager", "onepager_app", "job-one-pager-gradio/app.py", ["job-one-pager-gradio"]),
    ("Repo Sidekick", "sidekick_app", "repo_onboarding_sidekick/app.py", ["repo_onboarding_sidekick"]),
]

# app.py exposes its root Blocks under one of these names.
_BLOCKS_ATTRS = ("demo", "ui", "app", "iface", "block")

blocks: list[gr.Blocks] = []
labels: list[str] = []
for label, mod_name, rel_file, deps in SPECS:
    try:
        module = _load(mod_name, rel_file, deps)
        obj = next((getattr(module, a) for a in _BLOCKS_ATTRS if hasattr(module, a)), None)
        if not isinstance(obj, gr.Blocks):
            raise AttributeError(f"{rel_file} has no top-level Gradio Blocks ({_BLOCKS_ATTRS})")
        blocks.append(obj)
    except Exception as e:  # noqa: BLE001 — one broken sub-app shouldn't sink the playground
        print(f"[launcher] {label} failed to load: {e!r}", file=sys.stderr)
        blocks.append(_placeholder(label, e))
    labels.append(label)

with gr.Blocks(title="AI Projects — Playground") as demo:
    gr.Markdown("# AI Projects — Playground")
    with gr.Tabs():
        for _label, _blk in zip(labels, blocks):
            with gr.Tab(_label):
                _blk.render()

# One shared request queue for all tabs (keeps a public Space from stampeding
# the API keys). Tune with GRADIO_CONCURRENCY.
demo.queue(default_concurrency_limit=int(os.getenv("GRADIO_CONCURRENCY", "4")))


if __name__ == "__main__":
    auth = None
    user, pw = os.getenv("PLAYGROUND_USER"), os.getenv("PLAYGROUND_PASSWORD")
    if user and pw:
        auth = (user, pw)
    demo.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"),
        server_port=int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", "7860"))),
        auth=auth,
        theme=gr.themes.Soft(),
    )
