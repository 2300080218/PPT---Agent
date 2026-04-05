# Reflection Document: The "Auto-PPT" Agent

**Student Name:** [Your Name Here]
**Course:** AI Agents & MCP Architecture
**Date:** April 5, 2026

---

### 1. Where did your agent fail its first attempt?

My agent’s first significant failure occurred during **dynamic constraint alignment**. Initially, the agentic loop was too rigid: although the user could specify a slide count in the UI, the backend structural planner was only capable of returning a fixed-length JSON object with 4 slides. This meant even if a user requested 10 slides, the agent would "fail" to fulfill that specific instruction, only producing the hardcoded 4 slides from its internal mock template.

**The Fix:** I redesigned the `generator_core.py` and `api_main.py` pipeline to ensure the structural plan was fully generated based on the user's numeric input. I also implemented a "Theme Detection" step in the planning phase. Now, the agent explicitly checks the user's prompt to decide whether to trigger a **Professional**, **Normal**, or **Aesthetic** design theme before it ever touches the PowerPoint tools.

---

### 2. How did MCP prevent you from writing hardcoded scripts?

The Model Context Protocol (MCP) shifted the architecture from a monolithic script to a **modular tool-based ecosystem**. Without MCP, I would have likely written a single Python script where the AI logic and the PowerPoint generation logic (via `python-pptx`) were tightly coupled. Every time I wanted to change a slide’s font or color, I would have had to risk breaking the AI's core generation loop.

**The MCP Advantage:** By implementing the PowerPoint logic as a standalone MCP server (`slides_plugin.py`), I decoupled the **"The Brain"** (LLM orchestrator) from the **"The Hands"** (Slide constructor). 

This provided two massive benefits:
*   **Encapsulation**: The main agent only knows *what* it wants to create (tools like `init_presentation` and `push_slide`). It doesn't need to know *how* `python-pptx` handles RGB colors or layouts.
*   **Design Agility**: I was able to upgrade the entire visual design of the PowerPoint slides—adding header bars, separators, and high-readability fonts—solely by updating the MCP server. I never had to modify the core Agent code, which proved the power of a truly tool-augmented architecture.

---

### 3. Conclusion

This project demonstrates a production-ready agent that doesn't just "talk"; it plans, selects tools, and executes complex file-level tasks across a modern full-stack environment. By leveraging FastAPI, Streamlit, and FastMCP, the final result is a robust, theme-aware generator that effectively turns a single line of text into a high-end corporate presentation.
