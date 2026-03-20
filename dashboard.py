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
CSS = """
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@48,400,1,0" />
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

html, body, [class*="st-"] { font-family: 'Outfit', sans-serif; }
.stApp { background: radial-gradient(circle at top right, #1e293b, #020617 90%); }
#MainMenu, footer, header { visibility: hidden; }

/* Responsive Dashboard Container */
.main-container { padding: 1rem 5vw; max-width: 1400px; margin: 0 auto; }

/* Counter Box (Glassmorphism & Adaptive) */
.counter-box {
    background: linear-gradient(145deg, rgba(30,41,59,0.3), rgba(15,23,42,0.5));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 40px; padding: clamp(2rem, 5vw, 4rem) 2rem;
    text-align: center; backdrop-filter: blur(30px);
    box-shadow: 0 40px 100px -20px rgba(0,0,0,0.7); margin: 1.5rem 0;
}

.digits-row { display: flex; justify-content: center; align-items: center; gap: clamp(2px, 0.5vw, 8px); margin: 1rem 0; flex-wrap: wrap; }
.digit-cell {
    display: inline-flex; align-items: center; justify-content: center;
    width: clamp(40px, 8vw, 80px); height: clamp(60px, 12vw, 120px);
    background: #0f172a; border: 1px solid rgba(255,255,255,0.1);
    border-radius: clamp(10px, 2vw, 24px); 
    font-size: clamp(2.5rem, 6vw, 6rem); font-weight: 800; color: #f8fafc;
    font-variant-numeric: tabular-nums; box-shadow: 0 10px 30px rgba(0,0,0,0.8);
}
.digit-sep { font-size: clamp(2rem, 4vw, 4rem); font-weight: 800; color: #334155; }

.metric-card {
    background: rgba(30,41,59,0.4); border: 1px solid rgba(255,255,255,0.05);
    border-radius: 32px; padding: clamp(1.5rem, 3vw, 2.5rem); text-align: center;
    box-shadow: 0 20px 40px rgba(0,0,0,0.4); transition: all 0.4s;
    transform-style: preserve-3d; margin-bottom: 1rem;
}
.metric-card:hover {
    transform: translateY(-10px) perspective(1000px) rotateX(10deg);
    border-color: rgba(255,255,255,0.15); box-shadow: 0 40px 80px rgba(0,0,0,0.6);
}
.metric-value { font-size: clamp(1.8rem, 3vw, 2.8rem); font-weight: 800; color: #f8fafc; }
.metric-label { color: #64748b; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 2px; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 8px; }

/* Sidebar Premium styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617 0%, #0f172a 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* Sidebar Toggle Hint */
[data-testid="stSidebarNav"] { display: none; }
button[kind="header"] { 
    background: rgba(129,140,248,0.2) !important; 
    border: 1px solid rgba(129,140,248,0.4) !important;
    border-radius: 50% !important; margin: 10px !important;
    width: 50px !important; height: 50px !important;
}

/* Landing Page Search */
.hero-search-box {
    background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 40px; padding: 4rem 2rem; text-align: center;
    backdrop-filter: blur(20px); max-width: 800px; margin: 0 auto;
    box-shadow: 0 50px 100px rgba(0,0,0,0.8);
}
.hero-title { font-size: clamp(2.5rem, 6vw, 4.5rem); font-weight: 900; letter-spacing: -2px; margin-bottom: 0.5rem; background: linear-gradient(135deg, #fff, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

/* Animations */
.live-dot {
    display: inline-block; width: 15px; height: 15px; background: #f43f5e; border-radius: 50%;
    margin-right: 12px; animation: pulse 2s infinite; vertical-align: middle;
}
@keyframes pulse { 0%, 100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(244,63,94,0.7); } 50% { transform: scale(1.1); box-shadow: 0 0 0 20px rgba(244,63,94,0); } }

/* Mobile Adjustments */
@media (max-width: 768px) {
    .main-container { padding: 1rem 1.5rem; }
    .digit-cell { width: 50px; height: 80px; font-size: 3rem; }
    .counter-label { font-size: 1.2rem; letter-spacing: 4px; }
    .user-name { font-size: 2.2rem; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ──────────────────────────── Platforms ───────────────────────────────
PLATFORMS = {
    "🔴 YouTube — Suscriptores": {"key": "yt_subs", "badge": "badge-youtube", "label": "SUSCRIPTORES", "color": "#ef4444", "icon": "subscriptions"},
    "🔴 YouTube — Vistas de Video": {"key": "yt_views", "badge": "badge-youtube", "label": "VISTAS", "color": "#ef4444", "icon": "visibility"},
    "🎵 TikTok — Seguidores": {"key": "tt_followers", "badge": "badge-tiktok", "label": "SEGUIDORES", "color": "#00f2ea", "icon": "music_note"},
}

# ──────────────────────────── Sidebar ────────────────────────────────
with st.sidebar:
    st.markdown('<div style="text-align:center;margin-bottom:3rem;"><span class="material-symbols-rounded" style="font-size:4rem;color:#818cf8;filter:drop-shadow(0 0 15px rgba(129,140,248,0.5));">bubble_chart</span><h2 style="font-weight:900;color:white;margin-top:0.5rem;letter-spacing:-1px;">Livecounts Pro</h2><p style="color:#64748b;font-size:0.75rem;letter-spacing:2px;">ENGINE v3.0</p></div>', unsafe_allow_html=True)
    pk_sidebar = st.selectbox("PLATAFORMA", list(PLATFORMS.keys()), index=0, key="side_pk")
    query_sidebar = st.text_input("BUSCAR USUARIO / ID", placeholder="Ej: Cristiano", key="side_q")
    search_side = st.button("OBTENER DATOS", use_container_width=True, type="primary", key="side_btn")
    st.markdown("<div style='margin-top:10rem;text-align:center;font-size:0.7rem;color:#334155;letter-spacing:1px;'>© 2026 BY PROFESSIONAL SYSTEMS</div>", unsafe_allow_html=True)

# ──────────────────────────── State ──────────────────────────────────
defaults = {"user_id": None, "user_name": "", "user_avatar": "", "user_handle": "", "platform_key": "", "prev_count": 0, "search_results": [], "show_results": False, "history_times": [], "history_values": []}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# ──────────────────────────── Helpers ────────────────────────────────
def fmt(n): return f"{int(n):,}".replace(",", ".")

def render_digits(current: int, previous: int) -> str:
    c, p = str(current), str(previous) if previous else str(current)
    m = max(len(c), len(p))
    c, p = c.zfill(m), p.zfill(m)
    diff, cells = current - previous, []
    # Force stacking on very small screens via container
    for i, (cd, pd) in enumerate(zip(c, p)):
        if i > 0 and (m - i) % 3 == 0: cells.append('<span class="digit-sep">.</span>')
        cls = "digit-cell" + (" up" if cd != pd and diff > 0 else " down" if cd != pd else "")
        cells.append(f'<span class="{cls}">{cd}</span>')
    badge = ""
    if previous and diff != 0:
        sign, icon = ("+", "trending_up") if diff > 0 else ("", "trending_down")
        badge = f'<div><span class="diff-badge {"diff-up" if diff > 0 else "diff-down"}"><span class="material-symbols-rounded" style="font-size:1.4rem;">{icon}</span> {sign}{fmt(diff)}</span></div>'
    return f'<div class="digits-row">{"".join(cells)}</div>{badge}'

def build_chart(times, values, color, label):
    v_min, v_max = min(values), max(values)
    span = max(v_max - v_min, 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=[v_min - span*0.1]*len(times), mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=times, y=values, mode='lines', line=dict(color=color, width=6, shape='spline', smoothing=0.9), fill='tonexty', fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.1)", hovertemplate=f"<b>{label}</b>: %{{y:,.0f}}<extra></extra>", showlegend=False))
    fig.update_layout(height=450, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", color="#334155", size=12), xaxis=dict(showgrid=False, zeroline=False, linecolor="rgba(255,255,255,0.05)"), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.02)", zeroline=False, linecolor="rgba(255,255,255,0.05)", range=[v_min - span*0.1, v_max + span*0.1], tickformat=","))
    return fig

def get_metrics_api(uid, pk):
    try:
        if pk == "yt_subs":
            raw = send_request(f"{YOUTUBE_CHANNEL_STATS_API}/{uid}")
            subs = raw.get("followerCount", 0)
            b = raw.get("bottomOdos", [0,0,0,0])
            return {"main": subs, "label": "SUSCRIPTORES", "extra": [{"val": b[0], "lbl": "TOTAL VIEWS", "ico": "visibility"}, {"val": b[2], "lbl": "VIDEOS", "ico": "movie_filter"}, {"val": _calc_goal(subs), "lbl": "META", "ico": "stars"}]}
        elif pk == "yt_views":
            raw = send_request(f"{YOUTUBE_VIDEO_STATS_API}/{uid}")
            views = raw.get("followerCount", 0)
            b = raw.get("bottomOdos", [0,0,0])
            return {"main": views, "label": "VISTAS", "extra": [{"val": b[0], "lbl": "LIKES", "ico": "favorite"}, {"val": b[1], "lbl": "DISLIKES", "ico": "thumb_down"}, {"val": b[2], "lbl": "COMMENTS", "ico": "chat_bubble"}]}
        elif pk == "tt_followers":
            m = api.tiktok.fetch_user_metrics(uid)
            return {"main": m["followers"], "label": "SEGUIDORES", "extra": [{"val": m.get("likes",0), "lbl": "LIKES", "ico": "favorite"}, {"val": m.get("following",0), "lbl": "SIGUIENDO", "ico": "group"}, {"val": m.get("videos",0), "lbl": "VIDEOS", "ico": "movie"}]}
    except: return {"main": 0, "label": "ERROR"}
    return {"main": 0, "label": "—"}

def _calc_goal(n):
    if not n: return 1000
    mag = 10 ** (len(str(int(n))) - 1)
    return ((int(n) // mag) + 1) * mag

# ──────────────────────────── Logic ──────────────────────────────────
def search_action(q, pk):
    try:
        if pk.startswith("yt"): results = [{"id": r["id"], "name": r["name"], "avatar": r.get("avatar","")} for r in (api.youtube.find_channel(q) if pk=="yt_subs" else api.youtube.find_video(q))]
        elif pk == "tt_followers": results = [{"id": r.user_id, "handle": r.username, "name": r.display_name, "avatar": r.thumbnail} for r in api.tiktok.find_user(q)]
        st.session_state.update(search_results=results, show_results=True, platform_key=pk, user_id=None, prev_count=0, history_times=[], history_values=[])
    except Exception as e: st.error(f"Error: {e}")

# Handle Sidebar Trigger
if search_side and query_sidebar: search_action(query_sidebar, PLATFORMS[pk_sidebar]["key"])

# Main Area Search Result Selection
if st.session_state.show_results and not st.session_state.user_id:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f'<h2 style="text-align:center;color:white;margin-bottom:2rem;">RESULTADOS ENCONTRADOS ({len(st.session_state.search_results)})</h2>', unsafe_allow_html=True)
    for i, r in enumerate(st.session_state.search_results):
        if st.button(f"🚀 {r['name']} ({r.get('handle', r['id'][:10])})", key=f"sel_{i}", use_container_width=True):
            st.session_state.update(user_id=r["id"], user_name=r["name"], user_avatar=r.get("avatar",""), user_handle=r.get("handle",""), show_results=False, prev_count=0, history_times=[], history_values=[]); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Dashboard Display
elif st.session_state.user_id:
    m = get_metrics_api(st.session_state.user_id, st.session_state.platform_key)
    main_count = m.get("main", 0)
    
    st.session_state.history_times.append(datetime.now().strftime("%H:%M:%S"))
    st.session_state.history_values.append(main_count)
    if len(st.session_state.history_times) > 100: st.session_state.history_times, st.session_state.history_values = st.session_state.history_times[-100:], st.session_state.history_values[-100:]

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;margin-bottom:1rem;"><span class="live-dot"></span><span style="color:#f43f5e;font-weight:900;letter-spacing:8px;font-size:1.1rem;">LIVE MONITORING</span></div>', unsafe_allow_html=True)
    
    pinfo = [v for k,v in PLATFORMS.items() if v["key"] == st.session_state.platform_key][0]
    avatar = f'<img src="{st.session_state.user_avatar}" style="width:clamp(80px, 15vw, 130px); height:clamp(80px, 15vw, 130px); border-radius:50%; border:6px solid rgba(255,255,255,0.1); margin: 0 auto 1.5rem; display:block; box-shadow:0 20px 40px rgba(0,0,0,0.8);" />' if st.session_state.user_avatar else ""
    handle = f'<div class="user-handle"><span class="material-symbols-rounded">stars</span> @{st.session_state.user_handle}</div>' if st.session_state.user_handle else ""

    st.markdown(f'<div class="counter-box"><div style="display:flex;justify-content:center;margin-bottom:1.5rem;"><span style="background:rgba(255,255,255,0.05);padding:0.6rem 1.8rem;border-radius:99px;font-weight:900;letter-spacing:3px;font-size:0.8rem;color:#94a3b8;border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;gap:10px;"><span class="material-symbols-rounded" style="color:#818cf8;">{pinfo["icon"]}</span>DATA FEED</span></div>{avatar}<div class="user-name">{st.session_state.user_name}</div>{handle}{render_digits(main_count, st.session_state.prev_count)}<div class="counter-label">{m.get("label","")}</div></div>', unsafe_allow_html=True)
    st.session_state.prev_count = main_count

    extra = m.get("extra", [])
    if extra:
        st.markdown("<div style='margin:2rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(len(extra))
        for i, itm in enumerate(extra):
            with cols[i]: st.markdown(f'<div class="metric-card"><div class="metric-value">{fmt(itm["val"])}</div><div class="metric-label"><span class="material-symbols-rounded" style="font-size:1.8rem;">{itm["ico"]}</span> {itm["lbl"]}</div></div>', unsafe_allow_html=True)

    if len(st.session_state.history_values) >= 2:
        st.plotly_chart(build_chart(st.session_state.history_times, st.session_state.history_values, pinfo["color"], m.get("label","")), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 CAMBIAR DE CANAL / VOLVER", use_container_width=False):
        st.session_state.update(user_id=None, show_results=False, prev_count=0, history_times=[], history_values=[])
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    time.sleep(2); st.rerun()

# Welcome / Central Search Screen
else:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-search-box">'
        '<div class="material-symbols-rounded" style="font-size:8rem;margin-bottom:2rem;background:linear-gradient(135deg, #818cf8, #c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 30px rgba(129,140,248,0.4));">rocket_launch</div>'
        '<h1 class="hero-title">SISTEMA LISTO</h1>'
        '<p style="color:#94a3b8;font-size:1.3rem;margin-bottom:3rem;">Busca un canal o usuario para iniciar el monitoreo en tiempo real.</p>',
        unsafe_allow_html=True
    )
    
    # Hero Search Forms
    c1, c2 = st.columns([1, 2])
    with c1: pk_hero = st.selectbox("PLATAFORMA", list(PLATFORMS.keys()), index=0, key="hero_pk", label_visibility="collapsed")
    with c2: q_hero = st.text_input("NOMBRE O ID", placeholder="Ej: Cristiano", key="hero_q", label_visibility="collapsed")
    
    if st.button("OBTENER DATOS EN VIVO", use_container_width=True, type="primary", key="hero_btn"):
        if q_hero: search_action(q_hero, PLATFORMS[pk_hero]["key"])
        else: st.warning("Escribe algo para buscar")
    
    st.markdown('</div></div>', unsafe_allow_html=True)
