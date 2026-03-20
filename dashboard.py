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
    page_title="Livecounts Elite Pro",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────── ELITE 3D NEOMORPHIC CSS ────────────────
CSS = (
    "font-family:'Outfit',sans-serif;.stApp{background:#020617}"
    "#MainMenu,footer,header{visibility:hidden}.main-container{padding:2rem 5vw;max-width:1300px;margin:0 auto}"
    ".hero-title{font-size:clamp(3.5rem,10vw,6.5rem);font-weight:900;letter-spacing:-5px;background:linear-gradient(135deg,#fff,#818cf8); "
    "-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 40px rgba(129,140,248,0.5));line-height:0.9}"
    ".search-card{background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.08);border-radius:32px;padding:12px; "
    "display:flex;align-items:center;gap:15px;max-width:1100px;margin:0 auto;box-shadow:25px 25px 50px #01040a,-25px -25px 50px #030a1c;backdrop-filter:blur(40px)}"
    ".elite-btn{background:linear-gradient(135deg,#6366f1,#a855f7)!important;border:none!important;border-radius:24px!important; "
    "color:white!important;font-weight:900!important;padding:16px 40px!important;box-shadow:0 10px 20px rgba(99,102,241,0.3)!important;height:65px!important}"
    ".counter-box{background:rgba(15,23,42,0.45);border:1px solid rgba(255,255,255,0.06);border-radius:56px;padding:5rem 2.5rem;text-align:center;"
    "box-shadow:30px 30px 60px #01040a,-30px -30px 60px #030a1c,inset 0 1px 1px rgba(255,255,255,0.1);backdrop-filter:blur(30px)}"
    ".digits-row{display:flex;justify-content:center;align-items:center;gap:clamp(6px,1.2vw,16px);margin:2rem 0;flex-wrap:wrap}"
    ".digit-cell{display:inline-flex;align-items:center;justify-content:center;width:clamp(60px,10vw,100px);height:clamp(90px,15vw,155px); "
    "background:#0f172a;border:1px solid rgba(255,255,255,0.15);border-radius:clamp(20px,2vw,40px);font-size:clamp(4.5rem,8vw,9.5rem);font-weight:900;color:#f8fafc; "
    "font-variant-numeric:tabular-nums;box-shadow:inset 8px 8px 16px #01040a,inset -8px -8px 16px #030a1c,0 25px 50px rgba(0,0,0,0.8)}"
    ".digit-sep{font-size:clamp(3.5rem,6vw,6.5rem);font-weight:900;color:#334155;margin:0 5px}"
    ".metric-card{background:rgba(30,41,59,0.35);border:1px solid rgba(255,255,255,0.07);border-radius:40px;padding:3rem 2rem;text-align:center;"
    "box-shadow:15px 15px 30px #01040a,-15px -15px 30px #030a1c;transition:all 0.4s;transform-style:preserve-3d}"
    ".metric-card:hover{transform:translateY(-15px) perspective(1000px) rotateX(10deg);border-color:rgba(129,140,248,0.5);box-shadow:0 40px 80px rgba(0,0,0,0.8)}"
    ".result-card{background:rgba(30,41,59,0.3);border:1px solid rgba(255,255,255,0.06);border-radius:32px;padding:2rem;text-align:center;transition:all 0.3s}"
    ".result-card:hover{background:rgba(30,41,59,0.6);transform:scale(1.05);border-color:rgba(129,140,248,0.4)}"
    ".result-avatar{width:120px;height:120px;border-radius:50%;margin:0 auto 1.5rem;border:5px solid rgba(255,255,255,0.1);box-shadow:0 15px 30px rgba(0,0,0,0.6)}"
    ".icon-3d{font-size:3.5rem!important;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
    "filter:drop-shadow(0 6px 12px rgba(0,0,0,0.6));transition:all 0.3s}.metric-card:hover .icon-3d{transform:scale(1.2) translateZ(40px)}"
    ".live-dot{display:inline-block;width:20px;height:20px;background:#f43f5e;border-radius:50%;margin-right:20px;animation:pulse 2s infinite}"
    "@keyframes pulse{0%,100%{transform:scale(0.9);box-shadow:0 0 0 0 rgba(244,63,94,0.7)}50%{transform:scale(1.2);box-shadow:0 0 0 35px rgba(244,63,94,0)}}"
    ".stPlotlyChart{background:rgba(15,23,42,0.4)!important;border-radius:48px;padding:2rem;border:1px solid rgba(255,255,255,0.05)}"
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
            return {"main": val, "extra": [{"v": b[0], "l": "VISTAS TOTALES", "i": "visibility"}, {"v": b[2], "l": "VIDEOS", "i": "movie"}, {"v": _goal(val), "l": "META (GOAL)", "i": "stars"}]}
        elif pk == "yt_views":
            r = send_request(f"{YOUTUBE_VIDEO_STATS_API}/{uid}")
            val = r.get("followerCount", 0)
            b = r.get("bottomOdos", [0,0,0])
            return {"main": val, "extra": [{"v": b[0], "l": "LIKES", "i": "favorite"}, {"v": b[1] if len(b)>1 else 0, "l": "DISLIKES", "i": "thumb_down"}, {"v": b[2] if len(b)>2 else 0, "l": "COMENTARIOS", "i": "forum"}]}
        elif pk == "tt_followers":
            m = api.tiktok.fetch_user_metrics(uid)
            return {"main": m["followers"], "extra": [{"v": m["likes"], "l": "LIKES", "i": "favorite"}, {"v": m["following"], "l": "SIGUIENDO", "i": "group"}, {"v": m["videos"], "l": "VIDEOS", "i": "video_library"}]}
    except Exception as e: return {"error": f"Elite Engine Sync Failed: {e}"}
def _goal(n):
    if not n: return 1000
    mag = 10 ** (len(str(int(n))) - 1)
    return ((int(n) // mag) + 1) * mag

# ──────────────────────────── STATE ──────────────────────────────────
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

def clear_all():
    st.query_params.clear()
    st.session_state.update(user_id=None, show_results=False, platform_key="", prev_count=0, history_times=[], history_values=[])

# ──────────────────────────── UI ─────────────────────────────────────
if st.session_state.show_results and not st.session_state.user_id:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f'<h1 style="color:white;text-align:center;margin-bottom:4rem;font-weight:900;font-size:3.5rem;letter-spacing:-3px;">RESULTADOS PARA "{st.session_state.get("last_q","")}"</h1>', unsafe_allow_html=True)
    
    if not st.session_state.search_results:
        st.warning("No se encontraron coincidencias exactas. Prueba con un nombre diferente.")
        if st.button("⬅️ VOLVER AL INICIO"): clear_all(); st.rerun()
    else:
        grid = st.columns(3)
        for i, r in enumerate(st.session_state.search_results):
            with grid[i % 3]:
                # Robust extraction for both YT and TT
                rid = r.get("id") if isinstance(r, dict) else r.user_id
                rname = r.get("name") if isinstance(r, dict) else r.display_name
                ravatar = r.get("avatar") if isinstance(r, dict) else r.thumbnail
                rhandle = r.get("handle") if isinstance(r, dict) else r.username
                
                st.markdown(f'<div class="result-card"><img src="{ravatar}" class="result-avatar" /><div style="color:white;font-weight:900;font-size:1.5rem;margin-bottom:0.5rem;line-height:1;">{rname}</div><div style="color:#818cf8;font-weight:800;letter-spacing:1px;font-size:0.9rem;margin-bottom:1.5rem;">@{rhandle}</div></div>', unsafe_allow_html=True)
                if st.button(f"Sincronizar Canal № {i+1}", key=f"sync_{i}", use_container_width=True, type="primary"):
                    st.query_params.update(id=rid, p=st.session_state.platform_key, n=rname, a=ravatar, h=rhandle)
                    st.session_state.update(user_id=rid, user_name=rname, user_avatar=ravatar, user_handle=rhandle, show_results=False, prev_count=0, history_times=[], history_values=[])
                    st.rerun()
                st.markdown('<div style="margin-bottom:2rem;"></div>', unsafe_allow_html=True)

    if st.button("⬅️ CANCELAR BÚSQUEDA", use_container_width=True): clear_all(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.user_id:
    res = fetch_live_data(st.session_state.user_id, st.session_state.platform_key)
    if "error" in res:
        st.error(res["error"]); st.button("🔄 REINTENTAR", on_click=st.rerun); st.button("⬅️ VOLVER", on_click=clear_all); st.stop()
    
    count = res["main"]
    st.session_state.history_times.append(datetime.now().strftime("%H:%M:%S"))
    st.session_state.history_values.append(count)
    if len(st.session_state.history_times) > 100: st.session_state.history_times, st.session_state.history_values = st.session_state.history_times[-100:], st.session_state.history_values[-100:]

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1: st.markdown(f'<div style="color:#64748b;font-weight:900;letter-spacing:6px;font-size:1.2rem;"><span class="live-dot"></span>ELITE LIVE FEED</div>', unsafe_allow_html=True)
    with c2: 
        if st.button("🔄 BUSCAR NUEVO CANAL", use_container_width=False, type="primary"): clear_all(); st.rerun()

    avatar = f'<img src="{st.session_state.user_avatar}" style="width:160px;height:160px;border-radius:50%;border:8px solid rgba(255,255,255,0.1);margin:0 auto 2.5rem;display:block;box-shadow:0 30px 60px rgba(0,0,0,0.8);" />' if st.session_state.user_avatar else ""
    handle = f'<div style="color:#818cf8;font-size:1.8rem;font-weight:800;margin-bottom:2rem;display:flex;align-items:center;justify-content:center;gap:12px;"><span class="material-symbols-rounded" style="color:#818cf8;font-size:2rem;">verified</span> @{st.session_state.user_handle}</div>' if st.session_state.user_handle else ""

    pinfo = [v for k,v in PLATFORMS.items() if v["key"]==st.session_state.platform_key][0]
    st.markdown(f'<div class="counter-box">{avatar}<h1 style="color:white;font-size:5rem;font-weight:900;letter-spacing:-3px;margin-bottom:0.5rem;line-height:0.8;">{st.session_state.user_name}</h1>{handle}', unsafe_allow_html=True)
    
    c_str = str(count)
    cells = []
    for i, digit in enumerate(c_str):
        if i > 0 and (len(c_str) - i) % 3 == 0: cells.append('<span class="digit-sep">.</span>')
        cells.append(f'<span class="digit-cell">{digit}</span>')
    st.markdown(f'<div class="digits-row">{"".join(cells)}</div><div style="color:#64748b;font-size:2.5rem;font-weight:900;letter-spacing:15px;margin-top:3rem;">TOTAL {pinfo["label"]}</div></div>', unsafe_allow_html=True)
    st.session_state.prev_count = count

    if res.get("extra"):
        st.markdown("<div style='margin-top:5rem;'></div>", unsafe_allow_html=True)
        cols = st.columns(len(res["extra"]))
        for i, itm in enumerate(res["extra"]):
            with cols[i]: st.markdown(f'<div class="metric-card"><div class="metric-value">{fmt(itm["v"])}</div><div class="metric-label"><span class="material-symbols-rounded icon-3d">{itm["i"]}</span> {itm["l"]}</div></div>', unsafe_allow_html=True)

    v_min, v_max = min(st.session_state.history_values), max(st.session_state.history_values)
    span = max(v_max - v_min, 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.history_times, y=st.session_state.history_values, mode='lines', line=dict(color=pinfo["color"], width=8, shape='spline', smoothing=1.3), fill='tonexty', fillcolor=f"rgba({int(pinfo['color'][1:3],16)},{int(pinfo['color'][3:5],16)},{int(pinfo['color'][5:7],16)},0.15)", showlegend=False))
    fig.update_layout(height=550, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", color="#475569", size=15), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.02)", range=[v_min - span*0.15, v_max + span*0.15], tickformat=","))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    time.sleep(2); st.rerun()

else:
    st.markdown('<div class="main-container"><div style="text-align:center;padding:10vh 0;"><h1 class="hero-title">Livecounts Elite</h1><p style="color:#64748b;font-size:1.5rem;margin-bottom:5rem;font-weight:300;letter-spacing:3px;">PRECISIÓN ABSOLUTA PARA CREADORES MUNDIALES</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="search-card">', unsafe_allow_html=True)
        c0, c1, c2 = st.columns([1.3, 2.5, 1])
        with c0: h_pk = st.selectbox("P", list(PLATFORMS.keys()), key="h_pk", label_visibility="collapsed")
        with c1: h_q = st.text_input("Q", placeholder="Buscar canal o video...", key="h_q", label_visibility="collapsed")
        with c2: 
            if st.button("INICIAR MOTOR ⚡", use_container_width=True, type="primary"):
                if h_q:
                    pk = PLATFORMS[h_pk]["key"]
                    try:
                        if pk.startswith("yt"): res = (api.youtube.find_channel(h_q) if pk=="yt_subs" else api.youtube.find_video(h_q))
                        else: res = [{"user_id": r.user_id, "id": r.username, "name": r.display_name, "avatar": r.thumbnail} for r in api.tiktok.find_user(h_q)]
                        st.session_state.update(search_results=res, show_results=True, platform_key=pk, last_q=h_q)
                        st.rerun()
                    except Exception as e: st.error(f"Elite Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#0f172a;font-weight:900;font-size:10rem;margin-top:10vh;opacity:0.3;letter-spacing:20px;user-select:none;">PRO SYSTEMS</div></div></div>', unsafe_allow_html=True)
