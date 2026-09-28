# ComicCraft — AI Comic Story Creator

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

ComicCraft is a full-stack generative AI creative application that transforms a user's informal story idea and creative preferences into a 5-panel, illustrated comic. It orchestrates multi-model generative intelligence across outline planning, narrative dialogue synthesis, text-to-image artwork generation, layout composition, and multi-page PDF publishing.

---

## Architecture Overview

ComicCraft follows a clean, three-layer modular architecture:

```
                                  ┌─────────────────────────────┐
                                  │   Browser / Web Client      │
                                  └──────────────┬──────────────┘
                                                 │ HTTP / Form / JSON
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ FastAPI Application Core (app/main.py, app/routes.py)                                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  1. Outline Planner      2. Narrative Writer     3. Image Generator   4. Layout Builder │
│  (gemini_flash.py)       (gemini_pro.py)         (image_generator.py) (layout_builder.py)│
└────────┬───────────────────────┬─────────────────────────┬──────────────────────┬───────┘
         │                       │                         │                      │
         ▼                       ▼                         ▼                      ▼
┌──────────────────┐    ┌──────────────────┐    ┌────────────────────┐   ┌────────────────┐
│  Gemini Flash    │    │   Gemini Pro     │    │  Stable Diffusion  │   │  FPDF2 Engine  │
│ (Story Planning) │    │ (Story/Dialogue) │    │  (Visual Art)      │   │ (PDF Exporter) │
└──────────────────┘    └──────────────────┘    └────────────────────┘   └────────────────┘
```

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `app/main.py` | FastAPI application initialization, middleware, static directory mounting, and lifecycle events. |
| `app/routes.py` | Web interface endpoints (`GET /`, `POST /generate`, `GET /export-success`) and JSON API endpoints (`POST /generate-comic/json`, `GET /test-image`). |
| `app/models.py` | Pydantic V2 schemas for request validation, panel records, outline structures, and layout models. |
| `app/config.py` | Centralized environment variable management with fallback configuration. |
| `app/gemini_flash.py` | 5-panel storyboard planner leveraging Google Gemini Flash with strict JSON schema enforcement. |
| `app/gemini_pro.py` | Creative writer generating captions, atmospheric narrative, and character dialogue via Google Gemini Pro. |
| `app/image_generator.py` | Adaptive visual generation supporting Hugging Face Inference API, local Diffusers, and styled offline placeholders. |
| `app/layout_builder.py` | Authoritative synchronization binding outline records, story text, and rendered artwork by panel number. |
| `app/exporters.py` | Multi-page PDF generator embedding metadata, cover page, and formatted panel cards with custom typography. |

---

## Prerequisites

- **Python**: Version 3.10, 3.11, or 3.12.
- **Git**: For repository version control.
- **API Keys** (optional for local/test mode, recommended for production quality):
  - **Google Gemini API Key**: [Get a key from Google AI Studio](https://aistudio.google.com/).
  - **Hugging Face API Token**: [Get a token from Hugging Face](https://huggingface.co/settings/tokens).

---

## Quickstart & Installation

### 1. Clone & Set Up Virtual Environment

```bash
# Windows (PowerShell)
python -m venv env
.\env\Scripts\activate

# macOS / Linux
python3 -m venv env
source env/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the provided `.env.example` to `.env`:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and fill in your credentials:

```env
GEMINI_API_KEY=your_gemini_api_key_here
HF_API_KEY=your_huggingface_api_key_here
GEMINI_FLASH_MODEL=gemini-1.5-flash
GEMINI_PRO_MODEL=gemini-1.5-pro
SD_MODEL_id=runwayml/stable-diffusion-v1-5
HOST=127.0.0.1
PORT=8000
DEBUG=True
```

*(Note: ComicCraft features an intelligent offline baseline generator. If API keys are not supplied during initial testing, the application gracefully synthesizes cohesive sample storylines, stylized artwork placeholders, and compiled PDFs without crashing).*

---

## Running the Application

Start the development server with live reload:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, access the services:
- **Interactive Web App**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc Docs**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## API Documentation & Contract

### Programmatic Comic Generation

**`POST /generate-comic/json`**

**Request Header**: `Content-Type: application/json`

**Request Body**:
```json
{
  "story_prompt": "A brave fox explores an enchanted forest",
  "character_name": "Ember",
  "setting": "Forest",
  "tone": "Dramatic",
  "art_style": "Anime"
}
```

**Response** (`200 OK`):
```json
{
  "status": "success",
  "comic_id": "a1b2c3d4e5",
  "title": "Ember's Quest in the Forest",
  "pdf_url": "/static/exports/a1b2c3d4e5_comic.pdf",
  "layout": {
    "comic_id": "a1b2c3d4e5",
    "title": "Ember's Quest in the Forest",
    "character_name": "Ember",
    "setting": "Forest",
    "tone": "Dramatic",
    "art_style": "Anime",
    "panels": [
      {
        "panel_number": 1,
        "title": "Ember's Beginning",
        "scene_description": "Ember stands at the boundary...",
        "image_prompt": "Anime style, wide shot...",
        "caption": "The adventure begins...",
        "narration": "Ember advanced with steady determination...",
        "dialogue": "Ember: I must see this through!",
        "image_path": "/static/panels/a1b2c3d4e5_panel_1.png"
      }
    ],
    "pdf_path": "/static/exports/a1b2c3d4e5_comic.pdf",
    "created_at": "2026-09-23 15:50:00 UTC"
  }
}
```

---

## Testing & Quality Assurance

Run the automated test suite with pytest:

```bash
# Run all tests
pytest -v

# Run with test summary output
pytest -v --tb=short
```

### Test Coverage Breakdown
- `tests/test_models.py`: Validates Pydantic schemas, boundaries (panel count 1–5), and string constraints.
- `tests/test_pipeline.py`: Tests Gemini Flash outline planning, Gemini Pro narrative writing, Pillow panel creation, and layout consistency.
- `tests/test_exporters.py`: Tests end-to-end multi-page FPDF2 PDF rendering and verifies binary `%PDF-` signature.
- `tests/test_routes.py`: Tests web form requests, JSON API endpoints, image utilities, PDF downloads, and template responses.

---

## Local Development in VS Code

1. **Recommended Extensions**:
   - Python (`ms-python.python`)
   - Pylance (`ms-python.vscode-pylance`)
   - Jinja (`samuelcolvin.jinja-html`)
2. **Interpreter Selection**:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P`) $\rightarrow$ `Python: Select Interpreter` $\rightarrow$ Choose your virtual environment (`.\env\Scripts\python.exe`).
3. **Run & Debug Configuration**:
   Create `.vscode/launch.json`:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "FastAPI: ComicCraft",
               "type": "debugpy",
               "request": "launch",
               "module": "uvicorn",
               "args": [
                   "app.main:app",
                   "--reload",
                   "--port",
                   "8000"
               ],
               "jinja": true,
               "justMyCode": true
           }
       ]
   }
   ```

---

## Security & Best Practices

- **Zero Hard-coded Secrets**: Credentials are strictly loaded through Pydantic Settings from `.env` or system environment variables.
- **Input Sanitization**: Pydantic models enforce character limits and string sanitization on user input.
- **Safe Asset Handling**: Panel images and export PDFs are generated with random UUID-tagged filenames to avoid path traversal and asset overwrite collisions.
- **Resilient Fallbacks**: Network interruptions and third-party API rate limits are intercepted and caught with structured fallback generation.

---

## License

MIT License. Developed as a production-grade implementation of the ComicCraft AI Comic Story Creator project.
