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
    ".hero-section{text-align:center;padding:8vh 0} "
    ".hero-title{font-size:clamp(3rem,8vw,5.5rem);font-weight:900;letter-spacing:-4px;color:white;margin-bottom:1rem;line-height:1} "
    ".hero-subtitle{color:#64748b;font-size:1.3rem;margin-bottom:4rem;font-weight:300;letter-spacing:1px} "
    ".search-card{background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.08);border-radius:32px;padding:12px; "
    "display:flex;align-items:center;gap:12px;max-width:1000px;margin:0 auto;box-shadow:0 40px 80px rgba(0,0,0,0.6);backdrop-filter:blur(30px)} "
    ".search-input{flex:1;background:transparent!important;border:none!important;color:white!important;font-size:1.2rem!important;padding:0 24px!important} "
    ".platform-select{width:240px!important;background:transparent!important;border:none!important;border-right:1px solid rgba(255,255,255,0.1)!important} "
    ".elite-btn{background:linear-gradient(135deg,#6366f1,#a855f7)!important;border:none!important;border-radius:22px!important; "
    "color:white!important;font-weight:900!important;padding:14px 32px!important;transition:all 0.3s!important;height:64px!important;letter-spacing:1px!important} "
    ".elite-btn:hover{transform:translateY(-3px);box-shadow:0 15px 30px rgba(99,102,241,0.4)!important} "
    ".result-card{background:rgba(30,41,59,0.3);border:1px solid rgba(255,255,255,0.05);border-radius:24px;padding:1.5rem;text-align:center; "
    "transition:all 0.3s;cursor:pointer;height:100%} .result-card:hover{background:rgba(30,41,59,0.5);transform:translateY(-5px);border-color:rgba(129,140,248,0.3)} "
    ".result-avatar{width:100px;height:100px;border-radius:50%;margin:0 auto 1.2rem;border:4px solid rgba(255,255,255,0.1);display:block} "
    ".result-name{color:white;font-weight:900;font-size:1.3rem;margin-bottom:0.3rem;line-height:1.2} "
    ".result-handle{color:#818cf8;font-weight:700;font-size:0.9rem;letter-spacing:1px} "
    ".counter-box{background:rgba(15,23,42,0.5);border:1px solid rgba(255,255,255,0.05);border-radius:48px;padding:5rem 2.5rem;text-align:center;backdrop-filter:blur(30px)} "
    ".digits-row{display:flex;justify-content:center;align-items:center;gap:clamp(4px,1vw,14px);margin:2rem 0;flex-wrap:wrap} "
    ".digit-cell{display:inline-flex;align-items:center;justify-content:center;width:clamp(55px,9vw,95px);height:clamp(85px,14vw,145px); "
    "background:#0f172a;border:1px solid rgba(255,255,255,0.15);border-radius:clamp(16px,2vw,36px);font-size:clamp(4rem,7vw,8.5rem);font-weight:900;color:#f8fafc; "
    "font-variant-numeric:tabular-nums;box-shadow:inset 5px 5px 12px #01040a,inset -5px -5px 12px #030a1c,0 20px 40px rgba(0,0,0,0.8)} "
    ".metric-card{background:rgba(30,41,59,0.3);border:1px solid rgba(255,255,255,0.05);border-radius:32px;padding:2.5rem;text-align:center;transition:all 0.4s} "
    ".metric-card:hover{transform:translateY(-12px);border-color:rgba(129,140,248,0.4);background:rgba(30,41,59,0.5)} "
    "@media(max-width:768px){.search-card{flex-direction:column;padding:16px} .platform-select{width:100%!important;border-right:none!important;border-bottom:1px solid rgba(255,255,255,0.1)!important}}"
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
    except Exception as e: return {"error": f"API Bridge Error: {e}"}
