import json
import logging
from typing import Optional
import google.generativeai as genai
from app.config import settings
from app.models import ComicOutline, PanelOutline, PromptRequest

logger = logging.getLogger("comiccraft.gemini_flash")


def is_valid_gemini_key() -> bool:
    """Checks if GEMINI_API_KEY is properly set and not a placeholder."""
    key = settings.gemini_api_key.strip()
    return bool(key) and not key.startswith("your_") and len(key) > 10


def get_flash_model():
    """Initializes and returns the configured Gemini Flash GenerativeModel instance."""
    if not is_valid_gemini_key():
        return None
    try:
        genai.configure(api_key=settings.gemini_api_key)
        return genai.GenerativeModel(
            model_name=settings.gemini_flash_model,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.7,
            }
        )
    except Exception as e:
        logger.warning("Could not initialize Gemini Flash client: %s", e)
        return None


def generate_fallback_outline(request: PromptRequest) -> ComicOutline:
    """Provides a coherent 5-panel outline baseline when the external model is unavailable."""
    return ComicOutline(
        story_title=f"{request.character_name}'s Quest in the {request.setting.title()}",
        panels=[
            PanelOutline(
                panel_number=1,
                title=f"{request.character_name}'s Beginning",
                scene_description=f"{request.character_name} stands at the boundary of the {request.setting}, preparing for the journey.",
                image_prompt=f"{request.art_style} style, wide shot of {request.character_name} entering {request.setting}, {request.tone} atmosphere, cinematic lighting, vivid colors."
            ),
            PanelOutline(
                panel_number=2,
                title="The First Discovery",
                scene_description=f"{request.character_name} navigates deeper into the {request.setting} and discovers an intriguing relic or sign.",
                image_prompt=f"{request.art_style} style, medium shot of {request.character_name} inspecting a mysterious ancient relic in the {request.setting}, {request.tone} mood, detailed foreground."
            ),
            PanelOutline(
                panel_number=3,
                title="Unexpected Challenge",
                scene_description=f"An unexpected obstacle or adversary appears in the {request.setting}, challenging {request.character_name}.",
                image_prompt=f"{request.art_style} style, dynamic action angle, {request.character_name} confronting a sudden hazard in the {request.setting}, {request.tone} tension, dramatic shadows."
            ),
            PanelOutline(
                panel_number=4,
                title="The Critical Moment",
                scene_description=f"{request.character_name} summons courage and acts decisively to overcome the challenge.",
                image_prompt=f"{request.art_style} style, heroic close-up of {request.character_name} taking decisive action, glowing energy effects, {request.tone} intensity."
            ),
            PanelOutline(
                panel_number=5,
                title="Triumphant Aftermath",
                scene_description=f"The ordeal is resolved as {request.character_name} gazes across the peaceful {request.setting}.",
                image_prompt=f"{request.art_style} style, wide cinematic vista, {request.character_name} standing victoriously in the tranquil {request.setting}, warm golden hour lighting."
            ),
        ]
    )


def generate_panel_outline(request: PromptRequest) -> ComicOutline:
    """Generates a structured 5-panel comic outline using Gemini Flash with JSON validation."""
    model = get_flash_model()
    if not model:
        return generate_fallback_outline(request)

    system_prompt = (
        "You are an expert comic book director and storyboard artist. "
        "Break the provided story idea into a structured 5-panel comic outline.\n"
        "Return STRICT JSON matching this exact schema:\n"
        "{\n"
        '  "story_title": "Short catchy title",\n'
        '  "panels": [\n'
        '    {\n'
        '      "panel_number": 1,\n'
        '      "title": "Panel Title",\n'
        '      "scene_description": "Contextual description of character, environment, mood, and action",\n'
        '      "image_prompt": "Art-directed prompt for text-to-image generator, including art style, lighting, camera angle, and character details"\n'
        '    }\n'
        "  ]\n"
        "}\n"
        "You must generate exactly 5 panels in ascending order (1 to 5): Panel 1 (Introduction), Panel 2 (Rising Action), "
        "Panel 3 (Midpoint/Conflict), Panel 4 (Climax), Panel 5 (Resolution).\n"
        "Keep image prompts visually descriptive, cinematic, and cohesive."
    )

    user_prompt = (
        f"Story Idea: {request.story_prompt}\n"
        f"Main Character: {request.character_name}\n"
        f"Setting: {request.setting}\n"
        f"Tone: {request.tone}\n"
        f"Art Style: {request.art_style}\n"
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
        outline = ComicOutline.model_validate(data)
        if len(outline.panels) != 5:
            logger.warning("Gemini Flash returned %s panels instead of 5. Falling back.", len(outline.panels))
            return generate_fallback_outline(request)
        return outline
    except Exception as e:
        logger.error("Failed to generate outline via Gemini Flash: %s. Using baseline fallback.", e)
        return generate_fallback_outline(request)
