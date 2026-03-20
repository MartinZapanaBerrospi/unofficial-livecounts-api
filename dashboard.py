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

# ──────────────────────────── CSS (v6.0: Obsidian SaaS Aesthetic) ───────────────────
CSS = (
    "@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&display=swap');"
    "body, .stApp { "
    "   background: radial-gradient(circle at 50% -20%, #1a1b1e 0%, #050505 100%) !important; "
    "   color: #e5e5e5 !important; "
    "   font-family: 'Outfit', sans-serif !important; "
    "}"
    "#MainMenu, footer, header { visibility: hidden; }"
    ".main-container { padding: 0; max-width: 1100px; margin: 0 auto; }"
    
    # Hero Section
    ".hero-section { text-align: center; padding: 14vh 2rem 6vh; }"
    ".hero-title { font-size: clamp(3.5rem, 9vw, 6.5rem); font-weight: 900; letter-spacing: -5px; color: #fff; margin-bottom: 0.2rem; line-height: 0.9; text-shadow: 0 0 30px rgba(255,255,255,0.1); }"
    ".hero-subtitle { color: #6b7280; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 8px; font-weight: 600; margin-bottom: 5rem; }"
    
    # Glassmorphism Search Card
    ".search-card-container { "
    "   max-width: 900px; margin: 0 auto; "
    "   background: rgba(15, 15, 15, 0.6); "
    "   backdrop-filter: blur(12px); "
    "   border: 1px solid rgba(255, 255, 255, 0.08); "
    "   border-radius: 28px; padding: 16px; "
    "   box-shadow: 0 40px 100px rgba(0,0,0,0.7), inset 0 0 0 1px rgba(255,255,255,0.02); "
    "}"
    
    # Input Styling
    "div[data-baseweb='select'] > div { background: rgba(0,0,0,0.3) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 12px !important; }"
    "input { background: rgba(0,0,0,0.3) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 12px !important; color: #fff !important; padding: 12px 18px !important; }"
    
    # Results List
    ".list-divider { border-top: 1px solid rgba(255,255,255,0.05); margin: 25px 0; width: 100%; }"
    ".mini-avatar { width: 48px; height: 48px; border-radius: 12px; object-fit: cover; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }"
    "div.stButton > button { "
    "   width: 100% !important; background: transparent !important; border: none !important; color: #a3a3a3 !important; "
    "   text-align: left !important; font-size: 1.2rem !important; font-weight: 500 !important; padding: 12px 20px !important; "
    "   text-transform: none !important; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; "
    "}"
    "div.stButton > button:hover { color: #fff !important; background: rgba(255,255,255,0.03) !important; padding-left: 28px !important; }"
    
    # Dashboard Premium
    ".dashboard-banner { width: 100%; height: 320px; background: linear-gradient(180deg, rgba(8,8,8,1) 0%, rgba(0,0,0,1) 100%); border-bottom: 1px solid rgba(255,255,255,0.05); position: relative; overflow: hidden; }"
    ".banner-glow { position: absolute; top: -50%; left: 50%; width: 100%; height: 100%; background: radial-gradient(circle, rgba(239, 68, 68, 0.08) 0%, transparent 70%); transform: translateX(-50%); pointer-events: none; }"
    ".profile-overlay { width: 160px; height: 160px; border-radius: 50%; border: 8px solid #000; position: absolute; bottom: -80px; left: 50%; transform: translateX(-50%); background: #111; z-index: 10; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }"
    ".dashboard-content { padding: 120px 1rem 4rem; text-align: center; }"
    ".main-count { font-size: clamp(5rem, 12vw, 10rem); font-weight: 900; color: #fff; letter-spacing: -4px; line-height: 0.9; margin-bottom: 1.5rem; text-shadow: 0 0 40px rgba(255,255,255,0.1); }"
    ".count-label { color: #6b7280; font-size: 1.4rem; font-weight: 600; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 5rem; }"
    
    # Metric Cards
    ".metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; padding: 0 2rem; }"
    ".metric-box { "
    "   background: rgba(10, 10, 10, 0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; "
    "   padding: 2.5rem 1.5rem; text-align: center; transition: all 0.4s ease; "
    "}"
    ".metric-box:hover { background: rgba(20, 20, 20, 0.6); border-color: rgba(255,255,255,0.1); transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.4); }"
    ".metric-val { font-size: 2.2rem; font-weight: 800; color: #fff; margin-bottom: 0.6rem; }"
    ".metric-title { color: #4b5563; font-size: 0.95rem; font-weight: 700; letter-spacing: 1px; display: flex; align-items: center; justify-content: center; gap: 10px; }"
    ".metric-title .material-symbols-rounded { font-size: 1.6rem; color: #ef4444; opacity: 0.8; }"
    
    # Chart Premium
    ".chart-container { background: rgba(10,10,10,0.2); border-radius: 30px; padding: 2rem; border: 1px solid rgba(255,255,255,0.03); margin-top: 6rem; }"
)
st.markdown(f"<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@48,700,1,0' /><style>{CSS}</style>", unsafe_allow_html=True)

