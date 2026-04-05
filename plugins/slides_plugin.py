"""
Slide Deck Generator MCP Server
Offers Slide Creation via FastMCP framework.
Stateful handling of slide structures.
"""

import os
import logging
from pathlib import Path
from typing import List

from fastmcp import FastMCP
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

logging.basicConfig(level=logging.INFO, format="[SLIDES-MCP] %(asctime)s | %(levelname)s - %(message)s")
logger = logging.getLogger("slides_mcp")

mcp_app = FastMCP(name="slide-builder-mcp")

# Storage for the current PPT session
session_state = {
    "deck": None,
    "output_file": None,
    "total_slides": 0,
}

# Professional Corporate Theme
COLOR_BACKGROUND = RGBColor(255, 255, 255) # Pure White
COLOR_DARK       = RGBColor(15, 23, 42)    # Slate 900 (Professional dark)
COLOR_ACCENT     = RGBColor(37, 99, 235)   # Royal Blue (Industry standard)
COLOR_TEXT       = RGBColor(51, 65, 85)    # Slate 700 (High-readability text)

DIMENSION_W = Inches(13.33)
DIMENSION_H = Inches(7.5)


def apply_bg(slide_obj, color_val: RGBColor):
    """Set the slide background color"""
    bg_fill = slide_obj.background.fill
    bg_fill.solid()
    bg_fill.fore_color.rgb = color_val


def insert_textbox(slide_obj, x: float, y: float, w: float, h: float, content: str, size: int, is_bold: bool, clr: RGBColor, alignment=PP_ALIGN.LEFT):
    """Insert a text shape into the slide"""
    box = slide_obj.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.word_wrap = True
    paragraph = frame.paragraphs[0]
    paragraph.alignment = alignment
    run = paragraph.add_run()
    run.text = content
    run.font.size = Pt(size)
    run.font.bold = is_bold
    run.font.color.rgb = clr
    run.font.name = 'Arial'  # Clean professional font


def create_the_title_slide(deck: Presentation, heading: str):
    """Generate the initial cover slide with high-end typography"""
    empty_layout = deck.slide_layouts[6]
    cover = deck.slides.add_slide(empty_layout)
    apply_bg(cover, COLOR_DARK)
    
    # Left accent vertical bar
    accent_bar = cover.shapes.add_shape(1, Inches(0.5), Inches(2.5), Inches(0.1), Inches(2.5))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = COLOR_ACCENT
    accent_bar.line.fill.background()

    insert_textbox(cover, 0.8, 2.5, 11.5, 2.0, heading, 54, True, RGBColor(255, 255, 255))
    insert_textbox(cover, 0.8, 4.2, 8.0, 1.0, "Strategic Overview & Analysis", 22, False, COLOR_ACCENT)
    
    logger.info(f"Cover slide created: {heading}")


def create_a_bullet_slide(deck: Presentation, heading: str, bullet_list: List[str], index: int):
    """Generate a clean, high-readability professional slide"""
    empty_layout = deck.slide_layouts[6]
    slide = deck.slides.add_slide(empty_layout)
    apply_bg(slide, COLOR_BACKGROUND)

    # Top thin header bar (Sleek professional accent)
    header_bar = slide.shapes.add_shape(1, Inches(0), Inches(0), DIMENSION_W, Inches(0.08))
    header_bar.fill.solid()
    header_bar.fill.fore_color.rgb = COLOR_ACCENT
    header_bar.line.fill.background()

    # Title with underline
    insert_textbox(slide, 0.5, 0.4, 12.0, 1.0, heading, 32, True, COLOR_DARK)
    
    # Subtle separator line
    line = slide.shapes.add_shape(1, Inches(0.5), Inches(1.3), Inches(12.3), Inches(0.01))
    line.fill.solid()
    line.line.color.rgb = RGBColor(226, 232, 240) # Slate 200

    start_y = 1.8
    for idx, item in enumerate(bullet_list[:5]):
        # Modern circular bullet
        bullet_point = slide.shapes.add_shape(9, Inches(0.6), Inches(start_y + idx * 0.9 + 0.15), Inches(0.12), Inches(0.12))
        bullet_point.fill.solid()
        bullet_point.fill.fore_color.rgb = COLOR_ACCENT
        bullet_point.line.fill.background()

        insert_textbox(slide, 0.9, start_y + idx * 0.9, 11.8, 0.8, item, 22, False, COLOR_TEXT)

    # Page number at bottom right
    insert_textbox(slide, 12.0, 6.9, 1.0, 0.5, str(index), 12, False, COLOR_TEXT, PP_ALIGN.RIGHT)
    logger.info(f"Added bullet slide #{index}: {heading}")


@mcp_app.tool()
def init_presentation(filename: str) -> str:
    """Prepare a new PPTX deck to save at the specified filename"""
    global session_state
    ppt = Presentation()
    ppt.slide_width = DIMENSION_W
    ppt.slide_height = DIMENSION_H

    session_state["deck"] = ppt
    session_state["output_file"] = filename
    session_state["total_slides"] = 0

    return f"New presentation initialized for {filename}"


@mcp_app.tool()
def push_slide(title: str, bullet_points: List[str]) -> str:
    """Push a single slide into the active deck"""
    deck = session_state.get("deck")
    if not deck:
        return "Failure: Initialize presentation first."

    # Pad bullets to avoid crashes if empty
    while len(bullet_points) < 3:
        bullet_points.append("Placeholder content.")
    bullet_points = bullet_points[:5]

    session_state["total_slides"] += 1
    current = session_state["total_slides"]

    if current == 1:
        create_the_title_slide(deck, title)
    else:
        create_a_bullet_slide(deck, title, bullet_points, current - 1)

    return f"Appended slide '{title}' (Slide {current})"


@mcp_app.tool()
def finalize_presentation() -> str:
    """Commit the slide deck to disk"""
    deck = session_state.get("deck")
    fname = session_state.get("output_file")

    if not deck or not fname:
        return "Failure: Nothing to save or filename missing."

    fp = Path(os.getcwd()) / fname
    deck.save(str(fp))
    logger.info(f"Saved: {fp} with {session_state['total_slides']} slides")
    return f"Saved PPTX to {fp}"


if __name__ == "__main__":
    logger.info("Initializing Slide Builder MCP...")
    mcp_app.run(transport="stdio")
