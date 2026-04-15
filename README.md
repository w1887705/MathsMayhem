# Maths Mayhem

## Run locally

```bash
cd mathsmayhem_merged   # or whatever the folder is called
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo     # creates tasks, shop items, demo user
python manage.py runserver
```

Visit http://127.0.0.1:8000

**Demo login:** `demochild` / `demo12345`

Anyone can register their own account at `/register/` — accounts are saved to the database automatically.

---

## How the database works

Django uses **SQLite** locally (a single file `db.sqlite3` in the project folder).
Every user that registers gets a row in the `auth_user` table.
When they play a task their score/stars are stored in the `core_progress` table linked to their user.
When they buy a shop item it's stored in `core_usershopitem`.

Each table = one Django Model (see `core/models.py`):
- `Task` — the 3 tasks (ribbon, cookie, pizza)
- `Progress` — per-user per-task progress (stars, completed, score)
- `UserProfile` — total star balance for each user
- `ShopItem` — items in the shop
- `UserShopItem` — which items each user has bought


---

## Admin Panel (database browser)

The Django admin panel lets you view and edit everything in the database from a clean web UI.

### Set it up (run once):
```bash
python manage.py createsuperuser
```
Enter a username, email (can be blank), and password when prompted.

### Access it:
Run the server then go to: **http://127.0.0.1:8000/admin**

### What you can do:
| Section | What you can see / edit |
|---|---|
| **Users** | All accounts, reset passwords |
| **User profiles** | Role (student/teacher), stars, classroom |
| **Classrooms** | Teacher classes and join codes |
| **Progress** | Every student's stars per task/difficulty |
| **Shop items** | Enable/disable packs, change prices |
| **User shop items** | Which packs each student owns |
| **Tasks** | Enable/disable tasks |

---

## Deploy to Render (free hosting)

1. Push this folder to a GitHub repo
2. Go to https://render.com → **New → Blueprint**
3. Connect your GitHub repo — Render will read `render.yaml` automatically
4. Click **Apply** — Render creates the web service + PostgreSQL database
5. Wait ~3 minutes for the first deploy to finish
6. Your site will be live at `https://mathsmayhem.onrender.com` (or similar)

Render runs `build.sh` automatically which:
- Installs packages
- Runs database migrations
- Seeds the demo user + shop items
- Collects static files

### Environment variables (set automatically by render.yaml)
| Variable | Value |
|---|---|
| `SECRET_KEY` | Auto-generated secure key |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `DATABASE_URL` | PostgreSQL connection (from Render DB) |

---

## Logout

Logout uses a POST form (required by Django's security model).
The "Log out" button in the top nav submits a form — this is correct and intentional.

---

## Shop themes

After buying a pack in the shop, the theme activates the next time you open that task:
- **Ribbon Colour Packs** — changes the ribbon and bow colour (red, blue, rainbow, glitter)
- **Cookie Character Packs** — replaces Mouse/Wolf/Human/Lion with Jungle/Ocean/Space animals
- **Pizza Theme Packs** — changes the pizza slice colours (Christmas red+green, Easter purple+yellow)
