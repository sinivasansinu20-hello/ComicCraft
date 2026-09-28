from typing import List, Optional
from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    """Structured request payload for comic story creation."""
    story_prompt: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Core story idea or narrative brief",
        examples=["A brave fox explores an enchanted forest"]
    )
    character_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the main character",
        examples=["Ember"]
    )
    setting: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Story setting or primary environment",
        examples=["Forest"]
    )
    tone: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Narrative tone or mood",
        examples=["Dramatic"]
    )
    art_style: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Visual style for artwork generation",
        examples=["Anime"]
    )


class PanelOutline(BaseModel):
    """Structured outline representation for a single comic panel."""
    panel_number: int = Field(..., ge=1, le=5, description="Sequential panel identifier (1-5)")
    title: str = Field(..., description="Short heading for the panel")
    scene_description: str = Field(..., description="Contextual description of setting, action, and mood")
    image_prompt: str = Field(..., description="Detailed visual prompt tailored for image generation")


class ComicOutline(BaseModel):
    """Complete 5-panel outline produced by the planner."""
    story_title: str = Field(default="My Comic Story", description="Title for the overall comic")
    panels: List[PanelOutline] = Field(..., min_length=5, max_length=5, description="Exact 5-panel sequence")


class PanelNarrative(BaseModel):
    """Narrative storytelling content for a single panel."""
    panel_number: int = Field(..., ge=1, le=5)
    caption: str = Field(..., description="Short comic caption or opening hook")
    narration: str = Field(..., description="Detailed scene narration")
    dialogue: Optional[str] = Field(default="", description="Spoken dialogue or thought bubble text")


class StoryNarrative(BaseModel):
    """Complete narrative expansion across all 5 panels."""
    panels: List[PanelNarrative] = Field(..., min_length=5, max_length=5)


class StoryPanel(BaseModel):
    """Fully bound panel record containing outline, story, and visual asset path."""
    panel_number: int = Field(..., ge=1, le=5)
    title: str
    scene_description: str
    image_prompt: str
    caption: str
    narration: str
    dialogue: Optional[str] = ""
    image_path: str = Field(..., description="Web-accessible or filesystem path to rendered panel image")


class ComicLayout(BaseModel):
    """Complete assembled comic layout ready for preview and PDF export."""
    comic_id: str
    title: str
    story_prompt: str
    character_name: str
    setting: str
    tone: str
    art_style: str
    panels: List[StoryPanel]
    pdf_path: Optional[str] = None
    created_at: str
