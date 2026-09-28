import json
import logging
import uuid
from pathlib import Path
from typing import Dict, Optional
from fastapi import APIRouter, Form, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.exporters import export_comic_to_pdf
from app.gemini_flash import generate_panel_outline
from app.gemini_pro import generate_story_narrative
from app.image_generator import generate_panel_image, generate_single_test_image
from app.layout_builder import build_comic_layout
from app.models import ComicLayout, PromptRequest

logger = logging.getLogger("comiccraft.routes")

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.templates_dir))

# In-memory session store & filesystem cache
comic_cache: Dict[str, ComicLayout] = {}


def persist_comic_layout(layout: ComicLayout):
    """Saves layout metadata to filesystem cache."""
    comic_cache[layout.comic_id] = layout
    cache_file = settings.exports_dir / f"{layout.comic_id}_layout.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(layout.model_dump_json(indent=2))


def retrieve_comic_layout(comic_id: str) -> Optional[ComicLayout]:
    """Retrieves comic layout from memory or disk cache."""
    if comic_id in comic_cache:
        return comic_cache[comic_id]
    cache_file = settings.exports_dir / f"{comic_id}_layout.json"
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            layout = ComicLayout.model_validate(data)
            comic_cache[comic_id] = layout
            return layout
    return None


@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Renders the creative brief input form."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "ComicCraft - AI Comic Story Creator",
            "default_settings": ["Forest", "Futuristic City", "Medieval Castle", "Deep Space", "Cyberpunk Metropolis", "Haunted Mansion", "Underwater Realm"],
            "default_tones": ["Dramatic", "Humorous", "Adventurous", "Dark & Mysterious", "Whimsical", "Epic Action"],
            "default_styles": ["Realistic", "Comic Book", "Anime / Manga", "Watercolor", "Cyberpunk", "Vintage 1950s Pulp"]
        }
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate_comic_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...)
):
    """
    Handles form submission from browser, executes full AI pipeline,
    and returns comic_preview.html with rendered panels and PDF download link.
    """
    try:
        prompt_req = PromptRequest(
            story_prompt=story_prompt.strip(),
            character_name=character_name.strip(),
            setting=setting.strip(),
            tone=tone.strip(),
            art_style=art_style.strip()
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid form input: {e}")

    comic_id = uuid.uuid4().hex[:10]
    logger.info("Executing comic generation pipeline for comic_id=%s...", comic_id)

    # Step 1: Generate 5-panel outline via Gemini Flash
    outline = generate_panel_outline(prompt_req)

    # Step 2: Generate narration & dialogue via Gemini Pro
    narrative = generate_story_narrative(outline, prompt_req)

    # Step 3: Generate panel illustrations
    image_paths: Dict[int, str] = {}
    for panel in outline.panels:
        img_url = generate_panel_image(
            prompt=panel.image_prompt,
            comic_id=comic_id,
            panel_number=panel.panel_number,
            title=panel.title,
            art_style=prompt_req.art_style
        )
        image_paths[panel.panel_number] = img_url

    # Step 4: Bind into unified ComicLayout
    layout = build_comic_layout(
        request=prompt_req,
        outline=outline,
        narrative=narrative,
        image_paths=image_paths,
        comic_id=comic_id
    )

    # Step 5: Export to PDF
    pdf_rel_path = export_comic_to_pdf(layout)
    layout.pdf_path = pdf_rel_path
    persist_comic_layout(layout)

    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={
            "comic": layout,
            "title": f"Preview - {layout.title}"
        }
    )


@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    """
    Programmatic JSON API route for generating a full comic package.
    Returns structured panels and the PDF export URL.
    """
    comic_id = uuid.uuid4().hex[:10]
    logger.info("Processing JSON generation request for comic_id=%s...", comic_id)

    outline = generate_panel_outline(payload)
    narrative = generate_story_narrative(outline, payload)

    image_paths: Dict[int, str] = {}
    for panel in outline.panels:
        img_url = generate_panel_image(
            prompt=panel.image_prompt,
            comic_id=comic_id,
            panel_number=panel.panel_number,
            title=panel.title,
            art_style=payload.art_style
        )
        image_paths[panel.panel_number] = img_url

    layout = build_comic_layout(
        request=payload,
        outline=outline,
        narrative=narrative,
        image_paths=image_paths,
        comic_id=comic_id
    )

    pdf_rel_path = export_comic_to_pdf(layout)
    layout.pdf_path = pdf_rel_path
    persist_comic_layout(layout)

    return {
        "status": "success",
        "comic_id": layout.comic_id,
        "title": layout.title,
        "pdf_url": layout.pdf_path,
        "layout": layout.model_dump()
    }


@router.get("/test-image")
async def test_image(prompt: str = "A heroic red fox exploring an enchanted forest, vibrant anime style"):
    """Developer utility route for verifying image generation configuration."""
    result = generate_single_test_image(prompt)
    return result


@router.get("/download-pdf/{comic_id}")
async def download_pdf(comic_id: str):
    """Streams the generated PDF file directly to client with attachment header."""
    layout = retrieve_comic_layout(comic_id)
    filename = f"{comic_id}_comic.pdf"
    file_path = settings.exports_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Requested comic PDF was not found.")

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename
    )


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, comic_id: Optional[str] = None):
    """Renders the export confirmation page matching the project documentation."""
    layout = retrieve_comic_layout(comic_id) if comic_id else None
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "comic_id": comic_id,
            "comic": layout,
            "title": "Comic Exported Successfully!"
        }
    )
