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

# ──────────────────────────── CSS (v7.0: Hyper-SaaS Glassmorphism) ───────────────────
CSS = (
    "@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800;900&display=swap');"
    
    # Core Base
    "body, .stApp { "
    "   background: radial-gradient(circle at 50% -20%, #1e293b 0%, #020617 100%) !important; "
    "   color: #f8fafc !important; "
    "   font-family: 'Outfit', sans-serif !important; "
    "}"
    "#MainMenu, footer, header { visibility: hidden; }"
    ".main-container { padding: 0; max-width: 1100px; margin: 0 auto; }"
    
    # Hero & Typography
    ".hero-section { text-align: center; padding: 14vh 2rem 6vh; }"
    ".hero-title { font-size: clamp(3.5rem, 9.5vw, 7rem); font-weight: 900; letter-spacing: -6px; color: #fff; margin-bottom: 0.2rem; line-height: 0.85; text-shadow: 0 0 50px rgba(255,255,255,0.05); }"
    ".hero-subtitle { color: #94a3b8; font-size: 1rem; text-transform: uppercase; letter-spacing: 10px; font-weight: 700; margin-bottom: 5rem; opacity: 0.8; }"
    
    # Glassmorphism Box (Search Card)
    ".search-card-container { "
    "   max-width: 900px; margin: 0 auto; "
    "   background: rgba(15, 23, 42, 0.4); "
    "   backdrop-filter: blur(24px) saturate(180%); "
    "   border: 1px solid rgba(255, 255, 255, 0.08); "
    "   border-top: 1px solid rgba(255, 255, 255, 0.15); "
    "   border-radius: 32px; padding: 18px; "
    "   box-shadow: 0 40px 120px rgba(0,0,0,0.8), inset 0 0 0 1px rgba(255,255,255,0.03); "
    "}"
    
    # SaaS Input Overrides
    "div[data-baseweb='select'] > div { background: rgba(0,0,0,0.4) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 14px !important; box-shadow: inset 0 2px 4px rgba(0,0,0,0.2) !important; }"
    "input { background: rgba(0,0,0,0.4) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 14px !important; color: #fff !important; padding: 14px 22px !important; font-size: 1rem !important; transition: all 0.3s ease !important; }"
    "input:focus { border-color: #3b82f6 !important; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15) !important; }"
    
    # Gradient Buttons (The "Wow" Factor)
    "div.stButton > button { "
    "   width: 100% !important; border: 1px solid rgba(255,255,255,0.08) !important; "
    "   background: linear-gradient(145deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.01) 100%) !important; "
    "   color: #cbd5e1 !important; border-radius: 14px !important; "
    "   text-align: left !important; font-size: 1.1rem !important; font-weight: 600 !important; padding: 12px 20px !important; "
    "   text-transform: none !important; transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1) !important; "
    "   box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important; "
    "}"
    "div.stButton > button:hover { "
    "   color: #fff !important; background: rgba(255,255,255,0.08) !important; "
    "   transform: translateY(-2px) !important; box-shadow: 0 8px 24px rgba(0,0,0,0.3) !important; "
    "   border-color: rgba(255,255,255,0.2) !important; "
    "}"
    "div.stButton > button:active { transform: translateY(0px) !important; }"
    
    # Primary Call-to-Action
    "button[kind='primary'] { "
    "   background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important; "
    "   border: none !important; color: #fff !important; font-weight: 800 !important; letter-spacing: 1px !important; "
    "}"
    "button[kind='primary']:hover { "
    "   background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important; "
    "   box-shadow: 0 0 25px rgba(37, 99, 235, 0.4) !important; "
    "}"
    
    # Dashboard Visuals
    ".dashboard-banner { width: 100%; height: 350px; background: linear-gradient(180deg, #020617 0%, #000 100%); border-bottom: 1px solid rgba(255,255,255,0.05); position: relative; overflow: hidden; }"
    ".mesh-gradient { position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle at 50% 50%, rgba(59,130,246,0.1) 0%, transparent 50%), radial-gradient(circle at 20% 80%, rgba(239,68,68,0.05) 0%, transparent 40%); opacity: 0.6; pointer-events: none; }"
    ".profile-overlay { width: 180px; height: 180px; border-radius: 50%; border: 10px solid #020617; position: absolute; bottom: -90px; left: 50%; transform: translateX(-50%); background: #0f172a; z-index: 10; box-shadow: 0 30px 60px rgba(0,0,0,0.8); }"
    ".dashboard-content { padding: 140px 1rem 4rem; text-align: center; }"
    ".main-count { font-size: clamp(5.5rem, 13vw, 11rem); font-weight: 900; color: #fff; letter-spacing: -6px; line-height: 0.8; margin-bottom: 2rem; text-shadow: 0 0 60px rgba(255,255,255,0.08); }"
    ".count-label { color: #94a3b8; font-size: 1.5rem; font-weight: 700; letter-spacing: 6px; text-transform: uppercase; margin-bottom: 6rem; display: flex; align-items: center; justify-content: center; gap: 12px; }"
    
    # Metric Grid
    ".metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; padding: 0 2.5rem; }"
    ".metric-box { "
    "   background: rgba(15, 23, 42, 0.3); border: 1px solid rgba(255,255,255,0.04); border-top: 1px solid rgba(255,255,255,0.08); "
    "   border-radius: 24px; padding: 2.5rem 1.5rem; text-align: center; transition: all 0.5s ease; "
    "   box-shadow: inset 0 0 20px rgba(0,0,0,0.1); "
    "}"
    ".metric-box:hover { background: rgba(30, 41, 59, 0.4); border-color: rgba(255,255,255,0.15); transform: translateY(-12px); box-shadow: 0 30px 70px rgba(0,0,0,0.5); }"
    ".metric-val { font-size: 2.4rem; font-weight: 900; color: #fff; margin-bottom: 0.8rem; letter-spacing: -1px; }"
    ".metric-title { color: #64748b; font-size: 1rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; display: flex; align-items: center; justify-content: center; gap: 12px; }"
    
    # Mini Avatar & List
    ".mini-avatar { width: 52px; height: 52px; border-radius: 14px; object-fit: cover; border: 1px solid rgba(255,255,255,0.15); box-shadow: 0 6px 18px rgba(0,0,0,0.4); }"
    ".list-divider { border-bottom: 1px solid rgba(255,255,255,0.04); margin: 15px 0; width: 100%; }"
)
st.markdown(f"<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@48,700,1,0' /><style>{CSS}</style>", unsafe_allow_html=True)

