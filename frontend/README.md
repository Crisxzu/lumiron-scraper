# LumironScraper Frontend

Interface React pour LumironScraper - Scraping et analyse intelligente de profils professionnels.

## 🎯 Fonctionnalités

- **Recherche intuitive** - Formulaire simple (prénom, nom, entreprise)
- **Force refresh** - Option pour ignorer le cache
- **Indicateur cache** - Affiche si les données viennent du cache ou sont fraîches
- **Affichage structuré** - Profil professionnel formaté et lisible
- **Responsive** - Design adaptatif mobile/desktop
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
│   ├── App.jsx              # Composant principal
│   ├── main.jsx             # Point d'entrée
│   ├── index.css            # Styles globaux + Tailwind
│   ├── components/
│   │   ├── SearchForm.jsx   # Formulaire de recherche
│   │   └── ProfileResults.jsx  # Affichage du profil
│   └── services/
│       └── api.js           # Client API Axios
├── public/                  # Assets statiques
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

Configuration automatique via `vite.config.js`.

### Docker

```bash
# Build
docker build -t lumironscraper-frontend .

# Run
docker run -p 80:80 lumironscraper-frontend
```

**Dockerfile exemple:**
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

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

Breakpoints Tailwind :
- `sm:` - 640px et +
- `md:` - 768px et +
- `lg:` - 1024px et +
- `xl:` - 1280px et +

Exemple :
```jsx
<div className="text-4xl md:text-5xl">
  {/* 4xl sur mobile, 5xl sur tablette+ */}
</div>
```

## 📚 Stack Technique

- **React 18** - Library UI
- **Vite** - Build tool rapide
- **Tailwind CSS** - Utility-first CSS
- **Axios** - Client HTTP
- **ESLint** - Linting
