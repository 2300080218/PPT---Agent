"""
FastAPI Server for Slide Engine
Exposes API endpoints to trigger the MCP pipeline.
"""
import json
import logging
import os
import re
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

# Import from our modified agent
from generator_core import (
    process_prompt,
    SYSTEM_RULES,
    TARGET_FILE,
    fetch_mcp_tools,
    invoke_mcp,
    get_params,
    parse_json_from_llm
)
from mcp import ClientSession
from mcp.client.stdio import stdio_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [WEB] %(message)s")
log = logging.getLogger("web")

async def build_deck_pipeline(user_query: str) -> dict:
    async with stdio_client(get_params("io_plugin.py")) as (r1, w1):
        async with ClientSession(r1, w1) as fs_sess:
            await fs_sess.initialize()
            
            async with stdio_client(get_params("slides_plugin.py")) as (r2, w2):
                async with ClientSession(r2, w2) as ppt_sess:
                    await ppt_sess.initialize()
                    
                    async with stdio_client(get_params("calc_plugin.py")) as (r3, w3):
                        async with ClientSession(r3, w3) as math_sess:
                            await math_sess.initialize()

                            async with stdio_client(get_params("clock_plugin.py")) as (r4, w4):
                                async with ClientSession(r4, w4) as time_sess:
                                    await time_sess.initialize()

                                    # Run the pipeline
                                    log.info("Planning slides...")
                                    raw_text = process_prompt(
                                        [{"role": "user", "content": user_query}],
                                        SYSTEM_RULES,
                                        2048
                                    )
                                    try:
                                        plan = json.loads(parse_json_from_llm(raw_text))
                                    except Exception as e:
                                        raise RuntimeError(f"JSON Parse failure: {e}")
                                    
                                    slides = plan.get("slide_content", [])
                                    if not slides: raise RuntimeError("Plan is empty.")

                                    # Initialize deck
                                    await invoke_mcp(ppt_sess, "init_presentation", {"filename": TARGET_FILE})
                                    
                                    # Add slides
                                    for idx, s in enumerate(slides, 1):
                                        title = s.get("heading", f"Slide {idx}")
                                        bullets = s.get("items", [])
                                        if idx > 1 and len(bullets) < 3:
                                            b_raw = process_prompt([
                                                {"role": "user", "content": f'4 bullets array for "{title}" with context "{user_query}". JSON array only.'}
                                            ], limit=512)
                                            try:
                                                m = re.search(r"\[.*\]", b_raw, re.DOTALL)
                                                bullets = json.loads(m.group(0)) if m else bullets
                                            except:
                                                bullets = ["Detail one", "Detail two", "Detail three"]
                                            s["items"] = bullets
                                            plan["slide_content"][idx-1]["items"] = bullets
                                        
                                        await invoke_mcp(ppt_sess, "push_slide", {"title": title, "bullet_points": bullets})

                                    await invoke_mcp(ppt_sess, "finalize_presentation", {})
                                    return plan

async def compile_existing_plan(slides_list: list):
    async with stdio_client(get_params("slides_plugin.py")) as (r2, w2):
        async with ClientSession(r2, w2) as ppt_sess:
            await ppt_sess.initialize()
            await invoke_mcp(ppt_sess, "init_presentation", {"filename": TARGET_FILE})
            for s in slides_list:
                points = s["items"]
                while len(points) < 3: points.append("Add detailed text here.")
                await invoke_mcp(ppt_sess, "push_slide", {"title": s["heading"], "bullet_points": points[:5]})
            await invoke_mcp(ppt_sess, "finalize_presentation", {})


class SlideData(BaseModel):
    heading: str
    items: List[str]

class DeckStructure(BaseModel):
    deck_title: str
    slide_content: List[SlideData]

class CreateReq(BaseModel):
    query: str = Field(...)
    total_slides: int = Field(5, ge=3, le=10)

class ModifyReq(BaseModel):
    structure: DeckStructure

@asynccontextmanager
async def lifespan(api: FastAPI):
    log.info("API Booting...")
    yield

app = FastAPI(title="SlideDeck Builder", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/v1/ping")
async def ping_check():
    return {"status": "running"}

@app.post("/api/v1/build")
async def build_presentation(req: CreateReq):
    try:
        struct = await build_deck_pipeline(f"{req.query} (Generate exactly {req.total_slides} slides)")
        return {"status": "ok", "file": TARGET_FILE, "structure": struct}
    except Exception as e:
        log.exception("Creation error")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/export")
async def export_presentation():
    fp = BASE_DIR / TARGET_FILE
    if not fp.exists(): raise HTTPException(status_code=404, detail="File missing.")
    return FileResponse(path=str(fp), filename="slide_deck.pptx",
                        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")

@app.post("/api/v1/reload")
async def reload_presentation(req: ModifyReq):
    try:
        slides = [s.model_dump() for s in req.structure.slide_content]
        await compile_existing_plan(slides)
        return {"status": "reloaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=True)