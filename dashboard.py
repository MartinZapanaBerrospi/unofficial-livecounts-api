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
    page_title="Livecounts Elite Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────── Elite UI CSS ───────────────────────────
CSS = (
    "font-family:'Outfit',sans-serif; .stApp{background:#020617} "
    "#MainMenu,footer,header{visibility:hidden} .main-container{padding:2rem 5vw;max-width:1200px;margin:0 auto} "
    ".hero-section{text-align:center;padding:10vh 0} "
    ".hero-title{font-size:clamp(2.5rem,6vw,5rem);font-weight:900;letter-spacing:-3px;color:white;margin-bottom:1rem;line-height:1} "
    ".hero-subtitle{color:#64748b;font-size:1.2rem;margin-bottom:4rem;font-weight:300;letter-spacing:1px} "
    ".search-card{background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.08);border-radius:24px;padding:8px; "
    "display:flex;align-items:center;gap:8px;max-width:900px;margin:0 auto;box-shadow:0 30px 60px rgba(0,0,0,0.5);backdrop-filter:blur(20px)} "
    ".search-input{flex:1;background:transparent!important;border:none!important;color:white!important;font-size:1.1rem!important;padding:0 20px!important} "
    ".platform-select{width:200px!important;background:transparent!important;border:none!important;border-right:1px solid rgba(255,255,255,0.1)!important} "
    ".elite-btn{background:linear-gradient(135deg,#6366f1,#a855f7)!important;border:none!important;border-radius:16px!important; "
    "color:white!important;font-weight:800!important;padding:12px 24px!important;transition:all 0.3s!important;height:54px!important} "
    ".elite-btn:hover{transform:translateY(-2px);box-shadow:0 10px 20px rgba(99,102,241,0.3)!important} "
    ".counter-box{background:rgba(15,23,42,0.5);border:1px solid rgba(255,255,255,0.05);border-radius:40px;padding:4rem 2rem; "
    "text-align:center;box-shadow:0 40px 100px rgba(0,0,0,0.8);backdrop-filter:blur(30px);margin-bottom:3rem} "
    ".digits-row{display:flex;justify-content:center;align-items:center;gap:clamp(4px,1vw,12px);margin:1.5rem 0;flex-wrap:wrap} "
    ".digit-cell{display:inline-flex;align-items:center;justify-content:center;width:clamp(45px,8vw,85px);height:clamp(70px,12vw,130px); "
    "background:#0f172a;border:1px solid rgba(255,255,255,0.15);border-radius:clamp(12px,2vw,28px);font-size:clamp(3rem,6vw,7rem);font-weight:900;color:#f8fafc; "
    "font-variant-numeric:tabular-nums;box-shadow:inset 4px 4px 10px #01040a,inset -4px -4px 10px #030a1c,0 15px 35px rgba(0,0,0,0.8)} "
    ".metric-card{background:rgba(30,41,59,0.3);border:1px solid rgba(255,255,255,0.05);border-radius:28px;padding:2rem;text-align:center;transition:all 0.4s} "
    ".metric-card:hover{transform:translateY(-10px);border-color:rgba(129,140,248,0.3);background:rgba(30,41,59,0.5)} "
    ".icon-3d{font-size:2.5rem!important;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
    "filter:drop-shadow(0 4px 10px rgba(0,0,0,0.5))} @media(max-width:768px){.search-card{flex-direction:column;padding:12px} .platform-select{width:100%!important;border-right:none!important;border-bottom:1px solid rgba(255,255,255,0.1)!important}}"
)

st.markdown(f"<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@48,700,1,0' /><style>{CSS}</style>", unsafe_allow_html=True)

# ──────────────────────────── PLATFORMS ──────────────────────────────
PLATFORMS = {
    "🔴 YouTube Subs": {"key": "yt_subs", "color": "#ef4444", "icon": "subscriptions", "label": "SUSCRIPTORES"},
    "🔴 YouTube Views": {"key": "yt_views", "color": "#ef4444", "icon": "video_library", "label": "VISTAS"},
    "🎵 TikTok Follows": {"key": "tt_followers", "color": "#00f2ea", "icon": "music_note", "label": "SEGUIDORES"},
}

# ──────────────────────────── HELPERS ────────────────────────────────
def fmt(n): return f"{int(n):,}".replace(",", ".")

