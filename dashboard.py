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

# ──────────────────────────── CSS (v8.0: Lux-Branding Centered) ─────────────────────
CSS = (
    "@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800;900&display=swap');"
    
    # Core Base
    "body, .stApp { "
    "   background: #050505 !important; "
    "   color: #f8fafc !important; "
    "   font-family: 'Outfit', sans-serif !important; "
    "}"
    "#MainMenu, footer, header { visibility: hidden; }"
    ".main-container { padding: 0; max-width: 1200px; margin: 0 auto; }"
    
    # Hero & Search Row
    ".hero-section { text-align: center; padding: 12vh 2rem 5vh; }"
    ".hero-title { font-size: clamp(3.2rem, 8vw, 6.5rem); font-weight: 900; letter-spacing: -5px; color: #fff; line-height: 0.9; margin-bottom: 0.5rem; }"
    ".hero-subtitle { color: #64748b; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 8px; font-weight: 700; margin-bottom: 4rem; }"
    
    # Input Styling
    "div[data-baseweb='select'] > div { background: #0f172a !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 12px !important; height: 52px !important; }"
    "div[data-testid='stTextInput'] input { background: #0f172a !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 12px !important; color: #fff !important; height: 52px !important; font-size: 1rem !important; }"
    "div[data-baseweb='select'] input { padding: 0 !important; width: 0 !important; height: 0 !important; }"
    
    # Buttons
    "div.stButton > button { "
    "   border-radius: 12px !important; height: 52px !important; font-weight: 700 !important; "
    "   background: rgba(255,255,255,0.05) !important; color: #fff !important; border: 1px solid rgba(255,255,255,0.1) !important; "
    "   transition: all 0.3s ease !important; "
    "}"
    "div.stButton > button:hover { background: rgba(255,255,255,0.1) !important; transform: translateY(-2px); }"
    "button[kind='primary'] { background: #1d4ed8 !important; border: none !important; }"
    
    # DASHBOARD BRANDING (v8.0)
    ".banner-section { width: 100%; height: 320px; position: relative; overflow: hidden; background: #111; }"
    ".banner-img { width: 100%; height: 100%; object-fit: cover; filter: brightness(0.6); }"
    ".centered-avatar-box { position: absolute; bottom: -80px; left: 50%; transform: translateX(-50%); z-index: 100; }"
    ".main-avatar { width: 160px; height: 160px; border-radius: 50%; border: 4px solid #FF2B2B; box-shadow: 0 20px 50px rgba(0,0,0,0.8); object-fit: cover; background: #000; }"
    
    ".dashboard-header { text-align: center; padding-top: 100px; padding-bottom: 50px; position: relative; }"
    ".channel-name { font-size: 3rem; font-weight: 800; color: #cbd5e1; margin-bottom: 1rem; background: rgba(255,255,255,0.05); padding: 5px 20px; border-radius: 8px; display: inline-block; }"
    ".platform-badge { font-size: 1.5rem; color: #FF2B2B; margin-bottom: 3rem; }"
    ".mega-count { font-size: clamp(6rem, 15vw, 12rem); font-weight: 900; color: #fff; line-height: 0.8; letter-spacing: -5px; margin-bottom: 1rem; }"
    ".mega-label { font-size: 1.2rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 4px; }"
    
    # METRIC BOXES (Pixel-Perfect Image Match)
    ".metric-container { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 60px; padding: 0 1rem; }"
    ".lux-metric-box { "
    "   background: rgba(0,0,0,0.4); border: 2px solid rgba(255,255,255,0.15); border-radius: 8px; "
    "   padding: 2.5rem 1rem; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 8px; "
    "}"
    ".lux-val { font-size: 2.8rem; font-weight: 800; color: #fff; letter-spacing: -1px; }"
    ".lux-title { color: #3b82f6; font-size: 1rem; font-weight: 700; display: flex; align-items: center; gap: 8px; text-transform: none; }"
    
    # Graph & Back
    ".stPlotlyChart { margin-top: 60px; padding: 0 10px; }"
    ".back-container { margin-top: 80px; text-align: center; padding-bottom: 100px; }"
    
    # Search List
    ".mini-avatar { width: 52px; height: 52px; border-radius: 14px; object-fit: cover; border: 1px solid rgba(255,255,255,0.1); }"
    ".list-divider { border-bottom: 1px solid rgba(255,255,255,0.05); margin: 15px 0; }"
)
st.markdown(f"<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@48,700,1,0' /><style>{CSS}</style>", unsafe_allow_html=True)

