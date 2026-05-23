# 📸 Lumina — Photo Album Management System

A production-ready Django photo album application with cloud storage, role-based access control, and PostgreSQL — deployed on Render.

---

## Live Demo

**Render URL:** `https://lumina-photo-albums.onrender.com`  
*(Replace with your actual Render URL after deployment)*

---

## Features

- **Class-Based Views** for all CRUD operations (Album + Photo)
- **Role-Based Access Control** — owners, collaborators, guests, staff
- **Cloudinary** cloud media storage (no local disk in production)
- **PostgreSQL** via Render managed databases
- **Whitenoise** for static file serving
- Public / Private / Shared album visibility modes
- Multi-photo upload with titles and captions
- Collaborator system for shared albums
- Responsive editorial design

---

## RBAC Permissions

| Action | Guest | Authenticated | Collaborator | Owner | Staff |
|--------|-------|---------------|--------------|-------|-------|
| View public albums | ✅ | ✅ | ✅ | ✅ | ✅ |
| View private albums | ❌ | ❌ | ✅ | ✅ | ✅ |
| Create albums | ❌ | ✅ | ✅ | ✅ | ✅ |
| Upload photos | ❌ | ❌ | ✅ | ✅ | ✅ |
| Edit album | ❌ | ❌ | ❌ | ✅ | ✅ |
| Delete album/photo | ❌ | ❌ | ❌ | ✅ | ✅ |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 4.2 |
| Database | PostgreSQL (Render) / SQLite (dev) |
| Media Storage | Cloudinary |
| Static Files | WhiteNoise |
| Server | Gunicorn |
| Hosting | Render |
| Config | python-decouple |

---

## Project Structure

```
photoalbum/
├── config/               # Django project config
│   ├── settings.py       # Environment-driven settings
│   ├── urls.py           # Root URL routing
│   └── wsgi.py
├── albums/               # Core app
│   ├── models.py         # Album, Photo models
│   ├── views.py          # All CBVs
│   ├── forms.py          # AlbumForm, PhotoForm, PhotoUploadForm
│   ├── urls.py           # Album/Photo URL patterns
│   └── admin.py          # Admin config with inlines
├── accounts/             # Auth app
│   ├── views.py          # Register, Login, Profile CBVs
│   ├── forms.py          # RegisterForm, ProfileForm
│   └── urls.py
├── templates/            # HTML templates
│   ├── base.html
│   ├── albums/
│   └── accounts/
├── static/               # CSS, JS, images
├── requirements.txt
├── Procfile              # Render/Heroku process file
├── render.yaml           # Render IaC config
└── .env.example          # Environment variable template
```

---

## Local Development Setup

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/lumina-photo-albums.git
cd lumina-photo-albums
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your values
```

**`.env` for local development:**
```env
SECRET_KEY=your-long-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

# Optional for local (images stored locally if blank)
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

### 3. Run

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://localhost:8000`

---

## Cloudinary Setup

1. Create a free account at [cloudinary.com](https://cloudinary.com)
2. Go to **Dashboard** → copy your Cloud Name, API Key, API Secret
3. Add to your `.env` (local) or Render environment variables (production)

---

## Deployment on Render

### Option A: render.yaml (Infrastructure as Code)

The `render.yaml` file provisions everything automatically:

```bash
# Push to GitHub, then in Render dashboard:
# New → Blueprint → connect your repo → render.yaml is auto-detected
```

### Option B: Manual Setup

1. **Create Web Service** on [render.com](https://render.com)
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput`
   - Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

2. **Create PostgreSQL Database** on Render → copy the Internal Database URL

3. **Set Environment Variables** in Render dashboard:
   ```
   SECRET_KEY         = <generate with: python -c "import secrets; print(secrets.token_urlsafe(50))">
   DEBUG              = False
   ALLOWED_HOSTS      = your-app.onrender.com
   DATABASE_URL       = <from Render PostgreSQL>
   CLOUDINARY_CLOUD_NAME = <your cloud name>
   CLOUDINARY_API_KEY    = <your api key>
   CLOUDINARY_API_SECRET = <your api secret>
   ```

4. **Deploy** — Render will build and run automatically.

### First Deploy: Create Superuser

In Render dashboard → your web service → **Shell**:
```bash
python manage.py createsuperuser
```

---

## Class-Based Views Reference

| View | CBV Base | URL | Permission |
|------|----------|-----|------------|
| `AlbumListView` | `ListView` | `/` | Public |
| `AlbumDetailView` | `DetailView` | `/album/<pk>/` | Owner/Public |
| `AlbumCreateView` | `CreateView` | `/album/create/` | Authenticated |
| `AlbumUpdateView` | `UpdateView` | `/album/<pk>/edit/` | Owner/Staff |
| `AlbumDeleteView` | `DeleteView` | `/album/<pk>/delete/` | Owner/Staff |
| `PhotoUploadView` | `View` | `/album/<pk>/upload/` | Owner/Collaborator |
| `PhotoDetailView` | `DetailView` | `/photo/<pk>/` | Can-view album |
| `PhotoUpdateView` | `UpdateView` | `/photo/<pk>/edit/` | Owner/Staff |
| `PhotoDeleteView` | `DeleteView` | `/photo/<pk>/delete/` | Owner/Staff |
| `MyAlbumsView` | `ListView` | `/my-albums/` | Authenticated |
| `RegisterView` | `CreateView` | `/accounts/register/` | Public |
| `ProfileView` | `UpdateView` | `/accounts/profile/` | Authenticated |

---

## Admin Panel

Django admin at `/admin/` provides:
- Album management with inline photo editing
- User management with collaborator assignment
- Photo bulk operations

---

## Requirements

```
Django>=4.2,<5.0
psycopg2-binary>=2.9
cloudinary>=1.36
django-cloudinary-storage>=0.3
Pillow>=10.0
gunicorn>=21.0
whitenoise>=6.5
dj-database-url>=2.0
python-decouple>=3.8
```

---

## License

MIT — free to use and modify.