# ──────────────────────────── PLATFORMS ──────────────────────────────
PLATFORMS = {
    "🔴 YouTube Subs": {"key": "yt_subs", "color": "#FF4B4B", "icon": "subscriptions", "label": "Subscribers", "slug": "youtube-live-subscriber-counter"},
    "🔴 YouTube Views": {"key": "yt_views", "color": "#FF4B4B", "icon": "video_library", "label": "Views", "slug": "youtube-live-view-counter"},
    "🎵 TikTok Follows": {"key": "tt_followers", "color": "#00F2EA", "icon": "music_note", "label": "Followers", "slug": "tiktok-live-follower-counter"},
}
SLUG_TO_KEY = {v["slug"]: v["key"] for v in PLATFORMS.values()}

# ──────────────────────────── STATE SYNC ─────────────────────────────
params = st.query_params
u_val = params.get("u")
target_uid, target_pk = None, "yt_subs"

if u_val and "/" in str(u_val):
    slug, uid = str(u_val).split("/")[:2]
    target_pk = SLUG_TO_KEY.get(slug, "yt_subs")
    target_uid = uid
elif u_val:
    target_uid = u_val
    target_pk = params.get("p", "yt_subs")

defaults = {"user_id": None, "user_name": "", "user_avatar": "", "user_handle": "", "platform_key": "yt_subs", "history_values": [], "history_times": [], "show_results": False, "search_results": []}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

if st.session_state.user_id != target_uid:
    st.session_state.update(user_id=target_uid, platform_key=target_pk, user_name="", user_avatar="", user_handle="", history_values=[], history_times=[])

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
            return {"main": val, "extra": [{"v": b[0], "l": "Canal Views", "i": "visibility"}, {"v": b[2], "l": "Videos", "i": "movie"}, {"v": _goal(val), "l": "Meta", "i": "track_changes"}]}
        elif pk == "yt_views":
            r = send_request(f"{YOUTUBE_VIDEO_STATS_API}/{uid}")
            val = r.get("followerCount", 0)
            b = r.get("bottomOdos", [0,0,0])
            return {"main": val, "extra": [{"v": b[0], "l": "Me gusta", "i": "favorite"}, {"v": b[1] if len(b)>1 else 0, "l": "No me gusta", "i": "thumb_down"}, {"v": b[2] if len(b)>2 else 0, "l": "Comentarios", "i": "forum"}]}
        elif pk == "tt_followers":
            m = api.tiktok.fetch_user_metrics(uid)
            return {"main": m["followers"], "extra": [{"v": m["likes"], "l": "Me gusta", "i": "favorite"}, {"v": m["following"], "l": "Siguiendo", "i": "group"}, {"v": m["videos"], "l": "Videos", "i": "video_library"}]}
    except Exception as e: return {"error": f"Error de conexión: {e}"}

def clear_all():
    st.session_state.update(user_id=None, show_results=False, history_values=[], history_times=[])
    st.query_params.clear()

