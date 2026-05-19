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

import base64
import io
import json
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

import streamlit as st

# Pillow is used to downscale + recompress local photos before inlining them
# as base64 data URIs. The fallback path still works without it.
try:
    from PIL import Image as PILImage
    HAS_PIL = True
except Exception:
    HAS_PIL = False


# ---------------------------------------------------------------------------
# Configuration - edit these placeholders before deploying.
# ---------------------------------------------------------------------------

# Personal links. Replace the placeholder strings with your real ones.
MY_EMAIL_HERE = "madhavmukherjee1@gmail.com"
INSTAGRAM_URL = "https://www.instagram.com/breadbastket?igsh=c2sya3kycjcwZWZk"
DISCORD_INVITE_URL = "https://discord.gg/tZPh377qeP"
WHATSAPP_URL = "https://wa.me/61416232736"
SPOTIFY_OR_YOUTUBE_URL = "https://music.youtube.com/playlist?list=PL6H4rqMvHT-H8h6ORnTMFQJqXM4Z1pz6h&si=yt35oKTsnGLTdNIE"

# Ticker/admin timestamps are shown in this timezone.
APP_TIMEZONE = "Australia/Sydney"

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
THOUGHTS_CACHE_FILE = ROOT / "thoughts_cache.json"
THOUGHTS_LOG_FILE = ROOT / "thoughts_log.jsonl"

