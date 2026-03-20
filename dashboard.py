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

# ──────────────────────────── Definitive CSS Fix ─────────────────────
# Minified CSS to prevent Streamlit Markdown misinterpretation
RAW_CSS = (
    "font-family:'Outfit',sans-serif; .stApp{background:radial-gradient(circle at top right,#1e293b,#020617 90%)} "
    "#MainMenu,footer,header{visibility:hidden} .main-container{padding:1rem 5vw;max-width:1400px;margin:0 auto} "
    ".counter-box{background:linear-gradient(145deg,rgba(30,41,59,0.3),rgba(15,23,42,0.5));border:1px solid rgba(255,255,255,0.1); "
    "border-radius:40px;padding:clamp(2rem,5vw,4rem) 2rem;text-align:center;backdrop-filter:blur(30px);box-shadow:0 40px 100px -20px rgba(0,0,0,0.7);margin:1.5rem 0} "
    ".digits-row{display:flex;justify-content:center;align-items:center;gap:clamp(2px,0.5vw,10px);margin:1rem 0;flex-wrap:wrap} "
    ".digit-cell{display:inline-flex;align-items:center;justify-content:center;width:clamp(45px,8vw,85px);height:clamp(70px,12vw,130px); "
    "background:#0f172a;border:1px solid rgba(255,255,255,0.15);border-radius:clamp(12px,2vw,28px);font-size:clamp(3rem,6vw,6.5rem);font-weight:800;color:#f8fafc; "
    "font-variant-numeric:tabular-nums;box-shadow:0 15px 35px rgba(0,0,0,0.8)} .digit-sep{font-size:clamp(2.5rem,4vw,4.5rem);font-weight:800;color:#334155} "
    ".metric-card{background:rgba(30,41,59,0.4);border:1px solid rgba(255,255,255,0.06);border-radius:32px;padding:clamp(1.5rem,3vw,2.5rem);text-align:center; "
    "box-shadow:0 15px 40px rgba(0,0,0,0.5);transition:all 0.4s;transform-style:preserve-3d;margin-bottom:1rem} "
    ".metric-card:hover{transform:translateY(-12px) perspective(1000px) rotateX(8deg);border-color:rgba(255,255,255,0.2);box-shadow:0 40px 80px rgba(0,0,0,0.7)} "
    ".metric-value{font-size:clamp(2rem,3vw,3.2rem);font-weight:800;color:#f8fafc;margin-bottom:0.8rem} "
    ".metric-label{color:#94a3b8;font-size:1rem;text-transform:uppercase;letter-spacing:2px;font-weight:700;display:flex;align-items:center;justify-content:center;gap:12px} "
    "[data-testid='stSidebar']{background:linear-gradient(180deg,#020617 0%,#0f172a 100%)!important;border-right:1px solid rgba(255,255,255,0.05)} "
    ".hero-search-box{background:rgba(15,23,42,0.6);border:1px solid rgba(255,255,255,0.1);border-radius:48px;padding:clamp(3rem,8vw,6rem) 2rem;text-align:center; "
    "backdrop-filter:blur(40px);max-width:900px;margin:2rem auto;box-shadow:0 60px 120px rgba(0,0,0,0.9)} "
    ".hero-title{font-size:clamp(3rem,8vw,5rem);font-weight:900;letter-spacing:-3px;margin-bottom:0.8rem;background:linear-gradient(135deg,#fff,#818cf8); "
    "-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 20px rgba(129,140,248,0.3))} "
    ".live-dot{display:inline-block;width:16px;height:16px;background:#f43f5e;border-radius:50%;margin-right:15px;animation:pulse 2s infinite;vertical-align:middle} "
    ".stPlotlyChart{background:rgba(0,0,0,0.2)!important;border-radius:36px;padding:1.5rem;border:1px solid rgba(255,255,255,0.04)} "
    "@keyframes pulse{0%,100%{transform:scale(0.9);box-shadow:0 0 0 0 rgba(244,63,94,0.7)}50%{transform:scale(1.1);box-shadow:0 0 0 20px rgba(244,63,94,0)}} "
    "@media(max-width:768px){.digit-cell{width:55px;height:85px;font-size:3.5rem;border-radius:15px} .digit-sep{font-size:3rem} .user-name{font-size:2.5rem}} "
    ".stSelectbox, .stTextInput { border-radius: 12px !important; } .stButton button { border-radius: 14px !important; font-weight: 800 !important; }"
)
st.markdown(f"<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@48,400,1,0' /><style>{RAW_CSS}</style>", unsafe_allow_html=True)

