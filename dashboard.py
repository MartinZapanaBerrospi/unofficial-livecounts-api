import streamlit as st
import time
from unofficial_livecounts_api import (
    api, RequestApiError,
    YoutubeAgent, TwitterAgent, TwitchAgent, KickAgent, TiktokAgent
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

/* Global */
html, body, [class*="st-"] { font-family: 'Outfit', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%); }

/* Hide default Streamlit elements */
#MainMenu, footer, header { visibility: hidden; }

/* Main counter */
.counter-box {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(168,85,247,0.1));
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px;
    padding: 3rem 2rem;
    text-align: center;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    margin: 1rem 0;
}

/* ── Animated digit counter (livecounts-style) ── */
.digits-row {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 4px;
    margin: 1rem 0;
}
.digit-cell {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 58px; height: 80px;
    background: rgba(15,23,42,0.8);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    font-size: 3.5rem;
    font-weight: 800;
    color: #c4b5fd;
    font-variant-numeric: tabular-nums;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    transition: color 0.3s ease;
}
.digit-cell.changed-up {
    animation: glow-green 0.6s ease;
}
.digit-cell.changed-down {
    animation: glow-red 0.6s ease;
}
@keyframes glow-green {
    0% { color: #c4b5fd; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
    40% { color: #4ade80; box-shadow: 0 0 20px rgba(74,222,128,0.5); }
    100% { color: #c4b5fd; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
}
@keyframes glow-red {
    0% { color: #c4b5fd; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
    40% { color: #f87171; box-shadow: 0 0 20px rgba(248,113,113,0.5); }
    100% { color: #c4b5fd; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
}
.digit-separator {
    font-size: 3rem;
    font-weight: 800;
    color: #475569;
    padding: 0 2px;
}
.diff-badge {
    display: inline-block;
    padding: 0.3rem 1rem;
    border-radius: 99px;
    font-size: 0.9rem;
    font-weight: 600;
    margin-top: 0.8rem;
}
.diff-up { background: rgba(74,222,128,0.15); color: #4ade80; }
.diff-down { background: rgba(248,113,113,0.15); color: #f87171; }
.diff-neutral { background: rgba(148,163,184,0.1); color: #94a3b8; }

.counter-label {
    color: #94a3b8;
    font-size: 1.3rem;
    margin-top: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 3px;
}
.user-name {
    color: #e2e8f0;
    font-size: 1.8rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

/* ── Search result cards ── */
.search-results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}
.result-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.2rem;
    background: rgba(30,41,59,0.7);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.result-card:hover {
    border-color: rgba(129,140,248,0.4);
    background: rgba(30,41,59,0.9);
    transform: translateY(-2px);
}
.result-avatar {
    width: 50px; height: 50px;
    border-radius: 50%;
    border: 2px solid rgba(129,140,248,0.3);
    object-fit: cover;
    flex-shrink: 0;
}
.result-name {
    color: #e2e8f0;
    font-weight: 600;
    font-size: 1rem;
}
.result-id {
    color: #64748b;
    font-size: 0.8rem;
}

/* Metric cards */
.metric-card {
    background: rgba(30,41,59,0.7);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    backdrop-filter: blur(8px);
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #f8fafc;
}
.metric-label {
    color: #64748b;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 0.3rem;
}

/* Platform badge */
.platform-badge {
    display: inline-block;
    padding: 0.4rem 1.2rem;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 1rem;
}
.badge-youtube { background: rgba(255,0,0,0.15); color: #ff4444; }
.badge-tiktok { background: rgba(0,242,234,0.15); color: #00f2ea; }
.badge-twitter { background: rgba(29,161,242,0.15); color: #1da1f2; }
.badge-twitch { background: rgba(145,70,255,0.15); color: #9146ff; }
.badge-kick { background: rgba(83,252,24,0.15); color: #53fc18; }

/* Live indicator */
.live-dot {
    display: inline-block;
    width: 10px; height: 10px;
    background: #ef4444;
    border-radius: 50%;
    margin-right: 8px;
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(239,68,68,0.7); }
    50% { opacity: 0.7; box-shadow: 0 0 0 8px rgba(239,68,68,0); }
}

/* Avatar */
.avatar-img {
    width: 100px; height: 100px;
    border-radius: 50%;
    border: 3px solid rgba(129,140,248,0.5);
    object-fit: cover;
    margin: 0 auto 1rem;
    display: block;
}

/* Sidebar overrides */
[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.05);
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    color: #94a3b8 !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 0.8rem;
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
    auto_refresh = st.toggle("⚡ Actualización en vivo", value=True)
    refresh_rate = st.slider("Frecuencia (segundos)", 2, 10, 2)
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#475569;font-size:0.75rem;'>"
        "Potenciado por<br><b>Unofficial Livecounts API</b><br>© 2026</div>",
        unsafe_allow_html=True,
    )

# ──────────────────────────── State Management ───────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = None
    st.session_state.user_name = ""
    st.session_state.user_avatar = ""
    st.session_state.platform_key = ""
    st.session_state.prev_count = 0
    st.session_state.search_results = []  # list of dicts
    st.session_state.show_results = False

# ──────────────────────────── Digit Renderer ─────────────────────────
def render_animated_digits(current: int, previous: int) -> str:
    """Build HTML for digit-by-digit counter with green/red glow on change."""
    cur_str = str(current)
    prev_str = str(previous) if previous else cur_str
    
    # Pad shorter string
    max_len = max(len(cur_str), len(prev_str))
    cur_str = cur_str.zfill(max_len)
    prev_str = prev_str.zfill(max_len)
    
    diff = current - previous
    cells = []
    digit_count = 0
    
    for i, (c, p) in enumerate(zip(cur_str, prev_str)):
        # Add thousands separator
        remaining = max_len - i
        if digit_count > 0 and remaining % 3 == 0:
            cells.append('<span class="digit-separator">.</span>')
        
        css_class = "digit-cell"
        if c != p:
            css_class += " changed-up" if diff > 0 else " changed-down"
        
        cells.append(f'<span class="{css_class}">{c}</span>')
        digit_count += 1
    
    # Difference badge
    diff_html = ""
    if previous and diff != 0:
        sign = "+" if diff > 0 else ""
        badge_cls = "diff-up" if diff > 0 else "diff-down"
        diff_html = f'<div><span class="diff-badge {badge_cls}">{sign}{diff:,}</span></div>'.replace(",", ".")
    elif previous:
        diff_html = '<div><span class="diff-badge diff-neutral">= 0</span></div>'
    
    return f'<div class="digits-row">{"".join(cells)}</div>{diff_html}'

# ──────────────────────────── Search Logic ───────────────────────────
def do_search(query: str, platform_key: str):
    """Search and populate results list for user selection."""
    results = []
    try:
        if platform_key == "yt_subs":
            raw = api.youtube.find_channel(query)
            results = [{"id": r["id"], "name": r["name"], "avatar": r.get("avatar", "")} for r in raw]
        elif platform_key == "yt_views":
            raw = api.youtube.find_video(query)
            results = [{"id": r["id"], "name": r["name"], "avatar": r.get("avatar", "")} for r in raw]
        elif platform_key == "tt_followers":
            raw = api.tiktok.find_user(query)
            results = [{"id": r.user_id, "name": r.display_name or r.username, "avatar": r.thumbnail} for r in raw]
        elif platform_key == "tt_views":
            st.session_state.user_id = query
            st.session_state.user_name = f"Video: {query}"
            st.session_state.user_avatar = ""
            st.session_state.platform_key = platform_key
            st.session_state.prev_count = 0
            st.session_state.show_results = False
            return
        elif platform_key == "tw_followers":
            raw = api.twitter.find_user(query)
            if raw:
                results = [{"id": raw["id"], "name": raw["username"], "avatar": raw.get("avatar", "")}]
        elif platform_key == "twitch_followers":
            raw = api.twitch.find_user(query)
            results = [{"id": r["id"], "name": r["username"], "avatar": r.get("avatar", "")} for r in raw]
        elif platform_key == "kick_followers":
            raw = api.kick.find_user(query)
            results = [{"id": r["id"], "name": r["username"], "avatar": r.get("avatar", "")} for r in raw]
    except RequestApiError as e:
        st.error(f"Error de búsqueda: {e}")
        return
    
    st.session_state.search_results = results
    st.session_state.show_results = True
    st.session_state.platform_key = platform_key
    st.session_state.user_id = None  # Clear previous selection
    st.session_state.prev_count = 0

def select_user(idx: int):
    """Select a user from search results."""
    r = st.session_state.search_results[idx]
    st.session_state.user_id = r["id"]
    st.session_state.user_name = r["name"]
    st.session_state.user_avatar = r.get("avatar", "")
    st.session_state.show_results = False
    st.session_state.prev_count = 0

def get_metrics(user_id: str, platform_key: str) -> dict:
    """Fetch real-time metrics for the current user."""
    try:
        if platform_key == "yt_subs":
            m = api.youtube.fetch_channel_metrics(user_id)
            return {"main": m["subscribers"], "label": "Suscriptores"}
        elif platform_key == "yt_views":
            m = api.youtube.fetch_video_metrics(user_id)
            return {"main": m["views"], "label": "Vistas"}
        elif platform_key == "tt_followers":
            m = api.tiktok.fetch_user_metrics(user_id)
            return {"main": m["followers"], "label": "Seguidores",
                    "extra": {"❤️ Likes": m.get("likes", 0), "👥 Siguiendo": m.get("following", 0), "🎬 Videos": m.get("videos", 0)}}
        elif platform_key == "tt_views":
            m = api.tiktok.fetch_video_stats(user_id)
            return {"main": m["views"], "label": "Vistas",
                    "extra": {"❤️ Likes": m.get("likes", 0), "💬 Comentarios": m.get("comments", 0), "🔄 Shares": m.get("shares", 0)}}
        elif platform_key == "tw_followers":
            m = api.twitter.fetch_user_metrics(user_id)
            return {"main": m["followers"], "label": "Seguidores"}
        elif platform_key == "twitch_followers":
            m = api.twitch.fetch_user_metrics(user_id)
            return {"main": m["followers"], "label": "Seguidores"}
        elif platform_key == "kick_followers":
            m = api.kick.fetch_user_metrics(user_id)
            return {"main": m["followers"], "label": "Seguidores"}
    except RequestApiError as e:
        return {"main": 0, "label": "Error", "error": str(e)}
    return {"main": 0, "label": "—"}

# ──────────────────────────── Search Trigger ──────────────────────────
if search_btn and query:
    do_search(query, platform_info["key"])

# ──────────────────────────── Search Results List ─────────────────────
if st.session_state.show_results and not st.session_state.user_id:
    results = st.session_state.search_results
    
    if not results:
        st.markdown(
            '<div style="text-align:center;padding:4rem 2rem;">'
            '<div style="font-size:3rem;margin-bottom:1rem;">🔍</div>'
            '<div style="color:#f87171;font-size:1.2rem;font-weight:600;">No se encontraron usuarios</div>'
            '<div style="color:#64748b;margin-top:0.5rem;">Intenta con otro nombre o verifica la plataforma seleccionada.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="text-align:center;color:#94a3b8;margin:1rem 0;font-size:1.1rem;">'
            f'Se encontraron <b style="color:#c4b5fd;">{len(results)}</b> resultados. Selecciona un usuario:'
            f'</div>',
            unsafe_allow_html=True,
        )
        
        # Render results as selectable buttons
        cols_per_row = 3
        for row_start in range(0, len(results), cols_per_row):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                i = row_start + col_idx
                if i >= len(results):
                    break
                r = results[i]
                with cols[col_idx]:
                    avatar_url = r.get("avatar", "")
                    avatar_html = f'<img src="{avatar_url}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;" />' if avatar_url else '<div style="width:40px;height:40px;border-radius:50%;background:#334155;display:flex;align-items:center;justify-content:center;color:#94a3b8;font-size:1.2rem;">?</div>'
                    
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:0.8rem;padding:0.8rem;'
                        f'background:rgba(30,41,59,0.7);border:1px solid rgba(255,255,255,0.08);'
                        f'border-radius:12px;margin-bottom:0.3rem;">'
                        f'{avatar_html}'
                        f'<div><div style="color:#e2e8f0;font-weight:600;">{r["name"]}</div>'
                        f'<div style="color:#64748b;font-size:0.75rem;">{r["id"][:20]}...</div></div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(f"Seleccionar", key=f"sel_{i}", use_container_width=True):
                        select_user(i)
                        st.rerun()

# ──────────────────────────── Main Dashboard ─────────────────────────
elif st.session_state.user_id:
    metrics = get_metrics(st.session_state.user_id, st.session_state.platform_key)
    badge_class = platform_info["badge"]
    main_count = metrics.get("main", 0)
    prev_count = st.session_state.prev_count
    
    # Header
    st.markdown(
        f'<div style="text-align:center;margin-bottom:0.5rem;">'
        f'<span class="live-dot"></span>'
        f'<span style="color:#ef4444;font-weight:600;font-size:0.85rem;letter-spacing:2px;">EN VIVO</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    
    # Counter box
    avatar_html = ""
    if st.session_state.user_avatar:
        avatar_html = f'<img src="{st.session_state.user_avatar}" class="avatar-img" />'
    
    digits_html = render_animated_digits(main_count, prev_count)
    
    st.markdown(
        f'<div class="counter-box">'
        f'<span class="platform-badge {badge_class}">{selected_platform.split("—")[0].strip()}</span>'
        f'{avatar_html}'
        f'<div class="user-name">{st.session_state.user_name}</div>'
        f'{digits_html}'
        f'<div class="counter-label">{metrics.get("label", "")}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    
    # Update previous count for next cycle
    st.session_state.prev_count = main_count
    
    # Extra metrics
    extra = metrics.get("extra", {})
    if extra:
        cols = st.columns(len(extra))
        for i, (label, value) in enumerate(extra.items()):
            with cols[i]:
                val_formatted = f"{value:,}".replace(",", ".")
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-value">{val_formatted}</div>'
                    f'<div class="metric-label">{label}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
    
    # Error display
    if "error" in metrics:
        st.warning(f"⚠️ Error al obtener datos: {metrics['error']}")
    
    # Back button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Cambiar Usuario", use_container_width=False):
        st.session_state.user_id = None
        st.session_state.show_results = True
        st.session_state.prev_count = 0
        st.rerun()
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_rate)
        st.rerun()
else:
    # Welcome screen
    st.markdown(
        '<div style="text-align:center;padding:6rem 2rem;">'
        '<div style="font-size:4rem;margin-bottom:1rem;">📊</div>'
        '<div style="color:#94a3b8;font-size:1.3rem;font-weight:300;">'
        'Selecciona una plataforma y busca un usuario<br>para ver sus estadísticas en tiempo real.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