# Inline SVG icons (currentColor-based so they inherit the parent text color).
# Kept lightweight so the page stays fast and offline-safe.
ICONS = {
    "instagram": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="2" y="2" width="20" height="20" rx="5"/>'
        '<path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>'
        '<line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>'
    ),
    "discord": (
        '<svg viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M19.27 5.33C17.94 4.71 16.5 4.26 15 4a.09.09 0 0 0-.07.03c-.18.33-.39.76'
        '-.53 1.09a16.09 16.09 0 0 0-4.8 0c-.14-.34-.35-.76-.54-1.09c-.01-.02-.04-.03-.07-.03'
        'c-1.5.26-2.93.71-4.27 1.33c-.01 0-.02.01-.03.02c-2.72 4.07-3.47 8.03-3.1 11.95'
        'c0 .02.01.04.03.05c1.8 1.32 3.53 2.12 5.24 2.65c.03.01.06 0 .07-.02c.4-.55.76'
        '-1.13 1.07-1.74c.02-.04 0-.08-.04-.09c-.57-.22-1.11-.48-1.64-.78c-.04-.02-.04'
        '-.08-.01-.11c.11-.08.22-.17.33-.25c.02-.02.05-.02.07-.01c3.44 1.57 7.15 1.57 '
        '10.55 0c.02-.01.05 0 .07.01c.11.09.22.17.33.26c.04.03.04.09-.01.11c-.52.31'
        '-1.07.56-1.64.78c-.04.01-.05.06-.04.09c.32.61.68 1.19 1.07 1.74c.03.01.06.02.09.01'
        'c1.72-.53 3.45-1.33 5.25-2.65c.02-.01.03-.03.03-.05c.44-4.53-.73-8.46-3.1'
        '-11.95c-.01-.01-.02-.02-.04-.02zM8.52 14.91c-1.03 0-1.89-.95-1.89-2.12s.84'
        '-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12c0 1.17-.84 2.12-1.89 2.12zm6.97 0'
        'c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12c0 '
        '1.17-.83 2.12-1.89 2.12z"/></svg>'
    ),
    "mail": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
        '<rect width="20" height="16" x="2" y="4" rx="2"/>'
        '<path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>'
    ),
    "whatsapp": (
        '<svg viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M17.6 6.32A7.85 7.85 0 0 0 12.05 4 7.94 7.94 0 0 0 5.1 15.93L4 20'
        'l4.18-1.09a7.93 7.93 0 0 0 3.86 1h.01a7.94 7.94 0 0 0 7.94-7.94c0-2.12-.83'
        '-4.12-2.39-5.65zm-5.55 12.21a6.58 6.58 0 0 1-3.36-.92l-.24-.14-2.49.65'
        '.67-2.42-.16-.25a6.59 6.59 0 1 1 12.2-3.52c0 3.64-2.97 6.6-6.6 6.6h-.02z'
        'm3.62-4.94c-.2-.1-1.17-.58-1.36-.64s-.32-.1-.45.1c-.13.2-.51.64-.62.77'
        'c-.12.13-.23.15-.42.05c-.2-.1-.84-.31-1.6-.99c-.59-.53-.99-1.18-1.1-1.38'
        'c-.12-.2-.01-.31.09-.41c.09-.09.2-.23.3-.35c.1-.12.13-.2.2-.33c.07-.13'
        '.03-.25-.02-.35c-.05-.1-.45-1.09-.62-1.49c-.16-.39-.33-.34-.45-.34c-.12 0'
        '-.25-.02-.38-.02s-.35.05-.53.25c-.18.2-.7.69-.7 1.67c0 .98.72 1.94.82 '
        '2.07c.1.13 1.4 2.14 3.4 3c.48.21.85.33 1.14.42c.48.15.92.13 1.26.08c.39'
        '-.06 1.17-.48 1.34-.94c.16-.46.16-.85.12-.94c-.05-.08-.18-.13-.38-.23z"/></svg>'
    ),
    "quote": (
        '<svg viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M7.17 6A5.17 5.17 0 0 0 2 11.17V18h6.83v-6.83H5.5A1.67 1.67 0 0 1 7.17 9.5z"/>'
        '<path d="M17.17 6A5.17 5.17 0 0 0 12 11.17V18h6.83v-6.83H15.5a1.67 1.67 0 0 1 1.67-1.67z"/></svg>'
    ),
    "music": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M9 18V5l12-2v13"/>'
        '<circle cx="6" cy="18" r="3"/>'
        '<circle cx="18" cy="16" r="3"/></svg>'
    ),
}


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
    initial_sidebar_state="collapsed",
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

        /* Streamlit chrome: make the header transparent so the warm gradient
           shows through (no black bar) but keep the sidebar toggle visible. */
        #MainMenu { visibility: hidden; }
        [data-testid="stHeader"] {
            background: transparent !important;
        }
        [data-testid="stDecoration"] { display: none !important; }
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

        /* ---------- Little-things cards ---------- */
        .little-card {
            position: relative;
            overflow: hidden;
        }
        /* Warm hairline accent across the top edge */
        .little-card::before {
            content: "";
            position: absolute;
            inset: 0 0 auto 0;
            height: 2px;
            background: linear-gradient(90deg,
                rgba(255,178,140,0.0),
                rgba(255,178,140,0.7) 30%,
                rgba(240,138,168,0.7) 70%,
                rgba(240,138,168,0.0));
        }
        .little-eyebrow {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            font-size: 0.7rem;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            color: rgba(246, 239, 233, 0.55);
            margin-bottom: 0.5rem;
        }
        .little-eyebrow svg {
            width: 14px;
            height: 14px;
            opacity: 0.85;
            color: #ffd0b8;
        }
        .little-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.7rem;
            color: #fff5ec;
            line-height: 1.2;
            margin-bottom: 0.25rem;
        }
        .little-sub {
            color: rgba(246, 239, 233, 0.62);
            font-size: 0.92rem;
            margin-bottom: 1rem;
        }
        .pulled-quote {
            position: relative;
            padding: 0.5rem 0.6rem 0.5rem 1.1rem;
            border-left: 2px solid rgba(255, 178, 140, 0.55);
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            font-size: 1.2rem;
            line-height: 1.55;
            color: #fdf6ef;
            margin-top: 0.4rem;
        }
        .pulled-quote .quote-mark {
            position: absolute;
            top: -1.8rem;
            right: 0.1rem;
            font-family: 'Cormorant Garamond', serif;
            font-size: 5rem;
            line-height: 1;
            color: rgba(255, 178, 140, 0.16);
            pointer-events: none;
            user-select: none;
            font-weight: 700;
        }
        .vibe-visualizer {
            display: flex;
            align-items: flex-end;
            gap: 4px;
            height: 28px;
            margin: 0.2rem 0 1rem 0;
        }
        .vibe-visualizer span {
            display: block;
            width: 4px;
            border-radius: 2px;
            background: linear-gradient(180deg, rgba(255,178,140,0.9), rgba(240,138,168,0.9));
            transform-origin: bottom;
            animation: bar-bounce 1.3s ease-in-out infinite;
        }
        .vibe-visualizer span:nth-child(1) { animation-delay: 0.00s; height: 60%; }
        .vibe-visualizer span:nth-child(2) { animation-delay: 0.15s; height: 90%; }
        .vibe-visualizer span:nth-child(3) { animation-delay: 0.30s; height: 45%; }
        .vibe-visualizer span:nth-child(4) { animation-delay: 0.45s; height: 75%; }
        .vibe-visualizer span:nth-child(5) { animation-delay: 0.60s; height: 55%; }
        @keyframes bar-bounce {
            0%, 100% { transform: scaleY(0.5); }
            50%      { transform: scaleY(1); }
        }

        /* ---------- Horizontal gallery carousel ---------- */
        .scroll-hint {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            font-size: 0.72rem;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            color: rgba(246, 239, 233, 0.5);
            margin: 0.2rem 0 0.7rem 0;
        }
        .scroll-hint .dot {
            width: 6px; height: 6px; border-radius: 50%;
            background: rgba(255, 178, 140, 0.7);
            animation: hint-pulse 2.2s ease-in-out infinite;
        }
        @keyframes hint-pulse {
            0%,100% { opacity: 0.35; transform: scale(1); }
            50%     { opacity: 1;    transform: scale(1.4); }
        }
        .gallery-strip-wrap {
            position: relative;
        }
        /* Soft fades on either edge so the scroll strip feels infinite */
        .gallery-strip-wrap::before,
        .gallery-strip-wrap::after {
            content: "";
            position: absolute;
            top: 0;
            bottom: 18px;
            width: 56px;
            pointer-events: none;
            z-index: 2;
            border-radius: 18px;
        }
        .gallery-strip-wrap::before {
            left: 0;
            background: linear-gradient(90deg, rgba(26,16,20,0.95), rgba(26,16,20,0));
        }
        .gallery-strip-wrap::after {
            right: 0;
            background: linear-gradient(270deg, rgba(26,16,20,0.95), rgba(26,16,20,0));
        }
        .gallery-strip {
            display: flex;
            gap: 1.1rem;
            overflow-x: auto;
            overflow-y: visible;
            padding: 0.5rem 1.4rem 1rem 1.4rem;
            scroll-snap-type: x mandatory;
            scroll-padding-left: 1.4rem;
            scroll-behavior: smooth;
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 178, 140, 0.55) rgba(255,255,255,0.06);
        }
        .gallery-strip::-webkit-scrollbar { height: 8px; }
        .gallery-strip::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.05);
            border-radius: 999px;
        }
        .gallery-strip::-webkit-scrollbar-thumb {
            background: linear-gradient(90deg, rgba(255,178,140,0.65), rgba(240,138,168,0.65));
            border-radius: 999px;
        }
        .gallery-card {
            flex: 0 0 auto;
            width: clamp(220px, 28vw, 320px);
            aspect-ratio: 3 / 4;
            position: relative;
            border-radius: 18px;
            overflow: hidden;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 16px 34px -20px rgba(0,0,0,0.55);
            scroll-snap-align: start;
            transition: transform 0.35s ease, box-shadow 0.35s ease;
        }
        .gallery-card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.7s ease;
        }
        .gallery-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 22px 44px -18px rgba(0,0,0,0.6);
        }
        .gallery-card:hover img { transform: scale(1.05); }
        .gallery-card .photo-caption {
            position: absolute;
            inset: auto 0 0 0;
            padding: 0.65rem 0.9rem 0.85rem 0.9rem;
            background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.62) 100%);
            color: #fdf6ef;
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            font-size: 0.95rem;
            letter-spacing: 0.01em;
        }
        @media (max-width: 640px) {
            .gallery-card { width: 74vw; }
            .gallery-strip { padding-left: 1rem; padding-right: 1rem; scroll-padding-left: 1rem; }
            .gallery-strip-wrap::before,
            .gallery-strip-wrap::after { width: 32px; }
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
        .connect-grid {
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)) !important;
        }
        .connect-card {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            padding: 0.9rem 1rem;
            border-radius: 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.10);
            text-decoration: none !important;
            color: #f6efe9 !important;
            transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
        }
        .connect-card:hover {
            transform: translateY(-3px);
            background: rgba(255,255,255,0.09);
            border-color: rgba(255, 178, 140, 0.35);
        }
        .connect-icon {
            flex: 0 0 auto;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
            background: linear-gradient(135deg, rgba(255,178,140,0.18), rgba(240,138,168,0.14));
            border: 1px solid rgba(255,178,140,0.20);
            color: #ffd0b8;
        }
        .connect-icon svg { width: 20px; height: 20px; }
        .connect-text { min-width: 0; flex: 1; }
        .connect-card .label {
            font-size: 0.68rem;
            letter-spacing: 0.20em;
            text-transform: uppercase;
            color: rgba(246, 239, 233, 0.55);
            line-height: 1.2;
        }
        .connect-card .value {
            /* Inter (sans-serif) so digits, letters, and the difference
               between "1" and "I" are unambiguous in emails / handles. */
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-feature-settings: "tnum" 1, "lnum" 1, "ss01" 1;
            font-size: 0.98rem;
            font-weight: 500;
            margin-top: 0.15rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
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
    "updated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
}