# ──────────────────────────── PLATFORMS ──────────────────────────────
PLATFORMS = {
    "🔴 YouTube Subs": {"key": "yt_subs", "color": "#FF2B2B", "icon": "subscriptions", "label": "Subscribers", "slug": "youtube-live-subscriber-counter", "tag": "youtube"},
    "🔴 YouTube Views": {"key": "yt_views", "color": "#FF2B2B", "icon": "video_library", "label": "Views", "slug": "youtube-live-view-counter", "tag": "youtube"},
    "🎵 TikTok Follows": {"key": "tt_followers", "color": "#00F5FF", "icon": "music_note", "label": "Followers", "slug": "tiktok-live-follower-counter", "tag": "tiktok"},
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

defaults = {"user_id": None, "user_name": "", "user_avatar": "", "user_banner": None, "user_handle": "", "platform_key": "yt_subs", "history_values": [], "history_times": [], "show_results": False, "search_results": []}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

if st.session_state.user_id != target_uid:
    st.session_state.update(user_id=target_uid, platform_key=target_pk, user_name="", user_avatar="", user_banner=None, user_handle="", history_values=[], history_times=[])

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
            return {"main": val, "extra": [{"v": b[0], "l": "Channel Views", "i": "visibility"}, {"v": b[1] if b[1]>0 else b[2], "l": "Videos", "i": "movie"}, {"v": _goal(val), "l": "Goal", "i": "track_changes"}]}
        elif pk == "yt_views":
            r = send_request(f"{YOUTUBE_VIDEO_STATS_API}/{uid}")
            val = r.get("followerCount", 0)
            b = r.get("bottomOdos", [0,0,0])
            return {"main": val, "extra": [{"v": b[0], "l": "Likes", "i": "favorite"}, {"v": b[1] if len(b)>1 else 0, "l": "Dislikes", "i": "thumb_down"}, {"v": b[2] if len(b)>2 else 0, "l": "Comments", "i": "forum"}]}
        elif pk == "tt_followers":
            m = api.tiktok.fetch_user_metrics(uid)
            return {"main": m["followers"], "extra": [{"v": m["likes"], "l": "Likes", "i": "favorite"}, {"v": m["following"], "l": "Following", "i": "group"}, {"v": m["videos"], "l": "Videos", "i": "video_library"}]}
    except Exception as e: return {"error": f"Connection Error: {e}"}

def clear_all():
    st.session_state.update(user_id=None, show_results=False, history_values=[], history_times=[])
    st.query_params.clear()

def hex_to_rgba(hex_str, opacity):
    h = hex_str.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({rgb[0]},{rgb[1]},{rgb[2]},{opacity})'

# ──────────────────────────── UI ─────────────────────────────────────
if st.session_state.user_id:
    # Fetch Metadata (Banner & Verification) if missing
    if not st.session_state.user_name or st.session_state.user_banner is None:
        try:
            pk = st.session_state.platform_key
            if pk.startswith("yt"):
                meta = api.youtube.fetch_metadata(st.session_state.user_id, pk)
                st.session_state.user_banner = meta.get("banner")
                # Also find name/avatar if missing
                found = (api.youtube.find_channel(st.session_state.user_id) if pk=="yt_subs" else api.youtube.find_video(st.session_state.user_id))
                for r in found:
                    if r.get("id") == st.session_state.user_id:
                        st.session_state.update(user_name=r.get("name"), user_avatar=r.get("avatar"))
                        break
            else: # TikTok
                st.session_state.user_banner = "https://www.tiktok.com/static/images/tiktok_logo_black.png" # Fallback
        except: pass

    res = fetch_live_data(st.session_state.user_id, st.session_state.platform_key)
    if "error" in res:
        st.error(res["error"]); st.button("🔄 RETRY", on_click=st.rerun); st.button("⬅️ BACK", on_click=clear_all); st.stop()
    
    count = res["main"]
    st.session_state.history_times.append(datetime.now().strftime("%H:%M:%S"))
    st.session_state.history_values.append(count)
    if len(st.session_state.history_times) > 100:
        st.session_state.history_times = st.session_state.history_times[-100:]
        st.session_state.history_values = st.session_state.history_values[-100:]

    pinfo = [v for k,v in PLATFORMS.items() if v["key"]==st.session_state.platform_key][0]
    
    # BRANDING SECTION (v8.0)
    banner_url = st.session_state.user_banner or "https://images.unsplash.com/photo-1614850523296-d8c1af93d400?q=80&w=2070&auto=format&fit=crop"
    st.markdown('<div class="banner-section">', unsafe_allow_html=True)
    st.markdown(f'<img src="{banner_url}" class="banner-img">', unsafe_allow_html=True)
    st.markdown(f'<div class="centered-avatar-box"><img src="{st.session_state.user_avatar}" class="main-avatar" style="border-color:{pinfo["color"]};"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="main-container"><div class="dashboard-header">', unsafe_allow_html=True)
    st.markdown(f'<div class="channel-name">{st.session_state.user_name}</div>', unsafe_allow_html=True)
    
    # Platform Icon Badge
    if pinfo["tag"] == "youtube":
        st.markdown('<div class="platform-badge" style="color:#FF0000;"><span class="material-symbols-rounded">play_circle</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="platform-badge" style="color:#00F5FF;"><span class="material-symbols-rounded">music_note</span></div>', unsafe_allow_html=True)
        
    st.markdown(f'<div class="mega-count">{fmt(count)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mega-label">{pinfo["label"]} <span class="material-symbols-rounded" style="font-size:1.2rem;vertical-align:middle;margin-left:8px;">groups</span></div>', unsafe_allow_html=True)
    
    # LUX METRIC GRID (Pixel Match)
    if res.get("extra"):
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, itm in enumerate(res["extra"][:3]):
            with cols[i]:
                st.markdown(f'''
                    <div class="lux-metric-box">
                        <div class="lux-val">{fmt(itm["v"])}</div>
                        <div class="lux-title">{itm["l"]} <span class="material-symbols-rounded" style="font-size:1rem;color:{pinfo["color"]}aa;">{itm["i"]}</span></div>
                    </div>
                ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Plotly Graph
    if len(st.session_state.history_values) > 1:
        fig = go.Figure(); fig.add_trace(go.Scatter(x=st.session_state.history_times, y=st.session_state.history_values, mode='lines', line=dict(color=pinfo["color"], width=6), fill='tonexty', fillcolor=hex_to_rgba(pinfo['color'], 0.1), showlegend=False))
        fig.update_layout(height=420, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", color="#475569"), xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)", zeroline=False, tickformat=","))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    
    # Back Button
    st.markdown('<div class="back-container">', unsafe_allow_html=True)
    if st.button("⬅️ SEARCH ANOTHER CREATOR"): clear_all(); st.rerun()
    st.markdown('</div></div></div>', unsafe_allow_html=True)
    time.sleep(2); st.rerun()

else:
    st.markdown('<div class="main-container"><div class="hero-section"><h1 class="hero-title">Livecounts Elite</h1><p class="hero-subtitle">PREMIUM DASHBOARD ARCHITECTURE</p>', unsafe_allow_html=True)
    
    c0, c1, c2 = st.columns([1.2, 2.5, 1])
    with c0: h_pk_label = st.selectbox("P", list(PLATFORMS.keys()), key="h_pk", label_visibility="collapsed")
    with c1: h_q = st.text_input("Q", placeholder="Enter Channel ID or Name...", key="h_q", label_visibility="collapsed")
    with c2: 
        if st.button("SEARCH ⚡", use_container_width=True, type="primary"):
            if h_q:
                pk = PLATFORMS[h_pk_label]["key"]
                try:
                    res = (api.youtube.find_channel(h_q) if pk=="yt_subs" else api.youtube.find_video(h_q)) if pk.startswith("yt") else api.tiktok.find_user(h_q)
                    st.session_state.update(search_results=res, show_results=True, platform_key=pk); st.rerun()
                except Exception as e: st.error(f"Error: {e}")
    
    if st.session_state.show_results:
        st.markdown('<div style="max-width:900px;margin:40px auto 0 auto;padding:0 12px;">', unsafe_allow_html=True)
        _, list_col, _ = st.columns([1.2, 2.5, 1])
        with list_col:
            if not st.session_state.search_results:
                st.markdown('<p style="text-align:center;color:#64748b;">NO RESULTS FOUND</p>', unsafe_allow_html=True)
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
                            st.session_state.update(user_id=rid, user_name=r.get("name", rid), user_avatar=ravatar, show_results=False, history_values=[], history_times=[])
                            st.rerun()
                    st.markdown('<div class="list-divider"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
