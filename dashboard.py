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
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

html, body, [class*="st-"] { font-family: 'Outfit', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%); }
#MainMenu, footer, header { visibility: hidden; }

.counter-box {
    background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(168,85,247,0.08));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 2.5rem 2rem 2rem;
    text-align: center;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    margin: 0.5rem 0;
}

.digits-row { display: flex; justify-content: center; align-items: center; gap: 4px; margin: 0.8rem 0; }
.digit-cell {
    display: inline-flex; align-items: center; justify-content: center;
    width: 65px; height: 90px;
    background: rgba(15,23,42,0.95);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    font-size: 4rem; font-weight: 800; color: #f8fafc;
    font-variant-numeric: tabular-nums;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
}
.digit-cell.up { animation: glow-g 0.6s ease; }
.digit-cell.down { animation: glow-r 0.6s ease; }
@keyframes glow-g {
    0%{color:#f8fafc;box-shadow:0 4px 15px rgba(0,0,0,0.5)}
    40%{color:#4ade80;box-shadow:0 0 25px rgba(74,222,128,0.7)}
    100%{color:#f8fafc;box-shadow:0 4px 15px rgba(0,0,0,0.5)}
}
@keyframes glow-r {
    0%{color:#f8fafc;box-shadow:0 4px 15px rgba(0,0,0,0.5)}
    40%{color:#f87171;box-shadow:0 0 25px rgba(248,113,113,0.7)}
    100%{color:#f8fafc;box-shadow:0 4px 15px rgba(0,0,0,0.5)}
}
.digit-sep { font-size: 3.2rem; font-weight: 800; color: #475569; padding: 0 2px; }

.diff-badge {
    display: inline-block; padding: 0.3rem 1rem; border-radius: 99px;
    font-size: 1rem; font-weight: 700; margin-top: 0.8rem;
}
.diff-up   { background: rgba(74,222,128,0.2); color: #4ade80; }
.diff-down { background: rgba(248,113,113,0.2); color: #f87171; }

.counter-label {
    color: #94a3b8; font-size: 1.4rem; margin-top: 0.5rem;
    text-transform: uppercase; letter-spacing: 4px; font-weight: 700;
}
.user-name { color: #f8fafc; font-size: 2.2rem; font-weight: 800; margin-bottom: 0.2rem; }
.user-handle { color: #6366f1; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.6rem; opacity: 0.9; }

.metric-card {
    background: rgba(30,41,59,0.8);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 1.8rem; text-align: center;
    box-shadow: 0 6px 16px rgba(0,0,0,0.3);
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-4px); border-color: rgba(255,255,255,0.15); }
.metric-value { font-size: 2rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.4rem; }
.metric-label {
    color: #94a3b8; font-size: 1rem; text-transform: uppercase;
    letter-spacing: 2px; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 8px;
}

.platform-badge {
    display: inline-block; padding: 0.4rem 1.2rem; border-radius: 99px;
    font-size: 0.8rem; font-weight: 800; text-transform: uppercase;
    letter-spacing: 2.5px; margin-bottom: 1rem;
}
.badge-youtube { background: rgba(255,0,0,0.25); color: #ff4444; border: 1px solid rgba(255,0,0,0.4); }
.badge-tiktok  { background: rgba(0,242,234,0.2); color: #00f2ea; border: 1px solid rgba(0,242,234,0.4); }

.live-dot {
    display: inline-block; width: 12px; height: 12px;
    background: #ef4444; border-radius: 50%; margin-right: 10px;
    animation: pulse 1.5s ease-in-out infinite; vertical-align: middle;
}
@keyframes pulse {
    0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(239,68,68,0.7)}
    50%{opacity:0.6;box-shadow:0 0 0 12px rgba(239,68,68,0)}
}

.avatar-img {
    width: 110px; height: 110px; border-radius: 50%;
    border: 5px solid rgba(255,255,255,0.12);
    object-fit: cover; margin: 0 auto 1rem; display: block;
    box-shadow: 0 8px 24px rgba(0,0,0,0.6);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.99) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────── Platforms ───────────────────────────────
PLATFORMS = {
    "🔴 YouTube — Suscriptores": {"key": "yt_subs", "badge": "badge-youtube", "label": "SUSCRIPTORES", "color": "#ff4444"},
    "🔴 YouTube — Vistas de Video": {"key": "yt_views", "badge": "badge-youtube", "label": "VISTAS", "color": "#ff4444"},
    "🎵 TikTok — Seguidores": {"key": "tt_followers", "badge": "badge-tiktok", "label": "SEGUIDORES", "color": "#00f2ea"},
    "🎵 TikTok — Vistas de Video": {"key": "tt_views", "badge": "badge-tiktok", "label": "VISTAS", "color": "#00f2ea"},
    "🐦 Twitter/X — Seguidores": {"key": "tw_followers", "badge": "badge-twitter", "label": "S SEGUIDORES", "color": "#1da1f2"},
    "💜 Twitch — Seguidores": {"key": "twitch_followers", "badge": "badge-twitch", "label": "SEGUIDORES", "color": "#9146ff"},
    "💚 Kick — Seguidores": {"key": "kick_followers", "badge": "badge-kick", "label": "SEGUIDORES", "color": "#53fc18"},
}

# ──────────────────────────── Sidebar ────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Livecounts Pro")
    st.markdown("---")
    selected_platform = st.selectbox("Plataforma", list(PLATFORMS.keys()), index=0)
    platform_info = PLATFORMS[selected_platform]
    query = st.text_input("Buscar usuario o canal", placeholder="Ej: Cristiano")
    search_btn = st.button("🔍 Buscar", use_container_width=True, type="primary")
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#475569;font-size:0.75rem;'>"
        "Potenciado por<br><b>Unofficial Livecounts API</b><br>© 2026</div>",
        unsafe_allow_html=True)

# ──────────────────────────── State ──────────────────────────────────
defaults = {
    "user_id": None, "user_name": "", "user_avatar": "", "user_handle": "",
    "platform_key": "", "prev_count": 0,
    "search_results": [], "show_results": False,
    "history_times": [], "history_values": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────── Helpers ────────────────────────────────
def fmt(n):
    return f"{int(n):,}".replace(",", ".")

def render_digits(current: int, previous: int) -> str:
    c, p = str(current), str(previous) if previous else str(current)
    m = max(len(c), len(p))
    c, p = c.zfill(m), p.zfill(m)
    diff = current - previous
    cells, cnt = [], 0
    for i, (cd, pd) in enumerate(zip(c, p)):
        if cnt > 0 and (m - i) % 3 == 0:
            cells.append('<span class="digit-sep">.</span>')
        cls = "digit-cell" + (" up" if cd != pd and diff > 0 else " down" if cd != pd else "")
        cells.append(f'<span class="{cls}">{cd}</span>')
        cnt += 1
    badge = ""
    if previous and diff != 0:
        sign, bcls = ("+" if diff > 0 else "", "diff-up" if diff > 0 else "diff-down")
        badge = f'<div><span class="diff-badge {bcls}">{sign}{fmt(diff)}</span></div>'
    return f'<div class="digits-row">{"".join(cells)}</div>{badge}'

def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def build_chart(times: list, values: list, color: str, label: str) -> go.Figure:
    fill_rgba = _hex_to_rgba(color, 0.25)
    v_min, v_max = min(values), max(values)
    span = v_max - v_min if v_max > v_min else 10
    y_lo, y_hi = v_min - span*0.4, v_max + span*0.4

    fig = go.Figure()
    # Baseline for fill
    fig.add_trace(go.Scatter(x=times, y=[y_lo] * len(times), mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
    # Main line
    fig.add_trace(go.Scatter(
        x=times, y=values, mode='lines',
        line=dict(color=color, width=4, shape='spline', smoothing=0.8),
        fill='tonexty', fillcolor=fill_rgba,
        hovertemplate=f"<b>{label}</b>: %{{y:,.0f}}<br>%{{x}}<extra></extra>",
        showlegend=False,
    ))
    fig.update_layout(
        height=350, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.4)",
        font=dict(family="Outfit", color="#94a3b8", size=12),
        xaxis=dict(showgrid=False, zeroline=False, linecolor="rgba(255,255,255,0.05)", tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", zeroline=False, linecolor="rgba(255,255,255,0.05)", range=[y_lo, y_hi], tickfont=dict(size=10), tickformat=","),
    )
    return fig

# ──────────────────────────── Search ─────────────────────────────────
def do_search(q, pk):
    results = []
    try:
        if pk in ("yt_subs", "yt_views"):
            fn = api.youtube.find_channel if pk == "yt_subs" else api.youtube.find_video
            results = [{"id": r.get("id",""), "name": r.get("name",""), "avatar": r.get("avatar","")} for r in fn(q)]
        elif pk == "tt_followers":
            results = [{"id": r.user_id, "handle": r.username, "name": r.display_name, "avatar": r.thumbnail} for r in api.tiktok.find_user(q)]
        elif pk == "tw_followers" or pk == "twitch_followers" or pk == "kick_followers":
            agent = getattr(api, pk.split('_')[0])
            res = agent.find_user(q)
            if isinstance(res, list): results = [{"id": r["id"], "name": r["username"], "avatar": r.get("avatar","")} for r in res]
            else: results = [{"id": res["id"], "name": res["username"], "avatar": res.get("avatar","")}] if res else []
    except Exception as e:
        st.error(f"Error de búsqueda: {e}"); return
    st.session_state.update(search_results=results, show_results=True, platform_key=pk, user_id=None, prev_count=0, history_times=[], history_values=[])

def select_user(idx):
    r = st.session_state.search_results[idx]
    st.session_state.update(user_id=r["id"], user_name=r["name"], user_avatar=r.get("avatar",""), user_handle=r.get("handle",""), show_results=False, prev_count=0, history_times=[], history_values=[])

def get_metrics(uid, pk):
    try:
        if pk == "yt_subs":
            raw = send_request(f"{YOUTUBE_CHANNEL_STATS_API}/{uid}")
            subs = raw.get("followerCount", 0)
            b = raw.get("bottomOdos", [0, 0, 0, 0])
            return {"main": subs, "label": "SUSCRIPTORES",
                    "extra": {"CHANNEL VIEWS 👁️": b[0] if len(b) > 0 else 0,
                              "VIDEOS 🎬": b[2] if len(b) > 2 else 0,
                              "GOAL 🎯": _goal(subs)}}
        elif pk == "yt_views":
            raw = send_request(f"{YOUTUBE_VIDEO_STATS_API}/{uid}")
            views = raw.get("followerCount", 0)
            b = raw.get("bottomOdos", [0, 0, 0])
            return {"main": views, "label": "VISTAS",
                    "extra": {"LIKES 👍": b[0] if len(b) > 0 else 0, "COMMENTS 💬": b[2] if len(b) > 2 else 0}}
        elif pk == "tt_followers":
            m = api.tiktok.fetch_user_metrics(uid)
            return {"main": m["followers"], "label": "SEGUIDORES",
                    "extra": {"LIKES ❤️": m.get("likes",0), "FOLLOWING 👥": m.get("following",0), "VIDEOS 🎬": m.get("videos",0)}}
    except Exception as e:
        return {"main": 0, "label": "ERROR", "error": str(e)}
    return {"main": 0, "label": "—"}

def _goal(n):
    if n <= 0: return 1000
    mag = 10 ** (len(str(int(n))) - 1)
    if mag < 1: mag = 1
    return ((int(n) // mag) + 1) * mag

# ──────────────────────────── Logic ──────────────────────────────────
if search_btn and query:
    do_search(query, platform_info["key"])

if st.session_state.show_results and not st.session_state.user_id:
    for i, r in enumerate(st.session_state.search_results):
        if st.button(f"{r['name']} ({r.get('handle', r['id'][:10])})", key=f"sel_{i}", use_container_width=True):
            select_user(i); st.rerun()

elif st.session_state.user_id:
    metrics = get_metrics(st.session_state.user_id, st.session_state.platform_key)
    main_count = metrics.get("main", 0)
    
    # History
    st.session_state.history_times.append(datetime.now().strftime("%H:%M:%S"))
    st.session_state.history_values.append(main_count)
    if len(st.session_state.history_times) > 100:
        st.session_state.history_times = st.session_state.history_times[-100:]
        st.session_state.history_values = st.session_state.history_values[-100:]

    # Header
    st.markdown('<div style="text-align:center;margin-bottom:0.5rem;"><span class="live-dot"></span><span style="color:#ef4444;font-weight:800;letter-spacing:3px;font-size:0.9rem;">EN VIVO</span></div>', unsafe_allow_html=True)
    
    avatar_html = f'<img src="{st.session_state.user_avatar}" class="avatar-img" />' if st.session_state.user_avatar else ""
    handle_html = f'<div class="user-handle">@{st.session_state.user_handle} 🎵</div>' if st.session_state.platform_key == "tt_followers" and st.session_state.user_handle else ""

    st.markdown(
        f'<div class="counter-box">'
        f'<span class="platform-badge {platform_info["badge"]}">{selected_platform.split("—")[0].strip()}</span>'
        f'{avatar_html}'
        f'<div class="user-name">{st.session_state.user_name}</div>'
        f'{handle_html}'
        f'{render_digits(main_count, st.session_state.prev_count)}'
        f'<div class="counter-label">{metrics.get("label","")}</div>'
        f'</div>', unsafe_allow_html=True)
    
    st.session_state.prev_count = main_count

    # Metric Cards (NO BUTTONS HERE)
    extra = metrics.get("extra", {})
    if extra:
        st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)
        cols = st.columns(len(extra))
        for i, (label, value) in enumerate(extra.items()):
            with cols[i]:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-value">{fmt(value)}</div>'
                    f'<div class="metric-label">{label}</div>'
                    f'</div>', unsafe_allow_html=True)

    # Chart
    if len(st.session_state.history_values) >= 2:
        st.plotly_chart(build_chart(st.session_state.history_times, st.session_state.history_values, platform_info["color"], metrics.get("label", "Count")), use_container_width=True, config={"displayModeBar": False})

    if st.button("🔄 Cambiar Usuario", use_container_width=False):
        st.session_state.update(user_id=None, show_results=True, prev_count=0, history_times=[], history_values=[])
        st.rerun()

    time.sleep(2); st.rerun()
else:
    st.markdown('<div style="text-align:center;padding:10rem 2rem;"><div style="font-size:6rem;margin-bottom:2rem;">📊</div><div style="color:#94a3b8;font-size:1.6rem;font-weight:300;">Selecciona una plataforma en el menú lateral para comenzar.</div></div>', unsafe_allow_html=True)
