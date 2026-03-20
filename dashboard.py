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

# ──────────────────────────── INTEGRATED LIST CSS ───────────────────
CSS = (
    "font-family:'Outfit',sans-serif;.stApp{background:#000}"
    "#MainMenu,footer,header{visibility:hidden}.main-container{padding:0;max-width:1100px;margin:0 auto}"
    ".hero-section{text-align:center;padding:12vh 2rem 4vh}"
    ".hero-title{font-size:clamp(3rem,8vw,5.5rem);font-weight:900;letter-spacing:-4px;color:white;margin-bottom:0.5rem;line-height:1}"
    ".hero-subtitle{color:#404040;font-size:1.3rem;text-transform:uppercase;letter-spacing:6px;font-weight:400;margin-bottom:4rem}"
    ".search-card-container{max-width:900px;margin:0 auto;background:#0a0a0a;border:1px solid #1f1f1f;border-radius:24px;padding:12px;box-shadow:0 30px 60px rgba(0,0,0,0.5)}"
    ".elite-btn{background:#ff4b4b!important;border:none!important;border-radius:12px!important;color:white!important;font-weight:800!important;padding:12px 24px!important;height:54px!important;text-transform:uppercase;letter-spacing:1px}"
    ".inline-list{max-width:900px;margin:1rem auto;background:#0f0f0f;border:1px solid #1f1f1f;border-radius:20px;overflow:hidden;box-shadow:0 20px 40px rgba(0,0,0,0.6)}"
    ".list-item-btn{width:100%;background:transparent;border:none;border-bottom:1px solid #1a1a1a;padding:1.2rem 2rem;display:flex;align-items:center;gap:20px;text-align:left;transition:all 0.2s}"
    ".list-item-btn:hover{background:#161616}.list-item-btn:last-child{border-bottom:none}"
    ".list-avatar{width:55px;height:55px;border-radius:50%;border:2px solid #262626;object-fit:cover}"
    ".list-info{display:flex;flex-direction:column}.list-name{color:white;font-weight:700;font-size:1.2rem}"
    ".list-handle{color:#737373;font-size:0.9rem}"
    ".dashboard-banner{width:100%;height:280px;background:linear-gradient(to bottom,#0a0a0a,#000);border-bottom:1px solid #1f1f1f;position:relative}"
    ".profile-overlay{width:140px;height:140px;border-radius:50%;border:6px solid #000;position:absolute;bottom:-70px;left:50%;transform:translateX(-50%);background:#171717;z-index:10}"
    ".dashboard-content{padding:100px 1rem 4rem;text-align:center}"
    ".main-count{font-size:clamp(4.5rem,11vw,9rem);font-weight:900;color:white;letter-spacing:-3px;line-height:1;margin-bottom:1rem}"
    ".count-label{color:#a3a3a3;font-size:1.3rem;font-weight:600;letter-spacing:2px;text-transform:uppercase}"
    ".metric-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:5rem;padding:0 1.5rem}"
    ".metric-box{background:#0a0a0a;border:1px solid #1f1f1f;border-radius:12px;padding:2rem 1.5rem;text-align:center}"
    ".metric-val{font-size:2rem;font-weight:800;color:white;margin-bottom:0.5rem}"
    ".metric-title{color:#737373;font-size:0.9rem;font-weight:700;letter-spacing:1px;display:flex;align-items:center;justify-content:center;gap:8px}"
    ".metric-title .material-symbols-rounded{font-size:1.4rem;color:#ef4444}"
    "@media(max-width:768px){.metric-grid{grid-template-columns:1fr}.search-card-container{padding:16px}}"
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
    st.session_state.user_name = ""
    st.session_state.user_avatar = ""
    st.session_state.user_handle = ""

defaults = {"user_id": None, "user_name": "", "user_avatar": "", "user_handle": "", "platform_key": "yt_subs", "history_values": [], "history_times": [], "show_results": False, "search_results": []}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

def clear_all():
    st.session_state.update(user_id=None, show_results=False, history_values=[], history_times=[])
    st.query_params.clear()

# ──────────────────────────── METADATA AUTO-DISCOVERY ────────────────
if st.session_state.user_id and not st.session_state.user_name:
    try:
        if st.session_state.platform_key.startswith("yt"):
            found = (api.youtube.find_channel(st.session_state.user_id) if st.session_state.platform_key=="yt_subs" else api.youtube.find_video(st.session_state.user_id))
            for r in found:
                if r.get("id") == st.session_state.user_id:
                    st.session_state.update(user_name=r.get("name"), user_avatar=r.get("avatar"), user_handle=r.get("handle", r.get("name")))
                    break
        else:
            m = api.tiktok.find_user(st.session_state.user_id)
            if m: st.session_state.update(user_name=m[0]["name"], user_avatar=m[0]["avatar"], user_handle=m[0]["id"])
    except: pass

# ──────────────────────────── UI ─────────────────────────────────────
if st.session_state.user_id:
    res = fetch_live_data(st.session_state.user_id, st.session_state.platform_key)
    if "error" in res:
        st.error(res["error"]); st.button("🔄 REINTENTAR", on_click=st.rerun); st.button("⬅️ INICIO", on_click=clear_all); st.stop()
    
    count = res["main"]
    st.session_state.history_times.append(datetime.now().strftime("%H:%M:%S"))
    st.session_state.history_values.append(count)
    if len(st.session_state.history_times) > 100: 
        st.session_state.history_times = st.session_state.history_times[-100:]
        st.session_state.history_values = st.session_state.history_values[-100:]

    st.markdown(f'<div class="dashboard-banner"><img src="{st.session_state.user_avatar}" class="profile-overlay" /></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="dashboard-content"><h1 style="color:white;font-size:3.5rem;font-weight:800;margin-bottom:0.1rem;">{st.session_state.user_name}</h1>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:#ef4444;font-size:1.5rem;margin-bottom:3rem;"><span class="material-symbols-rounded">play_circle</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="main-count">{fmt(count)}</div>', unsafe_allow_html=True)
    pinfo = [v for k,v in PLATFORMS.items() if v["key"]==st.session_state.platform_key][0]
    st.markdown(f'<div class="count-label">{pinfo["label"]} <span class="material-symbols-rounded" style="font-size:1.2rem;vertical-align:middle;">groups</span></div>', unsafe_allow_html=True)
    
    if res.get("extra"):
        st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, itm in enumerate(res["extra"][:3]):
            with cols[i]: st.markdown(f'<div class="metric-box"><div class="metric-val">{fmt(itm["v"])}</div><div class="metric-title">{itm["l"]} <span class="material-symbols-rounded">{itm["i"]}</span></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if len(st.session_state.history_values) > 1:
        st.markdown("<div style='margin-top:4rem;'></div>", unsafe_allow_html=True)
        fig = go.Figure(); fig.add_trace(go.Scatter(x=st.session_state.history_times, y=st.session_state.history_values, mode='lines', line=dict(color=pinfo["color"], width=4), fill='tonexty', fillcolor=f"rgba(255,255,255,0.03)", showlegend=False))
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="#000", plot_bgcolor="#000", font=dict(family="Outfit", color="#525252"), xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=True, gridcolor="#141414", zeroline=False, tickformat=","))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    
    st.markdown('<div style="margin-top:2rem;text-align:center;">', unsafe_allow_html=True)
    if st.button("⬅️ BUSCAR OTRO CANAL", use_container_width=False, type="primary"): clear_all(); st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
    time.sleep(2); st.rerun()

