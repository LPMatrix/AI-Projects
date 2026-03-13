---
title: Bank Statement Chat Assistant
emoji: 🏦
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
---

# 🏦 Bank Statement Chat Assistant

This application allows you to upload a PDF bank statement and chat with an AI assistant to analyze your finances.

## Features
- **Intelligent Extraction:** Uses LLM (Gemini 2.0 Flash) to clean and structure raw PDF text into a readable summary.
- **Conversational AI:** Ask questions about spending, balances, or specific transactions.
- **Secure:** Processes data locally (text extraction) and uses API calls for analysis.

## Setup Instructions
1. **API Key:** This Space requires an `OPENROUTER_API_KEY` to function. 
2. **Environment Variables:** Set the `OPENROUTER_API_KEY` in the Space settings (Settings > Variables and Secrets).

## How to use
1. Upload your bank statement in PDF format.
2. Wait for the "PDF Processed!" status and structured summary.
3. Start chatting with the financial assistant on the right!

## Disclaimer
This is for demonstration purposes. Please ensure you are comfortable uploading your statement to a cloud-based AI model (via OpenRouter).
