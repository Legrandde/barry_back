# barry_back — API du mini CMS du portfolio d'Alhassane Barry

API FastAPI inspirée de `cherfiBack`, permettant de modifier tout le contenu du portfolio (`../Barry`) — textes, images, projets, compétences, parcours, formations, témoignages, visibilité des sections, médias, messages de contact et statistiques de visite — **sans toucher au code ni redéployer** le front.

## Démarrage

```bash
cp .env.example .env        # puis définir SECRET_KEY et ADMIN_PASSWORD
uv sync
uv run uvicorn main:app --reload
```

- Documentation interactive (Swagger) : http://localhost:8000/docs
- Au premier démarrage, la base SQLite (`cms.db`) est créée et remplie avec tout le contenu actuel du portfolio d'Alhassane Barry, et le compte admin est créé à partir de `ADMIN_USERNAME` / `ADMIN_PASSWORD`.
- Créer ou réinitialiser un compte admin en CLI : `uv run python -m db.create_admin`
- Tests : `uv run pytest`

## Architecture

```
main.py      application, CORS, gestion des erreurs, montage de /media
core/        configuration (.env), sécurité (hash scrypt, JWT), dépendances (admin connecté)
db/          moteur SQLAlchemy, initialisation et contenu initial (seed_data.py)
models/      tables SQLAlchemy
schemas/     schémas Pydantic (JSON en camelCase, comme les types TypeScript du front)
services/    logique métier (sections, collections, médias + compression vidéo, contact, analytics)
routers/     endpoints HTTP
tests/       tests pytest
```

Le contenu est découpé en deux familles :

| Type | Contenu | Stockage |
|---|---|---|
| **Sections** (blocs uniques) | `site`, `theme`, `hero`, `about`, `services`, `skills`, `stats`, `parcours`, `formation`, `process`, `projects`, `testimonials`, `contact`, `cta` | table `sections`, JSON validé par un schéma par section + drapeau `isVisible` |
| **Collections** (listes ordonnées) | projets, services, catégories de compétences, parcours, formations, témoignages, réseaux sociaux | une table par liste, avec `position` et `isPublished` |

## Endpoints

### Santé & Public (utilisés par le portfolio)

| Méthode | Route | Description |
|---|---|---|
| GET | `/api/health` | Vérification de l'état de l'API |
| GET | `/api/public/content` | **Tout le contenu publié du portfolio en un seul appel** |
| GET | `/api/public/sections/{key}` | Une section visible |
| GET | `/api/public/projects/{slug}` | Un projet publié par son slug |
| POST | `/api/public/contact` | Envoyer un message depuis le formulaire de contact (avec anti-spam honeypot) |
| POST | `/api/public/track` | Enregistrer une visite (`pageview`) ou une action sans cookies |

### Admin (header `Authorization: Bearer <token>`)

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/auth/login` | Connexion (`username` / `password`) → `access_token` |
| GET | `/api/auth/me` | Admin connecté |
| PUT | `/api/auth/password` | `{ currentPassword, newPassword }` |
| PUT | `/api/auth/username` | `{ currentPassword, newUsername }` → nouveau token |
| GET | `/api/admin/sections` | Toutes les sections |
| GET / PUT / PATCH | `/api/admin/sections/{key}` | Lire, remplacer, ou modifier certains champs d'une section |
| GET / PUT | `/api/admin/sections/{key}/visibility` | Lire / basculer la visibilité d'une section (sauf `site` et `theme`) |
| GET / POST | `/api/admin/{collection}` | Lister (y compris brouillons) / créer |
| GET / PATCH / DELETE | `/api/admin/{collection}/{id}` | Lire / modifier / supprimer |
| PUT | `/api/admin/{collection}/reorder` | `{ ids: [...] }` dans le nouvel ordre |
| GET / POST / DELETE | `/api/admin/media` / `/{id}` | Lister / téléverser (`multipart`, champ `file`) / supprimer |
| GET / PATCH / DELETE | `/api/admin/messages` / `/{id}` | Lister les messages, marquer lu/non lu, supprimer |
| GET | `/api/admin/messages/unread-count` | Compteur de messages non lus |
| GET | `/api/admin/analytics/summary?days=30` | Tableau de bord statistiques (sans cookies ni IP stockée) |

`{collection}` : `projects`, `services`, `skill-categories`, `experiences`, `educations`, `testimonials`, `social-links`.

## Médias & Compression vidéo

- Images acceptées : JPEG, PNG, WebP, GIF, AVIF (20 Mo max), vérifiées par signature binaire (magic bytes).
- Vidéos acceptées : MP4, WebM (300 Mo max), compressées automatiquement en arrière-plan via ffmpeg (`imageio-ffmpeg`) au-delà de `VIDEO_COMPRESSION_THRESHOLD_MB` (15 Mo par défaut).
"# barry_back" 
