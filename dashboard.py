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

# ──────────────────────────── CSS (SaaS Dropdown & Premium Look) ───────────────────
CSS = (
    "font-family:'Outfit',sans-serif;.stApp{background:#000}"
    "#MainMenu,footer,header{visibility:hidden}.main-container{padding:0;max-width:1100px;margin:0 auto}"
    ".hero-section{text-align:center;padding:12vh 2rem 4vh}"
    ".hero-title{font-size:clamp(3rem,8vw,5.5rem);font-weight:900;letter-spacing:-4px;color:white;margin-bottom:0.5rem;line-height:1}"
    ".hero-subtitle{color:#404040;font-size:1.3rem;text-transform:uppercase;letter-spacing:6px;font-weight:400;margin-bottom:4rem}"
    ".search-card-container{max-width:900px;margin:0 auto;background:#0a0a0a;border:1px solid #1f1f1f;border-radius:24px;padding:12px;box-shadow:0 30px 60px rgba(0,0,0,0.5)}"
    ".dropdown-list{max-width:450px;margin:10px auto;background:#111;border:1px solid #262626;border-radius:16px;overflow:hidden;z-index:100;box-shadow:0 15px 30px rgba(0,0,0,0.8)}"
    ".dropdown-item{display:flex;align-items:center;gap:12px;padding:10px 15px;cursor:pointer;transition:all 0.2s;border-bottom:1px solid #1a1a1a}"
    ".dropdown-item:last-child{border-bottom:none}.dropdown-item:hover{background:#1a1a1a}"
    ".mini-avatar{width:36px;height:36px;border-radius:8px;object-fit:cover;border:1px solid #333}"
    "div.stButton > button{width:100%!important;background:transparent!important;border:none!important;color:#fff!important;text-align:left!important;font-size:1rem!important;font-weight:600!important;padding:5px 0!important;text-transform:none!important}"
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
)
st.markdown(f"<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@48,700,0,0' /><style>{CSS}</style>", unsafe_allow_html=True)

# ──────────────────────────── PLATFORMS ──────────────────────────────
PLATFORMS = {
    "🔴 YouTube Subs": {"key": "yt_subs", "color": "#ef4444", "icon": "subscriptions", "label": "Subscribers"},
    "🔴 YouTube Views": {"key": "yt_views", "color": "#ef4444", "icon": "video_library", "label": "Views"},
    "🎵 TikTok Follows": {"key": "tt_followers", "color": "#00f2ea", "icon": "music_note", "label": "Followers"},
}

# ──────────────────────────── STATE SYNC (FIX FOR BROWSER BUTTONS) ───
params = st.query_params
# CRITICAL: Always sync state with URL to respect Back/Forward buttons
uid_param = params.get("u")
pk_param = params.get("p", "yt_subs")

# Initialize default session variables if missing
defaults = {"user_id": None, "user_name": "", "user_avatar": "", "user_handle": "", "platform_key": "yt_subs", "history_values": [], "history_times": [], "show_results": False, "search_results": []}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# Update internal state if URL changed (e.g. user pressed Back)
if st.session_state.user_id != uid_param:
    st.session_state.update(user_id=uid_param, platform_key=pk_param, user_name="", user_avatar="", user_handle="", history_values=[], history_times=[])

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

def clear_all():
    st.session_state.update(user_id=None, show_results=False, history_values=[], history_times=[])
    st.query_params.clear()

# ──────────────────────────── UI ─────────────────────────────────────
if st.session_state.user_id:
    # Metadata Discovery if missing
    if not st.session_state.user_handle:
        try:
            pk = st.session_state.platform_key
            found = (api.youtube.find_channel(st.session_state.user_id) if pk=="yt_subs" else api.youtube.find_video(st.session_state.user_id)) if pk.startswith("yt") else api.tiktok.find_user(st.session_state.user_id)
            for r in found:
                rid = r.get("id", r.get("userId", ""))
                if rid == st.session_state.user_id:
                    st.session_state.update(user_name=r.get("name"), user_avatar=r.get("avatar"), user_handle=r.get("handle", r.get("username", r.get("name"))))
                    break
        except: pass

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
    
    # IDENTITY: Always start with @
    display_handle = f"@{st.session_state.user_handle or st.session_state.user_name}".replace("@@", "@")
    st.markdown(f'<div class="dashboard-content"><h1 style="color:white;font-size:3.5rem;font-weight:800;margin-bottom:0.1rem;">{display_handle}</h1>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:#ef4444;font-size:1.5rem;margin-bottom:3rem;"><span class="material-symbols-rounded">verified</span></div>', unsafe_allow_html=True)
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
        fig.update_layout(height=450, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="#000", plot_bgcolor="#000", font=dict(family="Outfit", color="#525252"), xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=True, gridcolor="#141414", zeroline=False, tickformat=","))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    
    st.markdown('<div style="margin-top:4rem;text-align:center;">', unsafe_allow_html=True)
    st.button("⬅️ BUSCAR NUEVO", type="primary", on_click=clear_all)
    st.markdown('</div></div>', unsafe_allow_html=True)
    time.sleep(2); st.rerun()

else:
    st.markdown('<div class="main-container"><div class="hero-section"><h1 class="hero-title">Livecounts Elite</h1><p class="hero-subtitle">PRECISIÓN EN TIEMPO REAL</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="search-card-container">', unsafe_allow_html=True)
    c0, c1, c2 = st.columns([1.2, 2.5, 1])
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
    
    if st.session_state.show_results:
        if not st.session_state.search_results:
            st.warning("No se hallaron resultados.")
        else:
            with st.container():
                st.markdown('<div class="dropdown-list">', unsafe_allow_html=True)
                for i, r in enumerate(st.session_state.search_results):
                    rid = r.get("id", r.get("userId", ""))
                    rname = r.get("name", rid)
                    rhandle = r.get("handle", r.get("username", rname))
                    ravatar = r.get("avatar", r.get("thumbnail", ""))
                    h_label = f"@{rhandle or rname}".replace("@@", "@")
                    
                    st.markdown(f'<div class="dropdown-item"><img src="{ravatar}" class="mini-avatar">', unsafe_allow_html=True)
                    if st.button(h_label, key=f"drp_{i}"):
                        st.query_params.update(u=rid, p=st.session_state.platform_key)
                        st.session_state.update(user_id=rid, user_name=rname, user_avatar=ravatar, user_handle=rhandle, show_results=False, history_values=[], history_times=[])
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
