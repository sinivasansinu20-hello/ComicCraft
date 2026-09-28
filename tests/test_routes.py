import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "ComicCraft"


def test_index_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Create Your Comic" in response.text
    assert "story_prompt" in response.text
    assert "character_name" in response.text


def test_test_image_endpoint():
    response = client.get("/test-image?prompt=A+cute+robot+in+a+cyberpunk+alley")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "image_path" in data


def test_generate_comic_json_api():
    payload = {
        "story_prompt": "A small robot discovers a secret greenhouse on a derelict starship",
        "character_name": "Unit-7",
        "setting": "Deep Space",
        "tone": "Whimsical",
        "art_style": "Comic Book"
    }
    response = client.post("/generate-comic/json", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "comic_id" in data
    assert "pdf_url" in data
    assert len(data["layout"]["panels"]) == 5


def test_generate_comic_form_submission():
    form_data = {
        "story_prompt": "A wandering ranger protects a hidden mountain shrine",
        "character_name": "Kaelen",
        "setting": "Forest",
        "tone": "Dramatic",
        "art_style": "Realistic"
    }
    response = client.post("/generate", data=form_data)
    assert response.status_code == 200
    assert "Your Comic Preview" in response.text
    assert "Kaelen" in response.text
    assert "Panel 1:" in response.text
    assert "Panel 5:" in response.text


def test_export_success_page():
    response = client.get("/export-success")
    assert response.status_code == 200
    assert "Comic Exported Successfully!" in response.text
