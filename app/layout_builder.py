import uuid
from datetime import datetime
from typing import Dict, List
from app.models import ComicLayout, ComicOutline, PromptRequest, StoryNarrative, StoryPanel


def build_comic_layout(
    request: PromptRequest,
    outline: ComicOutline,
    narrative: StoryNarrative,
    image_paths: Dict[int, str],
    comic_id: str = None
) -> ComicLayout:
    """
    Binds panel outlines, narrative text, and rendered image assets into a unified ComicLayout.
    Uses panel_number as the authoritative synchronization key.
    """
    if not comic_id:
        comic_id = uuid.uuid4().hex[:10]

    # Index narratives by panel number for safe lookup
    narrative_map = {n.panel_number: n for n in narrative.panels}

    bound_panels: List[StoryPanel] = []

    for panel_outline in outline.panels:
        p_num = panel_outline.panel_number
        n_rec = narrative_map.get(p_num)
        img_path = image_paths.get(p_num, "")

        bound_panels.append(
            StoryPanel(
                panel_number=p_num,
                title=panel_outline.title,
                scene_description=panel_outline.scene_description,
                image_prompt=panel_outline.image_prompt,
                caption=n_rec.caption if n_rec else f"Scene {p_num}",
                narration=n_rec.narration if n_rec else panel_outline.scene_description,
                dialogue=n_rec.dialogue if n_rec and n_rec.dialogue else "",
                image_path=img_path
            )
        )

    # Sort strictly by panel_number to ensure reading order
    bound_panels.sort(key=lambda p: p.panel_number)

    layout = ComicLayout(
        comic_id=comic_id,
        title=outline.story_title or f"{request.character_name}'s Comic Adventure",
        story_prompt=request.story_prompt,
        character_name=request.character_name,
        setting=request.setting,
        tone=request.tone,
        art_style=request.art_style,
        panels=bound_panels,
        pdf_path=None,
        created_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    )

    return layout