def _get_app_timezone():
    if ZoneInfo is not None:
        try:
            return ZoneInfo(APP_TIMEZONE)
        except Exception:
            pass
    local_tz = datetime.now().astimezone().tzinfo
    return local_tz if local_tz is not None else timezone.utc


def _local_today_str() -> str:
    return datetime.now(_get_app_timezone()).date().isoformat()


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _to_local_display(utc_iso: str) -> str:
    """Format an ISO UTC timestamp in APP_TIMEZONE for UI display."""
    try:
        parsed = datetime.fromisoformat(str(utc_iso).strip().replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        local_dt = parsed.astimezone(_get_app_timezone())
        return local_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return ""


def _atomic_write_json(path: Path, payload: dict) -> None:
    """Atomically write JSON so abrupt restarts don't leave partial files."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temp_path.replace(path)


def _read_json_if_exists(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _normalize_thought_record(data: Optional[dict]) -> Optional[dict]:
    """Return a validated thought record or None for invalid payloads."""
    if not isinstance(data, dict):
        return None
    text = str(data.get("latest_thought", "")).strip()
    if not text:
        return None
    updated_at = str(data.get("updated_at") or _local_today_str())
    updated_at_utc = str(data.get("updated_at_utc") or "").strip()
    if not updated_at_utc:
        updated_at_utc = f"{updated_at}T00:00:00+00:00"
    # Guard against poisoned future timestamps that can pin reconciliation
    # to an old message forever (e.g. manually seeded bootstrap values).
    try:
        parsed = datetime.fromisoformat(updated_at_utc.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        parsed = parsed.astimezone(timezone.utc)
        if parsed > datetime.now(timezone.utc) + timedelta(minutes=5):
            updated_at_utc = f"{updated_at}T00:00:00+00:00"
    except Exception:
        updated_at_utc = f"{updated_at}T00:00:00+00:00"
    updated_at_local = str(data.get("updated_at_local") or "").strip() or _to_local_display(updated_at_utc)
    return {
        "latest_thought": text,
        "updated_at": updated_at,
        "updated_at_utc": updated_at_utc,
        "updated_at_local": updated_at_local,
    }


def _record_sort_key(record: dict) -> datetime:
    raw = str(record.get("updated_at_utc", "")).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(raw)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        pass
    raw_date = str(record.get("updated_at", "")).strip()
    try:
        parsed_date = date.fromisoformat(raw_date)
        return datetime(parsed_date.year, parsed_date.month, parsed_date.day, tzinfo=timezone.utc)
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


def _append_log_entry(event: str, record: dict) -> None:
    """Append a write-ahead event so the newest message can be recovered."""
    THOUGHTS_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "event": event,
        "logged_at_utc": _iso_utc_now(),
        "record": _normalize_thought_record(record),
    }
    with THOUGHTS_LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _load_log_records() -> List[dict]:
    records: List[dict] = []
    if not THOUGHTS_LOG_FILE.exists():
        return records
    try:
        with THOUGHTS_LOG_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                raw = line.strip()
                if not raw:
                    continue
                try:
                    row = json.loads(raw)
                except Exception:
                    continue
                record = _normalize_thought_record(row.get("record") if isinstance(row, dict) else None)
                if record:
                    records.append(record)
    except Exception:
        return []
    return records


def _record_datetime_utc(record: dict) -> datetime:
    """Best-effort UTC datetime extraction for record ordering."""
    return _record_sort_key(record)


def _last_log_record() -> Optional[dict]:
    records = _load_log_records()
    return records[-1] if records else None


def _sync_primary_and_cache(record: dict) -> None:
    """Write latest state to both files so either one can restore the other."""
    _atomic_write_json(THOUGHTS_FILE, record)
    _atomic_write_json(THOUGHTS_CACHE_FILE, record)


def _choose_latest_record(primary: Optional[dict], cache: Optional[dict], log_records: List[dict]) -> Optional[dict]:
    """Choose latest record with deterministic tie-breakers.

    Tie-breaking precedence (latest wins):
    1) newer UTC timestamp
    2) source priority: log > cache > primary
    3) log sequence (later line wins)
    """
    ranked: List[tuple[datetime, int, int, dict]] = []

    if primary:
        ranked.append((_record_datetime_utc(primary), 1, 0, primary))
    if cache:
        ranked.append((_record_datetime_utc(cache), 2, 0, cache))
    for idx, record in enumerate(log_records):
        ranked.append((_record_datetime_utc(record), 3, idx, record))

    if not ranked:
        return None
    return max(ranked, key=lambda item: (item[0], item[1], item[2]))[3]


def reconcile_thought_storage() -> dict:
    """Recover latest thought from primary file, cache mirror, or log history."""
    primary_record = _normalize_thought_record(_read_json_if_exists(THOUGHTS_FILE))
    cache_record = _normalize_thought_record(_read_json_if_exists(THOUGHTS_CACHE_FILE))
    log_records = _load_log_records()

    latest = _choose_latest_record(primary_record, cache_record, log_records)
    if latest:
        _sync_primary_and_cache(latest)
        # Only append when startup recovery promoted a different record.
        if _last_log_record() != latest:
            _append_log_entry("reconcile", latest)
        return latest

    bootstrap = {
        "latest_thought": DEFAULT_THOUGHT["latest_thought"],
        "updated_at": str(date.today()),
        "updated_at_utc": _iso_utc_now(),
    }
    _sync_primary_and_cache(bootstrap)
    _append_log_entry("bootstrap", bootstrap)
    return bootstrap


def load_thought() -> dict:
    """Load the latest thought with startup recovery across file/cache/log."""
    try:
        return reconcile_thought_storage()
    except Exception:
        return dict(DEFAULT_THOUGHT)


def save_thought(text: str) -> dict:
    """Persist thought to primary file, cache mirror, and append-only log."""
    updated_at_utc = _iso_utc_now()
    payload = {
        "latest_thought": text.strip(),
        "updated_at": _local_today_str(),
        "updated_at_utc": updated_at_utc,
        "updated_at_local": _to_local_display(updated_at_utc),
    }
    _sync_primary_and_cache(payload)
    _append_log_entry("save", payload)
    return payload


def get_cached_message_history(limit: int = 10) -> List[dict]:
    """Return recent cached messages for operator visibility."""
    records = _load_log_records()
    if not records:
        latest = _normalize_thought_record(_read_json_if_exists(THOUGHTS_CACHE_FILE))
        return [latest] if latest else []
    # Deduplicate consecutive duplicate messages while preserving recency.
    deduped: List[dict] = []
    for record in records:
        if deduped and deduped[-1].get("latest_thought") == record.get("latest_thought"):
            continue
        deduped.append(record)
    return deduped[-limit:]


def load_local_photos() -> List[Path]:
    """Return image paths from assets/photos, sorted by filename."""
    if not PHOTO_DIR.exists():
        return []
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    return sorted([p for p in PHOTO_DIR.iterdir() if p.suffix.lower() in exts])


@st.cache_data(show_spinner=False)
def _encode_local_image(path_str: str, _mtime: float, max_dim: int = 1400, quality: int = 82) -> str:
    """Read a local image, optionally downscale, return a base64 data URI.

    Cached on (path, mtime) so re-uploads invalidate automatically and the
    Streamlit rerun loop doesn't re-encode every photo on every interaction.
    """
    path = Path(path_str)
    if HAS_PIL:
        with PILImage.open(path) as im:
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGB")
            im.thumbnail((max_dim, max_dim), PILImage.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=quality, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    # Fallback: inline raw bytes (no resize). Page weight grows fast, but it works.
    mime = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png",  ".webp": "image/webp",
    }.get(path.suffix.lower(), "application/octet-stream")
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def image_to_data_uri(path: Path) -> str:
    """Safe wrapper around _encode_local_image that never raises."""
    try:
        return _encode_local_image(str(path), path.stat().st_mtime)
    except Exception:
        return ""


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

    # Build uniform cards for both local files and URL photos so the strip
    # has a consistent rhythm regardless of where the image came from.
    cards: List[str] = []

    def _card(src: str, cap: str) -> str:
        safe_cap = cap.replace("<", "&lt;").replace(">", "&gt;")
        caption_html = f'<div class="photo-caption">{safe_cap}</div>' if safe_cap else ""
        return (
            '<div class="gallery-card">'
            f'<img src="{src}" alt="{safe_cap}" loading="lazy"/>'
            f"{caption_html}"
            "</div>"
        )

    for p in local_photos:
        data_uri = image_to_data_uri(p)
        if not data_uri:
            continue
        cards.append(_card(data_uri, caption_from_filename(p.name)))

    for u in url_photos:
        cards.append(_card(u, caption_from_filename(u)))

    st.markdown(
        '<div class="scroll-hint"><span class="dot"></span>scroll &middot; swipe &middot; browse</div>'
        f'<div class="gallery-strip-wrap"><div class="gallery-strip">{"".join(cards)}</div></div>',
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

    if "quote_idx" not in st.session_state:
        st.session_state.quote_idx = 0

    with left:
        quote = MEMORY_QUOTES[st.session_state.quote_idx]
        safe_quote = quote.replace("<", "&lt;").replace(">", "&gt;")
        st.markdown(
            f'''
            <div class="glass little-card">
                <div class="little-eyebrow">{ICONS["quote"]}<span>Memory quote</span></div>
                <div class="little-title">Shuffle a thought</div>
                <div class="little-sub">Lines written for this page only.</div>
                <div class="pulled-quote">
                    <span class="quote-mark">&ldquo;</span>{safe_quote}
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        if st.button("Shuffle", key="shuffle_btn"):
            # Avoid repeating the same quote twice in a row.
            new_idx = st.session_state.quote_idx
            while new_idx == st.session_state.quote_idx and len(MEMORY_QUOTES) > 1:
                new_idx = random.randrange(len(MEMORY_QUOTES))
            st.session_state.quote_idx = new_idx
            st.rerun()

    with right:
        bars = "".join("<span></span>" for _ in range(5))
        st.markdown(
            f'''
            <div class="glass little-card">
                <div class="little-eyebrow">{ICONS["music"]}<span>Vibe</span></div>
                <div class="little-title">Play our vibe</div>
                <div class="little-sub">A soft soundtrack, in case it helps.</div>
                <div class="vibe-visualizer">{bars}</div>
                <a class="pill" href="{SPOTIFY_OR_YOUTUBE_URL}" target="_blank" rel="noopener">
                    Open the playlist &#8599;
                </a>
            </div>
            ''',
            unsafe_allow_html=True,
        )

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

    # Pull the Instagram handle out of the URL cleanly (drop query params).
    ig_handle = INSTAGRAM_URL.rstrip("/").split("/")[-1].split("?")[0] or "instagram"

    cards = [
        ("instagram", "Instagram", "@" + ig_handle,    INSTAGRAM_URL),
        ("discord",   "Discord",   "Join the server", DISCORD_INVITE_URL),
        ("mail",      "Email",     MY_EMAIL_HERE,     mailto),
        ("whatsapp",  "WhatsApp",  "Say hi",          WHATSAPP_URL),
    ]
    cards_html = "".join(
        f'<a class="connect-card" href="{url}" target="_blank" rel="noopener">'
        f'<span class="connect-icon">{ICONS[icon]}</span>'
        f'<span class="connect-text">'
        f'<div class="label">{label}</div>'
        f'<div class="value">{value}</div>'
        f'</span></a>'
        for icon, label, value, url in cards
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
    updated = thought.get("updated_at_local", "") or thought.get("updated_at", "")
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
                        saved = save_thought(new_text)
                        current = saved
                        st.success("Saved.")
                        st.caption(f"Cached at {saved.get('updated_at_local', '')}")
                        # Streamlit will rerender; the ticker reads from disk.
                    else:
                        st.warning("Empty thoughts don't get saved.")
                st.caption(
                    f"Last updated: {current.get('updated_at_local', '') or current.get('updated_at', '')}"
                )
                with st.expander("Recent cached messages"):
                    history = get_cached_message_history(limit=8)
                    if not history:
                        st.caption("No cache history yet.")
                    else:
                        for item in reversed(history):
                            st.write(
                                f"{item.get('updated_at_local', '') or item.get('updated_at', '')} - "
                                f"{item.get('latest_thought', '')}"
                            )
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
