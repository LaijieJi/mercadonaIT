# Mercadona Chef

> AI-powered food recognition and recipe generation with Mercadona product integration.

Upload a photo of any dish, and Mercadona Chef will identify it, generate a Spanish recipe, and show you the ingredients available at Mercadona with real prices.

Built for the **Mercadona IT Hackathon** (April 2025).

---

## Features

- **Food Recognition** — Vision Transformer (ViT) model classifies dishes from 101 food categories
- **Recipe Generation** — AI generates step-by-step Spanish recipes using Qwen 2.5 LLM
- **Product Matching** — Fuzzy search finds matching Mercadona products for each ingredient
- **Price Calculation** — Real-time total cost estimation based on current Mercadona prices
- **Responsive UI** — Clean, modern interface built with Angular and Tailwind CSS

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Angular | 19.2 | Web framework |
| TypeScript | 5.7 | Type-safe JavaScript |
| Tailwind CSS | 4.1 | Utility-first styling |
| Lucide | 0.488 | Icon library |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.115 | REST API framework |
| PyTorch | 2.6 | Deep learning |
| Transformers | 4.51 | Hugging Face models |
| rapidfuzz | 3.9 | Fuzzy string matching |

### AI Models
| Model | Type | Purpose |
|-------|------|---------|
| `nateraw/vit-base-food101` | Vision Transformer | Food image classification |
| `Qwen/Qwen2.5-1.5B-Instruct` | LLM | Spanish recipe generation |

---

## Prerequisites

- **Python** 3.11+
- **Node.js** 18+ and npm
- **GPU** (optional) — CUDA or Apple Metal for faster inference

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/LaijieJi/mercadonaIT.git
cd mercadonaIT
```

### 2. Backend setup

```bash
cd api

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend setup

```bash
cd app

# Install dependencies
npm install
```

---

## Usage

### Start the backend server

```bash
cd api
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Start the frontend development server

```bash
cd app
npm start
```

Open your browser at `http://localhost:4200`

### How to use

1. Click the upload area or drag and drop an image of a dish
2. (Optional) Add extra instructions like "sin cebolla" or "con extra de queso"
3. Click **Analízalo**
4. View the identified dish, recipe steps, and Mercadona ingredients with prices

---

## Project Structure

```
mercadonaIT/
├── api/                        # Python backend
│   ├── main.py                 # FastAPI server & endpoints
│   ├── food_classifier.py      # ViT classification & recipe generation
│   ├── product_search.py       # Fuzzy product matching
│   ├── scraper_standalone.py   # Mercadona product scraper
│   ├── requirements.txt
│   └── data/
│       └── productos.json      # Product database (~1500 items)
│
├── app/                        # Angular frontend
│   ├── src/
│   │   └── app/
│   │       ├── app.component.ts
│   │       ├── app.component.html
│   │       └── models.ts
│   ├── package.json
│   └── angular.json
│
└── README.md
```

---

## API Reference

### Analyze dish image

```
POST /
Content-Type: multipart/form-data
```

**Request body:**
| Field | Type | Description |
|-------|------|-------------|
| `image` | File | Image file (JPEG, PNG, etc.) |

**Response:**
```json
{
  "name": "Paella",
  "recipe": [
    "Sofríe la cebolla y el ajo en aceite de oliva...",
    "Añade el arroz y el caldo de pollo...",
    "..."
  ],
  "ingredients": [
    {
      "name": "Arroz Hacendado",
      "img_url": "https://prod-mercadona.imgix.net/...",
      "price": 1.25
    }
  ]
}
```

---

## Updating Product Data

The product database can be refreshed by running the scraper:

```bash
cd api
python scraper_standalone.py
```

This fetches current products and prices from Mercadona's public API.

---

## Architecture

```
┌─────────────────┐      POST /image      ┌─────────────────┐
│                 │ ──────────────────────▶│                 │
│  Angular App    │                        │  FastAPI Server │
│  (Port 4200)    │◀────────────────────── │  (Port 8000)    │
│                 │      JSON response     │                 │
└─────────────────┘                        └────────┬────────┘
                                                    │
                              ┌─────────────────────┼─────────────────────┐
                              │                     │                     │
                              ▼                     ▼                     ▼
                    ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
                    │  ViT Classifier │   │   Qwen 2.5 LLM  │   │  Product Search │
                    │  (Food-101)     │   │  (Recipe Gen)   │   │  (rapidfuzz)    │
                    └─────────────────┘   └─────────────────┘   └─────────────────┘
```

---

## Development

### Run tests

```bash
# Frontend tests
cd app
npm test

# Backend (if tests are added)
cd api
pytest
```

### Build for production

```bash
cd app
npm run build
```

Output will be in `app/dist/mercadona-chef/`

---

## Performance Notes

- **First request** will be slow as models are loaded into memory
- **GPU acceleration** significantly improves inference speed:
  - NVIDIA CUDA for Linux/Windows
  - Apple Metal (MPS) for macOS
- Models are cached after first load for subsequent requests

---

## License

This project was created for the Mercadona IT Hackathon 2025.

---

## Acknowledgments

- [Mercadona](https://www.mercadona.es/) for the hackathon opportunity
- [Hugging Face](https://huggingface.co/) for pre-trained models
- [nateraw](https://huggingface.co/nateraw) for the Food-101 ViT model
- [Qwen](https://huggingface.co/Qwen) for the instruction-tuned LLM
