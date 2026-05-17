"""
Still, Always.
A small, quiet Streamlit app, a finished promise, made with care.

Run locally:
    streamlit run app.py

Deploy on Streamlit Community Cloud:
    1. Push this repo to GitHub.
    2. Create a new app at https://share.streamlit.io pointing at app.py.
    3. (Optional) Add secrets: ADMIN_PASSWORD, DISCORD_WEBHOOK_URL.
"""

from __future__ import annotations

import json
import random
from datetime import date
from pathlib import Path
from typing import List

import streamlit as st


# ---------------------------------------------------------------------------
# Configuration - edit these placeholders before deploying.
# ---------------------------------------------------------------------------

# Personal links. Replace the placeholder strings with your real ones.
MY_EMAIL_HERE = "madhavmukherjee1@gmail.com"
INSTAGRAM_URL = "https://www.instagram.com/breadbastket?igsh=c2sya3kycjcwZWZk"
DISCORD_INVITE_URL = "https://discord.gg/tZPh377qeP"
WHATSAPP_URL = "https://wa.me/61416232736"
SPOTIFY_OR_YOUTUBE_URL = "https://music.youtube.com/playlist?list=PL6H4rqMvHT-H8h6ORnTMFQJqXM4Z1pz6h&si=yt35oKTsnGLTdNIE"

# Optional direct image URLs. These render alongside any local photos found
# in assets/photos. Use direct image links (ending in .jpg/.png/.webp), e.g.
# GitHub raw URLs, public Dropbox direct links, etc.
# Google Photos album URLs are NOT reliable here - see README.md.
PHOTO_URLS: List[str] = [
    # "https://raw.githubusercontent.com/you/repo/main/example.jpg",
]

# Fallback admin password used ONLY when no Streamlit secret is configured.
# This exists so local testing works; configure ADMIN_PASSWORD in secrets
# before deploying anywhere public.
LOCAL_FALLBACK_ADMIN_PASSWORD = "Koibito"

# Paths
ROOT = Path(__file__).parent
PHOTO_DIR = ROOT / "assets" / "photos"
THOUGHTS_FILE = ROOT / "thoughts.json"

# Quotes written for this app - not famous copyrighted lines.
MEMORY_QUOTES = [
    "Some promises don't expire; they just wait quietly until they can be kept.",
    "I never wanted you to need this, only to know it existed if you ever wished it did.",
    "Care isn't loud. It is mostly the small things, done anyway.",
    "If memory is a kind of architecture, then this is one of its softer rooms.",
    "Not every story needs a reply. Some only need to be finished.",
    "I built this the way I would build a paper boat, gently, and to be let go.",
    "Time moved on. The intention didn't.",
    "There is a kind of love that asks nothing back. This is closer to that.",
]


