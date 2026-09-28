import os
import logging
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from huggingface_hub import InferenceClient
from app.config import settings

logger = logging.getLogger("comiccraft.image_generator")

_local_pipeline = None


def is_valid_hf_key() -> bool:
    """Checks if HF_API_KEY is properly set and not a placeholder."""
    key = settings.hf_api_key.strip()
    return bool(key) and not key.startswith("your_") and len(key) > 10


def get_local_diffusers_pipeline():
    """Attempts to initialize local Diffusers pipeline if torch and CUDA are available."""
    global _local_pipeline
    if _local_pipeline is not None:
        return _local_pipeline

    try:
        import torch
        from diffusers import StableDiffusionPipeline
        if torch.cuda.is_available():
            logger.info("Initializing local Stable Diffusion pipeline with CUDA...")
            _local_pipeline = StableDiffusionPipeline.from_pretrained(
                settings.sd_model_id,
                torch_dtype=torch.float16
            ).to("cuda")
            return _local_pipeline
        else:
            return None
    except Exception as e:
        logger.debug("Local diffusers initialization bypassed: %s", e)
        return None


def generate_via_hf_api(prompt: str) -> Optional[Image.Image]:
    """Generates a real AI artwork image using official Hugging Face InferenceClient."""
    if not is_valid_hf_key():
        return None

    try:
        client = InferenceClient(token=settings.hf_api_key)
        # Try state-of-the-art fast model FLUX.1-schnell, then SDXL, then SD 1.5
        models = [
            "black-forest-labs/FLUX.1-schnell",
            "stabilityai/stable-diffusion-xl-base-1.0",
            settings.sd_model_id
        ]
        for m in models:
            try:
                logger.info("Generating AI artwork via Hugging Face model: %s...", m)
                img = client.text_to_image(prompt, model=m)
                if img:
                    logger.info("Successfully generated real AI image from Hugging Face!")
                    return img.convert("RGB")
            except Exception as e:
                logger.warning("Hugging Face model %s failed: %s", m, e)
    except Exception as e:
        logger.error("Hugging Face client error: %s", e)

    return None


