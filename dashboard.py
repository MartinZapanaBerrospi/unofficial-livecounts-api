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
.counter-number {
    font-size: 5rem;
    font-weight: 800;
    background: linear-gradient(to right, #818cf8, #c084fc, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -3px;
    line-height: 1.1;
    font-variant-numeric: tabular-nums;
}
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

# ──────────────────────────── Search Logic ───────────────────────────
def do_search(query: str, platform_key: str):
    """Search for a user and store the first result in session state."""
    try:
        if platform_key == "yt_subs":
            results = api.youtube.find_channel(query)
            if results:
                st.session_state.user_id = results[0]["id"]
                st.session_state.user_name = results[0]["name"]
                st.session_state.user_avatar = results[0].get("avatar", "")
        elif platform_key == "yt_views":
            results = api.youtube.find_video(query)
            if results:
                st.session_state.user_id = results[0]["id"]
                st.session_state.user_name = results[0]["name"]
                st.session_state.user_avatar = results[0].get("avatar", "")
        elif platform_key == "tt_followers":
            results = api.tiktok.find_user(query)
            if results:
                st.session_state.user_id = results[0].user_id
                st.session_state.user_name = results[0].display_name or results[0].username
                st.session_state.user_avatar = results[0].thumbnail
        elif platform_key == "tt_views":
            # For TikTok video views, user provides a video URL/ID
            st.session_state.user_id = query
            st.session_state.user_name = f"Video: {query}"
            st.session_state.user_avatar = ""
        elif platform_key == "tw_followers":
            result = api.twitter.find_user(query)
            if result:
                st.session_state.user_id = result["id"]
                st.session_state.user_name = result["username"]
                st.session_state.user_avatar = result.get("avatar", "")
        elif platform_key == "twitch_followers":
            results = api.twitch.find_user(query)
            if results:
                st.session_state.user_id = results[0]["id"]
                st.session_state.user_name = results[0]["username"]
                st.session_state.user_avatar = results[0].get("avatar", "")
        elif platform_key == "kick_followers":
            results = api.kick.find_user(query)
            if results:
                st.session_state.user_id = results[0]["id"]
                st.session_state.user_name = results[0]["username"]
                st.session_state.user_avatar = results[0].get("avatar", "")
        
        st.session_state.platform_key = platform_key
    except RequestApiError as e:
        st.error(f"Error de búsqueda: {e}")

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

# ──────────────────────────── Main Dashboard ─────────────────────────
if st.session_state.user_id:
    metrics = get_metrics(st.session_state.user_id, st.session_state.platform_key)
    badge_class = platform_info["badge"]
    
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
    
    main_count = metrics.get("main", 0)
    formatted = f"{main_count:,}".replace(",", ".")
    
    st.markdown(
        f'<div class="counter-box">'
        f'<span class="platform-badge {badge_class}">{selected_platform.split("—")[0].strip()}</span>'
        f'{avatar_html}'
        f'<div class="user-name">{st.session_state.user_name}</div>'
        f'<div class="counter-number">{formatted}</div>'
        f'<div class="counter-label">{metrics.get("label", "")}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    
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
