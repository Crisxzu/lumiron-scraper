# 🔍 LumironScraper

**Intelligence de profils professionnels pour accompagner vos démarches commerciales**

Solution full-stack de scraping et d'analyse de profils professionnels. À partir d'un prénom, nom et entreprise, le système collecte des informations publiques sur le web et utilise l'IA pour générer un profil structuré en français.

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
- **Flask** - Framework web léger et performant
- **OpenAI GPT-4o** - Analyse et structuration des données en français
- **Firecrawl** - Scraping web robuste
- **Serper** - API de recherche Google
- **SQLite** - Cache avec expiration configurable (7 jours par défaut)
- **Pydantic** - Validation des schémas de données
- **Jinja2** - Templates pour les prompts LLM

### Frontend
- **React 18** - Interface utilisateur moderne
- **Vite** - Build tool ultra-rapide
- **Tailwind CSS** - Styling responsive et professionnel
- **Axios** - Client HTTP
- **Layout dynamique** - Côte à côte sur desktop, empilé sur mobile

### DevOps
- **Docker** - Containerisation
- **Docker Compose** - Orchestration multi-services
- **Gunicorn + Gevent** - Serveur WSGI performant
- **Nginx** - Serveur web pour le frontend

---

## ✨ Fonctionnalités

### Backend
- ✅ **Architecture modulaire** - Système de sources extensible (Serper, sites entreprises, etc.)
- ✅ **Cache SQLite intelligent** - TTL configurable + statistiques
- ✅ **Force refresh** - Option pour ignorer le cache
- ✅ **Multi-profils LinkedIn** - Fusion automatique de tous les profils trouvés
- ✅ **Prompts Jinja2** - Templates éditables sans toucher au code
- ✅ **CORS configurable** - Via variable d'environnement
- ✅ **Timezone-aware** - Gestion UTC pour le cache
- ✅ **Health check** - Endpoint de monitoring
- ✅ **Analyse LLM en français** - Tous les résultats structurés en français

### Frontend
- ✅ **Layout côte à côte** - Formulaire gauche, résultats droite (desktop)
- ✅ **Animations fluides** - Slide-in depuis la droite pour les résultats
- ✅ **Responsive design** - Mobile-first avec breakpoints Tailwind
- ✅ **Indicateur de cache** - Badge vert (cache) ou bleu (frais) avec âge
- ✅ **Force refresh checkbox** - Ignorer le cache facilement
- ✅ **Layout dynamique** - Formulaire centré par défaut, se déplace à gauche au chargement

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
│   │   │   └── person_profile.py    # Schémas Pydantic
│   │   ├── routes/
│   │   │   └── api_routes.py        # Endpoints REST
│   │   ├── services/
│   │   │   ├── cache_service.py     # Gestion cache SQLite
│   │   │   ├── llm_service.py       # OpenAI GPT-4
│   │   │   ├── profile_service.py   # Orchestration
│   │   │   └── scraper_service.py   # Pipeline scraping
│   │   ├── sources/                 # 🔌 Architecture modulaire
│   │   │   ├── base_source.py       # Classe abstraite
│   │   │   ├── serper_search_source.py
│   │   │   └── company_website_source.py
│   │   ├── templates/prompts/       # Templates Jinja2
│   │   │   └── profile_analysis.txt
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
│   │   │   └── ProfileResults.jsx   # Affichage profil
│   │   ├── services/
│   │   │   └── api.js               # Client Axios
│   │   ├── App.jsx                  # Layout dynamique
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
# Frontend: http://localhost:3000
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
nano .env  # Ajouter OPENAI_API_KEY, FIRECRAWL_API_KEY, SERPER_API_KEY

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

### Persistance des données

La base de données SQLite est automatiquement persistée via un volume Docker :

```yaml
volumes:
  - ./backend/data:/app/data
```

**Emplacement local:** `./backend/data/lumironscraper.db`

### Healthcheck

Le backend inclut un healthcheck Python natif :

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

### `POST /api/v1/search`

Recherche et analyse un profil professionnel.

**Body:**
```json
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
  "cache_created_at": "2025-12-04T10:00:00",
  "data": {
    "full_name": "Satya Nadella",
    "current_position": "Directeur Général",
    "company": "Microsoft",
    "professional_experience": [
      {
        "position": "CEO",
        "company": "Microsoft",
        "period": "2014 - Présent",
        "description": "..."
      }
    ],
    "skills": ["Leadership", "Cloud Computing", "Transformation digitale"],
    "publications": [
      {
        "title": "Hit Refresh",
        "date": "2017",
        "description": "..."
      }
    ],
    "public_contact": {
      "email": null,
      "phone": null,
      "linkedin": "https://linkedin.com/in/satyanadella"
    },
    "summary": "Satya Nadella est le Directeur Général de Microsoft depuis 2014...",
    "linkedin_url": "https://linkedin.com/in/satyanadella",
    "sources": [
      "https://linkedin.com/in/satyanadella",
      "https://microsoft.com/...",
      "..."
    ]
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

LumironScraper utilise un système de **sources modulaires** pour le scraping. Chaque source hérite de `BaseSource` et est automatiquement chargée.

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
nano backend/app/templates/prompts/profile_analysis.txt
```

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
| `PORT` | `5100` | Port du backend |
| `FLASK_DEBUG` | `0` | Mode debug (0=prod, 1=dev) |
| `OPENAI_MODEL` | `gpt-4o` | Modèle OpenAI |
| `MAX_TOTAL_SCRAPES` | `3` | Nombre max de scrapes |
| `DATABASE_PATH` | `data/lumironscraper.db` | Chemin de la DB SQLite |
| `CACHE_TTL_SECONDS` | `604800` | TTL du cache (7 jours) |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Origins CORS autorisées |

### Variables d'environnement Frontend

| Variable | Défaut | Description |
|----------|--------|-------------|
| `VITE_API_URL` | `http://localhost:5100/api/v1` | URL de l'API backend |

---

## 🎯 Utilisation

1. **Ouvrir l'interface** : http://localhost:3000
2. **Remplir le formulaire** :
   - Prénom (ex: Satya)
   - Nom (ex: Nadella)
   - Entreprise (ex: Microsoft)
   - ☑️ Force refresh (optionnel, pour ignorer le cache)
3. **Cliquer sur "Rechercher"**
4. **Consulter le profil** structuré :
   - Nom complet + poste actuel
   - Résumé professionnel
   - Expérience détaillée
   - Compétences
   - Publications
   - Contact public
   - Sources utilisées

**Badge de cache :**
- 🟢 Vert : Données du cache (avec âge en minutes)
- 🔵 Bleu : Données fraîches (nouvellement scrapées)

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