def _goal(n):
    if not n: return 1000
    mag = 10 ** (len(str(int(n))) - 1)
    return ((int(n) // mag) + 1) * mag

# ──────────────────────────── STATE ──────────────────────────────────
# Handle Query Params
params = st.query_params
if "user_id" not in st.session_state:
    st.session_state.user_id = params.get("id")
    st.session_state.platform_key = params.get("p")
    st.session_state.user_name = params.get("n", "")
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
    st.session_state.update(user_id=None, show_results=False, platform_key="", prev_count=0, history_times=[], history_values=[])

# ──────────────────────────── UI ─────────────────────────────────────
if st.session_state.show_results and not st.session_state.user_id:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f'<h1 style="color:white;text-align:center;margin-bottom:3.5rem;font-weight:900;letter-spacing:-2px;">RESULTADOS PARA "{st.session_state.get("last_query","")}"</h1>', unsafe_allow_html=True)
    
    if not st.session_state.search_results:
        st.warning("No se encontraron resultados exactos. Intenta con otro nombre.")
        if st.button("⬅️ VOLVER"): clear_params(); st.rerun()
    else:
        # Gallery Grid
        res_cols = st.columns(3)
        for i, r in enumerate(st.session_state.search_results):
            with res_cols[i % 3]:
                rid = r.get("id") if isinstance(r, dict) else r.user_id
                rname = r.get("name") if isinstance(r, dict) else r.display_name
                ravatar = r.get("avatar") if isinstance(r, dict) else r.thumbnail
                rhandle = r.get("handle") if isinstance(r, dict) else r.username
                
                # Professional Result Card
                st.markdown(f'<div class="result-card"><img src="{ravatar}" class="result-avatar" /><div class="result-name">{rname}</div><div class="result-handle">@{rhandle}</div></div>', unsafe_allow_html=True)
                if st.button(f"SELECCIONAR {i+1}", key=f"sel_{i}", use_container_width=True):
                    set_user_params(rid, st.session_state.platform_key, rname, ravatar, rhandle); st.rerun()
                st.markdown('<div style="margin-bottom:2rem;"></div>', unsafe_allow_html=True)

    if st.button("⬅️ CANCELAR BÚSQUEDA", use_container_width=True): clear_params(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.user_id:
    data = fetch_live_data(st.session_state.user_id, st.session_state.platform_key)
    if "error" in data:
        st.error(data["error"])
        with st.expander("Ver detalles técnicos"): st.write(data)
        if st.button("INTENTAR RECONECTAR"): st.rerun()
        if st.button("VOLVER AL INICIO"): clear_params(); st.rerun()
        st.stop()
    
    count = data["main"]
    st.session_state.history_times.append(datetime.now().strftime("%H:%M:%S"))
    st.session_state.history_values.append(count)
    if len(st.session_state.history_times) > 100: st.session_state.history_times, st.session_state.history_values = st.session_state.history_times[-100:], st.session_state.history_values[-100:]

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Dashboard Header
    c1, c2 = st.columns([1, 1])
    with c1: st.markdown(f'<div style="color:#64748b;font-weight:900;letter-spacing:5px;font-size:1.1rem;"><span style="color:#f43f5e">●</span> LIVE ANALYTICS</div>', unsafe_allow_html=True)
    with c2: 
        if st.button("🔄 BUSCAR OTRO", use_container_width=False, type="primary"): clear_params(); st.rerun()

    avatar = f'<img src="{st.session_state.user_avatar}" style="width:140px;height:140px;border-radius:50%;border:6px solid rgba(255,255,255,0.1);margin:0 auto 2.5rem;display:block;box-shadow:0 30px 60px rgba(0,0,0,0.8);" />' if st.session_state.user_avatar else ""
    handle = f'<div style="color:#818cf8;font-size:1.6rem;font-weight:800;margin-bottom:1.5rem;display:flex;align-items:center;justify-content:center;gap:10px;"><span class="material-symbols-rounded">verified</span> @{st.session_state.user_handle}</div>' if st.session_state.user_handle else ""

    pk_label = PLATFORMS[[k for k,v in PLATFORMS.items() if v["key"]==st.session_state.platform_key][0]]["label"]
    
    st.markdown(f'<div class="counter-box">{avatar}<h1 style="color:white;font-size:4.5rem;font-weight:900;letter-spacing:-3px;margin-bottom:0.8rem;line-height:0.9;">{st.session_state.user_name}</h1>{handle}', unsafe_allow_html=True)
    
    # Digits
    c_str = str(count)
    cells = []
    for i, digit in enumerate(c_str):
        if i > 0 and (len(c_str) - i) % 3 == 0: cells.append('<span class="digit-sep">.</span>')
        cells.append(f'<span class="digit-cell">{digit}</span>')
    st.markdown(f'<div class="digits-row">{"".join(cells)}</div><div style="color:#64748b;font-size:2.2rem;font-weight:900;letter-spacing:12px;margin-top:2.5rem;text-transform:uppercase;">TOTAL {pk_label}</div></div>', unsafe_allow_html=True)
    
    # Extra Metrics
    if data.get("extra"):
        st.markdown("<div style='margin-top:4rem;'></div>", unsafe_allow_html=True)
        cols = st.columns(len(data["extra"]))
        for i, itm in enumerate(data["extra"]):
            with cols[i]: st.markdown(f'<div class="metric-card"><div class="metric-value">{fmt(itm["v"])}</div><div class="metric-label"><span class="material-symbols-rounded" style="font-size:2.5rem;color:#818cf8;">{itm["i"]}</span> {itm["l"]}</div></div>', unsafe_allow_html=True)

    # Chart
    pcolor = PLATFORMS[[k for k,v in PLATFORMS.items() if v["key"]==st.session_state.platform_key][0]]["color"]
    v_min, v_max = min(st.session_state.history_values), max(st.session_state.history_values)
    span = max(v_max - v_min, 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.history_times, y=st.session_state.history_values, mode='lines', line=dict(color=pcolor, width=8, shape='spline', smoothing=1.3), fill='tonexty', fillcolor=f"rgba({int(pcolor[1:3],16)},{int(pcolor[3:5],16)},{int(pcolor[5:7],16)},0.15)", showlegend=False))
    fig.update_layout(height=480, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", color="#475569", size=14), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.02)", range=[v_min - span*0.15, v_max + span*0.15], tickformat=","))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    time.sleep(2); st.rerun()

else:
    # HERO SECTION (RE-DESIGNED)
    st.markdown('<div class="main-container"><div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Livecounts Elite</h1><p class="hero-subtitle">Analítica de precisión para los creadores más influyentes.</p>', unsafe_allow_html=True)
    
    # Integrated Search Bar
    with st.container():
        st.markdown('<div class="search-card">', unsafe_allow_html=True)
        cols = st.columns([1.2, 2, 1])
        with cols[0]: h_pk = st.selectbox("P", list(PLATFORMS.keys()), key="h_pk", label_visibility="collapsed")
        with cols[1]: h_q = st.text_input("Q", placeholder="Escribe el nombre del canal...", key="h_q", label_visibility="collapsed")
        with cols[2]: 
            if st.button("INICIAR MOTOR ⚡", use_container_width=True, type="primary"):
                if h_q:
                    pk = PLATFORMS[h_pk]["key"]
                    try:
                        if pk.startswith("yt"): res = (api.youtube.find_channel(h_q) if pk=="yt_subs" else api.youtube.find_video(h_q))
                        else: res = [{"user_id": r.user_id, "id": r.username, "name": r.display_name, "avatar": r.thumbnail} for r in api.tiktok.find_user(h_q)]
                        st.session_state.update(search_results=res, show_results=True, platform_key=pk, last_query=h_q)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error en búsqueda: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;color:#1e293b;font-weight:900;font-size:7rem;margin-top:8vh;opacity:0.15;letter-spacing:10px;">ELITE SYSTEMS</div>', unsafe_allow_html=True)
