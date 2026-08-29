# Environment setup — MonGoats (Windows + Mac)

Follow this once, in order. It's written so two people who've never touched this repo can get `python manage.py runserver` showing a working page inside about 10 minutes.

## 0. Prerequisites (both platforms)

- **Python 3.11 or 3.12.** Match this exactly across the team — a version mismatch is the single most common source of "works on my machine." Check with:
  - Mac: `python3 --version`
  - Windows: `python --version`
  If you're on something older/newer, install 3.11 from [python.org](https://www.python.org/downloads/) before continuing.
- **Git**, already installed if you can run `git --version`.
- A GitHub account with access to `github.com/signetb10/MonGoats` (ask whoever has admin to add you as a collaborator if you can't push).

## 1. Clone the repo

Same command on both platforms:

```bash
git clone https://github.com/signetb10/MonGoats.git
cd MonGoats
```

## 2. Create and activate a virtual environment

**Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```
If PowerShell refuses to run the activation script with a "running scripts is disabled" error, run this once first:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

You'll know it worked because your prompt now starts with `(venv)`. Do this every time you open a new terminal for this project.

## 3. Install dependencies

Same command both platforms, inside the activated venv:

```bash
pip install -r requirements.txt
```

If `psycopg[binary]` fails to install on Windows (rare, but happens on some setups), it means it's trying to compile from source instead of using a prebuilt wheel — make sure you're on Python 3.11/3.12 (step 0), not something unusual, and retry.

## 4. Set up your `.env`

```bash
cp .env.example .env        # Mac
copy .env.example .env      # Windows
```

Then fill in the values. **Never commit `.env` — it's already in `.gitignore`, leave it that way.**

- `DJANGO_SECRET_KEY` — any random string for local dev, doesn't need to be secure yet.
- `DATABASE_URL` — **get this from the team chat**, not from this file. One person creates the shared Supabase project (Postgres + pgvector), and everyone points at the *same* database for local dev. This is deliberate: nobody needs to install Postgres locally, which is the part that usually goes sideways on Windows. If you skip this, `runserver` still works against a local SQLite fallback — fine for poking around, but you won't see anyone else's data and pgvector search won't work.
- `CHIMEGE_API_KEY`, `ELEVENLABS_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY` — leave blank until you're actually implementing the piece that needs them. Get real keys from whoever owns each account; share them via the team chat or a password manager, never via a commit.

## 5. First run

```bash
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/admin/` — if you see the Django admin login page, your environment is correctly set up. (You'll need `python manage.py createsuperuser` once to actually log in, but seeing the login page is enough to confirm the environment works.)

If this fails, the error message will point at exactly one of: wrong Python version, venv not activated, `.env` missing/malformed, or `DATABASE_URL` unreachable — in that order of likelihood.

## 6. Git workflow for the next ~20 hours

Keep this lightweight — a full PR-review process costs more time than it saves at this scale.

- **Branch per feature**, not per person: `feature/pipeline`, `feature/search`, `feature/ui`, matching however you split the build order in `TECHNICAL_PLAN.md`.
- **Commit and push often** — every 30-60 minutes, even mid-feature. A half-working commit you can roll back to beats losing an hour of work to a bad merge.
- **Merge to `main` directly** when a feature branch works locally (`git checkout main && git pull && git merge feature/xyz && git push`). Don't wait for review; just don't merge something you haven't run.
- **Pull before you start work each session**: `git pull origin main`, so you're not diffing against a stale base.
- If you get a merge conflict in `.py` files, resolve it by reading both sides — don't blindly take "theirs" or "ours." If it's in a migration file, the safer fix is usually to delete your local migration and regenerate it after pulling (`python manage.py makemigrations`), rather than hand-merging migration internals.

## 7. Troubleshooting quick reference

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'django'` | venv not activated | Re-run step 2's activate command |
| PowerShell won't activate venv | execution policy | The `Set-ExecutionPolicy` line in step 2 |
| `runserver` works but admin page 500s | `DATABASE_URL` unreachable or malformed | Re-check the value from team chat, confirm no stray quotes/spaces |
| CRLF/LF noise in every diff | Windows vs Mac line endings | Already handled by `.gitattributes` in this repo — if it's still happening, run `git add --renormalize .` once |
| `pip install` hangs or fails on one package | Python version mismatch | Confirm step 0's version match |
