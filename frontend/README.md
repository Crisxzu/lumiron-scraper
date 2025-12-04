# LumironScraper Frontend

Interface React pour LumironScraper - Scraping et analyse intelligente de profils professionnels.

## 🎯 Fonctionnalités

- **Layout dynamique** - Formulaire centré par défaut, se déplace à gauche quand résultats affichés
- **Animations fluides** - Slide-in depuis la droite pour les résultats
- **Recherche intuitive** - Formulaire simple (prénom, nom, entreprise)
- **Force refresh** - Checkbox pour ignorer le cache
- **Indicateur cache** - Badge vert (cache) ou bleu (frais) avec âge en minutes
- **Affichage structuré** - Profil professionnel formaté et lisible
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
│   ├── App.jsx              # Composant principal + layout dynamique
│   ├── main.jsx             # Point d'entrée
│   ├── index.css            # Styles globaux + animations custom
│   ├── components/
│   │   ├── SearchForm.jsx   # Formulaire + force refresh
│   │   └── ProfileResults.jsx  # Affichage du profil
│   └── services/
│       └── api.js           # Client API Axios
├── public/                  # Assets statiques
├── nginx.conf               # Config Nginx pour Docker
├── Dockerfile               # Build multi-stage
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## 🔌 Intégration Backend

### API Endpoint utilisé

```javascript
POST /api/v1/search
Content-Type: application/json

{
  "first_name": "Satya",
  "last_name": "Nadella",
  "company": "Microsoft",
  "force_refresh": false // Optionnel
}
```

### Réponse attendue

```json
{
  "success": true,
  "cached": true,                    // ← Indicateur cache
  "cache_age_seconds": 3600,         // ← Âge du cache
  "cache_created_at": "2025-12-04T10:00:00",
  "data": {
    "full_name": "Satya Nadella",
    "current_position": "Directeur Général",
    "company": "Microsoft",
    "professional_experience": [...],
    "skills": [...],
    "publications": [...],
    "public_contact": {...},
    "summary": "...",
    "linkedin_url": "...",
    "sources": [...]
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

### ProfileResults

Affichage du profil avec sections :
- **En-tête** - Nom + poste actuel
- **Résumé** - Bio courte
- **Expérience** - Parcours professionnel
- **Compétences** - Tags
- **Publications** - Liste
- **Contact** - Email, téléphone, LinkedIn
- **Sources** - URLs utilisées (collapsible)

### Indicateur Cache

Badge affiché au-dessus du profil :
- **Vert** - Données du cache (avec âge en minutes)
- **Bleu** - Données fraîches (nouvellement scrapées)

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
