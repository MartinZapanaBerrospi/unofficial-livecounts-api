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
    page_title="Livecounts Pro Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────── Elite 3D CSS ───────────────────────────
# Minified CSS with Neumorphic/Glassmorphic Elite Effects
CSS = (
    "font-family:'Outfit',sans-serif;.stApp{background:radial-gradient(circle at top right,#1e293b,#020617 90%)}"
    "#MainMenu,footer,header{visibility:hidden}.main-container{padding:1rem 5vw;max-width:1400px;margin:0 auto}"
    ".counter-box{background:linear-gradient(135deg,rgba(30,41,59,0.4),rgba(15,23,42,0.6));border:1px solid rgba(255,255,255,0.1);"
    "border-radius:48px;padding:clamp(2rem,5vw,5rem) 2rem;text-align:center;backdrop-filter:blur(40px);"
    "box-shadow:20px 20px 60px #01040a,-20px -20px 60px #030a1c,inset 0 1px 1px rgba(255,255,255,0.1);margin:2rem 0}"
    ".digits-row{display:flex;justify-content:center;align-items:center;gap:clamp(4px,1vw,12px);margin:1.5rem 0;flex-wrap:wrap}"
    ".digit-cell{display:inline-flex;align-items:center;justify-content:center;width:clamp(50px,9vw,90px);height:clamp(80px,14vw,140px);"
    "background:#0f172a;border:1px solid rgba(255,255,255,0.1);border-radius:clamp(16px,2vw,32px);font-size:clamp(3.5rem,7vw,8rem);font-weight:900;color:#f8fafc;"
    "font-variant-numeric:tabular-nums;box-shadow:inset 6px 6px 12px #01040a,inset -6px -6px 12px #030a1c,0 20px 40px rgba(0,0,0,0.8)}"
    ".digit-sep{font-size:clamp(3rem,5vw,5.5rem);font-weight:900;color:#334155;margin:0 4px}"
    ".metric-card{background:rgba(30,41,59,0.4);border:1px solid rgba(255,255,255,0.08);border-radius:36px;padding:2.5rem 1.5rem;text-align:center;"
    "box-shadow:12px 12px 24px #01040a,-12px -12px 24px #030a1c;transition:all 0.4s;transform-style:preserve-3d;margin-bottom:1.5rem}"
    ".metric-card:hover{transform:translateY(-15px) perspective(1000px) rotateX(10deg);border-color:rgba(129,140,248,0.4);box-shadow:0 40px 80px rgba(0,0,0,0.8)}"
    ".metric-value{font-size:clamp(2.2rem,4vw,3.5rem);font-weight:900;color:#f8fafc;letter-spacing:-2px;margin-bottom:0.8rem}"
    ".metric-label{color:#94a3b8;font-size:1rem;text-transform:uppercase;letter-spacing:3px;font-weight:800;display:flex;align-items:center;justify-content:center;gap:12px}"
    ".icon-3d{font-size:2.8rem!important;background:linear-gradient(135deg,#818cf8,#c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
    "filter:drop-shadow(0 4px 8px rgba(0,0,0,0.5));transition:all 0.3s} .metric-card:hover .icon-3d{transform:scale(1.3) translateZ(30px) rotate(5deg)}"
    "[data-testid='stSidebar']{background:linear-gradient(180deg,#020617 0%,#0f172a 100%)!important;border-right:1px solid rgba(255,255,255,0.05)}"
    ".hero-box{background:rgba(15,23,42,0.6);border:1px solid rgba(255,255,255,0.1);border-radius:56px;padding:clamp(4rem,10vw,8rem) 2rem;text-align:center;"
    "backdrop-filter:blur(50px);max-width:1000px;margin:3rem auto;box-shadow:0 80px 160px rgba(0,0,0,0.9)} "
    ".hero-title{font-size:clamp(3.5rem,10vw,6rem);font-weight:900;letter-spacing:-4px;background:linear-gradient(135deg,#fff,#818cf8); "
    "-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 30px rgba(129,140,248,0.5))}"
    ".live-dot{display:inline-block;width:18px;height:18px;background:#f43f5e;border-radius:50%;margin-right:18px;animation:pulse 2s infinite;vertical-align:middle}"
    "@keyframes pulse{0%,100%{transform:scale(0.9);box-shadow:0 0 0 0 rgba(244,63,94,0.7)}50%{transform:scale(1.2);box-shadow:0 0 0 30px rgba(244,63,94,0)}}"
    "@media(max-width:768px){.digit-cell{width:60px;height:100px;font-size:4rem}.user-name{font-size:2.8rem}.counter-label{font-size:1.4rem}}"
    ".stSelectbox [data-baseweb='select']{border-radius:16px!important;background:rgba(255,255,255,0.05)!important;border:1px solid rgba(255,255,255,0.1)!important}"
    ".stButton button{border-radius:20px!important;font-weight:900!important;letter-spacing:1px!important;padding:0.8rem 2rem!important}"
)

