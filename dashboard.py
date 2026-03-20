import streamlit as st
import time
import plotly.graph_objects as go
from datetime import datetime
from unofficial_livecounts_api import (
    api, RequestApiError, send_request,
    YOUTUBE_CHANNEL_STATS_API, YOUTUBE_VIDEO_STATS_API,
)

# ──────────────────────────── Page Config ────────────────────────────
st.set_page_config(page_title="Livecounts Elite", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# ──────────────────────────── HIGH-FIDELITY V5 CSS ───────────────────
CSS = (
    "font-family:'Outfit',sans-serif;.stApp{background:#000000}"
    "#MainMenu,footer,header{visibility:hidden}.main-container{padding:0;max-width:1100px;margin:0 auto}"
    ".hero-section{text-align:center;padding:12vh 2rem 8vh}"
    ".hero-title{font-size:clamp(3.5rem,10vw,6rem);font-weight:900;letter-spacing:-4px;color:white;margin-bottom:0.5rem;line-height:1}"
    ".hero-subtitle{color:#525252;font-size:1.4rem;text-transform:uppercase;letter-spacing:6px;font-weight:400;margin-bottom:4rem}"
    ".search-card{background:rgba(23,23,23,0.8);border:1px solid #333;border-radius:24px;padding:12px;display:flex;align-items:center;gap:12px;max-width:900px;margin:0 auto;box-shadow:0 30px 60px rgba(0,0,0,0.5);backdrop-filter:blur(30px)}"
    ".elite-btn{background:#ff4b4b!important;border:none!important;border-radius:12px!important;color:white!important;font-weight:800!important;padding:12px 24px!important;height:54px!important;text-transform:uppercase;letter-spacing:1px}"
    ".list-container{background:#0a0a0a;border:1px solid #1f1f1f;border-radius:20px;max-width:800px;margin:2rem auto;overflow:hidden}"
    ".list-item{display:flex;align-items:center;gap:20px;padding:1.5rem 2rem;border-bottom:1px solid #141414;transition:all 0.2s;cursor:pointer}"
    ".list-item:hover{background:#111}.list-item:last-child{border-bottom:none}"
    ".list-avatar{width:70px;height:70px;border-radius:50%;border:2px solid #262626;flex-shrink:0}"
    ".list-name{color:white;font-weight:700;font-size:1.4rem;line-height:1.2}"
    ".list-handle{color:#737373;font-size:1rem;font-weight:400}"
    ".dashboard-banner{width:100%;height:300px;background:#171717;background-size:cover;background-position:center;border-bottom:1px solid #333;position:relative}"
    ".profile-overlay{width:140px;height:140px;border-radius:50%;border:6px solid #000;position:absolute;bottom:-70px;left:50%;transform:translateX(-50%);background:#171717;z-index:10}"
    ".dashboard-content{padding:100px 1rem 4rem;text-align:center}"
    ".main-count{font-size:clamp(5rem,12vw,10rem);font-weight:900;color:white;letter-spacing:-3px;line-height:1;margin-bottom:1rem}"
    ".count-label{color:#a3a3a3;font-size:1.5rem;font-weight:600;letter-spacing:2px;text-transform:capitalize}"
    ".metric-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:5rem;padding:0 1rem}"
    ".metric-box{background:#000;border:1px solid #1f1f1f;border-radius:8px;padding:2rem 1.5rem;text-align:center}"
    ".metric-val{font-size:2.2rem;font-weight:900;color:white;margin-bottom:0.5rem}"
    ".metric-title{color:#a3a3a3;font-size:1rem;font-weight:700;letter-spacing:1px;display:flex;align-items:center;justify-content:center;gap:8px}"
    ".metric-title .material-symbols-rounded{font-size:1.4rem;color:#3b82f6}"
    "@media(max-width:768px){.metric-grid{grid-template-columns:1fr}.search-card{flex-direction:column;padding:16px}.platform-select{width:100%!important;border-right:none!important;border-bottom:1px solid #333!important}}"
)

st.markdown(f"<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@48,700,0,0' /><style>{CSS}</style>", unsafe_allow_html=True)

# ──────────────────────────── PLATFORMS ──────────────────────────────
PLATFORMS = {
    "🔴 YouTube Subs": {"key": "yt_subs", "color": "#ef4444", "icon": "subscriptions", "label": "Subscribers"},
    "🔴 YouTube Views": {"key": "yt_views", "color": "#ef4444", "icon": "video_library", "label": "Views"},
    "🎵 TikTok Follows": {"key": "tt_followers", "color": "#00f2ea", "icon": "music_note", "label": "Followers"},
}

# ──────────────────────────── HELPERS ────────────────────────────────
def fmt(n): return f"{int(n):,}".replace(",", ".")
def _goal(n):
    if not n: return 1000
    mag = 10 ** (len(str(int(n))) - 1)
    return ((int(n) // mag) + 1) * mag

def fetch_live_data(uid, pk):
    try:
        if pk == "yt_subs":
            r = send_request(f"{YOUTUBE_CHANNEL_STATS_API}/{uid}")
            val = r.get("followerCount", 0)
            b = r.get("bottomOdos", [0,0,0,0])
            return {"main": val, "extra": [{"v": b[0], "l": "Channel Views", "i": "public"}, {"v": b[2], "l": "Videos", "i": "movie"}, {"v": _goal(val), "l": "Goal", "i": "track_changes"}]}
        elif pk == "yt_views":
            r = send_request(f"{YOUTUBE_VIDEO_STATS_API}/{uid}")
            val = r.get("followerCount", 0)
            b = r.get("bottomOdos", [0,0,0])
            return {"main": val, "extra": [{"v": b[0], "l": "Likes", "i": "favorite"}, {"v": b[1] if len(b)>1 else 0, "l": "Dislikes", "i": "thumb_down"}, {"v": b[2] if len(b)>2 else 0, "l": "Comments", "i": "forum"}]}
        elif pk == "tt_followers":
            m = api.tiktok.fetch_user_metrics(uid)
            return {"main": m["followers"], "extra": [{"v": m["likes"], "l": "Likes", "i": "favorite"}, {"v": m["following"], "l": "Following", "i": "group"}, {"v": m["videos"], "l": "Videos", "i": "video_library"}]}
    except Exception as e: return {"error": f"Connection Lost: {e}"}

# ──────────────────────────── STATE ──────────────────────────────────
params = st.query_params
if "user_id" not in st.session_state:
    st.session_state.user_id = params.get("u")
    st.session_state.platform_key = params.get("p", "yt_subs")
    st.session_state.user_name = params.get("n", "")
    st.session_state.user_avatar = params.get("a", "")
    st.session_state.user_handle = params.get("h", "")

defaults = {
    "user_id": None, "user_name": "", "user_avatar": "", "user_handle": "",
    "platform_key": "yt_subs", "history_values": [], "show_results": False,
    "search_results": []
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

def clear_all():
    st.query_params.clear()
    st.session_state.update(user_id=None, show_results=False)

# ──────────────────────────── UI ─────────────────────────────────────
if st.session_state.show_results and not st.session_state.user_id:
    st.markdown('<div class="main-container" style="padding:4rem 2rem;">', unsafe_allow_html=True)
    st.markdown('<h1 style="color:white;text-align:center;font-weight:900;margin-bottom:3rem;">RESULTADOS Hallados</h1>', unsafe_allow_html=True)
    
    if not st.session_state.search_results:
        st.warning("No se encontraron resultados para esta búsqueda.")
        if st.button("⬅️ VOLVER AL INICIO"): clear_all(); st.rerun()
    else:
        st.markdown('<div class="list-container">', unsafe_allow_html=True)
        for i, r in enumerate(st.session_state.search_results):
            rid = r.get("id", r.get("userId", ""))
            rname = r.get("name", r.get("display_name", rid))
            ravatar = r.get("avatar", r.get("thumbnail", ""))
            rhandle = r.get("handle", r.get("username", rname))
            if rname is None: rname = rid
            if rhandle is None: rhandle = rname
            
            # Use columns for layout but custom HTML for result row
            col1, col2 = st.columns([1, 8])
            with col1: st.image(ravatar, width=70) # Fallback for circle border in CSS is tricky with st.image
            with col2:
                if st.button(f"{rname} \n @{rhandle}", key=f"sel_{i}", help=rid, use_container_width=True):
                    st.query_params.update(u=rid, p=st.session_state.platform_key, n=rname, a=ravatar, h=rhandle)
                    st.session_state.update(user_id=rid, user_name=rname, user_avatar=ravatar, user_handle=rhandle, show_results=False, history_values=[])
                    st.rerun()
            st.markdown('<hr style="border-color:#141414;margin:0;">', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<p style="text-align:center;color:#404040;margin-top:2rem;font-size:0.9rem;">TIP: Press/Click on Search Result to Continue.</p>', unsafe_allow_html=True)
    if st.button("⬅️ CANCELAR BÚSQUEDA", use_container_width=True): clear_all(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.user_id:
    res = fetch_live_data(st.session_state.user_id, st.session_state.platform_key)
    if "error" in res:
        st.error(res["error"]); st.button("🔄 REINTENTAR", on_click=st.rerun); st.button("⬅️ INICIO", on_click=clear_all); st.stop()
    
    count = res["main"]
    st.session_state.history_values.append(count)
    if len(st.session_state.history_values) > 100: st.session_state.history_values = st.session_state.history_values[-100:]

    # Dashboard V5 Pixel-Perfect (IMAGE 4)
    st.markdown(f'<div class="dashboard-banner">', unsafe_allow_html=True)
    st.markdown(f'<img src="{st.session_state.user_avatar}" class="profile-overlay" />', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="dashboard-content"><h1 style="color:white;font-size:3.5rem;font-weight:800;margin-bottom:0.5rem;">{st.session_state.user_name}</h1>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:#ef4444;font-size:1.5rem;margin-bottom:3rem;"><span class="material-symbols-rounded" style="vertical-align:bottom;">play_circle</span></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="main-count">{fmt(count)}</div>', unsafe_allow_html=True)
    pinfo = [v for k,v in PLATFORMS.items() if v["key"]==st.session_state.platform_key][0]
    st.markdown(f'<div class="count-label">{pinfo["label"]} <span class="material-symbols-rounded" style="font-size:1.2rem;vertical-align:middle;">groups</span></div>', unsafe_allow_html=True)
    
    if res.get("extra"):
        st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, itm in enumerate(res["extra"][:3]):
            with cols[i]:
                st.markdown(f'<div class="metric-box"><div class="metric-val">{fmt(itm["v"])}</div><div class="metric-title">{itm["l"]} <span class="material-symbols-rounded">{itm["i"]}</span></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Minimalist History Chart at very bottom
    if len(st.session_state.history_values) > 1:
        st.markdown("<div style='margin-top:4rem;'></div>", unsafe_allow_html=True)
        fig = go.Figure(); fig.add_trace(go.Scatter(y=st.session_state.history_values, mode='lines', line=dict(color=pinfo["color"], width=4), fill='tonexty', fillcolor=f"rgba(255,255,255,0.03)", showlegend=False))
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", color="#262626"), xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=False, zeroline=False))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    time.sleep(2); st.rerun()

else:
    # HERO SECTION (RE-DESIGNED V5)
    st.markdown('<div class="main-container"><div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Livecounts Elite</h1><p class="hero-subtitle">PRECISIÓN EN TIEMPO REAL</p>', unsafe_allow_html=True)
    
    # Fixed Search Bar (No ghost box)
    c0, c1, c2 = st.columns([1, 2.5, 1])
    with c0: h_pk = st.selectbox("P", list(PLATFORMS.keys()), key="h_pk", label_visibility="collapsed")
    with c1: h_q = st.text_input("Q", placeholder="Buscar canal o video...", key="h_q", label_visibility="collapsed")
    with c2: 
        if st.button("BUSCAR ⚡", use_container_width=True, type="primary"):
            if h_q:
                pk = PLATFORMS[h_pk]["key"]
                try:
                    if pk.startswith("yt"): res = (api.youtube.find_channel(h_q) if pk=="yt_subs" else api.youtube.find_video(h_q))
                    else: res = api.tiktok.find_user(h_q)
                    st.session_state.update(search_results=res, show_results=True, platform_key=pk)
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")
    st.markdown('</div></div>', unsafe_allow_html=True)
