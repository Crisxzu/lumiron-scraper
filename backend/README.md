# LumironScraper Backend

API REST Flask pour scraping et analyse intelligente de profils professionnels.

## 🎯 Fonctionnalités

- **Scraping multi-sources** - Architecture modulaire (Serper, sites entreprises, LinkedIn)
- **Analyse LLM** - OpenAI GPT-4 pour structurer les données en français
- **Cache SQLite** - Expiration configurable + force refresh
- **Fusion LinkedIn** - Combine tous les profils trouvés
- **Prompts Jinja2** - Templates éditables

## 🔧 Prérequis

- **Python 3.12.6**
- pip + venv

## 📦 Installation

```bash
# Environnement virtuel
python3.12 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Dépendances
pip install -r requirements.txt
```

## ⚙️ Configuration

```bash
# Copier .env.example
cp .env.example .env

# Éditer et configurer les clés API
nano .env
```

### Variables essentielles

```bash
# APIs (obligatoires)
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
SERPER_API_KEY=...

# Flask
PORT=5100
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Cache
CACHE_TTL_SECONDS=604800  # 7 jours
DATABASE_PATH=data/lumironscraper.db

# Scraping
MAX_TOTAL_SCRAPES=3
OPENAI_MODEL=gpt-4o
```

### Obtenir les clés API

- **OpenAI**: https://platform.openai.com/api-keys (~$0.01/profil)
- **Firecrawl**: https://firecrawl.dev ($0.003/page)
- **Serper**: https://serper.dev (2500 recherches gratuites, puis $0.005/recherche)

## 🚀 Démarrage

### Développement

```bash
python main.py
# → http://localhost:5100
```

### Production

```bash
gunicorn --bind 0.0.0.0:5100 --workers 4 "app:create_app()"
```

### Docker

```bash
# Build
docker build -t lumironscraper-backend .

# Run
docker run -p 5100:5100 --env-file .env lumironscraper-backend
```

## 📡 API Endpoints

### Recherche de profil

```bash
POST /api/v1/search
Content-Type: application/json

{
  "first_name": "Satya",
  "last_name": "Nadella",
  "company": "Microsoft",
  "force_refresh": false  // Optionnel
}
```

**Réponse:**
```json
{
  "success": true,
  "cached": true,
  "cache_age_seconds": 3600,
  "data": {
    "full_name": "Satya Nadella",
    "current_position": "Directeur Général",
    "company": "Microsoft",
    "professional_experience": [...],
    "skills": [...],
    "summary": "...",
    "sources": [...]
  }
}
```

### Autres endpoints

```bash
GET  /api/v1/health           # Health check
GET  /api/v1/cache/stats      # Stats du cache
POST /api/v1/cache/clear-expired  # Nettoyage
```

## 🏗️ Architecture

```
backend/
├── app/
│   ├── __init__.py           # Factory Flask
│   ├── db/                   # SQLite setup
│   ├── models/               # Pydantic schemas
│   ├── routes/               # API routes
│   ├── services/
│   │   ├── cache_service.py
│   │   ├── llm_service.py
│   │   ├── profile_service.py
│   │   └── scraper_service.py
│   ├── sources/              # Sources modulaires
│   │   ├── base_source.py
│   │   ├── serper_search_source.py
│   │   └── company_website_source.py
│   ├── templates/prompts/    # Templates Jinja2
│   └── utils/                # Utilitaires
├── data/                     # SQLite DB (auto-créé)
├── main.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

## 🔌 Ajouter une Source

### 1. Créer le fichier

```python
# app/sources/my_source.py

from typing import List
from app.sources.base_source import BaseSource

class MySource(BaseSource):
    @classmethod
    def get_name(cls) -> str:
        return "my_source"

    @classmethod
    def get_description(cls) -> str:
        return "Ma source custom"

    def get_urls(self, first_name: str, last_name: str, company: str) -> List[str]:
        # Logique de génération d'URLs
        return [
            f"https://example.com/{first_name}-{last_name}",
            # ...
        ]
```

### 2. Enregistrer

```python
# app/sources/__init__.py

from app.sources.my_source import MySource

AVAILABLE_SOURCES = [
    SerperSearchSource,
    CompanyWebsiteSource,
    MySource,  # ← Ajouter ici
]
```

### 3. Redémarrer

```bash
python main.py
```

C'est tout ! La source sera automatiquement intégrée.

## 💾 Cache SQLite

Le cache stocke les profils dans `data/lumironscraper.db` avec:
- **Expiration** basée sur `CACHE_TTL_SECONDS`
- **Force refresh** via paramètre API
- **Compteur d'accès** pour analytics

```bash
# Backup
cp data/lumironscraper.db backups/lumironscraper_$(date +%Y%m%d).db

# Compacter
sqlite3 data/lumironscraper.db "VACUUM;"
```

## 🚢 Déploiement

### Heroku

```bash
heroku create lumironscraper-backend
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set FIRECRAWL_API_KEY=fc-...
heroku config:set SERPER_API_KEY=...
git push heroku main
```

### Railway

1. Connecter le repo GitHub
2. Ajouter les variables d'environnement
3. Déploiement automatique via `Procfile`

### VPS

```bash
sudo apt install python3.12 python3.12-venv
git clone https://github.com/your-repo/LumironScraper.git
cd LumironScraper/backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nano .env
gunicorn --bind 0.0.0.0:5100 --workers 4 "app:create_app()"
```

## 🛠️ Développement

### Modifier le prompt

```bash
nano app/templates/prompts/profile_analysis.txt
```

Redémarrer pour appliquer les changements.

### Logs

```python
print(f"[Service] ✓ Success")
print(f"[Service] ✗ Error")
print(f"[Service] ⚠ Warning")
```

### Tests

```bash
# Health check
curl http://localhost:5100/api/v1/health

# Search
curl -X POST http://localhost:5100/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Satya","last_name":"Nadella","company":"Microsoft"}'
```
