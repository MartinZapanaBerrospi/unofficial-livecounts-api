import streamlit as st
import time
import plotly.graph_objects as go
from datetime import datetime
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
# Load Material Symbols & Outfit Font
st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,1,0" />
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

html, body, [class*="st-"] { font-family: 'Outfit', sans-serif; }
.stApp { background: radial-gradient(circle at top right, #1e293b, #0f172a 60%); }
#MainMenu, footer, header { visibility: hidden; }

/* Dashboard Container */
.main-container { padding: 1rem 3rem; }

/* Counter Box (Glassmorphism & Depth) */
.counter-box {
    background: linear-gradient(145deg, rgba(30,41,59,0.4), rgba(15,23,42,0.6));
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 32px;
    padding: 3rem 2rem 2.5rem;
    text-align: center;
    backdrop-filter: blur(20px);
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5), inset 0 1px 1px rgba(255,255,255,0.1);
    margin: 1rem 0;
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.digits-row { display: flex; justify-content: center; align-items: center; gap: 6px; margin: 1rem 0; }
.digit-cell {
    display: inline-flex; align-items: center; justify-content: center;
    width: 70px; height: 100px;
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 18px;
    font-size: 4.5rem; font-weight: 800; color: #f8fafc;
    font-variant-numeric: tabular-nums;
    box-shadow: 0 10px 20px rgba(0,0,0,0.6), inset 0 2px 2px rgba(255,255,255,0.05);
}
.digit-cell.up { animation: glow-up 0.8s ease; }
.digit-cell.down { animation: glow-down 0.8s ease; }
@keyframes glow-up {
    0% { transform: scale(1); border-color: rgba(255,255,255,0.15); }
    50% { transform: scale(1.05); border-color: #4ade80; color: #4ade80; box-shadow: 0 0 30px rgba(74,222,128,0.4); }
    100% { transform: scale(1); border-color: rgba(255,255,255,0.15); }
}
@keyframes glow-down {
    0% { transform: scale(1); border-color: rgba(255,255,255,0.15); }
    50% { transform: scale(1.05); border-color: #f87171; color: #f87171; box-shadow: 0 0 30px rgba(248,113,113,0.4); }
    100% { transform: scale(1); border-color: rgba(255,255,255,0.15); }
}
.digit-sep { font-size: 3.5rem; font-weight: 800; color: #475569; padding: 0 4px; }

.diff-badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 0.4rem 1.2rem; border-radius: 99px;
    font-size: 1.1rem; font-weight: 800; margin-top: 1rem;
    backdrop-filter: blur(8px);
}
.diff-up   { background: rgba(74,222,128,0.1); color: #4ade80; border: 1px solid rgba(74,222,128,0.2); }
.diff-down { background: rgba(248,113,113,0.1); color: #f87171; border: 1px solid rgba(248,113,113,0.2); }

.counter-label {
    color: #94a3b8; font-size: 1.6rem; margin-top: 1rem;
    text-transform: uppercase; letter-spacing: 6px; font-weight: 800;
}
.user-name { color: #f8fafc; font-size: 2.8rem; font-weight: 800; margin-bottom: 0.2rem; }
.user-handle { color: #818cf8; font-size: 1.4rem; font-weight: 600; margin-bottom: 1rem; display: flex; align-items: center; justify-content: center; gap: 8px; }

/* Metric Cards (3D & Float) */
.metric-card {
    background: rgba(30,41,59,0.5);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px; padding: 2rem; 
    text-align: center;
    backdrop-filter: blur(10px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    cursor: default;
}
.metric-card:hover {
    transform: translateY(-8px) perspective(1000px) rotateX(5deg);
    border-color: rgba(255,255,255,0.2);
    box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    background: rgba(51,65,85,0.6);
}
.metric-value { font-size: 2.2rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.5rem; letter-spacing: -1px; }
.metric-label {
    color: #94a3b8; font-size: 0.9rem; text-transform: uppercase;
    letter-spacing: 2px; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 10px;
}
.metric-icon { 
    font-size: 1.8rem; vertical-align: middle; 
    transition: transform 0.3s ease;
}
.metric-card:hover .metric-icon { transform: scale(1.2) rotate(10deg); color: #f8fafc; }

/* Sidebar Premium styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.05);
    backdrop-filter: blur(15px);
}
section[data-testid="stSidebar"] > div { padding-top: 2rem; }

.search-btn-container .stButton > button {
    border-radius: 12px; height: 3.5rem; font-weight: 700; letter-spacing: 1px;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    border: none; color: white; transition: all 0.3s;
}
.search-btn-container .stButton > button:hover {
    transform: translateY(-2px); box-shadow: 0 10px 20px rgba(99,102,241,0.4);
}

.platform-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 0.5rem 1.4rem; border-radius: 99px;
    font-size: 0.8rem; font-weight: 800; text-transform: uppercase;
    letter-spacing: 2.5px; margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.badge-youtube { background: linear-gradient(90deg, #ef4444, #991b1b); color: white; }
.badge-tiktok  { background: linear-gradient(90deg, #00f2ea, #00b8b2); color: white; }

.live-dot {
    display: inline-block; width: 14px; height: 14px;
    background: #ef4444; border-radius: 50%; margin-right: 12px;
    animation: pulse 2s infinite; vertical-align: middle;
}
@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239,68,68,0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 15px rgba(239,68,68,0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239,68,68,0); }
}

.avatar-img {
    width: 120px; height: 120px; border-radius: 50%;
    border: 6px solid rgba(255,255,255,0.1);
    object-fit: cover; margin: 0 auto 1.5rem; display: block;
    box-shadow: 0 15px 35px rgba(0,0,0,0.7);
    transition: transform 0.5s;
}
.counter-box:hover .avatar-img { transform: scale(1.05) rotate(5deg); }

/* Animation for the chart container */
.stPlotlyChart { 
    background: rgba(15,23,42,0.4) !important;
    border-radius: 24px; padding: 1rem;
    border: 1px solid rgba(255,255,255,0.05);
}

/* Material Symbols CSS */
.material-symbols-rounded {
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────── Platforms ───────────────────────────────
PLATFORMS = {
    "🔴 YouTube — Suscriptores": {"key": "yt_subs", "badge": "badge-youtube", "label": "SUSCRIPTORES", "color": "#ff4444", "icon": "subscriptions"},
    "🔴 YouTube — Vistas de Video": {"key": "yt_views", "badge": "badge-youtube", "label": "VISTAS", "color": "#ff4444", "icon": "visibility"},
    "🎵 TikTok — Seguidores": {"key": "tt_followers", "badge": "badge-tiktok", "label": "SEGUIDORES", "color": "#00f2ea", "icon": "music_note"},
}

# ──────────────────────────── Sidebar ────────────────────────────────
with st.sidebar:
    st.markdown('<div style="text-align:center;"><h1 style="font-weight:800;font-size:1.8rem;color:#f8fafc;display:flex;align-items:center;justify-content:center;gap:15px;"><span class="material-symbols-rounded" style="font-size:2.5rem;color:#818cf8;">monitoring</span>Livecounts Pro</h1></div>', unsafe_allow_html=True)
    st.markdown("<div style='margin:2rem 0;'></div>", unsafe_allow_html=True)
    
    st.markdown("### 🛠️ CONFIGURACIÓN")
    selected_platform = st.selectbox("Plataforma", list(PLATFORMS.keys()), index=0)
    platform_info = PLATFORMS[selected_platform]
    
    query = st.text_input("BUSCAR USUARIO O CANAL", placeholder="Ej: Cristiano", help="Escribe el nombre o ID para buscar")
    
    st.markdown('<div class="search-btn-container">', unsafe_allow_html=True)
    search_btn = st.button("OBTENER DATOS EN VIVO", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:4rem; text-align:center; opacity:0.3; font-size:0.7rem;'>UNO-API v2.0 • 2026</div>", unsafe_allow_html=True)

# ──────────────────────────── State ──────────────────────────────────
defaults = {
    "user_id": None, "user_name": "", "user_avatar": "", "user_handle": "",
    "platform_key": "", "prev_count": 0,
    "search_results": [], "show_results": False,
    "history_times": [], "history_values": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────── Helpers ────────────────────────────────
def fmt(n):
    return f"{int(n):,}".replace(",", ".")

def render_digits(current: int, previous: int) -> str:
    c, p = str(current), str(previous) if previous else str(current)
    m = max(len(c), len(p))
    c, p = c.zfill(m), p.zfill(m)
    diff = current - previous
    cells, cnt = [], 0
    for i, (cd, pd) in enumerate(zip(c, p)):
        if cnt > 0 and (m - i) % 3 == 0:
            cells.append('<span class="digit-sep">.</span>')
        cls = "digit-cell" + (" up" if cd != pd and diff > 0 else " down" if cd != pd else "")
        cells.append(f'<span class="{cls}">{cd}</span>')
        cnt += 1
    badge = ""
    if previous and diff != 0:
        sign = "+" if diff > 0 else ""
        icon = "trending_up" if diff > 0 else "trending_down"
        bcls = "diff-up" if diff > 0 else "diff-down"
        badge = f'<div><span class="diff-badge {bcls}"><span class="material-symbols-rounded" style="font-size:1.2rem;">{icon}</span> {sign}{fmt(diff)}</span></div>'
    return f'<div class="digits-row">{"".join(cells)}</div>{badge}'

def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip('#')
    if len(h) == 3: h = ''.join([c*2 for c in h])
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def build_chart(times: list, values: list, color: str, label: str) -> go.Figure:
    fill_rgba = _hex_to_rgba(color, 0.2)
    v_min, v_max = min(values), max(values)
    span = max(v_max - v_min, 1)
    y_lo, y_hi = v_min - span*0.2, v_max + span*0.2

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=[y_lo] * len(times), mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
    fig.add_trace(go.Scatter(
        x=times, y=values, mode='lines',
        line=dict(color=color, width=5, shape='spline', smoothing=0.9),
        fill='tonexty', fillcolor=fill_rgba,
        hovertemplate=f"<b>{label}</b>: %{{y:,.0f}}<br>%{{x}}<extra></extra>",
        showlegend=False,
    ))
    fig.update_layout(
        height=380, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit", color="#94a3b8", size=12),
        xaxis=dict(showgrid=False, zeroline=False, linecolor="rgba(255,255,255,0.05)", tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)", zeroline=False, linecolor="rgba(255,255,255,0.05)", range=[y_lo, y_hi], tickfont=dict(size=10), tickformat=","),
    )
    return fig

# ──────────────────────────── Search ─────────────────────────────────
def do_search(q, pk):
    results = []
    try:
        if pk in ("yt_subs", "yt_views"):
            fn = api.youtube.find_channel if pk == "yt_subs" else api.youtube.find_video
            results = [{"id": r.get("id",""), "name": r.get("name",""), "avatar": r.get("avatar","")} for r in fn(q)]
        elif pk == "tt_followers":
            results = [{"id": r.user_id, "handle": r.username, "name": r.display_name, "avatar": r.thumbnail} for r in api.tiktok.find_user(q)]
    except Exception as e:
        st.error(f"Error de búsqueda: {e}"); return
    st.session_state.update(search_results=results, show_results=True, platform_key=pk, user_id=None, prev_count=0, history_times=[], history_values=[])

def select_user(idx):
    r = st.session_state.search_results[idx]
    st.session_state.update(user_id=r["id"], user_name=r["name"], user_avatar=r.get("avatar",""), user_handle=r.get("handle",""), show_results=False, prev_count=0, history_times=[], history_values=[])

def get_metrics(uid, pk):
    try:
        if pk == "yt_subs":
            raw = send_request(f"{YOUTUBE_CHANNEL_STATS_API}/{uid}")
            subs = raw.get("followerCount", 0)
            b = raw.get("bottomOdos", [0, 0, 0, 0])
            return {"main": subs, "label": "SUSCRIPTORES",
                    "extra": [{"val": b[0] if len(b) > 0 else 0, "lbl": "TOTAL VIEWS", "ico": "visibility"},
                              {"val": b[2] if len(b) > 2 else 0, "lbl": "VIDEOS", "ico": "movie_filter"},
                              {"val": _goal(subs), "lbl": "MÉTA", "ico": "ads_click"}]}
        elif pk == "yt_views":
            raw = send_request(f"{YOUTUBE_VIDEO_STATS_API}/{uid}")
            views = raw.get("followerCount", 0)
            b = raw.get("bottomOdos", [0, 0, 0])
            return {"main": views, "label": "VISTAS",
                    "extra": [{"val": b[0] if len(b) > 0 else 0, "lbl": "LIKES", "ico": "thumb_up"},
                              {"val": b[2] if len(b) > 2 else 0, "lbl": "COMENTARIOS", "ico": "chat_bubble"}]}
        elif pk == "tt_followers":
            m = api.tiktok.fetch_user_metrics(uid)
            return {"main": m["followers"], "label": "SEGUIDORES",
                    "extra": [{"val": m.get("likes",0), "lbl": "LIKES", "ico": "favorite"},
                              {"val": m.get("following",0), "lbl": "SIGUIENDO", "ico": "group"},
                              {"val": m.get("videos",0), "lbl": "VIDEOS", "ico": "video_library"}]}
    except Exception as e:
        return {"main": 0, "label": "ERROR", "error": str(e)}
    return {"main": 0, "label": "—"}

def _goal(n):
    if n <= 0: return 1000
    n_int = int(n)
    mag = 10 ** (len(str(n_int)) - 1)
    if mag == 0: mag = 1
    return ((n_int // mag) + 1) * mag

# ──────────────────────────── Logic ──────────────────────────────────
if search_btn and query:
    do_search(query, platform_info["key"])

if st.session_state.show_results and not st.session_state.user_id:
    st.markdown('<div style="text-align:center;margin:3rem 0;">', unsafe_allow_html=True)
    for i, r in enumerate(st.session_state.search_results):
        if st.button(f"{r['name']} ({r.get('handle', r['id'][:10])})", key=f"sel_{i}", use_container_width=True):
            select_user(i); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.user_id:
    metrics = get_metrics(st.session_state.user_id, st.session_state.platform_key)
    main_count = metrics.get("main", 0)
    
    # History
    st.session_state.history_times.append(datetime.now().strftime("%H:%M:%S"))
    st.session_state.history_values.append(main_count)
    if len(st.session_state.history_times) > 120:
        st.session_state.history_times = st.session_state.history_times[-120:]
        st.session_state.history_values = st.session_state.history_values[-120:]

    # Layout
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<div style="text-align:center;margin-bottom:1rem;"><span class="live-dot"></span><span style="color:#ef4444;font-weight:900;letter-spacing:5px;font-size:1rem;">LIVE STREAM DATA</span></div>', unsafe_allow_html=True)
    
    avatar_html = f'<img src="{st.session_state.user_avatar}" class="avatar-img" />' if st.session_state.user_avatar else ""
    handle_txt = f'@{st.session_state.user_handle}' if st.session_state.user_handle else ""
    icon_txt = "music_note" if st.session_state.platform_key.startswith("tt") else "verified"
    handle_html = f'<div class="user-handle"><span class="material-symbols-rounded" style="font-size:1.4rem;">{icon_txt}</span> {handle_txt}</div>' if handle_txt else ""

    st.markdown(
        f'<div class="counter-box">'
        f'<span class="platform-badge {platform_info["badge"]}"><span class="material-symbols-rounded" style="font-size:1.2rem;">{platform_info["icon"]}</span> {selected_platform.split("—")[0].strip()}</span>'
        f'{avatar_html}'
        f'<div class="user-name">{st.session_state.user_name}</div>'
        f'{handle_html}'
        f'{render_digits(main_count, st.session_state.prev_count)}'
        f'<div class="counter-label">{metrics.get("label","")}</div>'
        f'</div>', unsafe_allow_html=True)
    
    st.session_state.prev_count = main_count

    # Metric Cards
    extra = metrics.get("extra", [])
    if extra:
        st.markdown("<div style='margin:2rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(len(extra))
        for i, item in enumerate(extra):
            with cols[i]:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-value">{fmt(item["val"])}</div>'
                    f'<div class="metric-label">'
                    f'<span class="material-symbols-rounded metric-icon">{item["ico"]}</span>'
                    f'{item["lbl"]}</div>'
                    f'</div>', unsafe_allow_html=True)

    # Chart Section
    if len(st.session_state.history_values) >= 2:
        st.markdown("<div style='margin-top:3rem;'></div>", unsafe_allow_html=True)
        st.plotly_chart(build_chart(st.session_state.history_times, st.session_state.history_values, platform_info["color"], metrics.get("label", "Count")), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:2rem; text-align:center;'>", unsafe_allow_html=True)
    if st.button("🔄 CAMBIAR DE CANAL / USUARIO", use_container_width=False, type="secondary"):
        st.session_state.update(user_id=None, show_results=True, prev_count=0, history_times=[], history_values=[])
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    time.sleep(2); st.rerun()
else:
    st.markdown('<div style="text-align:center;padding:12rem 2rem;"><div style="font-size:8rem;margin-bottom:3rem;filter: drop-shadow(0 0 20px rgba(99,102,241,0.5));">📊</div><div style="color:#f8fafc;font-size:2.2rem;font-weight:800;margin-bottom:1rem;">Analítica en Tiempo Real</div><div style="color:#94a3b8;font-size:1.4rem;font-weight:300;">Selecciona una plataforma en el panel lateral para comenzar el monitoreo.</div></div>', unsafe_allow_html=True)
