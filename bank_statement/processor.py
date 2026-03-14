import os
import json
import pdfplumber
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

PARSER_MODEL = "google/gemini-2.0-flash-001"

PARSE_PROMPT = """Extract all transactions from this bank statement data as a JSON array.

Field definitions:
- date: transaction date in DD/MM/YY format
- money_in: amount credited (float or null)
- money_out: amount debited (float or null)
- category: e.g. "inward transfer", "outward transfer", "web payment", "bills", "airtime", "local funds transfer"
- to_from: counterparty name and account number (or null for web payments)
- description: short memo/narration (the label the user gave the transaction e.g. "upkeep", "groceries", "oshey")
- balance: running balance as a float

Return only a valid JSON array, no markdown, no explanation.
"""

def parse_pdf(pdf_path):
    all_transactions = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
            transactions = call_llm_parser(text)
            if transactions:
                all_transactions.extend(transactions)
    return all_transactions

def parse_tabular(file_path, file_type):
    try:
        if file_type == "csv":
            df = pd.read_csv(file_path)
        else: # excel
            df = pd.read_excel(file_path)
        
        # Convert dataframe to string representation for LLM to parse
        tabular_data = df.to_string()
        return call_llm_parser(tabular_data)
    except Exception as e:
        print(f"[error] Tabular parsing failed: {str(e)}")
        return []

def call_llm_parser(content_text):
    try:
        response = client.chat.completions.create(
            model=PARSER_MODEL,
            messages=[{
                "role": "user",
                "content": PARSE_PROMPT + "\n\nData:\n" + content_text
            }]
        )

        content = response.choices[0].message.content.strip()
        content = (
            content
            .removeprefix("```json")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )

        transactions = json.loads(content)
        return transactions if isinstance(transactions, list) else []
    except Exception as e:
        print(f"[warn] LLM parsing failed: {str(e)}")
        return []

def process_statement(file_path):
    if not file_path:
        return "No file uploaded.", None

    ext = file_path.lower().split('.')[-1]
    
    if ext == 'pdf':
        transactions = parse_pdf(file_path)
    elif ext in ['csv', 'xlsx', 'xls']:
        transactions = parse_tabular(file_path, 'csv' if ext == 'csv' else 'excel')
    else:
        return f"Unsupported file format: {ext}", None

    if not transactions:
        return "No transactions found or failed to parse.", None

    total_in = sum(t.get("money_in", 0) or 0 for t in transactions)
    total_out = sum(t.get("money_out", 0) or 0 for t in transactions)
    net = total_in - total_out

    status = (
        f"✓ Parsed {len(transactions)} transactions from {ext.upper()}\n\n"
        f"Money in:  ₦{total_in:,.2f}\n"
        f"Money out: ₦{total_out:,.2f}\n"
        f"Net:       ₦{net:,.2f}\n\n"
        f"Ask me anything about your statement."
    )

    session_data = {
        "transactions": transactions,
        "summary": {
            "total_transactions": len(transactions),
            "total_money_in": total_in,
            "total_money_out": total_out,
            "net": net,
        }
    }

    return status, session_data
