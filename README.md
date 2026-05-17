# Still, Always.

A small, quiet Streamlit app, a finished promise, made with care.

> "A small corner of the internet I once promised you, made with care, memories, and a little bit of hope."

This is a polished, deploy-ready Streamlit project. It runs out of the box with sensible defaults and degrades gracefully when optional things (photos, secrets) aren't configured.

---

## What's inside

- **Hero section** with cinematic gradient + glass card
- **Photo gallery** that reads from `assets/photos/` and/or a `PHOTO_URLS` list
- **Sticky "Current thought" ticker** at the bottom, backed by `thoughts.json`
- **Timeline / "The promise"** cards
- **Interactive bits**: shuffleable quote, vibe link, expandable tiny letter
- **Connect / ping section** with mailto + optional Discord webhook
- **Admin sidebar** (password-protected) for updating the ticker thought

---

## Run it locally

```bash
mkdir still-always
cd still-always
# (or just clone this repo into ./still-always)

python -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually <http://localhost:8501>).

---

## Add your photos

1. Drop image files into `assets/photos/`.
2. Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`.
3. Filenames become soft captions (`a_quiet_evening.jpg` → "A quiet evening").
4. Images are sorted alphabetically - prefix with `01_`, `02_`, … for a custom order.

You can also paste direct image URLs into the `PHOTO_URLS` list near the top of `app.py`. Local photos and URL photos render in the same grid.

> **About Google Photos album links:** Google Photos album URLs do not reliably expose direct image URLs, and any scraping approach tends to break the moment Google adjusts their HTML. Don't fight it.
>
> The easiest free options are, in order:
> 1. **Upload the photos to `assets/photos/` and commit them** with the repo. This is the most reliable path.
> 2. **Use direct image URLs**, e.g. GitHub raw file URLs (`https://raw.githubusercontent.com/you/repo/main/img.jpg`).
> 3. **A public Dropbox/Drive direct link** *only* if it actually resolves to a real image file (some Drive links require extra `uc?export=view&id=...` tweaking and may still fail).

---

## Update the thought ticker

Two ways:

1. **Edit `thoughts.json` directly:**
   ```json
   {
     "latest_thought": "I hope today was gentle with you.",
     "updated_at": "2026-05-17"
   }
   ```
2. **Use the sidebar admin pane.** Open the sidebar (top-left chevron), enter the admin password, edit the thought, and hit *Save*.

---

## Configure secrets (optional)

Both secrets are optional. The app runs fine without either.

On **Streamlit Community Cloud**, open your app → *Settings* → *Secrets* and paste:

```toml
ADMIN_PASSWORD = "your-password"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/…"
```

For **local development**, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill it in. That file is gitignored.

If `ADMIN_PASSWORD` is not set, the app falls back to the `LOCAL_FALLBACK_ADMIN_PASSWORD` constant in `app.py` - **change that constant or set a real secret before deploying publicly.**

If `DISCORD_WEBHOOK_URL` is not set, the "Send a ping" button quietly degrades to a `mailto:` link. No webhook URL is ever shown in the UI.

---

## Update social / personal links

Open `app.py` and edit the constants near the top:

```python
MY_EMAIL_HERE          = "you@example.com"
INSTAGRAM_URL          = "https://instagram.com/your_handle"
DISCORD_INVITE_URL     = "https://discord.gg/your_invite"
WHATSAPP_URL           = "https://wa.me/0000000000"
SPOTIFY_OR_YOUTUBE_URL = "https://open.spotify.com/playlist/..."
PHOTO_URLS             = [ ... ]
```

All placeholders are intentionally easy to grep for.

---

## Deploy to Streamlit Community Cloud

1. **Create a GitHub repo** and push this project to it.
2. **Add your photos** to `assets/photos/` and commit them.
3. Go to <https://share.streamlit.io> and sign in with GitHub.
4. Click **New app**, pick this repo and branch.
5. Set **Main file path** to `app.py`.
6. (Optional) Under **Advanced settings → Secrets**, paste your `ADMIN_PASSWORD` and `DISCORD_WEBHOOK_URL`.
7. Click **Deploy**.

That's it. The app will install `requirements.txt` and boot.

---

## Privacy

- No analytics, no visitor tracking, no data collection.
- Ping notifications only fire when a visitor explicitly clicks the button.
- The Discord webhook URL is never exposed in the rendered HTML.
- `thoughts.json` is the only thing the app ever writes to disk, and only when you update it via the admin pane.

---

## File map

```
.
├── app.py                      # The Streamlit app
├── requirements.txt            # streamlit, requests, Pillow
├── thoughts.json               # Latest "current thought" + timestamp
├── README.md                   # This file
├── .gitignore
├── .streamlit/
│   ├── config.toml             # Theme matching the custom CSS
│   └── secrets.toml.example    # Template for ADMIN_PASSWORD / webhook
└── assets/
    └── photos/                 # Drop your images here
```

Made quietly, carefully, and with care.
