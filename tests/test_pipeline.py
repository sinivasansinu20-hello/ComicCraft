from app.gemini_flash import generate_fallback_outline, generate_panel_outline
from app.gemini_pro import generate_fallback_narrative, generate_story_narrative
from app.image_generator import generate_panel_image, generate_placeholder_panel
from app.layout_builder import build_comic_layout
from app.models import PromptRequest


def test_outline_generation_fallback():
    req = PromptRequest(
        story_prompt="A courageous knight enters a glowing labyrinth",
        character_name="Arthur",
        setting="Medieval Castle",
        tone="Adventurous",
        art_style="Comic Book"
    )
    outline = generate_panel_outline(req)
    assert len(outline.panels) == 5
    assert outline.panels[0].panel_number == 1
    assert outline.panels[4].panel_number == 5
    assert "Arthur" in outline.panels[0].scene_description or "Arthur" in outline.story_title


def test_narrative_generation_fallback():
    req = PromptRequest(
        story_prompt="A courageous knight enters a glowing labyrinth",
        character_name="Arthur",
        setting="Medieval Castle",
        tone="Adventurous",
        art_style="Comic Book"
    )
    outline = generate_fallback_outline(req)
    narrative = generate_story_narrative(outline, req)
    assert len(narrative.panels) == 5
    assert narrative.panels[0].caption != ""
    assert narrative.panels[0].narration != ""


def test_placeholder_panel_generation():
    img = generate_placeholder_panel(
        prompt="Arthur enters the grand stone hall with torchlight flickering",
        panel_number=1,
        title="The Hall",
        art_style="Comic Book"
    )
    assert img.size == (768, 512)
    assert img.mode == "RGB"


def test_layout_builder_consistency():
    req = PromptRequest(
        story_prompt="A courageous knight enters a glowing labyrinth",
        character_name="Arthur",
        setting="Medieval Castle",
        tone="Adventurous",
        art_style="Comic Book"
    )
    outline = generate_fallback_outline(req)
    narrative = generate_fallback_narrative(outline, req)
    images = {i: f"/static/panels/test_p{i}.png" for i in range(1, 6)}

    layout = build_comic_layout(
        request=req,
        outline=outline,
        narrative=narrative,
        image_paths=images,
        comic_id="test1234"
    )

    assert layout.comic_id == "test1234"
    assert len(layout.panels) == 5
    for i, p in enumerate(layout.panels):
        assert p.panel_number == i + 1
        assert p.image_path == f"/static/panels/test_p{i+1}.png"