st.markdown(f"<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@48,700,1,0' /><style>{CSS}</style>", unsafe_allow_html=True)

# ──────────────────────────── PLATFORMS ──────────────────────────────
PLATFORMS = {
    "🔴 YouTube — Suscriptores": {"key": "yt_subs", "color": "#ef4444", "icon": "subscriptions", "title": "YT SUBS"},
    "🔴 YouTube — Vistas de Video": {"key": "yt_views", "color": "#ef4444", "icon": "video_library", "title": "YT VIEWS"},
    "🎵 TikTok — Seguidores": {"key": "tt_followers", "color": "#00f2ea", "icon": "music_note", "title": "TT FOLLOWS"},
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
            return {"main": val, "label": "SUSCRIPTORES", 
                    "extra": [{"v": b[0], "l": "CANAL VISTAS", "i": "visibility"}, 
                             {"v": b[2], "l": "VIDEOS", "i": "video_library"}, 
                             {"v": _goal(val), "l": "META (GOAL)", "i": "ads_click"}]}
        elif pk == "yt_views":
            r = send_request(f"{YOUTUBE_VIDEO_STATS_API}/{uid}")
            val = r.get("followerCount", 0)
            b = r.get("bottomOdos", [0,0,0,0])
            return {"main": val, "label": "VISTAS", 
                    "extra": [{"v": b[0], "l": "LIKES", "i": "favorite"}, 
                             {"v": b[1] if len(b)>1 else 0, "l": "DISLIKES", "i": "thumb_down"}, 
                             {"v": b[2] if len(b)>2 else 0, "l": "COMENTARIOS", "i": "forum"}]}
        elif pk == "tt_followers":
            m = api.tiktok.fetch_user_metrics(uid)
            return {"main": m["followers"], "label": "SEGUIDORES", 
                    "extra": [{"v": m["likes"], "l": "LIKES", "i": "favorite"}, 
                             {"v": m["following"], "l": "SIGUIENDO", "i": "group"}, 
                             {"v": m["videos"], "l": "VIDEOS", "i": "movie"}]}
    except Exception as e: return {"error": str(e)}

def render_digits(curr, prev):
    c, p = str(curr), str(prev) if prev else str(curr)
    m = max(len(c), len(p))
    c, p = c.zfill(m), p.zfill(m)
    diff, cells = curr - prev, []
    for i, (cd, pd) in enumerate(zip(c, p)):
        if i > 0 and (m - i) % 3 == 0: cells.append('<span class="digit-sep">.</span>')
        cls = "digit-cell" + (" up" if cd != pd and diff > 0 else " down" if cd != pd else "")
        cells.append(f'<span class="{cls}">{cd}</span>')
    badge = ""
    if prev and diff != 0:
        sign, icon = ("+", "trending_up") if diff > 0 else ("", "trending_down")
        color = "#4ade80" if diff > 0 else "#fb7185"
        badge = f'<div style="margin-top:2rem;"><span style="background:rgba(255,255,255,0.05);padding:0.8rem 2rem;border-radius:99px;font-weight:900;font-size:1.5rem;color:{color};border:2px solid {color}33;display:inline-flex;align-items:center;gap:12px;box-shadow:0 10px 30px rgba(0,0,0,0.5);"><span class="material-symbols-rounded">{icon}</span> {sign}{fmt(diff)}</span></div>'
    return f'<div class="digits-row">{"".join(cells)}</div>{badge}'

def build_chart(times, values, color):
    v_min, v_max = min(values), max(values)
    span = max(v_max - v_min, 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=values, mode='lines', line=dict(color=color, width=8, shape='spline', smoothing=1.3), fill='tonexty', fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15)", hovertemplate="<b>Valor</b>: %{y:,.0f}<extra></extra>", showlegend=False))
    fig.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", color="#64748b", size=14), xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.02)", range=[v_min - span*0.2, v_max + span*0.2], tickformat=","))
    return fig

# ──────────────────────────── STATE ──────────────────────────────────
defaults = {"user_id": None, "user_name": "", "user_avatar": "", "user_handle": "", "platform_key": "", "prev_count": 0, "search_results": [], "show_results": False, "history_times": [], "history_values": []}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# ──────────────────────────── SIDEBAR ────────────────────────────────
with st.sidebar:
    st.markdown('<div style="margin-bottom:3rem;text-align:center;"><span class="material-symbols-rounded" style="font-size:6rem;color:#818cf8;filter:drop-shadow(0 0 25px rgba(129,140,248,0.6));">rocket_launch</span><h1 style="font-weight:900;color:white;margin-top:0.5rem;letter-spacing:-2px;font-size:2.2rem;">LivePro</h1><p style="color:#64748b;font-weight:800;letter-spacing:4px;font-size:0.8rem;">ENGINE v3.8</p></div>', unsafe_allow_html=True)
    sel_pk = st.selectbox("PLATAFORMA", list(PLATFORMS.keys()), index=0, key="s_pk")
    sel_q = st.text_input("BÚSQUEDA RÁPIDA", placeholder="Ej: Cristiano", key="s_q")
    if st.button("DESPLEGAR ⚡", use_container_width=True, type="primary"):
        if sel_q:
            pk = PLATFORMS[sel_pk]["key"]
            try:
                if pk.startswith("yt"): res = (api.youtube.find_channel(sel_q) if pk=="yt_subs" else api.youtube.find_video(sel_q))
                else: res = [{"user_id": r.user_id, "id": r.username, "name": r.display_name, "avatar": r.thumbnail} for r in api.tiktok.find_user(sel_q)]
                st.session_state.update(search_results=res, show_results=True, platform_key=pk, user_id=None, prev_count=0, history_times=[], history_values=[])
                st.rerun()
            except: st.error("Error en búsqueda rápida")

# ──────────────────────────── MAIN LOGIC ─────────────────────────────
if st.session_state.show_results and not st.session_state.user_id:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center;color:white;font-weight:900;font-size:3rem;margin-bottom:3rem;letter-spacing:-2px;">SELECCIONA UN RESULTADO</h1>', unsafe_allow_html=True)
    for i, r in enumerate(st.session_state.search_results):
        # yt search returns dicts with 'id', 'name', 'avatar'. tiktok returns objects.
        rid = r.get("id") if isinstance(r, dict) else r.get("user_id")
        rname = r.get("name") if isinstance(r, dict) else r.get("name")
        ravatar = r.get("avatar") if isinstance(r, dict) else r.get("avatar")
        rhandle = r.get("handle", rid[:10])
        if st.button(f"🔥 {rname} ({rhandle})", key=f"btn_{i}", use_container_width=True):
            st.session_state.update(user_id=rid, user_name=rname, user_avatar=ravatar, user_handle=rhandle, show_results=False, prev_count=0, history_times=[], history_values=[]); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.user_id:
    data = fetch_live_data(st.session_state.user_id, st.session_state.platform_key)
    if "error" in data:
        st.error(f"Error sincronizando datos: {data['error']}"); time.sleep(5); st.rerun()
    
    count = data["main"]
    st.session_state.history_times.append(datetime.now().strftime("%H:%M:%S"))
    st.session_state.history_values.append(count)
    if len(st.session_state.history_times) > 120: st.session_state.history_times, st.session_state.history_values = st.session_state.history_times[-120:], st.session_state.history_values[-120:]

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;margin-bottom:1.5rem;"><span class="live-dot"></span><span style="color:#f43f5e;font-weight:900;letter-spacing:12px;font-size:1.3rem;">DATA LIVE FEED</span></div>', unsafe_allow_html=True)
    
    avatar = f'<img src="{st.session_state.user_avatar}" style="width:160px;height:160px;border-radius:50%;border:8px solid rgba(255,255,255,0.1);margin:0 auto 2rem;display:block;box-shadow:0 40px 80px rgba(0,0,0,0.8);" />' if st.session_state.user_avatar else ""
    handle = f'<div style="color:#818cf8;font-size:1.8rem;font-weight:800;display:flex;align-items:center;justify-content:center;gap:15px;margin-bottom:2rem;"><span class="material-symbols-rounded" style="color:#818cf8;font-size:2rem;">verified</span> @{st.session_state.user_handle}</div>' if st.session_state.user_handle else ""

    pinfo = [v for v in PLATFORMS.values() if v["key"] == st.session_state.platform_key][0]
    st.markdown(f'<div class="counter-box"><div style="display:flex;justify-content:center;margin-bottom:2.5rem;"><span style="background:rgba(129,140,248,0.1);padding:0.8rem 2.5rem;border-radius:99px;font-weight:900;letter-spacing:4px;font-size:1rem;color:#f8fafc;border:2px solid rgba(129,140,248,0.3);display:flex;align-items:center;gap:15px;box-shadow:0 15px 30px rgba(0,0,0,0.5);"><span class="material-symbols-rounded" style="color:#818cf8;font-size:1.8rem;">{pinfo["icon"]}</span>{pinfo["title"]}</span></div>{avatar}<div style="color:white;font-size:4.5rem;font-weight:900;letter-spacing:-2px;line-height:1;">{st.session_state.user_name}</div>{handle}{render_digits(count, st.session_state.prev_count)}<div style="color:#64748b;font-size:2.2rem;font-weight:900;letter-spacing:10px;margin-top:2.5rem;text-transform:uppercase;">TOTAL {data["label"]}</div></div>', unsafe_allow_html=True)
    st.session_state.prev_count = count

    if data.get("extra"):
        st.markdown("<div style='margin:4rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(len(data["extra"]))
        for i, item in enumerate(data["extra"]):
            with cols[i]: st.markdown(f'<div class="metric-card"><div class="metric-value">{fmt(item["v"])}</div><div class="metric-label"><span class="material-symbols-rounded icon-3d">{item["i"]}</span> {item["l"]}</div></div>', unsafe_allow_html=True)

    if len(st.session_state.history_values) >= 2:
        st.plotly_chart(build_chart(st.session_state.history_times, st.session_state.history_values, pinfo["color"]), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:5rem;text-align:center;'>", unsafe_allow_html=True)
    if st.button("💥 DESCONECTAR Y CAMBIAR", type="secondary"):
        st.session_state.update(user_id=None, show_results=False, prev_count=0, history_times=[], history_values=[]); st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
    time.sleep(2); st.rerun()

else:
    st.markdown('<div class="main-container"><div class="hero-box"><div class="material-symbols-rounded" style="font-size:12rem;background:linear-gradient(135deg,#818cf8,#c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 45px rgba(129,140,248,0.5));margin-bottom:3rem;">rocket_launch</div><h1 class="hero-title">SISTEMA LISTO</h1><p style="color:#94a3b8;font-size:1.8rem;font-weight:300;margin-bottom:5rem;letter-spacing:2px;max-width:700px;margin-left:auto;margin-right:auto;">Analítica de máxima precisión en tiempo real para YouTubers y Creadores Elite.</p>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2.5])
    with c1: h_pk = st.selectbox("PLATAFORMA", list(PLATFORMS.keys()), key="h_pk", label_visibility="collapsed")
    with c2: h_q = st.text_input("BUSCAR NOMBRE O URL", placeholder="Ej: Cristiano Ronaldo o ID del Canal", key="h_q", label_visibility="collapsed")
    if st.button("INICIAR MOTOR DE DATOS ⚡", use_container_width=True, type="primary"):
        if h_q:
            pk = PLATFORMS[h_pk]["key"]
            try:
                if pk.startswith("yt"): res = (api.youtube.find_channel(h_q) if pk=="yt_subs" else api.youtube.find_video(h_q))
                else: res = [{"user_id": r.user_id, "id": r.username, "name": r.display_name, "avatar": r.thumbnail} for r in api.tiktok.find_user(h_q)]
                st.session_state.update(search_results=res, show_results=True, platform_key=pk, user_id=None, prev_count=0, history_times=[], history_values=[])
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")
    st.markdown('</div></div>', unsafe_allow_html=True)
