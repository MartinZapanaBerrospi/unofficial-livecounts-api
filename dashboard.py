import streamlit as st
import time
from unofficial_livecounts_api import (
    api, RequestApiError, send_request,
    YOUTUBE_CHANNEL_STATS_API, YOUTUBE_VIDEO_STATS_API,
)

# ──────────────────────────── Page Config ────────────────────────────
st.set_page_config(
    page_title="Livecounts Dashboard Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────── Custom CSS ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

html, body, [class*="st-"] { font-family: 'Outfit', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%); }
#MainMenu, footer, header { visibility: hidden; }

/* Counter box */
.counter-box {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(168,85,247,0.1));
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px;
    padding: 2.5rem 2rem 2rem;
    text-align: center;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    margin: 0.5rem 0;
}

/* Digit cells */
.digits-row { display: flex; justify-content: center; align-items: center; gap: 4px; margin: 0.8rem 0; }
.digit-cell {
    display: inline-flex; align-items: center; justify-content: center;
    width: 54px; height: 74px;
    background: rgba(15,23,42,0.85);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    font-size: 3.2rem; font-weight: 800; color: #c4b5fd;
    font-variant-numeric: tabular-nums;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}
.digit-cell.up { animation: glow-green 0.6s ease; }
.digit-cell.down { animation: glow-red 0.6s ease; }
@keyframes glow-green {
    0%   { color: #c4b5fd; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
    40%  { color: #4ade80; box-shadow: 0 0 20px rgba(74,222,128,0.5); }
    100% { color: #c4b5fd; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
}
@keyframes glow-red {
    0%   { color: #c4b5fd; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
    40%  { color: #f87171; box-shadow: 0 0 20px rgba(248,113,113,0.5); }
    100% { color: #c4b5fd; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
}
.digit-sep { font-size: 2.8rem; font-weight: 800; color: #475569; padding: 0 2px; }
.diff-badge {
    display: inline-block; padding: 0.25rem 0.9rem; border-radius: 99px;
    font-size: 0.85rem; font-weight: 600; margin-top: 0.5rem;
}
.diff-up   { background: rgba(74,222,128,0.15); color: #4ade80; }
.diff-down { background: rgba(248,113,113,0.15); color: #f87171; }

.counter-label {
    color: #94a3b8; font-size: 1.2rem; margin-top: 0.3rem;
    text-transform: uppercase; letter-spacing: 3px;
}
.user-name { color: #e2e8f0; font-size: 1.6rem; font-weight: 600; margin-bottom: 0.3rem; }

/* Metric cards */
.metric-card {
    background: rgba(30,41,59,0.7);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 1.3rem; text-align: center;
    backdrop-filter: blur(8px);
}
.metric-value { font-size: 1.6rem; font-weight: 700; color: #f8fafc; }
.metric-label {
    color: #64748b; font-size: 0.8rem; text-transform: uppercase;
    letter-spacing: 2px; margin-top: 0.2rem;
}

/* Badges */
.platform-badge {
    display: inline-block; padding: 0.35rem 1rem; border-radius: 99px;
    font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 2px; margin-bottom: 0.8rem;
}
.badge-youtube { background: rgba(255,0,0,0.15); color: #ff4444; }
.badge-tiktok  { background: rgba(0,242,234,0.15); color: #00f2ea; }
.badge-twitter { background: rgba(29,161,242,0.15); color: #1da1f2; }
.badge-twitch  { background: rgba(145,70,255,0.15); color: #9146ff; }
.badge-kick    { background: rgba(83,252,24,0.15); color: #53fc18; }

/* Live dot */
.live-dot {
    display: inline-block; width: 10px; height: 10px;
    background: #ef4444; border-radius: 50%; margin-right: 8px;
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(239,68,68,0.7); }
    50% { opacity: 0.7; box-shadow: 0 0 0 8px rgba(239,68,68,0); }
}

.avatar-img {
    width: 90px; height: 90px; border-radius: 50%;
    border: 3px solid rgba(129,140,248,0.5);
    object-fit: cover; margin: 0 auto 0.8rem; display: block;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.05);
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    color: #94a3b8 !important; font-weight: 600;
    text-transform: uppercase; letter-spacing: 1px; font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────── Platform Config ────────────────────────
PLATFORMS = {
    "🔴 YouTube — Suscriptores": {"key": "yt_subs", "badge": "badge-youtube", "label": "Suscriptores"},
    "🔴 YouTube — Vistas de Video": {"key": "yt_views", "badge": "badge-youtube", "label": "Vistas"},
    "🎵 TikTok — Seguidores": {"key": "tt_followers", "badge": "badge-tiktok", "label": "Seguidores"},
    "🎵 TikTok — Vistas de Video": {"key": "tt_views", "badge": "badge-tiktok", "label": "Vistas"},
    "🐦 Twitter/X — Seguidores": {"key": "tw_followers", "badge": "badge-twitter", "label": "Seguidores"},
    "💜 Twitch — Seguidores": {"key": "twitch_followers", "badge": "badge-twitch", "label": "Seguidores"},
    "💚 Kick — Seguidores": {"key": "kick_followers", "badge": "badge-kick", "label": "Seguidores"},
}

# ──────────────────────────── Sidebar ────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Livecounts Pro")
    st.markdown("---")
    selected_platform = st.selectbox("Plataforma", list(PLATFORMS.keys()), index=0)
    platform_info = PLATFORMS[selected_platform]
    query = st.text_input("Buscar usuario o canal", placeholder="Ej: MrBeast")
    search_btn = st.button("🔍 Buscar", use_container_width=True, type="primary")
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#475569;font-size:0.75rem;'>"
        "Potenciado por<br><b>Unofficial Livecounts API</b><br>© 2026</div>",
        unsafe_allow_html=True,
    )

# ──────────────────────────── State ──────────────────────────────────
for k, v in {"user_id": None, "user_name": "", "user_avatar": "",
             "platform_key": "", "prev_count": 0,
             "search_results": [], "show_results": False}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────── Helpers ────────────────────────────────
def fmt(n):
    """Format a number with dots as thousands separator."""
    return f"{n:,}".replace(",", ".")

def render_digits(current: int, previous: int) -> str:
    """Digit-by-digit counter with green/red glow on changed digits."""
    c = str(current)
    p = str(previous) if previous else c
    m = max(len(c), len(p))
    c, p = c.zfill(m), p.zfill(m)
    diff = current - previous

    cells = []
    cnt = 0
    for i, (cd, pd) in enumerate(zip(c, p)):
        remaining = m - i
        if cnt > 0 and remaining % 3 == 0:
            cells.append('<span class="digit-sep">.</span>')
        cls = "digit-cell"
        if cd != pd:
            cls += " up" if diff > 0 else " down"
        cells.append(f'<span class="{cls}">{cd}</span>')
        cnt += 1

    # Diff badge — only show if there is an actual change
    badge = ""
    if previous and diff != 0:
        sign = "+" if diff > 0 else ""
        bcls = "diff-up" if diff > 0 else "diff-down"
        badge = f'<div><span class="diff-badge {bcls}">{sign}{fmt(diff)}</span></div>'

    return f'<div class="digits-row">{"".join(cells)}</div>{badge}'

# ──────────────────────────── Search ─────────────────────────────────
def do_search(q: str, pk: str):
    results = []
    try:
        if pk in ("yt_subs", "yt_views"):
            fn = api.youtube.find_channel if pk == "yt_subs" else api.youtube.find_video
            raw = fn(q)
            results = [{"id": r.get("id",""), "name": r.get("name",""), "avatar": r.get("avatar","")} for r in raw]
        elif pk == "tt_followers":
            raw = api.tiktok.find_user(q)
            results = [{"id": r.user_id, "name": r.display_name or r.username, "avatar": r.thumbnail} for r in raw]
        elif pk == "tt_views":
            st.session_state.update(user_id=q, user_name=f"Video: {q}", user_avatar="",
                                     platform_key=pk, prev_count=0, show_results=False)
            return
        elif pk == "tw_followers":
            raw = api.twitter.find_user(q)
            results = [{"id": raw["id"], "name": raw["username"], "avatar": raw.get("avatar","")}] if raw else []
        elif pk == "twitch_followers":
            raw = api.twitch.find_user(q)
            results = [{"id": r["id"], "name": r["username"], "avatar": r.get("avatar","")} for r in raw]
        elif pk == "kick_followers":
            raw = api.kick.find_user(q)
            results = [{"id": r["id"], "name": r["username"], "avatar": r.get("avatar","")} for r in raw]
    except RequestApiError as e:
        st.error(f"Error de búsqueda: {e}")
        return
    st.session_state.update(search_results=results, show_results=True,
                             platform_key=pk, user_id=None, prev_count=0)

def select_user(idx: int):
    r = st.session_state.search_results[idx]
    st.session_state.update(user_id=r["id"], user_name=r["name"],
                             user_avatar=r.get("avatar",""),
                             show_results=False, prev_count=0)

def get_metrics(uid: str, pk: str) -> dict:
    """Fetch ALL available metrics for the current (platform, user)."""
    try:
        if pk == "yt_subs":
            raw = send_request(f"{YOUTUBE_CHANNEL_STATS_API}/{uid}")
            subs = raw.get("followerCount", 0)
            bottom = raw.get("bottomOdos", [0, 0, 0])
            channel_views = bottom[0] if len(bottom) > 0 else 0
            video_count   = bottom[2] if len(bottom) > 2 else 0
            # Goal: next round milestone
            goal = _next_milestone(subs)
            return {"main": subs, "label": "Suscriptores",
                    "extra": {"👁️ Channel Views": channel_views, "🎬 Videos": video_count, "🎯 Goal": goal}}

        elif pk == "yt_views":
            raw = send_request(f"{YOUTUBE_VIDEO_STATS_API}/{uid}")
            views = raw.get("followerCount", 0)
            bottom = raw.get("bottomOdos", [0, 0, 0])
            likes    = bottom[0] if len(bottom) > 0 else 0
            dislikes = bottom[1] if len(bottom) > 1 else 0
            comments = bottom[2] if len(bottom) > 2 else 0
            return {"main": views, "label": "Vistas",
                    "extra": {"👍 Likes": likes, "👎 Dislikes": dislikes, "💬 Comments": comments}}

        elif pk == "tt_followers":
            m = api.tiktok.fetch_user_metrics(uid)
            return {"main": m["followers"], "label": "Seguidores",
                    "extra": {"❤️ Likes": m.get("likes", 0), "👥 Siguiendo": m.get("following", 0), "🎬 Videos": m.get("videos", 0)}}
        elif pk == "tt_views":
            m = api.tiktok.fetch_video_stats(uid)
            return {"main": m["views"], "label": "Vistas",
                    "extra": {"❤️ Likes": m.get("likes", 0), "💬 Comentarios": m.get("comments", 0), "🔄 Shares": m.get("shares", 0)}}
        elif pk == "tw_followers":
            m = api.twitter.fetch_user_metrics(uid)
            return {"main": m["followers"], "label": "Seguidores"}
        elif pk == "twitch_followers":
            m = api.twitch.fetch_user_metrics(uid)
            return {"main": m["followers"], "label": "Seguidores"}
        elif pk == "kick_followers":
            m = api.kick.fetch_user_metrics(uid)
            return {"main": m["followers"], "label": "Seguidores"}
    except RequestApiError as e:
        return {"main": 0, "label": "Error", "error": str(e)}
    return {"main": 0, "label": "—"}

def _next_milestone(current: int) -> int:
    """Calculate next round milestone (like livecounts Goal)."""
    if current <= 0:
        return 1000
    magnitude = 10 ** len(str(current))
    step = magnitude // 10
    return ((current // step) + 1) * step

# ──────────────────────────── Trigger ────────────────────────────────
if search_btn and query:
    do_search(query, platform_info["key"])

# ──────────────────────────── Search Results ─────────────────────────
if st.session_state.show_results and not st.session_state.user_id:
    results = st.session_state.search_results
    if not results:
        st.markdown(
            '<div style="text-align:center;padding:4rem 2rem;">'
            '<div style="font-size:3rem;margin-bottom:1rem;">🔍</div>'
            '<div style="color:#f87171;font-size:1.2rem;font-weight:600;">No se encontraron usuarios</div>'
            '<div style="color:#64748b;margin-top:0.5rem;">Intenta con otro nombre o verifica la plataforma.</div>'
            '</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div style="text-align:center;color:#94a3b8;margin:1rem 0;font-size:1.1rem;">'
            f'<b style="color:#c4b5fd;">{len(results)}</b> resultados encontrados — selecciona uno:</div>',
            unsafe_allow_html=True)

        cols_per = 3
        for rs in range(0, len(results), cols_per):
            cols = st.columns(cols_per)
            for ci in range(cols_per):
                i = rs + ci
                if i >= len(results):
                    break
                r = results[i]
                with cols[ci]:
                    av = r.get("avatar", "")
                    av_html = (f'<img src="{av}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;" />'
                               if av else '<div style="width:40px;height:40px;border-radius:50%;background:#334155;'
                               'display:flex;align-items:center;justify-content:center;color:#94a3b8;font-size:1.2rem;">?</div>')
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:0.8rem;padding:0.8rem;'
                        f'background:rgba(30,41,59,0.7);border:1px solid rgba(255,255,255,0.08);'
                        f'border-radius:12px;margin-bottom:0.3rem;">'
                        f'{av_html}'
                        f'<div><div style="color:#e2e8f0;font-weight:600;">{r["name"]}</div>'
                        f'<div style="color:#64748b;font-size:0.75rem;">{r["id"][:24]}</div></div>'
                        f'</div>', unsafe_allow_html=True)
                    if st.button("Seleccionar", key=f"sel_{i}", use_container_width=True):
                        select_user(i)
                        st.rerun()

# ──────────────────────────── Live Dashboard ─────────────────────────
elif st.session_state.user_id:
    metrics = get_metrics(st.session_state.user_id, st.session_state.platform_key)
    badge_class = platform_info["badge"]
    main_count = metrics.get("main", 0)
    prev_count = st.session_state.prev_count

    # EN VIVO header
    st.markdown(
        '<div style="text-align:center;margin-bottom:0.3rem;">'
        '<span class="live-dot"></span>'
        '<span style="color:#ef4444;font-weight:600;font-size:0.85rem;letter-spacing:2px;">EN VIVO</span>'
        '</div>', unsafe_allow_html=True)

    avatar_html = f'<img src="{st.session_state.user_avatar}" class="avatar-img" />' if st.session_state.user_avatar else ""
    digits_html = render_digits(main_count, prev_count)

    st.markdown(
        f'<div class="counter-box">'
        f'<span class="platform-badge {badge_class}">{selected_platform.split("—")[0].strip()}</span>'
        f'{avatar_html}'
        f'<div class="user-name">{st.session_state.user_name}</div>'
        f'{digits_html}'
        f'<div class="counter-label">{metrics.get("label", "")}</div>'
        f'</div>', unsafe_allow_html=True)

    st.session_state.prev_count = main_count

    # Secondary metrics
    extra = metrics.get("extra", {})
    if extra:
        cols = st.columns(len(extra))
        for i, (label, value) in enumerate(extra.items()):
            with cols[i]:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-value">{fmt(value)}</div>'
                    f'<div class="metric-label">{label}</div>'
                    f'</div>', unsafe_allow_html=True)

    if "error" in metrics:
        st.warning(f"⚠️ {metrics['error']}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Cambiar Usuario", use_container_width=False):
        st.session_state.update(user_id=None, show_results=True, prev_count=0)
        st.rerun()

    # Always-on real-time refresh (~2 seconds)
    time.sleep(2)
    st.rerun()

# ──────────────────────────── Welcome ────────────────────────────────
else:
    st.markdown(
        '<div style="text-align:center;padding:6rem 2rem;">'
        '<div style="font-size:4rem;margin-bottom:1rem;">📊</div>'
        '<div style="color:#94a3b8;font-size:1.3rem;font-weight:300;">'
        'Selecciona una plataforma y busca un usuario<br>para ver sus estadísticas en tiempo real.'
        '</div></div>', unsafe_allow_html=True)