# ──────────────────────────── PLATFORMS ──────────────────────────────
PLATFORMS = {
    "🔴 YouTube Subs": {"key": "yt_subs", "color": "#FF2B2B", "icon": "subscriptions", "label": "Subscribers", "slug": "youtube-live-subscriber-counter"},
    "🔴 YouTube Views": {"key": "yt_views", "color": "#FF2B2B", "icon": "video_library", "label": "Views", "slug": "youtube-live-view-counter"},
    "🎵 TikTok Follows": {"key": "tt_followers", "color": "#00F5FF", "icon": "music_note", "label": "Followers", "slug": "tiktok-live-follower-counter"},
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
    st.markdown(f'<div class="dashboard-banner"><div class="mesh-gradient" style="background: radial-gradient(circle at 50% 50%, {pinfo["color"]}1a 0%, transparent 60%); opacity:0.8;"></div><img src="{st.session_state.user_avatar}" class="profile-overlay" /></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-container"><div class="dashboard-content">', unsafe_allow_html=True)
    
    display_handle = f"@{st.session_state.user_handle or st.session_state.user_name}".replace("@@", "@")
    st.markdown(f'<h1 style="color:white;font-size:4.5rem;font-weight:900;margin-bottom:0.1rem;letter-spacing:-3px;">{display_handle}</h1>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:{pinfo["color"]};font-size:2.2rem;margin-bottom:5rem;filter:drop-shadow(0 0 15px {pinfo["color"]}40);"><span class="material-symbols-rounded">verified</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="main-count">{fmt(count)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="count-label">{pinfo["label"]} <span class="material-symbols-rounded" style="color:{pinfo["color"]};font-size:1.6rem;vertical-align:middle;margin-left:12px;">groups</span></div>', unsafe_allow_html=True)
    
    if res.get("extra"):
        st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, itm in enumerate(res["extra"][:3]):
            with cols[i]: st.markdown(f'<div class="metric-box"><div class="metric-val">{fmt(itm["v"])}</div><div class="metric-title">{itm["l"]} <span class="material-symbols-rounded" style="color:{pinfo["color"]}cc">{itm["i"]}</span></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if len(st.session_state.history_values) > 1:
        fig = go.Figure(); fig.add_trace(go.Scatter(x=st.session_state.history_times, y=st.session_state.history_values, mode='lines', line=dict(color=pinfo["color"], width=6), fill='tonexty', fillcolor=f"{pinfo['color']}08", showlegend=False))
        fig.update_layout(height=520, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", color="#64748b"), xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=11)), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)", zeroline=False, tickformat=","))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    
    st.markdown('<div style="margin-top:6rem;text-align:center;">', unsafe_allow_html=True)
    if st.button("⬅️ BUSCAR NUEVO CANAL", key="back_btn"): clear_all(); st.rerun()
    st.markdown('</div></div></div>', unsafe_allow_html=True)
    time.sleep(2); st.rerun()

else:
    st.markdown('<div class="main-container"><div class="hero-section"><h1 class="hero-title">Livecounts Elite</h1><p class="hero-subtitle">MÉTRICAS SaaS DE ALTA PRECISIÓN</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="search-card-container">', unsafe_allow_html=True)
    c0, c1, c2 = st.columns([1.2, 2.5, 1])
    with c0: h_pk_label = st.selectbox("P", list(PLATFORMS.keys()), key="h_pk", label_visibility="collapsed")
    with c1: h_q = st.text_input("Q", placeholder="Canal, usuario o video ID...", key="h_q", label_visibility="collapsed")
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
        st.markdown('<div style="max-width:900px;margin:50px auto 0 auto;padding:0 12px;">', unsafe_allow_html=True)
        _, list_col, _ = st.columns([1.2, 2.5, 1])
        with list_col:
            if not st.session_state.search_results:
                st.markdown('<p style="text-align:center;color:#64748b;font-weight:600;">SIN RESULTADOS</p>', unsafe_allow_html=True)
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
                    st.markdown('<div class="list-divider"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