else:
    st.markdown('<div class="main-container"><div class="hero-section"><h1 class="hero-title">Livecounts Elite</h1><p class="hero-subtitle">PRECISIÓN EN TIEMPO REAL</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="search-card-container">', unsafe_allow_html=True)
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
                    st.session_state.update(search_results=res, show_results=True, platform_key=pk); st.rerun()
                except Exception as e: st.error(f"Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # INLINE RESULTS LIST (Directly below search bar)
    if st.session_state.show_results:
        if not st.session_state.search_results:
            st.warning("No se hallaron resultados.")
        else:
            st.markdown('<div class="inline-list">', unsafe_allow_html=True)
            for i, r in enumerate(st.session_state.search_results):
                rid = r.get("id", r.get("userId", ""))
                rname = r.get("name", r.get("display_name", rid))
                ravatar = r.get("avatar", r.get("thumbnail", ""))
                rhandle = r.get("handle", r.get("username", rname))
                # Only show Name and Handle, NO CODES/IDs as requested
                rhandle_clean = f"@{rhandle}" if rhandle and not rhandle.startswith("UC") else ""
                
                # We use a custom styled column for the result row to make it click-friendly
                col_a, col_b = st.columns([1, 8])
                with col_a: st.image(ravatar, width=55)
                with col_b:
                    if st.button(f"{rname} \n {rhandle_clean}", key=f"sel_{i}", help=f"Seleccionar {rname}", use_container_width=True):
                        st.query_params.update(u=rid, p=st.session_state.platform_key)
                        st.session_state.update(user_id=rid, user_name=rname, user_avatar=ravatar, user_handle=rhandle, show_results=False, history_values=[], history_times=[])
                        st.rerun()
                st.markdown('<hr style="border-color:#1a1a1a;margin:0;">', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
