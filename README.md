# PPT Agent - AI Slide Generator

An intelligent, full-stack application that leverages the Model Context Protocol (MCP) and OpenRouter LLMs to automatically generate heavily structured, themed PowerPoint presentations (`.pptx`) from a simple text prompt.

## Architecture

* **Frontend**: Streamlit-based UI for requesting presentations and previewing slides.
* **Backend Brain**: FastAPI application that bridges the frontend and orchestrates multiple tools via MCP.
* **MCP Tools**: Found in `plugins/`, allowing the backend API to physically write slides, perform calculations, fetch the current time, and read the filesystem dynamically.

## Quick Start

### 1. Requirements

Ensure you have Python installed and the required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory and add your OpenRouter API key:
```env
OPENROUTER_API_KEY=your_api_key_here
```
*(If no API key is provided, the application safely falls back to a "local mock mode")*

### 3. Launching the App

You need to run both the Backend and the Frontend in two separate terminal sessions.

**Start the Backend Engine (FastAPI):**
```bash
python -m uvicorn api_main:app --port 8000
```

**Start the Frontend UI (Streamlit):**
```bash
python -m streamlit run frontend.py
```

Open `http://localhost:8501` in your browser. From there, input a presentation topic, set your slide count, and hit Generate. You will successfully receive your brand-new `.pptx` file!

## Built With
- **[FastAPI](https://fastapi.tiangolo.com/)** - Web Framework for the backend
- **[Streamlit](https://streamlit.io/)** - UI Framework for the frontend
- **[python-pptx](https://python-pptx.readthedocs.io/)** - Generating the PowerPoint files
- **[FastMCP](https://github.com/jlowin/fastmcp)** - Context tool integrations