def generate_placeholder_panel(
    prompt: str,
    panel_number: int = 1,
    title: str = "Comic Panel",
    art_style: str = "Comic Book"
) -> Image.Image:
    """
    Renders an aesthetically styled comic panel with atmospheric background scenery using Pillow.
    Used only as a safety fallback if the external AI service is unreachable or rate limited.
    """
    width, height = 768, 512
    
    palettes = [
        ((25, 33, 60), (60, 90, 140)),     # Deep midnight twilight
        ((30, 55, 40), (80, 130, 90)),     # Lush enchanted forest
        ((80, 35, 25), (160, 80, 45)),     # Ember sunset
        ((60, 25, 75), (130, 60, 145)),    # Mystical cosmic purple
        ((20, 50, 80), (50, 120, 170)),    # Oceanic azure horizon
    ]
    c1, c2 = palettes[(panel_number - 1) % len(palettes)]

    img = Image.new("RGB", (width, height), c1)
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / height
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    p_lower = prompt.lower()
    if "forest" in p_lower or panel_number == 1 or panel_number == 2:
        draw.polygon([(0, 380), (180, 260), (360, 360), (540, 240), (768, 370), (768, 512), (0, 512)], fill=(15, 22, 35))
        for tx in range(40, width - 40, 60):
            th = 60 + (tx * 13) % 50
            draw.polygon([(tx, 440 - th), (tx - 18, 440), (tx + 18, 440)], fill=(10, 15, 25))
    elif "space" in p_lower or "robot" in p_lower or panel_number == 4:
        draw.ellipse([(width // 2 - 90, 130), (width // 2 + 90, 310)], fill=(245, 180, 50))
        draw.arc([(width // 2 - 140, 190), (width // 2 + 140, 250)], start=0, end=360, fill=(255, 255, 255), width=3)
        for sx, sy in [(100, 80), (220, 110), (600, 90), (680, 140), (150, 220), (630, 260)]:
            draw.text((sx, sy), "*", fill=(255, 255, 200))
    else:
        draw.polygon([(0, 340), (240, 280), (480, 350), (768, 300), (768, 512), (0, 512)], fill=(20, 25, 38))

    border_margin = 16
    draw.rectangle(
        [(border_margin, border_margin), (width - border_margin, height - border_margin)],
        outline=(255, 255, 255),
        width=4
    )
    draw.rectangle(
        [(border_margin + 6, border_margin + 6), (width - border_margin - 6, height - border_margin - 6)],
        outline=(20, 20, 25),
        width=2
    )

    badge_w, badge_h = 280, 44
    draw.rectangle(
        [(border_margin + 12, border_margin + 12), (border_margin + 12 + badge_w, border_margin + 12 + badge_h)],
        fill=(255, 215, 0),
        outline=(20, 20, 25),
        width=2
    )

    font = ImageFont.load_default()
    
    draw.text(
        (border_margin + 24, border_margin + 24),
        f"PANEL {panel_number}: {title.upper()[:24]}",
        fill=(20, 20, 25),
        font=font
    )

    draw.text(
        (width - border_margin - 170, height - border_margin - 30),
        f"Style: {art_style.upper()}",
        fill=(240, 240, 240),
        font=font
    )

    prompt_box_top = height - 120
    draw.rectangle(
        [(border_margin + 20, prompt_box_top), (width - border_margin - 20, height - border_margin - 40)],
        fill=(15, 20, 30),
        outline=(200, 210, 225),
        width=1
    )

    wrapped_lines = []
    words = prompt.split()
    current_line = []
    for w in words:
        current_line.append(w)
        if len(" ".join(current_line)) > 75:
            wrapped_lines.append(" ".join(current_line))
            current_line = []
    if current_line:
        wrapped_lines.append(" ".join(current_line))

    start_y = prompt_box_top + 10
    for line in wrapped_lines[:3]:
        draw.text((border_margin + 32, start_y), line, fill=(240, 245, 255), font=font)
        start_y += 18

    return img


def generate_panel_image(
    prompt: str,
    comic_id: str,
    panel_number: int,
    title: str = "Comic Panel",
    art_style: str = "Comic Book"
) -> str:
    """
    Coordinates image generation across available backends and saves the panel to disk.
    Returns the relative URL path suitable for web rendering (/static/panels/...).
    """
    settings.panels_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{comic_id}_panel_{panel_number}.png"
    destination_path = settings.panels_dir / filename

    img = None

    # Tier 1: Generate real AI image via Hugging Face InferenceClient
    if is_valid_hf_key():
        # Enhance prompt with style prefix for vivid artistic output
        enhanced_prompt = f"{art_style} comic illustration of {prompt}, vibrant colors, graphic novel panel, masterpiece"
        img = generate_via_hf_api(enhanced_prompt)

    # Tier 2: Try local Diffusers GPU pipeline if CUDA is available
    if img is None:
        pipe = get_local_diffusers_pipeline()
        if pipe is not None:
            try:
                logger.info("Generating panel %d with local GPU Diffusers...", panel_number)
                result = pipe(prompt, num_inference_steps=20, guidance_scale=7.5)
                img = result.images[0]
            except Exception as e:
                logger.error("Local Diffusers inference failed: %s", e)

    # Tier 3: Styled visual fallback
    if img is None:
        logger.info("Using graphic visual fallback for panel %d...", panel_number)
        img = generate_placeholder_panel(
            prompt=prompt,
            panel_number=panel_number,
            title=title,
            art_style=art_style
        )

    img.save(str(destination_path), format="PNG")
    logger.info("Saved panel %d to %s", panel_number, destination_path)
    return f"/static/panels/{filename}"


def generate_single_test_image(prompt: str) -> dict:
    """Developer test utility endpoint logic matching /test-image."""
    settings.panels_dir.mkdir(parents=True, exist_ok=True)
    filename = "test_image.png"
    destination_path = settings.panels_dir / filename

    img = None
    if is_valid_hf_key():
        img = generate_via_hf_api(prompt)
    if img is None:
        pipe = get_local_diffusers_pipeline()
        if pipe is not None:
            try:
                img = pipe(prompt, num_inference_steps=15).images[0]
            except Exception as e:
                logger.error("Local diffusers test error: %s", e)
    if img is None:
        img = generate_placeholder_panel(prompt, panel_number=1, title="Test Image")

    img.save(str(destination_path), format="PNG")
    return {
        "status": "success",
        "prompt": prompt,
        "image_path": f"/static/panels/{filename}",
        "full_path": str(destination_path)
    }