# ---------------------------------------------------------------------------
# Page setup + global CSS
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Still, Always.",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    """Inject the custom CSS that gives the app its cinematic feel."""
    st.markdown(
        """
        <style>
        /* ---------- Typography ---------- */
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #f6efe9;
        }

        /* ---------- Global background (warm candlelit palette) ---------- */
        .stApp {
            background:
                radial-gradient(1200px 600px at 10% -10%, rgba(255, 178, 140, 0.24), transparent 60%),
                radial-gradient(900px 500px at 110% 10%, rgba(255, 196, 160, 0.20), transparent 55%),
                radial-gradient(800px 600px at 50% 120%, rgba(255, 168, 184, 0.18), transparent 60%),
                linear-gradient(180deg, #1a1014 0%, #2a1620 50%, #160c10 100%);
            background-attachment: fixed;
        }

        /* Remove default Streamlit chrome (but keep the sidebar toggle visible) */
        #MainMenu { visibility: hidden; }
        header [data-testid="stToolbar"] { visibility: hidden; }
        header [data-testid="stDecoration"] { visibility: hidden; }
        header { background: transparent; }
        footer { visibility: hidden; }
        .block-container {
            padding-top: 2.5rem;
            padding-bottom: 8rem;
            max-width: 1200px;
        }

        /* ---------- Floating hearts ---------- */
        .float-layer {
            position: fixed;
            inset: 0;
            pointer-events: none;
            overflow: hidden;
            z-index: 0;
        }
        .float-layer span {
            position: absolute;
            bottom: -40px;
            font-size: 14px;
            color: rgba(255, 210, 180, 0.40);
            animation: drift linear infinite;
        }
        @keyframes drift {
            0%   { transform: translateY(0) translateX(0) rotate(0deg); opacity: 0; }
            10%  { opacity: 0.7; }
            100% { transform: translateY(-110vh) translateX(20px) rotate(20deg); opacity: 0; }
        }

        /* ---------- Hero ---------- */
        .hero {
            position: relative;
            padding: 5rem 2.5rem 4rem 2.5rem;
            border-radius: 28px;
            background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 30px 60px -30px rgba(0,0,0,0.5);
            overflow: hidden;
            text-align: center;
        }
        .hero::before {
            content: "";
            position: absolute;
            inset: -40%;
            background: conic-gradient(from 90deg at 50% 50%,
                rgba(255,178,140,0.22), rgba(255,210,170,0.20),
                rgba(255,168,184,0.22), rgba(255,178,140,0.22));
            filter: blur(60px);
            opacity: 0.45;
            animation: spin 25s linear infinite;
            z-index: 0;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .hero > * { position: relative; z-index: 1; }

        .hero h1 {
            font-family: 'Cormorant Garamond', serif;
            font-weight: 600;
            font-size: clamp(3rem, 7vw, 5.5rem);
            letter-spacing: -0.02em;
            margin: 0 0 0.5rem 0;
            line-height: 1.05;
            background: linear-gradient(180deg, #fff7ec 0%, #ffd0b8 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .hero .sub {
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            font-size: clamp(1.05rem, 2vw, 1.4rem);
            color: rgba(246, 239, 233, 0.85);
            max-width: 720px;
            margin: 0 auto 1.5rem auto;
        }
        .hero .body {
            color: rgba(246, 239, 233, 0.72);
            max-width: 620px;
            margin: 0 auto 2rem auto;
            line-height: 1.7;
            font-size: 0.98rem;
        }
        .pill {
            display: inline-block;
            padding: 0.75rem 1.6rem;
            border-radius: 999px;
            background: linear-gradient(135deg, #ffb380, #f08aa8);
            color: #2a1612 !important;
            font-weight: 600;
            text-decoration: none !important;
            box-shadow: 0 10px 30px -10px rgba(240,138,168,0.55);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            border: 0;
        }
        .pill:hover {
            transform: translateY(-2px);
            box-shadow: 0 16px 36px -12px rgba(240,138,168,0.72);
        }
        .pill.ghost {
            background: rgba(255,255,255,0.08);
            color: #f6efe9 !important;
            border: 1px solid rgba(255,255,255,0.18);
            box-shadow: none;
        }
        .arrow-down {
            margin-top: 1.4rem;
            font-size: 1.4rem;
            opacity: 0.7;
            animation: bob 2.4s ease-in-out infinite;
            display: inline-block;
        }
        @keyframes bob {
            0%,100% { transform: translateY(0); }
            50%     { transform: translateY(6px); }
        }

        /* ---------- Section heading ---------- */
        .section-title {
            font-family: 'Cormorant Garamond', serif;
            font-weight: 600;
            font-size: clamp(1.75rem, 3.4vw, 2.6rem);
            letter-spacing: -0.01em;
            margin: 3.5rem 0 0.4rem 0;
            color: #fff5ec;
        }
        .section-sub {
            color: rgba(246, 239, 233, 0.65);
            margin-bottom: 1.6rem;
            font-size: 0.98rem;
        }

        /* ---------- Glass card ---------- */
        .glass {
            background: linear-gradient(135deg, rgba(255,255,255,0.07), rgba(255,255,255,0.02));
            border: 1px solid rgba(255,255,255,0.10);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border-radius: 22px;
            padding: 1.4rem 1.5rem;
            box-shadow: 0 20px 40px -30px rgba(0,0,0,0.5);
        }

        /* ---------- Photo gallery ---------- */
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 1.1rem;
        }
        .photo-card {
            position: relative;
            border-radius: 18px;
            overflow: hidden;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            transition: transform 0.35s ease, box-shadow 0.35s ease;
            aspect-ratio: 4 / 5;
        }
        .photo-card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.6s ease;
        }
        .photo-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 24px 50px -20px rgba(0,0,0,0.55);
        }
        .photo-card:hover img { transform: scale(1.05); }
        .photo-caption {
            position: absolute;
            left: 0; right: 0; bottom: 0;
            padding: 0.7rem 0.9rem;
            background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.55) 100%);
            color: #fdf6ef;
            font-size: 0.85rem;
            letter-spacing: 0.02em;
        }
        .placeholder-card {
            aspect-ratio: 4 / 5;
            border-radius: 18px;
            border: 1px dashed rgba(255,255,255,0.18);
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: rgba(246, 239, 233, 0.55);
            font-size: 0.85rem;
            padding: 1rem;
            background: rgba(255,255,255,0.02);
        }
        .metric-chip {
            display: inline-block;
            padding: 0.35rem 0.9rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            font-size: 0.82rem;
            color: rgba(246, 239, 233, 0.85);
            margin-left: 0.5rem;
        }

        /* ---------- Timeline ---------- */
        .timeline {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
        }
        .promise-card {
            padding: 1.4rem 1.3rem;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(255,255,255,0.07), rgba(255,255,255,0.02));
            border: 1px solid rgba(255,255,255,0.10);
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.15rem;
            line-height: 1.4;
            color: #fdf6ef;
            backdrop-filter: blur(12px);
            min-height: 130px;
            transition: transform 0.25s ease;
        }
        .promise-card:hover { transform: translateY(-3px); }
        .promise-card .idx {
            font-family: 'Inter', sans-serif;
            font-size: 0.75rem;
            color: rgba(246, 239, 233, 0.5);
            letter-spacing: 0.2em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
            display: block;
        }

        /* ---------- Connect cards ---------- */
        .connect-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.9rem;
        }
        .connect-card {
            display: block;
            padding: 1.1rem 1.2rem;
            border-radius: 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.10);
            text-decoration: none !important;
            color: #f6efe9 !important;
            transition: transform 0.2s ease, background 0.2s ease;
        }
        .connect-card:hover {
            transform: translateY(-3px);
            background: rgba(255,255,255,0.09);
        }
        .connect-card .label {
            font-size: 0.75rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: rgba(246, 239, 233, 0.55);
        }
        .connect-card .value {
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.3rem;
            margin-top: 0.15rem;
        }
        .gentle-note {
            color: rgba(246, 239, 233, 0.55);
            font-style: italic;
            font-size: 0.9rem;
            margin-top: 0.8rem;
        }

        /* ---------- Streamlit button override (for ping + shuffle) ---------- */
        div.stButton > button {
            background: linear-gradient(135deg, #ffb380, #f08aa8);
            color: #2a1612;
            border: 0;
            border-radius: 999px;
            padding: 0.55rem 1.4rem;
            font-weight: 600;
            box-shadow: 0 10px 30px -12px rgba(240,138,168,0.55);
            transition: transform 0.15s ease, box-shadow 0.2s ease;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 16px 34px -14px rgba(240,138,168,0.72);
            color: #2a1b2b;
        }
        div.stButton > button:focus { color: #2a1612; }

        /* ---------- Ticker (sticky bottom) ---------- */
        .ticker-wrap {
            position: fixed;
            left: 0; right: 0; bottom: 0;
            z-index: 50;
            padding: 0.55rem 1rem;
            background: linear-gradient(180deg, rgba(26,16,20,0) 0%, rgba(22,12,16,0.92) 40%, rgba(22,12,16,0.96) 100%);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-top: 1px solid rgba(255,255,255,0.08);
        }
        .ticker-inner {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            gap: 1rem;
            overflow: hidden;
        }
        .ticker-label {
            font-size: 0.7rem;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            color: rgba(255, 210, 180, 0.90);
            white-space: nowrap;
            padding: 0.25rem 0.7rem;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 999px;
        }
        .marquee {
            flex: 1;
            overflow: hidden;
            white-space: nowrap;
            position: relative;
            mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
        }
        .marquee-track {
            display: inline-block;
            padding-left: 100%;
            animation: marquee 32s linear infinite;
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            font-size: 1.05rem;
            color: #fdf6ef;
        }
        @keyframes marquee {
            0%   { transform: translateX(0); }
            100% { transform: translateX(-100%); }
        }
        .ticker-meta {
            font-size: 0.72rem;
            color: rgba(246, 239, 233, 0.5);
            white-space: nowrap;
        }

        /* ---------- Expander (tiny letter) styling ---------- */
        .streamlit-expanderHeader, details > summary {
            font-family: 'Cormorant Garamond', serif !important;
            font-size: 1.15rem !important;
            color: #fdf6ef !important;
        }

        /* ---------- Misc ---------- */
        a { color: #ffd0b8; }
        hr { border-color: rgba(255,255,255,0.08); }

        /* Mobile tuning */
        @media (max-width: 640px) {
            .hero { padding: 3.2rem 1.4rem 2.6rem 1.4rem; }
            .block-container { padding-top: 1.2rem; padding-bottom: 7rem; }
            .marquee-track { font-size: 0.95rem; }
        }
        </style>

        <div class="float-layer">
          <span style="left:8%;  animation-duration:22s; animation-delay:0s;">♡</span>
          <span style="left:22%; animation-duration:28s; animation-delay:4s;">✧</span>
          <span style="left:38%; animation-duration:25s; animation-delay:2s;">♡</span>
          <span style="left:55%; animation-duration:30s; animation-delay:6s;">✨</span>
          <span style="left:70%; animation-duration:26s; animation-delay:1s;">♡</span>
          <span style="left:84%; animation-duration:24s; animation-delay:5s;">✧</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

DEFAULT_THOUGHT = {
    "latest_thought": "I hope today was gentle with you.",
    "updated_at": str(date.today()),
}


def load_thought() -> dict:
    """Load the latest thought from thoughts.json, creating it if missing."""
    try:
        if not THOUGHTS_FILE.exists():
            save_thought(DEFAULT_THOUGHT["latest_thought"])
        with THOUGHTS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # Defensive: make sure required keys exist.
        if "latest_thought" not in data:
            data["latest_thought"] = DEFAULT_THOUGHT["latest_thought"]
        if "updated_at" not in data:
            data["updated_at"] = str(date.today())
        return data
    except Exception:
        return dict(DEFAULT_THOUGHT)


def save_thought(text: str) -> None:
    """Persist a new thought to thoughts.json."""
    payload = {
        "latest_thought": text.strip(),
        "updated_at": str(date.today()),
    }
    THOUGHTS_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def load_local_photos() -> List[Path]:
    """Return image paths from assets/photos, sorted by filename."""
    if not PHOTO_DIR.exists():
        return []
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    return sorted([p for p in PHOTO_DIR.iterdir() if p.suffix.lower() in exts])


def caption_from_filename(path_or_url: str) -> str:
    """Make a soft caption from a filename or URL stem."""
    name = Path(path_or_url).stem
    name = name.replace("_", " ").replace("-", " ").strip()
    if not name:
        return ""
    # Title-case but leave small words lowercase for a softer feel.
    words = name.split()
    smalls = {"a", "an", "the", "of", "and", "in", "on", "to"}
    return " ".join(
        w.capitalize() if (i == 0 or w.lower() not in smalls) else w.lower()
        for i, w in enumerate(words)
    )



def get_admin_password() -> str:
    """Read admin password from secrets, falling back to the local constant."""
    try:
        secret = st.secrets.get("ADMIN_PASSWORD", "")
        if secret:
            return secret
    except Exception:
        pass
    return LOCAL_FALLBACK_ADMIN_PASSWORD


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

def render_hero() -> None:
    st.markdown(
        """
        <div class="hero" id="top">
            <h1>Still, Always.</h1>
            <p class="sub">A small corner of the internet I once promised you, made with care, memories, and a little bit of hope.</p>
            <p class="body">No pressure. No expectation. Just something I said I would make, and something I still wanted to finish properly.</p>
            <a class="pill" href="#gallery">Wander through it</a>
            <a class="pill ghost" href="#promise" style="margin-left:0.6rem;">Read the promise</a>
            <div class="arrow-down">↓</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_gallery() -> None:
    st.markdown('<a id="gallery"></a>', unsafe_allow_html=True)

    local_photos = load_local_photos()
    url_photos = [u for u in PHOTO_URLS if isinstance(u, str) and u.strip()]
    total = len(local_photos) + len(url_photos)

    st.markdown(
        f'<div class="section-title">The gallery '
        f'<span class="metric-chip">{total} {"memory" if total == 1 else "memories"}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-sub">A quiet collection. Browse softly, there is no order to any of it.</div>',
        unsafe_allow_html=True,
    )

    if total == 0:
        # Elegant empty state with placeholder cards.
        st.markdown(
            '<div class="gallery-grid">'
            + "".join(
                [
                    '<div class="placeholder-card">Drop photos into<br/><code>assets/photos/</code><br/>to see them here.</div>'
                ]
                * 6
            )
            + "</div>",
            unsafe_allow_html=True,
        )
        return

    # Build the grid. Local files are embedded via Streamlit's image pipeline
    # using columns so they render reliably; URL photos use plain <img> tags
    # inside the same CSS card style.
    cols_per_row = 4
    items: List[tuple[str, str, str]] = []  # (kind, src, caption)
    for p in local_photos:
        items.append(("local", str(p), caption_from_filename(p.name)))
    for u in url_photos:
        items.append(("url", u, caption_from_filename(u)))

    for i in range(0, len(items), cols_per_row):
        row = items[i : i + cols_per_row]
        cols = st.columns(len(row), gap="small")
        for col, (kind, src, cap) in zip(cols, row):
            with col:
                if kind == "local":
                    # st.image handles local files cleanly across formats.
                    st.image(src, use_container_width=True, caption=cap or None)
                else:
                    safe_cap = cap.replace("<", "&lt;").replace(">", "&gt;")
                    st.markdown(
                        f"""
                        <div class="photo-card">
                            <img src="{src}" alt="{safe_cap}" loading="lazy"/>
                            {f'<div class="photo-caption">{safe_cap}</div>' if safe_cap else ''}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


def render_timeline() -> None:
    st.markdown('<a id="promise"></a>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">The promise</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">A few small lines, in order.</div>',
        unsafe_allow_html=True,
    )

    steps = [
        "I said I'd make something.",
        "Life moved, people changed, time passed.",
        "But some promises still deserve to be completed.",
        "So this is me finishing it, properly.",
        "No pressure. Just care.",
    ]
    cards_html = "".join(
        f'<div class="promise-card"><span class="idx">{i+1:02d}</span>{text}</div>'
        for i, text in enumerate(steps)
    )
    st.markdown(f'<div class="timeline">{cards_html}</div>', unsafe_allow_html=True)


def render_interactives() -> None:
    st.markdown('<div class="section-title">Little things</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">A few small interactions, if you feel like it.</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-family:\"Cormorant Garamond\",serif;font-size:1.4rem;'>"
            "Shuffle a memory quote</div>"
            "<div style='color:rgba(246,239,233,0.6);font-size:0.9rem;margin-bottom:0.8rem;'>"
            "Lines written for this page only.</div>",
            unsafe_allow_html=True,
        )
        if "quote_idx" not in st.session_state:
            st.session_state.quote_idx = 0
        if st.button("Shuffle", key="shuffle_btn"):
            # Avoid repeating the same quote twice in a row.
            new_idx = st.session_state.quote_idx
            while new_idx == st.session_state.quote_idx and len(MEMORY_QUOTES) > 1:
                new_idx = random.randrange(len(MEMORY_QUOTES))
            st.session_state.quote_idx = new_idx
        quote = MEMORY_QUOTES[st.session_state.quote_idx]
        st.markdown(
            f"<div style='font-family:\"Cormorant Garamond\",serif;font-style:italic;"
            f"font-size:1.25rem;line-height:1.5;color:#fdf6ef;margin-top:0.6rem;'>"
            f"&ldquo;{quote}&rdquo;</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-family:\"Cormorant Garamond\",serif;font-size:1.4rem;'>"
            "Play our vibe</div>"
            "<div style='color:rgba(246,239,233,0.6);font-size:0.9rem;margin-bottom:0.8rem;'>"
            "A soft soundtrack, in case it helps.</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<a class="pill" href="{SPOTIFY_OR_YOUTUBE_URL}" target="_blank" rel="noopener">'
            f"Open the playlist ↗</a>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Tiny letter
    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)
    with st.expander("A tiny letter (open only if you'd like)"):
        st.markdown(
            "<div style='font-family:\"Cormorant Garamond\",serif;font-size:1.1rem;"
            "line-height:1.75;color:#fdf6ef;'>"
            "I don't know what this will mean to you, or whether it should mean anything at all. "
            "I only know that I once wanted to build you something beautiful, and I did not want "
            "that promise to remain unfinished. So I made this, quietly, carefully, and with "
            "the same softness that the best memories deserve."
            "</div>",
            unsafe_allow_html=True,
        )


def render_connect_section() -> None:
    st.markdown('<a id="connect"></a>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">If you ever want to ping me</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-sub">All of these are optional. No pressure to reach out.</div>',
        unsafe_allow_html=True,
    )

    mailto = (
        f"mailto:{MY_EMAIL_HERE}"
        "?subject=A%20small%20ping"
        "&body=I%20visited%20the%20page."
    )

    cards = [
        ("Instagram", "@" + INSTAGRAM_URL.rstrip("/").split("/")[-1], INSTAGRAM_URL),
        ("Discord",   "Join the server",                                DISCORD_INVITE_URL),
        ("Email",     MY_EMAIL_HERE,                                    mailto),
        ("WhatsApp",  "Say hi",                                         WHATSAPP_URL),
    ]
    cards_html = "".join(
        f'<a class="connect-card" href="{url}" target="_blank" rel="noopener">'
        f'<div class="label">{label}</div><div class="value">{value}</div></a>'
        for label, value, url in cards
    )
    st.markdown(f'<div class="connect-grid">{cards_html}</div>', unsafe_allow_html=True)

    # Google Calendar embed
    st.markdown("<div style='height:1.6rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-family:\'Cormorant Garamond\',serif;font-size:1.15rem;'
        'color:rgba(246,239,233,0.75);margin-bottom:0.6rem;">When I\'m around</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style="border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,0.10);
                    box-shadow:0 20px 40px -30px rgba(0,0,0,0.5);">
            <iframe src="https://calendar.google.com/calendar/embed?src=64db8bd6c7d706543be719aa533ceb67cffb877cd0816312d31ddc51a6dd6a72%40group.calendar.google.com&ctz=Australia%2FSydney&bgcolor=%2315101c&showTitle=0&showNav=1&showDate=1&showPrint=0&showTabs=0&showCalendars=0&mode=WEEK"
                style="border:0;display:block;filter:invert(1) hue-rotate(180deg) brightness(0.85) saturate(0.9);"
                width="100%" height="420" frameborder="0" scrolling="no">
            </iframe>
        </div>
        <div class="gentle-note" style="margin-top:0.6rem;">
            Set this calendar to Public for viewing, and share with edit access for adding events.
        </div>
        <a class="pill" style="margin-top:0.8rem;display:inline-block;" target="_blank" rel="noopener"
           href="https://calendar.google.com/calendar/u/0?cid=NjRkYjhiZDZjN2Q3MDY1NDNiZTcxOWFhNTMzY2ViNjdjZmZiODc3Y2QwODE2MzEyZDMxZGRjNTFhNmRkNmE3MkBncm91cC5jYWxlbmRhci5nb29nbGUuY29t">
            Add or edit events ↗
        </a>
        """,
        unsafe_allow_html=True,
    )


def render_ticker() -> None:
    """Render the sticky bottom 'Current thought' marquee."""
    thought = load_thought()
    text = thought.get("latest_thought", "").strip() or DEFAULT_THOUGHT["latest_thought"]
    updated = thought.get("updated_at", "")
    safe_text = (text.replace("<", "&lt;").replace(">", "&gt;"))
    st.markdown(
        f"""
        <div class="ticker-wrap">
            <div class="ticker-inner">
                <span class="ticker-label">Current thought</span>
                <div class="marquee"><span class="marquee-track">{safe_text}</span></div>
                <span class="ticker-meta">updated {updated}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_admin() -> None:
    """Tiny admin pane to update the ticker thought."""
    with st.sidebar:
        st.markdown("### Caretaker")
        st.caption("A small admin pane for updating the thought ticker.")
        pwd = st.text_input("Password", type="password", key="admin_pw")
        expected = get_admin_password()
        if pwd:
            if pwd == expected:
                st.success("Unlocked.")
                current = load_thought()
                new_text = st.text_area(
                    "Latest thought",
                    value=current.get("latest_thought", ""),
                    height=120,
                    key="admin_thought",
                )
                if st.button("Save thought", key="admin_save"):
                    if new_text.strip():
                        save_thought(new_text)
                        st.success("Saved.")
                        # Streamlit will rerender; the ticker reads from disk.
                    else:
                        st.warning("Empty thoughts don't get saved.")
                st.caption(f"Last updated: {current.get('updated_at', '')}")
            else:
                st.error("Incorrect password.")
        st.markdown("---")
        st.caption(
            "Set `ADMIN_PASSWORD` and (optionally) `DISCORD_WEBHOOK_URL` "
            "in Streamlit secrets before deploying."
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    inject_css()
    render_sidebar_admin()
    render_hero()
    render_gallery()
    render_timeline()
    render_interactives()
    render_connect_section()
    render_ticker()


if __name__ == "__main__":
    main()
