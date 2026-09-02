# Job One-Pager Generator

A Gradio-based web application that turns any job posting (URL or text) into a structured, actionable one-pager for your job application.

Powered by LLMs via OpenRouter (GPT-4o, Claude 3.5 Sonnet, Gemini 2.0 Flash, Llama 3.1, etc.).

## Features

-   **Input Flexibility**: Paste a job URL (automatically scraped) or raw text.
-   **Model Selection**: Choose from top-tier models like GPT-4o, Claude 3.5 Sonnet, and Llama 3.1.
-   **Structured Output**: Generates a clean markdown summary including:
    -   Role Summary
    -   Key Requirements
    -   Nice-to-haves
    -   Suggested Cover Letter Bullets
    -   Resume Keywords
-   **Save Functionality**: Save the generated one-pager as a local Markdown file (`job_one_pager.md`).
-   **Streamed Response**: Real-time streaming of the generated content.

## Setup & Installation

### Prerequisites

-   Python 3.8+
-   An [OpenRouter](https://openrouter.ai/) API Key

### Local Development

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd job-one-pager-gradio
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the project root and add your OpenRouter API key:
    ```env
    OPENROUTER_API_KEY=sk-or-your-key-here
    ```

5.  **Run the application:**
    ```bash
    python app.py
    ```
    The app will launch in your browser at `http://127.0.0.1:7860`.

## Deployment (Hugging Face Spaces)

This project is ready to be deployed to [Hugging Face Spaces](https://huggingface.co/spaces).

1.  Create a new Space on Hugging Face.
2.  Select **Gradio** as the Space SDK.
3.  Upload the following files to your Space:
    -   `app.py`
    -   `requirements.txt`
    -   `one_pager.py`
    -   `scraper.py`
4.  Go to **Settings** > **Variables and secrets** in your Space.
5.  Add a new Secret:
    -   Name: `OPENROUTER_API_KEY`
    -   Value: Your actual OpenRouter API key.

## Project Structure

-   `app.py`: Main Gradio application entry point and UI layout.
-   `one_pager.py`: Core logic for interacting with the LLM to generate the one-pager.
-   `scraper.py`: Utility to fetch and clean text from job posting URLs.
-   `requirements.txt`: Python dependencies.
