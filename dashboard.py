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
    page_title="Livecounts Dashboard Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────── Custom CSS ─────────────────────────────
CSS = """
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,1,0" />
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
html, body, [class*="st-"] { font-family: 'Outfit', sans-serif; }
.stApp { background: radial-gradient(circle at top right, #1e293b, #020617 80%); }
#MainMenu, footer, header { visibility: hidden; }
.main-container { padding: 1rem 3rem; }
.counter-box {
    background: linear-gradient(145deg, rgba(30,41,59,0.3), rgba(15,23,42,0.5));
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 36px; padding: 3.5rem 2rem 3rem; text-align: center;
    backdrop-filter: blur(25px); box-shadow: 0 40px 80px -20px rgba(0,0,0,0.6); margin: 1.5rem 0;
}
.digits-row { display: flex; justify-content: center; align-items: center; gap: 8px; margin: 1rem 0; }
.digit-cell {
    display: inline-flex; align-items: center; justify-content: center;
    width: 75px; height: 110px; background: #0f172a; border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px; font-size: 5rem; font-weight: 800; color: #f8fafc;
    font-variant-numeric: tabular-nums; box-shadow: 0 15px 30px rgba(0,0,0,0.7);
}
.digit-cell.up { animation: glow-up 1s; }
.digit-cell.down { animation: glow-down 1s; }
@keyframes glow-up { 50% { color: #22c55e; transform: scale(1.1); box-shadow: 0 0 40px rgba(34,197,94,0.4); } }
@keyframes glow-down { 50% { color: #ef4444; transform: scale(1.1); box-shadow: 0 0 40px rgba(239,68,68,0.4); } }
.digit-sep { font-size: 4rem; font-weight: 800; color: #334155; padding: 0 4px; }
.diff-badge {
    display: inline-flex; align-items: center; gap: 6px; padding: 0.5rem 1.4rem; border-radius: 99px;
    font-size: 1.2rem; font-weight: 800; margin-top: 1.2rem;
}
.diff-up { background: rgba(34,197,94,0.1); color: #4ade80; border: 1px solid rgba(34,197,94,0.2); }
.diff-down { background: rgba(239,68,68,0.1); color: #f87171; border: 1px solid rgba(239,68,68,0.2); }
.counter-label { color: #64748b; font-size: 1.8rem; margin-top: 1.2rem; text-transform: uppercase; letter-spacing: 8px; font-weight: 800; }
.user-name { color: #f8fafc; font-size: 3.2rem; font-weight: 800; }
.user-handle { color: #818cf8; font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0 1.5rem; display: flex; align-items: center; justify-content: center; gap: 8px; }
.metric-card {
    background: rgba(30,41,59,0.4); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 28px; padding: 2.2rem; text-align: center;
    box-shadow: 0 12px 30px rgba(0,0,0,0.4); transition: all 0.4s;
    transform-style: preserve-3d;
}
.metric-card:hover {
    transform: translateY(-12px) perspective(1000px) rotateX(10deg);
    border-color: rgba(255,255,255,0.2); box-shadow: 0 30px 60px rgba(0,0,0,0.6);
}
.metric-value { font-size: 2.5rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.6rem; }
.metric-label { color: #94a3b8; font-size: 1rem; text-transform: uppercase; letter-spacing: 2px; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 10px; }
.metric-icon { font-size: 2rem; transition: transform 0.3s; }
.metric-card:hover .metric-icon { transform: scale(1.3) rotate(5deg); color: #f8fafc; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617 0%, #0f172a 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.05); padding: 1rem;
}
.stPlotlyChart { border-radius: 32px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); }
.live-dot {
    display: inline-block; width: 15px; height: 15px; background: #ef4444; border-radius: 50%;
    margin-right: 12px; animation: pulse 2s infinite; vertical-align: middle;
}
@keyframes pulse { 0%, 100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(239,68,68,0.7); } 50% { transform: scale(1.1); box-shadow: 0 0 0 15px rgba(239,68,68,0); } }
.avatar-img { width: 130px; height: 130px; border-radius: 50%; border: 6px solid rgba(255,255,255,0.1); margin: 0 auto 1.5rem; box-shadow: 0 20px 40px rgba(0,0,0,0.8); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ──────────────────────────── Platforms ───────────────────────────────
PLATFORMS = {
    "🔴 YouTube — Suscriptores": {"key": "yt_subs", "badge": "badge-youtube", "label": "SUSCRIPTORES", "color": "#ef4444", "icon": "subscriptions"},
    "🔴 YouTube — Vistas de Video": {"key": "yt_views", "badge": "badge-youtube", "label": "VISTAS", "color": "#ef4444", "icon": "visibility"},
    "🎵 TikTok — Seguidores": {"key": "tt_followers", "badge": "badge-tiktok", "label": "SEGUIDORES", "color": "#00f2ea", "icon": "music_note"},
}

# ──────────────────────────── Sidebar ────────────────────────────────
with st.sidebar:
    st.markdown('<div style="margin-bottom:2rem;text-align:center;"><span class="material-symbols-rounded" style="font-size:4rem;color:#818cf8;filter: drop-shadow(0 0 15px rgba(129,140,248,0.5));">bubble_chart</span><h2 style="font-weight:800;color:white;margin-top:0.5rem;letter-spacing:-1px;">Livecounts Pro</h2><p style="color:#64748b;font-size:0.8rem;letter-spacing:1px;">ELITE TRACKING SYSTEMS</p></div>', unsafe_allow_html=True)
    selected_platform = st.selectbox("PLATAFORMA", list(PLATFORMS.keys()), index=0)
    platform_info = PLATFORMS[selected_platform]
    query = st.text_input("BUSCAR CANAL / USUARIO", placeholder="Ej: Cristiano")
    search_btn = st.button("OBTENER DATOS EN VIVO", use_container_width=True, type="primary")
    st.markdown("<div style='margin-top:5rem;text-align:center;font-size:0.7rem;color:#334155;'>CORE ENGINE v2.5<br>© 2026 OFFICIAL DASHBOARD</div>", unsafe_allow_html=True)

# ──────────────────────────── State ──────────────────────────────────
defaults = {"user_id": None, "user_name": "", "user_avatar": "", "user_handle": "", "platform_key": "", "prev_count": 0, "search_results": [], "show_results": False, "history_times": [], "history_values": []}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# ──────────────────────────── Helpers ────────────────────────────────
def fmt(n): return f"{int(n):,}".replace(",", ".")
def render_digits(current: int, previous: int) -> str:
    c, p = str(current), str(previous) if previous else str(current)
    m = max(len(c), len(p))
    c, p = c.zfill(m), p.zfill(m)
    diff, cells = current - previous, []
    for i, (cd, pd) in enumerate(zip(c, p)):
        if i > 0 and (m - i) % 3 == 0: cells.append('<span class="digit-sep">.</span>')
        cls = "digit-cell" + (" up" if cd != pd and diff > 0 else " down" if cd != pd else "")
        cells.append(f'<span class="{cls}">{cd}</span>')
    badge = ""
    if previous and diff != 0:
        sign = "+" if diff > 0 else ""
        icon = "trending_up" if diff > 0 else "trending_down"
        badge = f'<div><span class="diff-badge {"diff-up" if diff > 0 else "diff-down"}"><span class="material-symbols-rounded" style="font-size:1.4rem;">{icon}</span> {sign}{fmt(diff)}</span></div>'
    return f'<div class="digits-row">{"".join(cells)}</div>{badge}'

def build_chart(times, values, color, label):
    v_min, v_max = min(values), max(values)
    span = max(v_max - v_min, 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=[v_min - span*0.2]*len(times), mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=times, y=values, mode='lines', line=dict(color=color, width=5, shape='spline', smoothing=0.9), fill='tonexty', fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15)", hovertemplate=f"<b>{label}</b>: %{{y:,.0f}}<extra></extra>", showlegend=False))
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", color="#64748b", size=12), xaxis=dict(showgrid=False, zeroline=False, linecolor="rgba(255,255,255,0.05)"), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.02)", zeroline=False, linecolor="rgba(255,255,255,0.05)", range=[v_min - span*0.2, v_max + span*0.2], tickformat=","))
    return fig

# ──────────────────────────── Main Logic ─────────────────────────────
if search_btn and query:
    try:
        pk = platform_info["key"]
        if pk.startswith("yt"): results = [{"id": r["id"], "name": r["name"], "avatar": r.get("avatar","")} for r in (api.youtube.find_channel(query) if pk=="yt_subs" else api.youtube.find_video(query))]
        elif pk == "tt_followers": results = [{"id": r.user_id, "handle": r.username, "name": r.display_name, "avatar": r.thumbnail} for r in api.tiktok.find_user(query)]
        st.session_state.update(search_results=results, show_results=True, platform_key=pk, user_id=None, prev_count=0, history_times=[], history_values=[])
    except Exception as e: st.error(f"Error: {e}")

if st.session_state.show_results and not st.session_state.user_id:
    for i, r in enumerate(st.session_state.search_results):
        if st.button(f"🚀 {r['name']} ({r.get('handle', r['id'][:10])})", key=f"sel_{i}", use_container_width=True):
            st.session_state.update(user_id=r["id"], user_name=r["name"], user_avatar=r.get("avatar",""), user_handle=r.get("handle",""), show_results=False, prev_count=0, history_times=[], history_values=[]); st.rerun()

elif st.session_state.user_id:
    try:
        pk = st.session_state.platform_key
        dat = get_metrics(st.session_state.user_id, pk) if "get_metrics" in globals() else (api.youtube.fetch_channel_metrics(st.session_state.user_id) if pk=="yt_subs" else api.tiktok.fetch_user_metrics(st.session_state.user_id))
        # Handle different API return formats from previous versions
        if isinstance(dat, dict):
            main_count = dat.get("main", dat.get("followers", 0))
            label = dat.get("label", "SEGUIDORES")
            extra = dat.get("extra", [])
        else: main_count, label, extra = 0, "ERROR", []

        st.session_state.history_times.append(datetime.now().strftime("%H:%M:%S"))
        st.session_state.history_values.append(main_count)
        if len(st.session_state.history_times) > 100: st.session_state.history_times, st.session_state.history_values = st.session_state.history_times[-100:], st.session_state.history_values[-100:]

        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center;"><span class="live-dot"></span><span style="color:#ef4444;font-weight:900;letter-spacing:8px;font-size:1.1rem;">LIVE MONITORING</span></div>', unsafe_allow_html=True)
        
        avatar = f'<img src="{st.session_state.user_avatar}" class="avatar-img" />' if st.session_state.user_avatar else ""
        handle = f'<div class="user-handle"><span class="material-symbols-rounded">stars</span> @{st.session_state.user_handle}</div>' if st.session_state.user_handle else ""

        st.markdown(f'<div class="counter-box"><div style="display:flex;justify-content:center;margin-bottom:1.5rem;"><span style="background:rgba(255,255,255,0.05);padding:0.6rem 1.8rem;border-radius:99px;font-weight:900;letter-spacing:3px;font-size:0.8rem;color:#94a3b8;border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;gap:10px;"><span class="material-symbols-rounded" style="color:#818cf8;">{platform_info["icon"]}</span>{selected_platform.split("—")[0]}</span></div>{avatar}<div class="user-name">{st.session_state.user_name}</div>{handle}{render_digits(main_count, st.session_state.prev_count)}<div class="counter-label">{label}</div></div>', unsafe_allow_html=True)
        st.session_state.prev_count = main_count

        if extra:
            st.markdown("<div style='margin:3rem 0;'></div>", unsafe_allow_html=True)
            cols = st.columns(len(extra))
            for i, itm in enumerate(extra):
                # Adaptive for both dict formats
                v, l, ci = (itm["val"], itm["lbl"], itm["ico"]) if isinstance(itm, dict) else (itm[0], itm[1], itm[2] if len(itm)>2 else "stat_1")
                with cols[i]: st.markdown(f'<div class="metric-card"><div class="metric-value">{fmt(v)}</div><div class="metric-label"><span class="material-symbols-rounded metric-icon">{ci}</span>{l}</div></div>', unsafe_allow_html=True)

        if len(st.session_state.history_values) >= 2:
            st.markdown("<div style='margin-top:4rem;'></div>", unsafe_allow_html=True)
            st.plotly_chart(build_chart(st.session_state.history_times, st.session_state.history_values, platform_info["color"], label), use_container_width=True, config={"displayModeBar": False})

        st.markdown("<div style='margin-top:4rem;text-align:center;'>", unsafe_allow_html=True)
        if st.button("🔄 DESCONECTAR Y CAMBIAR CANAL", use_container_width=False):
            st.session_state.update(user_id=None, show_results=True, prev_count=0, history_times=[], history_values=[]); st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)
        time.sleep(2); st.rerun()
    except Exception as e: st.error(f"Error de actualización: {e}"); time.sleep(5); st.rerun()

else:
    st.markdown('<div style="text-align:center;padding:12rem 2rem;"><div class="material-symbols-rounded" style="font-size:12rem;margin-bottom:2rem;background:linear-gradient(135deg, #818cf8, #c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter: drop-shadow(0 0 40px rgba(129,140,248,0.4));">rocket_launch</div><div style="color:white;font-size:3.5rem;font-weight:900;letter-spacing:-2px;margin-bottom:0.5rem;">SISTEMA LISTO</div><div style="color:#94a3b8;font-size:1.4rem;font-weight:300;letter-spacing:1px;">Selecciona una plataforma en el panel lateral para iniciar el monitoreo.</div></div>', unsafe_allow_html=True)

def get_metrics(uid, pk):
    try:
        if pk == "yt_subs":
            raw = send_request(f"{YOUTUBE_CHANNEL_STATS_API}/{uid}")
            subs = raw.get("followerCount", 0)
            b = raw.get("bottomOdos", [0,0,0,0])
            return {"main": subs, "label": "SUSCRIPTORES", "extra": [{"val": b[0], "lbl": "CANAL VISTAS", "ico": "visibility"}, {"val": b[2], "lbl": "VIDEOS", "ico": "movie_filter"}, {"val": _goal(subs), "lbl": "META", "ico": "stars"}]}
        elif pk == "yt_views":
            raw = send_request(f"{YOUTUBE_VIDEO_STATS_API}/{uid}")
            views = raw.get("followerCount", 0)
            b = raw.get("bottomOdos", [0,0,0])
            return {"main": views, "label": "VISTAS", "extra": [{"val": b[0], "lbl": "LIKES", "ico": "thumb_up"}, {"val": b[2], "lbl": "COMENTARIOS", "ico": "forum"}]}
        elif pk == "tt_followers":
            m = api.tiktok.fetch_user_metrics(uid)
            return {"main": m["followers"], "label": "SEGUIDORES", "extra": [{"val": m.get("likes",0), "lbl": "LIKES", "ico": "favorite"}, {"val": m.get("following",0), "lbl": "SIGUIENDO", "ico": "group"}, {"val": m.get("videos",0), "lbl": "VIDEOS", "ico": "video_library"}]}
    except: return {"main": 0, "label": "ERR", "extra": []}
def _goal(n):
    if not n: return 1000
    mag = 10 ** (len(str(int(n))) - 1)
    return ((int(n) // mag) + 1) * mag