def fetch_live_data(uid, pk):
    try:
        if pk == "yt_subs":
            r = send_request(f"{YOUTUBE_CHANNEL_STATS_API}/{uid}")
            val = r.get("followerCount", 0)
            b = r.get("bottomOdos", [0,0,0,0])
            return {"main": val, "extra": [{"v": b[0], "l": "CANAL VISTAS", "i": "visibility"}, {"v": b[2], "l": "VIDEOS", "i": "movie_filter"}, {"v": _goal(val), "l": "META", "i": "stars"}]}
        elif pk == "yt_views":
            r = send_request(f"{YOUTUBE_VIDEO_STATS_API}/{uid}")
            val = r.get("followerCount", 0)
            b = r.get("bottomOdos", [0,0,0,0])
            return {"main": val, "extra": [{"v": b[0], "l": "LIKES", "i": "favorite"}, {"v": b[1] if len(b)>1 else 0, "l": "DISLIKES", "i": "thumb_down"}, {"v": b[2] if len(b)>2 else 0, "l": "COMMENTS", "i": "forum"}]}
        elif pk == "tt_followers":
            m = api.tiktok.fetch_user_metrics(uid)
            return {"main": m["followers"], "extra": [{"v": m["likes"], "l": "LIKES", "i": "favorite"}, {"v": m["following"], "l": "SIGUIENDO", "i": "group"}, {"v": m["videos"], "l": "VIDEOS", "i": "video_library"}]}
    except: return {"error": "Conexión perdida"}
