import pytest
from pydantic import ValidationError
from app.models import ComicLayout, ComicOutline, PanelOutline, PromptRequest, StoryPanel


def test_prompt_request_valid():
    req = PromptRequest(
        story_prompt="A brave fox explores an enchanted forest",
        character_name="Ember",
        setting="Forest",
        tone="Dramatic",
        art_style="Anime"
    )
    assert req.character_name == "Ember"
    assert req.setting == "Forest"


def test_prompt_request_validation_failure():
    with pytest.raises(ValidationError):
        PromptRequest(
            story_prompt="ab", # too short (min 3)
            character_name="",
            setting="",
            tone="",
            art_style=""
        )


def test_panel_outline_bounds():
    with pytest.raises(ValidationError):
        PanelOutline(
            panel_number=6, # must be <= 5
            title="Invalid",
            scene_description="Desc",
            image_prompt="Prompt"
        )


def test_comic_outline_exact_five_panels():
    panels = [
        PanelOutline(panel_number=i, title=f"T{i}", scene_description=f"D{i}", image_prompt=f"P{i}")
        for i in range(1, 6)
    ]
    outline = ComicOutline(story_title="Fox Journey", panels=panels)
    assert len(outline.panels) == 5

    # Should fail if fewer than 5
    with pytest.raises(ValidationError):
        ComicOutline(story_title="Short", panels=panels[:3])
