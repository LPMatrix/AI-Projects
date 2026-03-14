import os
import json
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv
from processor import process_statement

load_dotenv(override=True)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

CHAT_MODEL = "google/gemini-2.0-flash-001"

SYSTEM_PROMPT = """You are a sharp, no-fluff financial assistant.
The user has uploaded a bank statement. Use the transaction data provided to answer accurately.
Format naira amounts with ₦ and commas. Be concise and direct."""

def chat_with_statement(message, history, session_data):
    if not session_data:
        return "Please upload a bank statement PDF, Excel, or CSV first."

    system = (
        SYSTEM_PROMPT + "\n\n"
        f"Summary:\n{json.dumps(session_data['summary'], indent=2)}\n\n"
        f"Transactions:\n{json.dumps(session_data['transactions'], indent=2)}"
    )

    messages = [{"role": "system", "content": system}]
    # Handle both tuple and dictionary formats for history
    for msg in history:
        if isinstance(msg, (list, tuple)) and len(msg) == 2:
            messages.append({"role": "user", "content": msg[0]})
            messages.append({"role": "assistant", "content": msg[1]})
        elif isinstance(msg, dict):
            messages.append(msg)
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    session_state = gr.State(None)

    gr.Markdown("# 🏦 Chat with your Bank Statement")
    gr.Markdown("Upload your PDF, CSV, or Excel bank statement and ask questions about your transactions.")

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(
                label="Upload Bank Statement", 
                file_types=[".pdf", ".csv", ".xlsx", ".xls"]
            )
            status_box = gr.Textbox(label="Status", interactive=False, lines=7)
        with gr.Column(scale=2):
            chat_ui = gr.ChatInterface(
                fn=chat_with_statement,
                additional_inputs=[session_state],
                title="Financial Assistant",
                description="Ask me about your statement data."
            )

    file_input.upload(
        fn=process_statement,
        inputs=[file_input],
        outputs=[status_box, session_state],
        api_name=False,
    )

if __name__ == "__main__":
    demo.launch()