# ──────────────────────────── Platforms ───────────────────────────────
PLATFORMS = {
    "🔴 YouTube — Suscriptores": {"key": "yt_subs", "badge": "badge-youtube", "label": "SUSCRIPTORES", "color": "#ef4444", "icon": "subscriptions"},
    "🔴 YouTube — Vistas de Video": {"key": "yt_views", "badge": "badge-youtube", "label": "VISTAS", "color": "#ef4444", "icon": "visibility"},
    "🎵 TikTok — Seguidores": {"key": "tt_followers", "badge": "badge-tiktok", "label": "SEGUIDORES", "color": "#00f2ea", "icon": "music_note"},
}

def fmt(n): return f"{int(n):,}".replace(",", ".")

def render_digits(current, previous):
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
        sign, icon = ("+", "trending_up") if diff > 0 else ("", "trending_down")
        badge = f'<div><span style="display:inline-flex;align-items:center;gap:8px;padding:0.6rem 1.6rem;border-radius:99px;font-size:1.3rem;font-weight:900;margin-top:1.5rem;background:rgba({(34,197,94) if diff>0 else (244,63,94)},0.1);color:{"#4ade80" if diff>0 else "#fb7185"};border:1px solid rgba({(34,197,94) if diff>0 else (244,63,94)},0.2);"><span class="material-symbols-rounded">{icon}</span> {sign}{fmt(diff)}</span></div>'
    return f'<div class="digits-row">{"".join(cells)}</div>{badge}'

