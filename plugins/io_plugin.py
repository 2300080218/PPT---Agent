"""
File System Service via FastMCP
Enables standard file IO capabilities.
"""

import os
import shutil
import logging
from pathlib import Path
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(asctime)s [FILEIO] %(message)s")
logger = logging.getLogger("fileio")

app = FastMCP(name="local-file-system")

def get_full_path(relative_name: str) -> Path:
    return Path(os.getcwd()) / relative_name

@app.tool()
def touch_file(file_path: str) -> str:
    """Creates an empty file."""
    p = get_full_path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch(exist_ok=True)
    logger.info(f"Touched: {p}")
    return f"Success: created {p}"

@app.tool()
def save_text(file_path: str, data: str) -> str:
    """Overwrites file with text."""
    p = get_full_path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data, encoding="utf8")
    return f"Success: wrote {len(data)} characters to {p}"

@app.tool()
def add_text_to_end(file_path: str, data: str) -> str:
    """Appends data to a file."""
    p = get_full_path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf8") as f:
        f.write(data)
    return f"Success: appended to {p}"

@app.tool()
def replace_in_file(file_path: str, target: str, replacement: str) -> str:
    """Substitutes the first occurrence of target."""
    p = get_full_path(file_path)
    if not p.exists(): return "Error: Missing file."
    
    txt = p.read_text(encoding="utf8")
    if target not in txt: return "Error: Target not found."
    
    p.write_text(txt.replace(target, replacement, 1), encoding="utf8")
    return f"Success: Modified {p}"

@app.tool()
def remove_file(file_path: str) -> str:
    """Deletes a single file."""
    p = get_full_path(file_path)
    if not p.exists(): return "Error: File missing."
    p.unlink()
    return f"Success: Removed {p}"

@app.tool()
def remove_dir(directory_path: str) -> str:
    """Deletes an entire folder and its contents."""
    p = get_full_path(directory_path)
    if not p.exists(): return "Error: Directory missing."
    shutil.rmtree(p)
    return f"Success: Removed directory {p}"

if __name__ == "__main__":
    logger.info("Starting FileIO MCP...")
    app.run(transport="stdio")
