from pathlib import Path
from app.config import settings
from app.exporters import export_comic_to_pdf
from app.gemini_flash import generate_fallback_outline
from app.gemini_pro import generate_fallback_narrative
from app.image_generator import generate_panel_image
from app.layout_builder import build_comic_layout
from app.models import PromptRequest


def test_pdf_export_generation():
    req = PromptRequest(
        story_prompt="A young wizard seeks a forgotten spell in ancient ruins",
        character_name="Lyra",
        setting="Ancient Ruins",
        tone="Mystical",
        art_style="Watercolor"
    )
    outline = generate_fallback_outline(req)
    narrative = generate_fallback_narrative(outline, req)

    comic_id = "test_export_99"
    # Generate at least one actual panel image on disk
    img_path = generate_panel_image(
        prompt=outline.panels[0].image_prompt,
        comic_id=comic_id,
        panel_number=1,
        title=outline.panels[0].title,
        art_style=req.art_style
    )

    images = {1: img_path}
    for i in range(2, 6):
        images[i] = generate_panel_image(
            prompt=outline.panels[i-1].image_prompt,
            comic_id=comic_id,
            panel_number=i,
            title=outline.panels[i-1].title,
            art_style=req.art_style
        )

    layout = build_comic_layout(
        request=req,
        outline=outline,
        narrative=narrative,
        image_paths=images,
        comic_id=comic_id
    )

    pdf_rel_path = export_comic_to_pdf(layout)
    pdf_full_path = settings.exports_dir / f"{comic_id}_comic.pdf"

    assert pdf_full_path.exists()
    assert pdf_full_path.stat().st_size > 1000

    # Verify PDF magic bytes
    with open(pdf_full_path, "rb") as f:
        header = f.read(5)
        assert header == b"%PDF-"
