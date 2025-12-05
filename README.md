# 🔍 LumironScraper

**Due Diligence OSINT - Intelligence économique et analyse de risque**

Solution full-stack pour l'analyse complète de profils professionnels avec données officielles françaises. <br/>
À partir d'un prénom, nom et entreprise, le système collecte des informations publiques (web + bases légales) et utilise GPT-4o pour générer une analyse Due Diligence enrichie en 18 sections avec scoring de risque.

---

## 📋 Table des matières

- [Stack Technique](#-stack-technique)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Démarrage Rapide](#-démarrage-rapide)
- [Docker Compose](#-docker-compose)
- [Documentation Détaillée](#-documentation-détaillée)
- [API Endpoints](#-api-endpoints)
- [Extensibilité](#-extensibilité)
- [Déploiement](#-déploiement)

---

## 🛠️ Stack Technique

### Backend
- **Python 3.12.6** - Runtime
- **Flask** - Framework web avec support SSE (Server-Sent Events)
- **OpenAI GPT-4o** - Analyse Due Diligence avec température 0.3
- **Firecrawl** - Scraping web robuste (15 scrapes/profil)
- **Serper** - API de recherche Google
- **Pappers API** - Données légales et financières françaises
- **DVF (open data)** - Transactions immobilières françaises
- **HATVP (open data)** - Personnes politiquement exposées (PPE)
- **SQLite** - Cache avec expiration configurable (7 jours par défaut)
- **Pydantic** - Validation des schémas v3 (18 sections)
- **Jinja2** - Templates pour les prompts avec exemples inline

### Frontend
- **React 18** - Interface utilisateur moderne avec 6 onglets
- **Vite** - Build tool ultra-rapide
- **Tailwind CSS** - Styling responsive et professionnel
- **Server-Sent Events** - Progression temps réel (~2-3min)
- **Layout dynamique** - Côte à côte sur desktop, empilé sur mobile

### DevOps
- **Docker** - Containerisation
- **Docker Compose** - Orchestration multi-services
- **Gunicorn + Gevent** - Serveur WSGI performant
- **Nginx** - Serveur web pour le frontend

---

## ✨ Fonctionnalités

### Backend (v3)
- ✅ **Due Diligence enrichie** - 18 sections vs 11 en v2 (psychologie, finances, réseau, analyse juridique)
- ✅ **Sources officielles FR** - Pappers (légal/financier), DVF (immobilier), HATVP (PPE)
- ✅ **SSE streaming** - Progression temps réel avec 6 étapes (~2-3min)
- ✅ **Double sécurité** - Prompt renforcé + validation Python post-LLM (anti-hallucination)
- ✅ **Scoring de risque** - Crédibilité, réputation, influence, fiabilité (/100) + niveau de risque
- ✅ **Red flags** - Détection automatique avec sévérité (Critique/Modéré/Mineur)
- ✅ **Traçabilité** - Sources obligatoires pour chaque donnée financière
- ✅ **Architecture modulaire** - Système de sources extensible
- ✅ **Cache SQLite intelligent** - TTL configurable + force refresh
- ✅ **Analyse en français** - Tous les résultats structurés en français

### Frontend (v3)
- ✅ **6 onglets organisés** - Vue d'ensemble, Expérience, Financier, Médias, Réseau, Analyse
- ✅ **Progression temps réel** - Barre de progression SSE avec 6 étapes visuelles
- ✅ **Scores visuels** - Affichage des 4 scores (/100) + badge niveau de risque
- ✅ **Red flags avec badges** - Alertes colorées par sévérité
- ✅ **Timeline chronologique** - Visualisation de la carrière avec dots et lignes
- ✅ **Traçabilité sources** - Affichage des sources sous chaque donnée financière
- ✅ **Layout dynamique** - Formulaire centré par défaut, se déplace à gauche au chargement
- ✅ **Responsive design** - Mobile-first avec breakpoints Tailwind

---

## 🏗️ Architecture

```
lumiron-scraper/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Factory Flask + CORS
│   │   ├── db/
│   │   │   └── database.py          # Setup SQLite
│   │   ├── models/
│   │   │   ├── person_profile.py    # Schémas Pydantic v3 (18 sections)
│   │   │   └── person_profile_v3.py # Modèles enrichis
│   │   ├── routes/
│   │   │   └── api_routes.py        # Endpoints REST + SSE streaming
│   │   ├── services/
│   │   │   ├── cache_service.py     # Gestion cache SQLite
│   │   │   ├── llm_service.py       # GPT-4o + validation post-LLM
│   │   │   ├── profile_service.py   # Orchestration
│   │   │   └── scraper_service.py   # Pipeline scraping
│   │   ├── sources/                 # 🔌 Architecture modulaire
│   │   │   ├── base_source.py       # Classe abstraite
│   │   │   ├── serper_search_source.py
│   │   │   ├── pappers_source.py    # Données légales FR
│   │   │   ├── dvf_source.py        # Immobilier FR
│   │   │   └── hatvp_source.py      # PPE FR
│   │   ├── templates/prompts/       # Templates Jinja2 + exemples inline
│   │   │   └── due_diligence_analysis.txt  # Prompt v3
│   │   └── utils/
│   │       └── url_validator.py
│   ├── data/                        # SQLite DB (auto-créé)
│   │   └── lumironscraper.db
│   ├── main.py                      # Point d'entrée
│   ├── wsgi.py                      # WSGI pour Gunicorn
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md                    # 📘 Documentation backend
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchForm.jsx       # Formulaire + force refresh
│   │   │   └── ProfileResults.jsx   # 6 onglets + 18 sections v3
│   │   ├── services/
│   │   │   └── api.js               # Client SSE + fetch
│   │   ├── App.jsx                  # Layout dynamique + progression SSE
│   │   ├── main.jsx
│   │   └── index.css                # Animations custom
│   ├── public/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── README.md                    # 📘 Documentation frontend
│
├── docker-compose.yml               # 🐳 Orchestration
└── README.md                        # 📘 Ce fichier
```

---

## 🚀 Démarrage Rapide

### Option 1 : Docker Compose (Recommandé)

```bash
# 1. Configuration
cp backend/.env.example backend/.env
nano backend/.env  # Ajouter vos clés API

# 2. Lancer l'application
docker-compose up -d

# 3. Accéder
# Frontend: http://localhost:5101
# Backend:  http://localhost:5100
# Health:   http://localhost:5100/api/v1/health
```

---

### Option 2 : Développement Local

#### Backend

```bash
cd backend

# Environnement virtuel
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
nano .env  # Ajouter OPENAI_API_KEY, FIRECRAWL_API_KEY, SERPER_API_KEY, PAPPERS_API_KEY

# Lancer
python main.py
# → http://localhost:5100
```

#### Frontend

```bash
cd frontend

# Dépendances
npm install

# Configuration (optionnel)
cp .env.example .env

# Lancer
npm run dev
# → http://localhost:5173
```

**Documentation détaillée:**
- Backend : [backend/README.md](./backend/README.md)
- Frontend : [frontend/README.md](./frontend/README.md)

---

## 🐳 Docker Compose

### Configuration Frontend

Le frontend nécessite l'URL de l'API au **moment du build** (pas au runtime) :

```bash
# 1. Configurer l'URL de l'API
cd frontend
cp .env.example .env
nano .env  # Éditer VITE_API_URL

# 2. Lancer avec Docker Compose
cd ..
docker-compose up -d --build
```

Le `docker-compose.yml` passe automatiquement `VITE_API_URL` depuis `frontend/.env` comme build argument.

### Démarrage

```bash
docker-compose up -d
```

### Logs

```bash
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuild après changement d'URL

```bash
# Si vous modifiez VITE_API_URL dans frontend/.env
docker-compose up -d --build frontend
```

### Persistance des données

La base de données SQLite est automatiquement persistée via un volume Docker :

```yaml
volumes:
  - ./backend/data:/app/data
```

**Emplacement local:** `./backend/data/lumironscraper.db`

### Healthcheck

Le backend inclut un healthcheck Python natif (pas besoin de curl) :

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5100/api/v1/health').read()"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

Le frontend attend que le backend soit "healthy" avant de démarrer.

---

## 📚 Documentation Détaillée

| Document | Description |
|----------|-------------|
| [backend/README.md](./backend/README.md) | Installation backend, configuration, architecture sources, deployment |
| [frontend/README.md](./frontend/README.md) | Setup frontend, composants React, responsive design, deployment |

---

## 📡 API Endpoints

### `GET /api/v1/health`

Vérifie l'état du serveur.

**Réponse:**
```json
{
  "status": "healthy",
  "message": "LumironScraper API is running"
}
```

---

### `POST /api/v1/search-stream` (Recommandé)

Recherche avec streaming SSE - Progression temps réel.

**Body:**
```json
{
  "first_name": "Anthony",
  "last_name": "Tartour",
  "company": "Lumiron",
  "force_refresh": false
}
```

**Réponse (Server-Sent Events):**
```
data: {"type":"progress","step":"cache","percent":5,"message":"Vérification du cache..."}
data: {"type":"progress","step":"pappers","percent":15,"message":"Récupération données Pappers..."}
data: {"type":"progress","step":"scraping","percent":50,"message":"Scraping des pages (15 scrapes, ~2min)..."}
data: {"type":"progress","step":"analysis","percent":85,"message":"Analyse GPT-4o..."}
data: {"type":"complete","data":{...profil v3...}}
```

---

### `POST /api/v1/search`

Recherche classique (sans streaming).

**Body:**
```json
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
    "media_presence": {...},
    "red_flags": [...],
    "career_timeline": [...],
    // + 12 autres sections
  }
}
```

---

### `GET /api/v1/cache/stats`

Statistiques du cache.

**Réponse:**
```json
{
  "total_entries": 42,
  "cache_size": "2.5 MB",
  "oldest_entry": "2025-11-27T10:00:00",
  "newest_entry": "2025-12-04T15:30:00"
}
```

---

### `POST /api/v1/cache/clear-expired`

Nettoie les entrées expirées du cache.

**Réponse:**
```json
{
  "success": true,
  "deleted_entries": 5
}
```

---

## 🔌 Extensibilité

### Architecture Modulaire des Sources

LumironScraper utilise un système de **sources modulaires** pour le scraping. <br/>
Chaque source hérite de `BaseSource` et est automatiquement chargée.

#### Ajouter une nouvelle source

**1. Créer le fichier** `backend/app/sources/my_source.py`

```python
from typing import List
from app.sources.base_source import BaseSource

class MySource(BaseSource):
    @classmethod
    def get_name(cls) -> str:
        return "my_source"

    @classmethod
    def get_description(cls) -> str:
        return "Ma source personnalisée"

    def get_urls(self, first_name: str, last_name: str, company: str) -> List[str]:
        # Logique pour générer les URLs à scraper
        return [
            f"https://example.com/search?q={first_name}+{last_name}",
            # ...
        ]
```

**2. Enregistrer** dans `backend/app/sources/__init__.py`

```python
from app.sources.my_source import MySource

AVAILABLE_SOURCES = [
    SerperSearchSource,
    CompanyWebsiteSource,
    MySource,  # ← Ajouter ici
]
```

**3. Redémarrer** le backend

```bash
docker-compose restart backend
# ou
python main.py
```

**C'est tout !** La source sera automatiquement utilisée dans le pipeline de scraping.

---

### Modifier le prompt LLM

Les prompts sont des **templates Jinja2** éditables sans toucher au code :

```bash
nano backend/app/templates/prompts/due_diligence_analysis.txt
```

Le prompt v3 inclut des **exemples inline** directement dans la structure JSON pour guider GPT-4o.

Redémarrer pour appliquer les changements.

---

### Changer de LLM

Modifier `backend/app/services/llm_service.py` :

```python
# Exemple avec Anthropic Claude
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
```

---

## 🚢 Déploiement

### Backend

#### Heroku

```bash
heroku create lumironscraper-backend
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set FIRECRAWL_API_KEY=fc-...
heroku config:set SERPER_API_KEY=...
heroku config:set PAPPERS_API_KEY=...
git push heroku main
```

#### Railway

1. Connecter le repo GitHub
2. Ajouter les variables d'environnement
3. Deploy automatique via `Procfile`

#### VPS

```bash
# Installer Python 3.12
sudo apt install python3.12 python3.12-venv

# Clone et setup
git clone https://github.com/Crisxzu/lumiron-scraper.git
cd LumironScraper/backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configuration
nano .env

# Lancer avec Gunicorn
gunicorn --bind 0.0.0.0:5100 --workers 4 "app:create_app()"
```

---

### Frontend

#### Netlify

```bash
# Build command
npm run build

# Publish directory
dist

# Environment variables
VITE_API_URL=https://your-api.com/api/v1
```

#### Vercel

```bash
vercel --prod
```

Configuration automatique via `vite.config.js`.

---

## 🔒 Sécurité

- ✅ Toutes les clés API dans des variables d'environnement
- ✅ CORS configurable via `.env`
- ✅ Validation des entrées avec Pydantic
- ✅ Pas de stockage de données sensibles
- ✅ HTTPS recommandé en production
- ✅ Healthcheck sans exposition de données sensibles

---

## 📊 Configuration

### Variables d'environnement Backend

| Variable | Défaut | Description |
|----------|--------|-------------|
| `OPENAI_API_KEY` | - | Clé API OpenAI (obligatoire) |
| `FIRECRAWL_API_KEY` | - | Clé API Firecrawl (obligatoire) |
| `SERPER_API_KEY` | - | Clé API Serper (obligatoire) |
| `PAPPERS_API_KEY` | - | Clé API Pappers (obligatoire) |
| `PAPPERS_MODE` | `standard` | Mode Pappers (`standard` ou `complete`) |
| `PORT` | `5100` | Port du backend |
| `FLASK_DEBUG` | `0` | Mode debug (0=prod, 1=dev) |
| `OPENAI_MODEL` | `gpt-4o` | Modèle OpenAI |
| `MAX_TOTAL_SCRAPES` | `15` | Nombre max de scrapes (v3) |
| `DATABASE_PATH` | `data/lumironscraper.db` | Chemin de la DB SQLite |
| `CACHE_TTL_SECONDS` | `604800` | TTL du cache (7 jours) |
| `CORS_ORIGINS` | `http://localhost:5101,...` | Origins CORS autorisées |

### Variables d'environnement Frontend

| Variable | Défaut | Description |
|----------|--------|-------------|
| `VITE_API_URL` | `http://localhost:5100/api/v1` | URL de l'API backend |

---

## 🎯 Utilisation

1. **Ouvrir l'interface** : http://localhost:5101
2. **Remplir le formulaire** :
   - Prénom (ex: Anthony)
   - Nom (ex: Tartour)
   - Entreprise (ex: Lumiron)
   - ☑️ Force refresh (optionnel, pour ignorer le cache)
3. **Cliquer sur "Rechercher"**
4. **Suivre la progression** (6 étapes, ~2-3min) :
   - Vérification cache → Pappers → DVF → HATVP → Scraping → Analyse GPT-4o
5. **Consulter le profil v3** (6 onglets) :
   - **Vue d'ensemble** : Scores, niveau de risque, résumé, red flags
   - **Expérience** : Parcours professionnel, timeline chronologique
   - **Financier** : Intelligence financière avec sources, écosystème d'affaires, patrimoine immobilier, PPE
   - **Médias & Réputation** : Présence médiatique avec sentiment, publications
   - **Réseau & Influence** : Connexions, indicateurs d'influence
   - **Analyse** : Psychologie avec traits justifiés, ice breakers, cohérence

---

## 🐛 Troubleshooting

### Backend ne démarre pas

```bash
# Vérifier les logs
docker-compose logs backend

# Vérifier les variables d'environnement
docker-compose exec backend env | grep API_KEY
```

### Frontend ne peut pas contacter le backend

```bash
# Vérifier que le backend est accessible
curl http://localhost:5100/api/v1/health

# Vérifier les CORS
docker-compose logs backend | grep CORS
```

### Base de données verrouillée

```bash
docker-compose down
docker-compose up -d
```
