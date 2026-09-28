import json
import logging
from typing import Optional
import google.generativeai as genai
from app.config import settings
from app.models import ComicOutline, PanelNarrative, PromptRequest, StoryNarrative

logger = logging.getLogger("comiccraft.gemini_pro")


def is_valid_gemini_key() -> bool:
    """Checks if GEMINI_API_KEY is properly set and not a placeholder."""
    key = settings.gemini_api_key.strip()
    return bool(key) and not key.startswith("your_") and len(key) > 10


def get_pro_model():
    """Initializes and returns the configured Gemini Pro GenerativeModel instance."""
    if not is_valid_gemini_key():
        return None
    try:
        genai.configure(api_key=settings.gemini_api_key)
        return genai.GenerativeModel(
            model_name=settings.gemini_pro_model,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.8,
            }
        )
    except Exception as e:
        logger.warning("Could not initialize Gemini Pro client: %s", e)
        return None


def generate_fallback_narrative(outline: ComicOutline, request: PromptRequest) -> StoryNarrative:
    """Provides rich narrative, dialogue, and caption fallback matching the outline."""
    narratives = []
    default_captions = [
        f"The adventure begins at the border of {request.setting}.",
        "Deeper into the unknown...",
        "Peril strikes without warning!",
        "A test of true resolve!",
        "Peace restored, legends born."
    ]
    
    for i, panel in enumerate(outline.panels):
        narratives.append(
            PanelNarrative(
                panel_number=panel.panel_number,
                caption=default_captions[i] if i < len(default_captions) else f"Chapter {panel.panel_number}",
                narration=(
                    f"{request.character_name} advanced with steady determination. "
                    f"{panel.scene_description} The atmosphere was distinctly {request.tone.lower()}, "
                    f"promising an unforgettable journey."
                ),
                dialogue=f'"{request.character_name}: I must see this through, whatever lies ahead!"' if i == 0 or i == 3 else ""
            )
        )
    return StoryNarrative(panels=narratives)


def generate_story_narrative(outline: ComicOutline, request: PromptRequest) -> StoryNarrative:
    """Generates panel narration, captions, and character dialogue using Gemini Pro."""
    model = get_pro_model()
    if not model:
        return generate_fallback_narrative(outline, request)

    system_prompt = (
        "You are an acclaimed comic book writer and dialogue specialist. "
        "Expand the given 5-panel comic outline into immersive comic narration, captions, and character dialogue.\n"
        "Return STRICT JSON matching this exact schema:\n"
        "{\n"
        '  "panels": [\n'
        '    {\n'
        '      "panel_number": 1,\n'
        '      "caption": "Short, punchy comic caption hook",\n'
        '      "narration": "Vivid storytelling prose establishing atmosphere, tension, and action",\n'
        '      "dialogue": "Character dialogue or thought bubble text, e.g. Character: \'Quote\' (or empty string if none)"\n'
        '    }\n'
        "  ]\n"
        "}\n"
        "Generate exactly 5 panels corresponding to the 5 outline panels."
    )

    panels_context = []
    for p in outline.panels:
        panels_context.append(
            f"Panel {p.panel_number}: Title='{p.title}', Scene='{p.scene_description}'"
        )

    user_prompt = (
        f"Story Title: {outline.story_title}\n"
        f"Main Character: {request.character_name}\n"
        f"Setting: {request.setting}\n"
        f"Tone: {request.tone}\n"
        f"Art Style: {request.art_style}\n"
        f"Outline Panels:\n" + "\n".join(panels_context)
    )

    try:
        response = model.generate_content([system_prompt, user_prompt])
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        data = json.loads(text)
        story = StoryNarrative.model_validate(data)
        if len(story.panels) != 5:
            logger.warning("Gemini Pro returned %s narrative panels instead of 5. Falling back.", len(story.panels))
            return generate_fallback_narrative(outline, request)
        return story
    except Exception as e:
        logger.error("Failed to generate narrative via Gemini Pro: %s. Using baseline fallback.", e)
        return generate_fallback_narrative(outline, request)
