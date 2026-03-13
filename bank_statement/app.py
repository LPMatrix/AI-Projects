import os
import json
import re

import pdfplumber
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def clean_amount(value):
    if not value or not isinstance(value, str):
        return None
    cleaned = re.sub(r'[₦,\s]', '', value.strip())
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_transactions(pdf_path):
    transactions = []

    expected_columns = {
        "date":        ["date", "date/time"],
        "money_in":    ["money in"],
        "money_out":   ["money out"],
        "category":    ["category"],
        "to_from":     ["to / from", "to/from"],
        "description": ["description"],
        "balance":     ["balance"],
    }

    with pdfplumber.open(pdf_path) as pdf:
        col_map = None

        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue

            for row in table:
                if not any(cell for cell in row if cell and cell.strip()):
                    continue

                if col_map is None:
                    row_lower = [str(c).lower().strip() if c else "" for c in row]
                    potential_map = {}
                    for field, aliases in expected_columns.items():
                        for i, cell in enumerate(row_lower):
                            if any(alias in cell for alias in aliases):
                                potential_map[field] = i
                                break
                    if "money_in" in potential_map and "money_out" in potential_map:
                        col_map = potential_map
                    continue

                def get_col(field):
                    idx = col_map.get(field)
                    if idx is None or idx >= len(row):
                        return None
                    val = row[idx]
                    return val.strip() if val and isinstance(val, str) else val

                money_in  = clean_amount(get_col("money_in"))
                money_out = clean_amount(get_col("money_out"))

                if money_in is None and money_out is None:
                    continue

                date = get_col("date")
                if date and any(s in str(date).lower() for s in ["kuda", "licensed", "account number"]):
                    continue

                transactions.append({
                    "date":        date,
                    "money_in":    money_in,
                    "money_out":   money_out,
                    "category":    get_col("category"),
                    "to_from":     get_col("to_from"),
                    "description": get_col("description"),
                    "balance":     clean_amount(get_col("balance")),
                    "type":        "credit" if money_in else "debit",
                })

    total_in  = sum(t["money_in"]  for t in transactions if t["money_in"])
    total_out = sum(t["money_out"] for t in transactions if t["money_out"])

    summary = {
        "total_transactions": len(transactions),
        "total_money_in":     total_in,
        "total_money_out":    total_out,
        "net":                total_in - total_out,
    }

    return transactions, summary


def process_upload(file):
    if not file:
        return None, "No file uploaded."

    try:
        transactions, summary = parse_transactions(file)
    except Exception as e:
        return None, f"Failed to parse PDF: {str(e)}"

    if not transactions:
        return None, "No transactions found. The PDF may be scanned or use an unsupported layout."

    state = {"transactions": transactions, "summary": summary}

    status = (
        f"✓ Parsed {summary['total_transactions']} transactions\n\n"
        f"Money in:  ₦{summary['total_money_in']:,.2f}\n"
        f"Money out: ₦{summary['total_money_out']:,.2f}\n"
        f"Net:       ₦{summary['net']:,.2f}\n\n"
        f"Ask me anything about your statement."
    )

    return state, status


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a sharp, no-fluff financial assistant.
The user has uploaded a bank statement. You have full access to every transaction below as structured JSON.

Rules:
- Answer accurately using only the data provided.
- For aggregations (totals, averages, counts), be precise.
- Format naira amounts with the ₦ symbol and commas, e.g. ₦1,400,000.00.
- If a question can't be answered from the data, say so clearly.
- Be concise. Don't pad responses.

Statement Summary:
{summary}

Transactions (JSON):
{transactions}
"""


def chat_with_statement(message, history, state):
    if not state:
        return "Please upload a bank statement PDF first."

    system_prompt = SYSTEM_PROMPT.format(
        summary=json.dumps(state["summary"], indent=2),
        transactions=json.dumps(state["transactions"], indent=2),
    )

    messages = [{"role": "system", "content": system_prompt}]

    for msg in history:
        if isinstance(msg, (list, tuple)) and len(msg) == 2:
            if msg[0]:
                messages.append({"role": "user",      "content": msg[0]})
            if msg[1]:
                messages.append({"role": "assistant", "content": msg[1]})
        elif isinstance(msg, dict) and msg.get("role") and msg.get("content"):
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling model: {str(e)}"


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

with gr.Blocks() as demo:
    gr.Markdown("# Chat with your Bank Statement")
    gr.Markdown("Upload a PDF bank statement and ask anything — totals, spending patterns, specific transactions.")

    state = gr.State()

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="Upload Bank Statement (PDF)", file_types=[".pdf"])
            status_box = gr.Textbox(label="Status", interactive=False, lines=7)

        with gr.Column(scale=2):
            gr.ChatInterface(
                fn=chat_with_statement,
                additional_inputs=[state],
                title="Financial Assistant",
                description="Ask about your transactions, spending habits, or account details.",
            )

    file_input.upload(
        fn=process_upload,
        inputs=[file_input],
        outputs=[state, status_box],
    )

if __name__ == "__main__":
    demo.launch()