def _goal(n):
    if not n: return 1000
    mag = 10 ** (len(str(int(n))) - 1)
    return ((int(n) // mag) + 1) * mag

# ──────────────────────────── STATE ──────────────────────────────────
# Handle Query Params
params = st.query_params
q_id = params.get("id")
q_pk = params.get("p")

if q_id and q_pk and "user_id" not in st.session_state:
    st.session_state.user_id = q_id
    st.session_state.platform_key = q_pk
    # We don't have name/avatar from URL, so we'll fetch them if needed or use ID
    st.session_state.user_name = params.get("n", q_id[:10])
    st.session_state.user_avatar = params.get("a", "")
    st.session_state.user_handle = params.get("h", "")

defaults = {"user_id": None, "user_name": "", "user_avatar": "", "user_handle": "", "platform_key": "", "prev_count": 0, "search_results": [], "show_results": False, "history_times": [], "history_values": []}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# ──────────────────────────── LOGIC ──────────────────────────────────
def set_user_params(rid, rpk, rname, ravatar="", rhandle=""):
    st.query_params.update(id=rid, p=rpk, n=rname, a=ravatar, h=rhandle)
    st.session_state.update(user_id=rid, platform_key=rpk, user_name=rname, user_avatar=ravatar, user_handle=rhandle, show_results=False, prev_count=0, history_times=[], history_values=[])

def clear_params():
    st.query_params.clear()
    st.session_state.update(user_id=None, show_results=False, prev_count=0, history_times=[], history_values=[])

# ──────────────────────────── UI ─────────────────────────────────────
if st.session_state.show_results and not st.session_state.user_id:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:white;text-align:center;margin-bottom:2rem;font-weight:900;">RESULTADOS HALLADOS</h2>', unsafe_allow_html=True)
    for i, r in enumerate(st.session_state.search_results):
        rid = r.get("id") if isinstance(r, dict) else r.user_id
        rname = r.get("name") if isinstance(r, dict) else r.display_name
        ravatar = r.get("avatar") if isinstance(r, dict) else r.thumbnail
        rhandle = r.get("handle") if isinstance(r, dict) else r.username
        if st.button(f"🚀 {rname} (@{rhandle})", key=f"r_{i}", use_container_width=True):
            set_user_params(rid, st.session_state.platform_key, rname, ravatar, rhandle); st.rerun()
    if st.button("⬅️ VOLVER AL INICIO", use_container_width=True): clear_params(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.user_id:
    data = fetch_live_data(st.session_state.user_id, st.session_state.platform_key)
    if "error" in data: st.error(data["error"]); time.sleep(3); st.rerun()
    
    count = data["main"]
    st.session_state.history_times.append(datetime.now().strftime("%H:%M:%S"))
    st.session_state.history_values.append(count)
    if len(st.session_state.history_times) > 100: st.session_state.history_times, st.session_state.history_values = st.session_state.history_times[-100:], st.session_state.history_values[-100:]

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Dashboard Header
    c1, c2 = st.columns([1, 1])
    with c1: st.markdown(f'<div style="color:#64748b;font-weight:900;letter-spacing:4px;font-size:0.9rem;"><span style="color:#f43f5e">●</span> LIVE FEED</div>', unsafe_allow_html=True)
    with c2: 
        if st.button("🔄 CAMBIAR", use_container_width=False): clear_params(); st.rerun()

    avatar = f'<img src="{st.session_state.user_avatar}" style="width:120px;height:120px;border-radius:50%;border:4px solid rgba(255,255,255,0.1);margin:0 auto 2rem;display:block;" />' if st.session_state.user_avatar else ""
    handle = f'<div style="color:#818cf8;font-size:1.2rem;font-weight:700;margin-bottom:1rem;">@{st.session_state.user_handle}</div>' if st.session_state.user_handle else ""

    pk_label = PLATFORMS[[k for k,v in PLATFORMS.items() if v["key"]==st.session_state.platform_key][0]]["label"]
    
    st.markdown(f'<div class="counter-box">{avatar}<h1 style="color:white;font-size:3.5rem;font-weight:900;letter-spacing:-2px;margin-bottom:0.5rem;">{st.session_state.user_name}</h1>{handle}', unsafe_allow_html=True)
    
    # Digits (Simplified for ELITE look)
    c_str = str(count)
    cells = []
    for i, digit in enumerate(c_str):
        if i > 0 and (len(c_str) - i) % 3 == 0: cells.append('<span class="digit-sep">.</span>')
        cells.append(f'<span class="digit-cell">{digit}</span>')
    st.markdown(f'<div class="digits-row">{"".join(cells)}</div><div style="color:#64748b;font-size:1.8rem;font-weight:900;letter-spacing:10px;margin-top:2rem;">{pk_label} TOTAL</div></div>', unsafe_allow_html=True)
    
    # Extra Metrics
    if data.get("extra"):
        cols = st.columns(len(data["extra"]))
        for i, itm in enumerate(data["extra"]):
            with cols[i]: st.markdown(f'<div class="metric-card"><div class="metric-value">{fmt(itm["v"])}</div><div class="metric-label"><span class="material-symbols-rounded icon-3d">{itm["i"]}</span> {itm["l"]}</div></div>', unsafe_allow_html=True)

    # Chart
    pcolor = PLATFORMS[[k for k,v in PLATFORMS.items() if v["key"]==st.session_state.platform_key][0]]["color"]
    v_min, v_max = min(st.session_state.history_values), max(st.session_state.history_values)
    span = max(v_max - v_min, 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.history_times, y=st.session_state.history_values, mode='lines', line=dict(color=pcolor, width=6, shape='spline'), fill='tonexty', fillcolor=f"rgba({int(pcolor[1:3],16)},{int(pcolor[3:5],16)},{int(pcolor[5:7],16)},0.1)", showlegend=False))
    fig.update_layout(height=450, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", color="#334155"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.02)", range=[v_min - span*0.1, v_max + span*0.1], tickformat=","))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    time.sleep(2); st.rerun()

else:
    # HERO SECTION (RE-DESIGNED)
    st.markdown('<div class="main-container"><div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Livecounts Elite</h1><p class="hero-subtitle">Métrica en tiempo real para creadores de alto impacto.</p>', unsafe_allow_html=True)
    
    # Integrated Search Bar
    with st.container():
        st.markdown('<div class="search-card">', unsafe_allow_html=True)
        cols = st.columns([1, 2, 0.8])
        with cols[0]: h_pk = st.selectbox("P", list(PLATFORMS.keys()), key="h_pk", label_visibility="collapsed")
        with cols[1]: h_q = st.text_input("Q", placeholder="Buscar canal o video...", key="h_q", label_visibility="collapsed")
        with cols[2]: 
            if st.button("BUSCAR ⚡", use_container_width=True, type="primary"):
                if h_q:
                    try:
                        pk = PLATFORMS[h_pk]["key"]
                        if pk.startswith("yt"): res = (api.youtube.find_channel(h_q) if pk=="yt_subs" else api.youtube.find_video(h_q))
                        else: res = [{"user_id": r.user_id, "id": r.username, "name": r.display_name, "avatar": r.thumbnail} for r in api.tiktok.find_user(h_q)]
                        st.session_state.update(search_results=res, show_results=True, platform_key=pk)
                        st.rerun()
                    except: st.error("Error en búsqueda")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;color:#1e293b;font-weight:900;font-size:6rem;margin-top:5vh;opacity:0.2;">LIVE ANALYTICS</div>', unsafe_allow_html=True)