# ──────────────────────────── UI ─────────────────────────────────────
if st.session_state.user_id:
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
        st.error(res["error"]); st.button("🔄 REINTENTAR", on_click=st.rerun); st.button("⬅️ REGRESAR", on_click=clear_all); st.stop()
    
    count = res["main"]
    st.session_state.history_times.append(datetime.now().strftime("%H:%M:%S"))
    st.session_state.history_values.append(count)
    if len(st.session_state.history_times) > 100:
        st.session_state.history_times = st.session_state.history_times[-100:]
        st.session_state.history_values = st.session_state.history_values[-100:]

    pinfo = [v for k,v in PLATFORMS.items() if v["key"]==st.session_state.platform_key][0]
    st.markdown(f'<div class="dashboard-banner"><div class="banner-glow" style="background:radial-gradient(circle, {pinfo["color"]}14 0%, transparent 70%);"></div><img src="{st.session_state.user_avatar}" class="profile-overlay" /></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-container"><div class="dashboard-content">', unsafe_allow_html=True)
    
    display_handle = f"@{st.session_state.user_handle or st.session_state.user_name}".replace("@@", "@")
    st.markdown(f'<h1 style="color:white;font-size:4rem;font-weight:900;margin-bottom:0.1rem;letter-spacing:-2px;">{display_handle}</h1>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:{pinfo["color"]};font-size:1.8rem;margin-bottom:4rem;"><span class="material-symbols-rounded">verified</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="main-count">{fmt(count)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="count-label">{pinfo["label"]} <span class="material-symbols-rounded" style="color:{pinfo["color"]};font-size:1.4rem;vertical-align:middle;margin-left:8px;">groups</span></div>', unsafe_allow_html=True)
    
    if res.get("extra"):
        st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, itm in enumerate(res["extra"][:3]):
            with cols[i]: st.markdown(f'<div class="metric-box"><div class="metric-val">{fmt(itm["v"])}</div><div class="metric-title">{itm["l"]} <span class="material-symbols-rounded" style="color:{pinfo["color"]}">{itm["i"]}</span></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if len(st.session_state.history_values) > 1:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        fig = go.Figure(); fig.add_trace(go.Scatter(x=st.session_state.history_times, y=st.session_state.history_values, mode='lines', line=dict(color=pinfo["color"], width=5), fill='tonexty', fillcolor=f"{pinfo['color']}05", showlegend=False))
        fig.update_layout(height=480, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", color="#4b5563"), xaxis=dict(showgrid=False, zeroline=False, tickangle=0, ntoks=5), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)", zeroline=False, tickformat=","))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div style="margin-top:6rem;text-align:center;">', unsafe_allow_html=True)
    if st.button("⬅️ BUSCAR NUEVO", type="primary"): clear_all(); st.rerun()
    st.markdown('</div></div></div>', unsafe_allow_html=True)
    time.sleep(2); st.rerun()

else:
    st.markdown('<div class="main-container"><div class="hero-section"><h1 class="hero-title">Livecounts Elite</h1><p class="hero-subtitle">MÉTRICAS PREMIUM EN TIEMPO REAL</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="search-card-container">', unsafe_allow_html=True)
    c0, c1, c2 = st.columns([1.2, 2.5, 1])
    with c0: h_pk_label = st.selectbox("P", list(PLATFORMS.keys()), key="h_pk", label_visibility="collapsed")
    with c1: h_q = st.text_input("Q", placeholder="Buscar canal, usuario o video...", key="h_q", label_visibility="collapsed")
    with c2: 
        if st.button("BUSCAR ⚡", use_container_width=True, type="primary"):
            if h_q:
                pk = PLATFORMS[h_pk_label]["key"]
                try:
                    res = (api.youtube.find_channel(h_q) if pk=="yt_subs" else api.youtube.find_video(h_q)) if pk.startswith("yt") else api.tiktok.find_user(h_q)
                    st.session_state.update(search_results=res, show_results=True, platform_key=pk); st.rerun()
                except Exception as e: st.error(f"Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.show_results:
        st.markdown('<div style="max-width:900px;margin:40px auto 0 auto;padding:0 12px;">', unsafe_allow_html=True)
        _, list_col, _ = st.columns([1.2, 2.5, 1])
        with list_col:
            st.markdown('<div class="list-divider"></div>', unsafe_allow_html=True)
            if not st.session_state.search_results:
                st.markdown('<p style="text-align:center;color:#6b7280;">No se hallaron resultados.</p>', unsafe_allow_html=True)
            else:
                for i, r in enumerate(st.session_state.search_results):
                    rid = r.get("id", r.get("userId", ""))
                    ravatar = r.get("avatar", r.get("thumbnail", ""))
                    h_label = f"@{r.get('handle', r.get('username', r.get('name', rid)))}".replace("@@", "@")
                    
                    l0, l1 = st.columns([0.18, 0.82])
                    with l0: st.markdown(f'<img src="{ravatar}" class="mini-avatar">', unsafe_allow_html=True)
                    with l1:
                        if st.button(h_label, key=f"sel_{i}"):
                            slug = [v["slug"] for v in PLATFORMS.values() if v["key"] == st.session_state.platform_key][0]
                            st.query_params.update(u=f"{slug}/{rid}")
                            st.session_state.update(user_id=rid, user_name=r.get("name", rid), user_avatar=ravatar, user_handle=r.get("handle", ""), show_results=False, history_values=[], history_times=[])
                            st.rerun()
                    st.markdown('<div style="border-bottom:1px solid rgba(255,255,255,0.03);margin:12px 0;"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
