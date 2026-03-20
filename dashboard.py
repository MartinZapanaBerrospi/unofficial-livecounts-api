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
    page_title="Livecounts Elite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────── SLEEK MINIMALIST CSS ───────────────────
CSS = (
    "font-family:'Outfit',sans-serif;.stApp{background:#020617}"
    "#MainMenu,footer,header{visibility:hidden}.main-container{padding:2rem 5vw;max-width:1200px;margin:0 auto}"
    ".hero-title{font-size:clamp(3rem,8vw,5.5rem);font-weight:900;letter-spacing:-4px;color:white;margin-bottom:1rem;line-height:1}"
    ".search-card{background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.08);border-radius:28px;padding:10px; "
    "display:flex;align-items:center;gap:12px;max-width:960px;margin:0 auto;box-shadow:0 30px 60px rgba(0,0,0,0.5);backdrop-filter:blur(30px)}"
    ".elite-btn{background:linear-gradient(135deg,#6366f1,#a855f7)!important;border:none!important;border-radius:20px!important; "
    "color:white!important;font-weight:900!important;padding:12px 32px!important;box-shadow:0 8px 16px rgba(99,102,241,0.2)!important;height:58px!important}"
    ".counter-box{background:rgba(15,23,42,0.5);border:1px solid rgba(255,255,255,0.05);border-radius:48px;padding:4rem 2rem;text-align:center;backdrop-filter:blur(30px)}"
    ".digits-row{display:flex;justify-content:center;align-items:center;gap:clamp(4px,1vw,12px);margin:1.5rem 0;flex-wrap:wrap}"
    ".digit-cell{display:inline-flex;align-items:center;justify-content:center;width:clamp(50px,8vw,85px);height:clamp(80px,13vw,135px); "
    "background:#0f172a;border:1px solid rgba(255,255,255,0.15);border-radius:clamp(16px,2vw,32px);font-size:clamp(3.5rem,6.5vw,8rem);font-weight:900;color:#f8fafc; "
    "font-variant-numeric:tabular-nums;box-shadow:inset 6px 6px 12px #01040a,inset -6px -6px 12px #030a1c,0 20px 40px rgba(0,0,0,0.8)}"
    ".digit-sep{font-size:clamp(2.5rem,5vw,5.5rem);font-weight:900;color:#334155;margin:0 4px}"
    ".metric-card{background:rgba(30,41,59,0.3);border:1px solid rgba(255,255,255,0.06);border-radius:32px;padding:2rem;text-align:center;transition:all 0.4s}"
    ".metric-card:hover{transform:translateY(-10px);border-color:rgba(129,140,248,0.4);background:rgba(30,41,59,0.5)}"
    ".result-card{background:rgba(30,41,59,0.25);border:1px solid rgba(255,255,255,0.05);border-radius:28px;padding:1.5rem;text-align:center;transition:all 0.3s}"
    ".result-card:hover{background:rgba(30,41,59,0.5);transform:translateY(-5px);border-color:rgba(129,140,248,0.3)}"
    ".result-avatar{width:110px;height:110px;border-radius:50%;margin:0 auto 1.2rem;border:4px solid rgba(255,255,255,0.1);display:block}"
    ".icon-3d{font-size:3rem!important;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
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
            return {"main": val, "extra": [{"v": b[0], "l": "VISTAS CANAL", "i": "visibility"}, {"v": b[2], "l": "VIDEOS", "i": "movie"}, {"v": _goal(val), "l": "META", "i": "stars"}]}
        elif pk == "yt_views":
            r = send_request(f"{YOUTUBE_VIDEO_STATS_API}/{uid}")
            val = r.get("followerCount", 0)
            b = r.get("bottomOdos", [0,0,0])
            return {"main": val, "extra": [{"v": b[0], "l": "LIKES", "i": "favorite"}, {"v": b[1] if len(b)>1 else 0, "l": "DISLIKES", "i": "thumb_down"}, {"v": b[2] if len(b)>2 else 0, "l": "COMENTARIOS", "i": "forum"}]}
        elif pk == "tt_followers":
            m = api.tiktok.fetch_user_metrics(uid)
            return {"main": m["followers"], "extra": [{"v": m["likes"], "l": "LIKES", "i": "favorite"}, {"v": m["following"], "l": "SIGUIENDO", "i": "group"}, {"v": m["videos"], "l": "VIDEOS", "i": "video_library"}]}
    except Exception as e: return {"error": f"Error de Sincronización: {e}"}
def _goal(n):
    if not n: return 1000
    mag = 10 ** (len(str(int(n))) - 1)
    return ((int(n) // mag) + 1) * mag

# ──────────────────────────── STATE ──────────────────────────────────
params = st.query_params
if "user_id" not in st.session_state:
    st.session_state.user_id = params.get("u")
    st.session_state.platform_key = params.get("p")
    # Lazy load extra data if needed, or just use ID as name for first pulse
    st.session_state.user_name = params.get("u", "")
    st.session_state.user_avatar = ""
    st.session_state.user_handle = ""

defaults = {"user_id": None, "user_name": "", "user_avatar": "", "user_handle": "", "platform_key": "", "prev_count": 0, "search_results": [], "show_results": False, "history_times": [], "history_values": []}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

def clear_all():
    st.query_params.clear()
    st.session_state.update(user_id=None, show_results=False, platform_key="", prev_count=0, history_times=[], history_values=[])

# ──────────────────────────── UI ─────────────────────────────────────
if st.session_state.show_results and not st.session_state.user_id:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f'<h1 style="color:white;text-align:center;margin-bottom:3rem;font-weight:900;">RESULTADOS Hallados</h1>', unsafe_allow_html=True)
    
    if not st.session_state.search_results:
        st.warning("No se encontraron resultados exactos.")
        if st.button("⬅️ VOLVER"): clear_all(); st.rerun()
    else:
        grid = st.columns(3)
        for i, r in enumerate(st.session_state.search_results):
            with grid[i % 3]:
                # Robust Key Mapping to avoid 'None'
                rid = r.get("id", r.get("userId", ""))
                rname = r.get("name", r.get("display_name", rid))
                ravatar = r.get("avatar", r.get("thumbnail", ""))
                rhandle = r.get("handle", r.get("username", rname))
                
                # Filter out None strings
                if rname is None: rname = rid
                if rhandle is None: rhandle = rname

                st.markdown(f'<div class="result-card"><img src="{ravatar}" class="result-avatar" /><div style="color:white;font-weight:900;font-size:1.3rem;line-height:1.1;">{rname}</div><div style="color:#818cf8;font-weight:700;font-size:0.9rem;margin-bottom:1rem;">@{rhandle}</div></div>', unsafe_allow_html=True)
                if st.button(f"SINCRONIZAR", key=f"sync_{i}", use_container_width=True, type="primary"):
                    st.query_params.update(u=rid, p=st.session_state.platform_key)
                    st.session_state.update(user_id=rid, user_name=rname, user_avatar=ravatar, user_handle=rhandle, show_results=False, prev_count=0, history_times=[], history_values=[])
                    st.rerun()
                st.markdown('<div style="margin-bottom:1.5rem;"></div>', unsafe_allow_html=True)

    if st.button("⬅️ CANCELAR", use_container_width=True): clear_all(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.user_id:
    res = fetch_live_data(st.session_state.user_id, st.session_state.platform_key)
    if "error" in res:
        st.error(res["error"]); st.button("🔄 REINTENTAR", on_click=st.rerun); st.button("⬅️ INICIO", on_click=clear_all); st.stop()
    
    count = res["main"]
    st.session_state.history_times.append(datetime.now().strftime("%H:%M:%S"))
    st.session_state.history_values.append(count)
    if len(st.session_state.history_times) > 100: st.session_state.history_times, st.session_state.history_values = st.session_state.history_times[-100:], st.session_state.history_values[-100:]

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1: st.markdown(f'<div style="color:#64748b;font-weight:900;letter-spacing:4px;font-size:1rem;"><span style="color:#f43f5e">●</span> LIVE FEED</div>', unsafe_allow_html=True)
    with c2: 
        if st.button("🔄 BUSCAR OTRO", use_container_width=False, type="primary"): clear_all(); st.rerun()

    avatar = f'<img src="{st.session_state.user_avatar}" style="width:130px;height:130px;border-radius:50%;border:4px solid rgba(255,255,255,0.1);margin:0 auto 2rem;display:block;" />' if st.session_state.user_avatar else ""
    handle = f'<div style="color:#818cf8;font-size:1.3rem;font-weight:700;margin-bottom:1.5rem;display:flex;align-items:center;justify-content:center;gap:8px;"><span class="material-symbols-rounded">verified</span> @{st.session_state.user_handle}</div>' if st.session_state.user_handle else ""

    pinfo = [v for k,v in PLATFORMS.items() if v["key"]==st.session_state.platform_key][0]
    st.markdown(f'<div class="counter-box">{avatar}<h1 style="color:white;font-size:4rem;font-weight:900;letter-spacing:-3px;margin-bottom:0.4rem;line-height:0.9;">{st.session_state.user_name}</h1>{handle}', unsafe_allow_html=True)
    
    c_str = str(count)
    cells = []
    for i, digit in enumerate(c_str):
        if i > 0 and (len(c_str) - i) % 3 == 0: cells.append('<span class="digit-sep">.</span>')
        cells.append(f'<span class="digit-cell">{digit}</span>')
    st.markdown(f'<div class="digits-row">{"".join(cells)}</div><div style="color:#64748b;font-size:2rem;font-weight:900;letter-spacing:10px;margin-top:2.5rem;">{pinfo["label"]} TOTAL</div></div>', unsafe_allow_html=True)

    if res.get("extra"):
        st.markdown("<div style='margin-top:4rem;'></div>", unsafe_allow_html=True)
        cols = st.columns(len(res["extra"]))
        for i, itm in enumerate(res["extra"]):
            with cols[i]: st.markdown(f'<div class="metric-card"><div class="metric-value">{fmt(itm["v"])}</div><div class="metric-label"><span class="material-symbols-rounded icon-3d">{itm["i"]}</span> {itm["l"]}</div></div>', unsafe_allow_html=True)

    v_min, v_max = min(st.session_state.history_values), max(st.session_state.history_values)
    span = max(v_max - v_min, 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.history_times, y=st.session_state.history_values, mode='lines', line=dict(color=pinfo["color"], width=6, shape='spline'), fill='tonexty', fillcolor=f"rgba({int(pinfo['color'][1:3],16)},{int(pinfo['color'][3:5],16)},{int(pinfo['color'][5:7],16)},0.1)", showlegend=False))
    fig.update_layout(height=480, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", color="#334155"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.02)", range=[v_min - span*0.1, v_max + span*0.1], tickformat=","))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    time.sleep(2); st.rerun()

else:
    st.markdown('<div class="main-container"><div style="text-align:center;padding:12vh 0;"><h1 class="hero-title">Livecounts Elite</h1><p style="color:#64748b;font-size:1.3rem;margin-bottom:4rem;font-weight:300;letter-spacing:2px;">PRECISIÓN EN TIEMPO REAL</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="search-card">', unsafe_allow_html=True)
        c0, c1, c2 = st.columns([1.2, 2.5, 1])
        with c0: h_pk = st.selectbox("P", list(PLATFORMS.keys()), key="h_pk", label_visibility="collapsed")
        with c1: h_q = st.text_input("Q", placeholder="Buscar canal o video...", key="h_q", label_visibility="collapsed")
        with c2: 
            if st.button("BUSCAR CHANNEL ⚡", use_container_width=True, type="primary"):
                if h_q:
                    pk = PLATFORMS[h_pk]["key"]
                    try:
                        if pk.startswith("yt"): res = (api.youtube.find_channel(h_q) if pk=="yt_subs" else api.youtube.find_video(h_q))
                        else: res = [{"user_id": r.user_id, "id": r.username, "name": r.display_name, "avatar": r.thumbnail} for r in api.tiktok.find_user(h_q)]
                        st.session_state.update(search_results=res, show_results=True, platform_key=pk)
                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
