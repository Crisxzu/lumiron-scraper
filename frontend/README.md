# LumironScraper Frontend

Interface React pour Due Diligence OSINT - Analyse complète de profils professionnels avec données officielles.

## 🎯 Fonctionnalités

- **Due Diligence v3** - 18 sections organisées en 6 onglets (Vue d'ensemble, Expérience, Financier, Médias, Réseau, Analyse)
- **Progression temps réel** - Suivi SSE avec 6 étapes visuelles (~2-3min)
- **Scores visuels** - Crédibilité, réputation, influence, fiabilité (/100)
- **Red flags** - Alertes avec badges de sévérité (Critique/Modéré/Mineur)
- **Traçabilité** - Sources affichées pour chaque donnée financière
- **Timeline** - Visualisation chronologique de la carrière
- **Layout dynamique** - Formulaire centré par défaut, se déplace à gauche quand résultats affichés
- **Animations fluides** - Slide-in depuis la droite pour les résultats
- **Responsive design** - Layout côte à côte (desktop), empilé (mobile)
- **Tailwind CSS** - Interface moderne et performante

## 🔧 Prérequis

- **Node.js 18+** (ou 20+)
- npm ou yarn

## 📦 Installation

```bash
cd frontend

# Installer les dépendances
npm install
# ou
yarn install
```

## ⚙️ Configuration

### Variables d'environnement

Créer un fichier `.env` :

```bash
# URL de l'API backend
VITE_API_URL=http://localhost:5100/api/v1
```

**Par défaut**, si `VITE_API_URL` n'est pas défini, l'app utilise `http://localhost:5100/api/v1`.

## 🚀 Démarrage

### Développement

```bash
npm run dev
# ou
yarn dev

# → http://localhost:5173
```

### Production

```bash
# Build
npm run build
# ou
yarn build

# Preview du build
npm run preview
```

Les fichiers buildés seront dans `dist/`.

## 🏗️ Architecture

```
frontend/
├── src/
│   ├── App.jsx              # Composant principal + layout + SSE progress
│   ├── main.jsx             # Point d'entrée
│   ├── index.css            # Styles globaux + animations custom
│   ├── components/
│   │   ├── SearchForm.jsx   # Formulaire + force refresh
│   │   └── ProfileResults.jsx  # 6 onglets + 18 sections v3
│   └── services/
│       └── api.js           # Client API (searchPersonStream + SSE)
├── public/                  # Assets statiques
├── nginx.conf               # Config Nginx pour Docker
├── Dockerfile               # Build multi-stage
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## 🔌 Intégration Backend

### API Endpoint principal (SSE)

```javascript
POST /api/v1/search-stream
Content-Type: application/json

{
  "first_name": "Anthony",
  "last_name": "Tartour",
  "company": "Lumiron",
  "force_refresh": false
}
```

### Progression temps réel (SSE)

```javascript
// 6 étapes de progression
data: {"type":"progress","step":"cache","percent":5,"message":"Vérification du cache..."}
data: {"type":"progress","step":"pappers","percent":15,"message":"Récupération données Pappers..."}
data: {"type":"progress","step":"dvf","percent":25,"message":"Recherche DVF (immobilier)..."}
data: {"type":"progress","step":"hatvp","percent":35,"message":"Vérification HATVP (PPE)..."}
data: {"type":"progress","step":"scraping","percent":50,"message":"Scraping des pages (15 scrapes, ~2min)..."}
data: {"type":"progress","step":"analysis","percent":85,"message":"Analyse GPT-4o (enrichissement)..."}
data: {"type":"complete","data":{...}}
```

### Réponse finale (v3 - 18 sections)

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

## 🎨 Composants

### SearchForm

Formulaire de recherche avec :
- Champs : Prénom, Nom, Entreprise
- Checkbox **Force Refresh** pour ignorer le cache
- Validation : tous les champs requis
- États : loading, disabled

### ProfileResults (v3)

**6 onglets organisés :**

1. **Vue d'ensemble** 📊
   - Header avec scores (crédibilité, réputation, influence, fiabilité)
   - Badge niveau de risque (Faible/Moyen/Élevé)
   - Résumé exécutif + recommandations
   - Red flags avec badges de sévérité

2. **Expérience** 💼
   - Parcours professionnel détaillé
   - Timeline visuelle chronologique
   - Formations et certifications

3. **Financier** 💰
   - Intelligence financière avec sources
   - Écosystème d'affaires (entreprises dirigées, mandats)
   - Patrimoine immobilier (DVF)
   - PPE détecté (HATVP)

4. **Médias & Réputation** 📰
   - Présence médiatique avec sentiment (Positif/Neutre/Négatif)
   - Publications et articles
   - Influence réseau professionnel

5. **Réseau & Influence** 🤝
   - Réseau professionnel
   - Indicateurs d'influence
   - Connexions clés

6. **Analyse** 🔍
   - Psychologie et approche (traits justifiés)
   - Ice breakers concrets
   - Analyse de cohérence
   - Données brutes (collapsible)

## 🚢 Déploiement

### Docker (Recommandé)

Le Dockerfile inclus utilise un **build multi-stage** avec Nginx :

```bash
# Build avec URL d'API custom
docker build --build-arg VITE_API_URL=https://your-api.com/api/v1 -t lumironscraper-frontend .

# Run
docker run -p 5101:80 lumironscraper-frontend
```

**Important :** Les variables d'environnement Vite (`VITE_*`) doivent être passées au **moment du build**, pas au runtime, car Vite les remplace lors de la compilation.

### Docker Compose

Le `docker-compose.yml` à la racine du projet gère automatiquement le build :

```yaml
frontend:
  build:
    context: ./frontend
    args:
      - VITE_API_URL=${VITE_API_URL:-http://localhost:5100/api/v1}
  env_file:
    - ./frontend/.env
```

Le fichier `./frontend/.env` est automatiquement lu et `VITE_API_URL` est passé comme build argument.

**Usage :**

```bash
# Configuration
cp .env.example .env
nano .env  # Éditer VITE_API_URL

# Build et lancer
docker-compose up -d --build frontend
```

### Netlify

```bash
# Build command
npm run build

# Publish directory
dist

# Environment variables
VITE_API_URL=https://your-api.com/api/v1
```

### Vercel

```bash
vercel --prod
```

Ajouter la variable d'environnement `VITE_API_URL` dans les settings du projet Vercel.

## 🛠️ Développement

### Structure des composants

```jsx
// Composant fonctionnel avec hooks
import { useState } from 'react';

const MyComponent = () => {
  const [state, setState] = useState(null);

  return (
    <div className="...">
      {/* JSX */}
    </div>
  );
};

export default MyComponent;
```

### Tailwind CSS

Classes utilitaires utilisées :
- `bg-primary-600` - Couleur principale
- `rounded-lg` - Bordures arrondies
- `shadow-md` - Ombre
- `hover:...` - États hover
- `disabled:...` - États désactivés

Configuration personnalisée dans `tailwind.config.js`.

### Hot Reload

Vite détecte automatiquement les changements et recharge la page.

## 📱 Responsive Design

### Layout adaptatif

- **Mobile (< 1024px)** : Layout vertical empilé (formulaire → résultats)
- **Desktop (≥ 1024px)** : Layout horizontal côte à côte (formulaire gauche, résultats droite)
- **Layout dynamique** : Le formulaire est centré par défaut, puis se déplace à gauche quand les résultats apparaissent

### Breakpoints Tailwind

- `sm:` - 640px et +
- `md:` - 768px et +
- `lg:` - 1024px et + (activation du layout côte à côte)
- `xl:` - 1280px et +

Exemple :
```jsx
<div className={`w-full transition-all duration-300 ${
  profile || loading ? 'lg:w-1/2 lg:sticky lg:top-8' : 'lg:w-full'
}`}>
  {/* Largeur dynamique selon l'état */}
</div>
```

### Animations CSS custom

```css
/* Slide-in depuis la droite (résultats) */
@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Fade-in simple (erreurs, instructions) */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

## 📚 Stack Technique

- **React 18** - Library UI
- **Vite** - Build tool rapide
- **Tailwind CSS** - Utility-first CSS
- **Axios** - Client HTTP
- **ESLint** - Linting