def build_chart(times, values, color, label):
    v_min, v_max = min(values), max(values)
    span = max(v_max - v_min, 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=[v_min - span*0.1]*len(times), mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=times, y=values, mode='lines', line=dict(color=color, width=8, shape='spline', smoothing=1.3), fill='tonexty', fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.12)", hovertemplate=f"<b>{label}</b>: %{{y:,.0f}}<extra></extra>", showlegend=False))
    fig.update_layout(height=480, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Outfit", color="#475569", size=13), xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.02)", range=[v_min - span*0.1, v_max + span*0.1], tickformat=","))
    return fig

def get_metrics_api(uid, pk):
    try:
        if pk == "yt_subs":
            raw = send_request(f"{YOUTUBE_CHANNEL_STATS_API}/{uid}")
            subs = raw.get("followerCount", 0)
            b = raw.get("bottomOdos", [0,0,0,0])
            return {"main": subs, "label": "SUSCRIPTORES", "extra": [{"val": b[0], "lbl": "VISTAS CANAL", "ico": "visibility"}, {"val": b[2], "lbl": "VIDEOS", "ico": "movie_filter"}, {"val": _goal(subs), "lbl": "META", "ico": "stars"}]}
        elif pk == "yt_views":
            raw = send_request(f"{YOUTUBE_VIDEO_STATS_API}/{uid}")
            views = raw.get("followerCount", 0)
            b = raw.get("bottomOdos", [0,0,0,0])
            return {"main": views, "label": "VISTAS", "extra": [{"val": b[0], "lbl": "LIKES", "ico": "thumb_up"}, {"val": b[2], "lbl": "COMMENTS", "ico": "forum"}, {"val": b[1] if len(b)>1 else 0, "lbl": "DISLIKES", "ico": "thumb_down"}]}
        elif pk == "tt_followers":
            m = api.tiktok.fetch_user_metrics(uid)
            return {"main": m["followers"], "label": "SEGUIDORES", "extra": [{"val": m.get("likes",0), "lbl": "LIKES", "ico": "favorite"}, {"val": m.get("following",0), "lbl": "SIGUIENDO", "ico": "group"}, {"val": m.get("videos",0), "lbl": "VIDEOS", "ico": "video_library"}]}
    except: return {"main": 0}
def _goal(n):
    if not n: return 1000
    mag = 10 ** (len(str(int(n))) - 1)
    return ((int(n) // mag) + 1) * mag

# ──────────────────────────── State ──────────────────────────────────
defaults = {"user_id": None, "user_name": "", "user_avatar": "", "user_handle": "", "platform_key": "", "prev_count": 0, "search_results": [], "show_results": False, "history_times": [], "history_values": []}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# ──────────────────────────── Sidebar ────────────────────────────────
with st.sidebar:
    st.markdown('<div style="margin-bottom:2.5rem;text-align:center;"><span class="material-symbols-rounded" style="font-size:4.5rem;color:#818cf8;filter:drop-shadow(0 0 15px rgba(129,140,248,0.5));">bubble_chart</span><h2 style="font-weight:900;color:white;margin-top:0.5rem;letter-spacing:-1px;">Livecounts Pro</h2><p style="color:#64748b;font-size:0.75rem;letter-spacing:3px;font-weight:700;">ELITE ENGINE v3.5</p></div>', unsafe_allow_html=True)
    pk_side = st.selectbox("PLATAFORMA", list(PLATFORMS.keys()), index=0, key="side_pk")
    q_side = st.text_input("BUSCAR USUARIO", key="side_q", placeholder="Ej: Cristiano")
    if st.button("INICIAR MONITOREO ⚡", use_container_width=True, type="primary"):
        if q_side:
            try:
                pk = PLATFORMS[pk_side]["key"]
                res = [{"id": r["id"], "name": r["name"], "avatar": r.get("avatar","")} for r in (api.youtube.find_channel(q_side) if pk=="yt_subs" else api.youtube.find_video(q_side))] if pk.startswith("yt") else [{"id": r.user_id, "handle": r.username, "name": r.display_name, "avatar": r.thumbnail} for r in api.tiktok.find_user(q_side)]
                st.session_state.update(search_results=res, show_results=True, platform_key=pk, user_id=None, prev_count=0, history_times=[], history_values=[])
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")

# ──────────────────────────── Main Logic ─────────────────────────────
if st.session_state.show_results and not st.session_state.user_id:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f'<h2 style="text-align:center;color:white;margin:2rem 0;font-weight:900;letter-spacing:-1px;font-size:2.5rem;">SELECCIONA UN RESULTADO</h2>', unsafe_allow_html=True)
    for i, r in enumerate(st.session_state.search_results):
        if st.button(f"🚀 {r['name']} ({r.get('handle', r['id'][:10])})", key=f"sel_{i}", use_container_width=True):
            st.session_state.update(user_id=r["id"], user_name=r["name"], user_avatar=r.get("avatar",""), user_handle=r.get("handle",""), show_results=False, prev_count=0, history_times=[], history_values=[]); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.user_id:
    dat = get_metrics_api(st.session_state.user_id, st.session_state.platform_key)
    main_count = dat.get("main", 0)
    st.session_state.history_times.append(datetime.now().strftime("%H:%M:%S"))
    st.session_state.history_values.append(main_count)
    if len(st.session_state.history_times) > 120: st.session_state.history_times, st.session_state.history_values = st.session_state.history_times[-120:], st.session_state.history_values[-120:]

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;margin-bottom:1rem;"><span class="live-dot"></span><span style="color:#f43f5e;font-weight:900;letter-spacing:10px;font-size:1.2rem;">STREAMING DATA</span></div>', unsafe_allow_html=True)
    
    avatar = f'<img src="{st.session_state.user_avatar}" style="width:130px;height:130px;border-radius:50%;border:6px solid rgba(255,255,255,0.1);margin:0 auto 1.5rem;display:block;box-shadow:0 30px 60px rgba(0,0,0,0.8);" />' if st.session_state.user_avatar else ""
    handle = f'<div style="color:#818cf8;font-size:1.5rem;font-weight:700;display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:1.5rem;"><span class="material-symbols-rounded">verified</span> @{st.session_state.user_handle}</div>' if st.session_state.user_handle else ""

    pinfo = [v for v in PLATFORMS.values() if v["key"] == st.session_state.platform_key][0]
    st.markdown(f'<div class="counter-box"><div style="display:flex;justify-content:center;margin-bottom:2rem;"><span style="background:rgba(255,255,255,0.06);padding:0.8rem 2.2rem;border-radius:99px;font-weight:900;letter-spacing:3px;font-size:0.9rem;color:#f8fafc;border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;gap:12px;box-shadow:0 10px 20px rgba(0,0,0,0.4);"><span class="material-symbols-rounded" style="color:#818cf8;">{pinfo["icon"]}</span>{pinfo["label"]}</span></div>{avatar}<div style="color:white;font-size:3.5rem;font-weight:900;letter-spacing:-1px;">{st.session_state.user_name}</div>{handle}{render_digits(main_count, st.session_state.prev_count)}<div style="color:#64748b;font-size:2rem;font-weight:800;letter-spacing:8px;margin-top:1.5rem;text-transform:uppercase;">TOTAL {dat.get("label","")}</div></div>', unsafe_allow_html=True)
    st.session_state.prev_count = main_count

    if dat.get("extra"):
        st.markdown("<div style='margin:3rem 0;'></div>", unsafe_allow_html=True)
        cols = st.columns(len(dat["extra"]))
        for i, itm in enumerate(dat["extra"]):
            with cols[i]: st.markdown(f'<div class="metric-card"><div class="metric-value">{fmt(itm["val"])}</div><div class="metric-label"><span class="material-symbols-rounded" style="font-size:2rem;color:#818cf8;">{itm["ico"]}</span>{itm["lbl"]}</div></div>', unsafe_allow_html=True)

    if len(st.session_state.history_values) >= 2:
        st.plotly_chart(build_chart(st.session_state.history_times, st.session_state.history_values, pinfo["color"], dat.get("label","")), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top:4rem;text-align:center;'>", unsafe_allow_html=True)
    if st.button("🔄 DESCONECTAR Y BUSCAR OTRO", type="secondary"):
        st.session_state.update(user_id=None, show_results=False, prev_count=0, history_times=[], history_values=[]); st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
    time.sleep(2); st.rerun()

else:
    st.markdown('<div class="main-container"><div class="hero-search-box"><div class="material-symbols-rounded" style="font-size:10rem;background:linear-gradient(135deg,#818cf8,#c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 35px rgba(129,140,248,0.4));margin-bottom:2rem;">rocket_launch</div><h1 class="hero-title">SISTEMA LISTO</h1><p style="color:#94a3b8;font-size:1.5rem;font-weight:300;margin-bottom:4rem;letter-spacing:1px;">Monitoreo en tiempo real de máxima precisión.</p>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1: pk_hero = st.selectbox("PLATAFORMA", list(PLATFORMS.keys()), key="h_pk", label_visibility="collapsed")
    with c2: q_hero = st.text_input("NOMBRE O ID", placeholder="Ej: Cristiano Ronaldo", key="h_q", label_visibility="collapsed")
    if st.button("INICIAR TRANSMISIÓN EN VIVO ⚡", use_container_width=True, type="primary", key="h_btn"):
        if q_hero:
            try:
                pk = PLATFORMS[pk_hero]["key"]
                res = [{"id": r["id"], "name": r["name"], "avatar": r.get("avatar","")} for r in (api.youtube.find_channel(q_hero) if pk=="yt_subs" else api.youtube.find_video(q_hero))] if pk.startswith("yt") else [{"id": r.user_id, "handle": r.username, "name": r.display_name, "avatar": r.thumbnail} for r in api.tiktok.find_user(q_hero)]
                st.session_state.update(search_results=res, show_results=True, platform_key=pk, user_id=None, prev_count=0, history_times=[], history_values=[])
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")
    st.markdown('</div></div>', unsafe_allow_html=True)
