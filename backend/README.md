# LumironScraper Backend

API REST Flask pour Due Diligence OSINT - Analyse complète de profils professionnels avec données officielles françaises.

## 🎯 Fonctionnalités

- **Due Diligence v3** - 18 sections enrichies (vs 11 en v2) : psychologie, finances, réseau, analyse juridique
- **Sources officielles** - Pappers (légal/financier), DVF (immobilier), HATVP (PPE)
- **Streaming SSE** - Suivi temps réel avec 6 étapes de progression (~2-3min)
- **Double sécurité** - Prompt renforcé + validation Python post-LLM (anti-hallucination)
- **Scraping multi-sources** - Architecture modulaire (Serper, Firecrawl, sites entreprises)
- **Analyse LLM** - GPT-4o avec température 0.3 pour précision maximale
- **Cache SQLite** - Expiration configurable + force refresh
- **Prompts Jinja2** - Templates éditables avec exemples inline

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
PAPPERS_API_KEY=...      # Données légales/financières
PAPPERS_MODE=standard    # ou 'complete' (mode étendu)

# Flask
PORT=5100
CORS_ORIGINS=http://localhost:5101,http://localhost:5173

# Cache
CACHE_TTL_SECONDS=604800  # 7 jours
DATABASE_PATH=data/lumironscraper.db

# Scraping
MAX_TOTAL_SCRAPES=15     # 15 scrapes pour v3 enrichi
OPENAI_MODEL=gpt-4o
```

### Obtenir les clés API

- **OpenAI**: https://platform.openai.com/api-keys (~$0.04/profil en v3)
- **Firecrawl**: https://firecrawl.dev ($0.003/page)
- **Serper**: https://serper.dev (2500 gratuites, puis $0.005/recherche)
- **Pappers**: https://www.pappers.fr/api (20€/mois = 1000 crédits, ~5-10 crédits/profil)

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

### Recherche classique

```bash
POST /api/v1/search
Content-Type: application/json

{
  "first_name": "Anthony",
  "last_name": "Tartour",
  "company": "Lumiron",
  "force_refresh": false
}
```

**Réponse (v3 - 18 sections):**
```json
{
  "success": true,
  "cached": false,
  "data": {
    "full_name": "Anthony Tartour",
    "current_position": "Co-Founder",
    "company": "Lumiron",
    "credibility_score": 75,
    "reputation_score": 80,
    "influence_score": 65,
    "reliability_score": 70,
    "risk_level": "Moyen",
    "professional_experience": [...],
    "business_ecosystem": {...},
    "financial_intelligence": {...},
    "psychology_and_approach": {...},
    "red_flags": [...],
    // + 13 autres sections
  }
}
```

### Recherche avec streaming SSE (recommandé)

```bash
POST /api/v1/search-stream
Content-Type: application/json

{
  "first_name": "Anthony",
  "last_name": "Tartour",
  "company": "Lumiron"
}
```

**Réponse (Server-Sent Events):**
```
data: {"type":"progress","step":"cache","percent":5,"message":"Vérification du cache..."}

data: {"type":"progress","step":"pappers","percent":15,"message":"Récupération données Pappers..."}

data: {"type":"progress","step":"dvf","percent":25,"message":"Recherche DVF (immobilier)..."}

data: {"type":"progress","step":"hatvp","percent":35,"message":"Vérification HATVP (PPE)..."}

data: {"type":"progress","step":"scraping","percent":50,"message":"Scraping des pages (15 scrapes, ~2min)..."}

data: {"type":"progress","step":"analysis","percent":85,"message":"Analyse GPT-4o (enrichissement)..."}

data: {"type":"complete","data":{...}}
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
│   ├── models/               # Pydantic schemas v3 (18 sections)
│   │   ├── person_profile.py
│   │   └── person_profile_v3.py
│   ├── routes/               # API routes (search, search-stream)
│   ├── services/
│   │   ├── cache_service.py
│   │   ├── llm_service.py      # + validation post-LLM
│   │   ├── profile_service.py
│   │   └── scraper_service.py
│   ├── sources/              # Sources modulaires
│   │   ├── base_source.py
│   │   ├── serper_search_source.py
│   │   ├── pappers_source.py    # Données légales FR
│   │   ├── dvf_source.py        # Immobilier FR
│   │   └── hatvp_source.py      # PPE FR
│   ├── templates/prompts/    # Prompts Jinja2 + exemples inline
│   │   └── due_diligence_analysis.txt  # Prompt v3
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
git clone https://github.com/Crisxzu/lumiron-scraper.git
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
