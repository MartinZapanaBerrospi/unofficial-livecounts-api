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
    padding: 2rem 2rem 1.5rem;
    text-align: center;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    margin: 0.3rem 0;
}

.digits-row { display: flex; justify-content: center; align-items: center; gap: 3px; margin: 0.6rem 0; }
.digit-cell {
    display: inline-flex; align-items: center; justify-content: center;
    width: 50px; height: 68px;
    background: rgba(15,23,42,0.85);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    font-size: 2.8rem; font-weight: 800; color: #c4b5fd;
    font-variant-numeric: tabular-nums;
    box-shadow: 0 3px 10px rgba(0,0,0,0.35);
}
.digit-cell.up { animation: glow-g 0.5s ease; }
.digit-cell.down { animation: glow-r 0.5s ease; }
@keyframes glow-g {
    0%{color:#c4b5fd;box-shadow:0 3px 10px rgba(0,0,0,.35)}
    40%{color:#4ade80;box-shadow:0 0 18px rgba(74,222,128,.5)}
    100%{color:#c4b5fd;box-shadow:0 3px 10px rgba(0,0,0,.35)}
}
@keyframes glow-r {
    0%{color:#c4b5fd;box-shadow:0 3px 10px rgba(0,0,0,.35)}
    40%{color:#f87171;box-shadow:0 0 18px rgba(248,113,113,.5)}
    100%{color:#c4b5fd;box-shadow:0 3px 10px rgba(0,0,0,.35)}
}
.digit-sep { font-size: 2.5rem; font-weight: 800; color: #475569; padding: 0 1px; }
.diff-badge {
    display: inline-block; padding: 0.2rem 0.8rem; border-radius: 99px;
    font-size: 0.8rem; font-weight: 600; margin-top: 0.4rem;
}
.diff-up   { background: rgba(74,222,128,0.15); color: #4ade80; }
.diff-down { background: rgba(248,113,113,0.15); color: #f87171; }

.counter-label {
    color: #94a3b8; font-size: 1.1rem; margin-top: 0.2rem;
    text-transform: uppercase; letter-spacing: 3px;
}
.user-name { color: #e2e8f0; font-size: 1.5rem; font-weight: 600; margin-bottom: 0.2rem; }

.metric-card {
    background: rgba(30,41,59,0.6);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 1.2rem; text-align: center;
}
.metric-value { font-size: 1.4rem; font-weight: 700; color: #f8fafc; }
.metric-label {
    color: #64748b; font-size: 0.75rem; text-transform: uppercase;
    letter-spacing: 2px; margin-top: 0.15rem;
}

.platform-badge {
    display: inline-block; padding: 0.3rem 0.9rem; border-radius: 99px;
    font-size: 0.65rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 2px; margin-bottom: 0.6rem;
}
.badge-youtube { background: rgba(255,0,0,0.15); color: #ff4444; }
.badge-tiktok  { background: rgba(0,242,234,0.15); color: #00f2ea; }
.badge-twitter { background: rgba(29,161,242,0.15); color: #1da1f2; }
.badge-twitch  { background: rgba(145,70,255,0.15); color: #9146ff; }
.badge-kick    { background: rgba(83,252,24,0.15); color: #53fc18; }

.live-dot {
    display: inline-block; width: 10px; height: 10px;
    background: #ef4444; border-radius: 50%; margin-right: 8px;
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
    0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(239,68,68,.7)}
    50%{opacity:.7;box-shadow:0 0 0 8px rgba(239,68,68,0)}
}

.avatar-img {
    width: 80px; height: 80px; border-radius: 50%;
    border: 3px solid rgba(129,140,248,0.4);
    object-fit: cover; margin: 0 auto 0.6rem; display: block;
}

[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.05);
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    color: #94a3b8 !important; font-weight: 600;
    text-transform: uppercase; letter-spacing: 1px; font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────── Platforms ───────────────────────────────
PLATFORMS = {
    "🔴 YouTube — Suscriptores": {"key": "yt_subs", "badge": "badge-youtube", "label": "Suscriptores", "color": "#ff4444"},
    "🔴 YouTube — Vistas de Video": {"key": "yt_views", "badge": "badge-youtube", "label": "Vistas", "color": "#ff4444"},
    "🎵 TikTok — Seguidores": {"key": "tt_followers", "badge": "badge-tiktok", "label": "Seguidores", "color": "#00f2ea"},
    "🎵 TikTok — Vistas de Video": {"key": "tt_views", "badge": "badge-tiktok", "label": "Vistas", "color": "#00f2ea"},
    "🐦 Twitter/X — Seguidores": {"key": "tw_followers", "badge": "badge-twitter", "label": "Seguidores", "color": "#1da1f2"},
    "💜 Twitch — Seguidores": {"key": "twitch_followers", "badge": "badge-twitch", "label": "Seguidores", "color": "#9146ff"},
    "💚 Kick — Seguidores": {"key": "kick_followers", "badge": "badge-kick", "label": "Seguidores", "color": "#53fc18"},
}

# ──────────────────────────── Sidebar ────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Livecounts Pro")
    st.markdown("---")
    selected_platform = st.selectbox("Plataforma", list(PLATFORMS.keys()), index=0)
    platform_info = PLATFORMS[selected_platform]
    query = st.text_input("Buscar usuario o canal", placeholder="Ej: MrBeast")
    search_btn = st.button("🔍 Buscar", use_container_width=True, type="primary")
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#475569;font-size:0.75rem;'>"
        "Potenciado por<br><b>Unofficial Livecounts API</b><br>© 2026</div>",
        unsafe_allow_html=True)

# ──────────────────────────── State ──────────────────────────────────
defaults = {
    "user_id": None, "user_name": "", "user_avatar": "",
    "platform_key": "", "prev_count": 0,
    "search_results": [], "show_results": False,
    "history_times": [], "history_values": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────── Helpers ────────────────────────────────
def fmt(n):
    return f"{n:,}".replace(",", ".")

def render_digits(current: int, previous: int) -> str:
    c, p = str(current), str(previous) if previous else str(current)
    m = max(len(c), len(p))
    c, p = c.zfill(m), p.zfill(m)
    diff = current - previous
    cells = []
    cnt = 0
    for i, (cd, pd) in enumerate(zip(c, p)):
        if cnt > 0 and (m - i) % 3 == 0:
            cells.append('<span class="digit-sep">.</span>')
        cls = "digit-cell"
        if cd != pd:
            cls += " up" if diff > 0 else " down"
        cells.append(f'<span class="{cls}">{cd}</span>')
        cnt += 1
    badge = ""
    if previous and diff != 0:
        sign = "+" if diff > 0 else ""
        bcls = "diff-up" if diff > 0 else "diff-down"
        badge = f'<div><span class="diff-badge {bcls}">{sign}{fmt(diff)}</span></div>'
    return f'<div class="digits-row">{"".join(cells)}</div>{badge}'

def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def build_chart(times: list, values: list, color: str, label: str) -> go.Figure:
    """Livecounts-style area chart zoomed into the data range."""
    fill_rgba = _hex_to_rgba(color, 0.25)
    v_min, v_max = min(values), max(values)
    pad = max((v_max - v_min) * 0.3, 1)
    y_lo, y_hi = v_min - pad, v_max + pad

    fig = go.Figure()
    # Invisible baseline
    fig.add_trace(go.Scatter(
        x=times, y=[y_lo] * len(times), mode='lines',
        line=dict(width=0), showlegend=False, hoverinfo='skip',
    ))
    # Data line with area fill
    fig.add_trace(go.Scatter(
        x=times, y=values, mode='lines',
        line=dict(color=color, width=2.5, shape='spline', smoothing=0.8),
        fill='tonexty', fillcolor=fill_rgba,
        hovertemplate=f"<b>{label}</b>: %{{y:,.0f}}<br>%{{x}}<extra></extra>",
        showlegend=False,
    ))
    fig.update_layout(
        height=280,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.5)",
        font=dict(family="Outfit", color="#94a3b8", size=11),
        xaxis=dict(showgrid=False, zeroline=False, color="#64748b",
                   linecolor="rgba(255,255,255,0.05)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                   zeroline=False, color="#64748b",
                   tickformat=",", separatethousands=True,
                   linecolor="rgba(255,255,255,0.05)",
                   range=[y_lo, y_hi]),
        hoverlabel=dict(bgcolor="#1e293b", font_color="#f8fafc",
                        bordercolor="rgba(255,255,255,0.1)"),
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
            results = [{"id": r.user_id, "name": r.display_name or r.username, "avatar": r.thumbnail} for r in api.tiktok.find_user(q)]
        elif pk == "tt_views":
            st.session_state.update(user_id=q, user_name=f"Video: {q}", user_avatar="",
                                     platform_key=pk, prev_count=0, show_results=False,
                                     history_times=[], history_values=[])
            return
        elif pk == "tw_followers":
            raw = api.twitter.find_user(q)
            results = [{"id": raw["id"], "name": raw["username"], "avatar": raw.get("avatar","")}] if raw else []
        elif pk == "twitch_followers":
            results = [{"id": r["id"], "name": r["username"], "avatar": r.get("avatar","")} for r in api.twitch.find_user(q)]
        elif pk == "kick_followers":
            results = [{"id": r["id"], "name": r["username"], "avatar": r.get("avatar","")} for r in api.kick.find_user(q)]
    except RequestApiError as e:
        st.error(f"Error: {e}"); return
    st.session_state.update(search_results=results, show_results=True,
                             platform_key=pk, user_id=None, prev_count=0,
                             history_times=[], history_values=[])

def select_user(idx):
    r = st.session_state.search_results[idx]
    st.session_state.update(user_id=r["id"], user_name=r["name"],
                             user_avatar=r.get("avatar",""),
                             show_results=False, prev_count=0,
                             history_times=[], history_values=[])

def get_metrics(uid, pk):
    try:
        if pk == "yt_subs":
            raw = send_request(f"{YOUTUBE_CHANNEL_STATS_API}/{uid}")
            subs = raw.get("followerCount", 0)
            b = raw.get("bottomOdos", [0, 0, 0])
            return {"main": subs, "label": "Suscriptores",
                    "extra": {"👁️ Channel Views": b[0] if len(b) > 0 else 0,
                              "🎬 Videos": b[2] if len(b) > 2 else 0,
                              "🎯 Goal": _goal(subs)}}
        elif pk == "yt_views":
            raw = send_request(f"{YOUTUBE_VIDEO_STATS_API}/{uid}")
            views = raw.get("followerCount", 0)
            b = raw.get("bottomOdos", [0, 0, 0])
            return {"main": views, "label": "Vistas",
                    "extra": {"👍 Likes": b[0] if len(b) > 0 else 0,
                              "👎 Dislikes": b[1] if len(b) > 1 else 0,
                              "💬 Comments": b[2] if len(b) > 2 else 0}}
        elif pk == "tt_followers":
            m = api.tiktok.fetch_user_metrics(uid)
            return {"main": m["followers"], "label": "Seguidores",
                    "extra": {"❤️ Likes": m.get("likes",0), "👥 Siguiendo": m.get("following",0), "🎬 Videos": m.get("videos",0)}}
        elif pk == "tt_views":
            m = api.tiktok.fetch_video_stats(uid)
            return {"main": m["views"], "label": "Vistas",
                    "extra": {"❤️ Likes": m.get("likes",0), "💬 Comentarios": m.get("comments",0), "🔄 Shares": m.get("shares",0)}}
        elif pk == "tw_followers":
            m = api.twitter.fetch_user_metrics(uid)
            return {"main": m["followers"], "label": "Seguidores"}
        elif pk == "twitch_followers":
            m = api.twitch.fetch_user_metrics(uid)
            return {"main": m["followers"], "label": "Seguidores"}
        elif pk == "kick_followers":
            m = api.kick.fetch_user_metrics(uid)
            return {"main": m["followers"], "label": "Seguidores"}
    except RequestApiError as e:
        return {"main": 0, "label": "Error", "error": str(e)}
    return {"main": 0, "label": "—"}

def _goal(n):
    if n <= 0: return 1000
    mag = 10 ** len(str(n))
    step = mag // 10
    return ((n // step) + 1) * step

# ──────────────────────────── Trigger ────────────────────────────────
if search_btn and query:
    do_search(query, platform_info["key"])

# ──────────────────────────── Results ────────────────────────────────
if st.session_state.show_results and not st.session_state.user_id:
    results = st.session_state.search_results
    if not results:
        st.markdown(
            '<div style="text-align:center;padding:4rem 2rem;">'
            '<div style="font-size:3rem;margin-bottom:1rem;">🔍</div>'
            '<div style="color:#f87171;font-size:1.2rem;font-weight:600;">No se encontraron usuarios</div>'
            '<div style="color:#64748b;margin-top:0.5rem;">Intenta con otro nombre o verifica la plataforma.</div>'
            '</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div style="text-align:center;color:#94a3b8;margin:1rem 0;font-size:1.05rem;">'
            f'<b style="color:#c4b5fd;">{len(results)}</b> resultados — selecciona uno:</div>',
            unsafe_allow_html=True)
        for rs in range(0, len(results), 3):
            cols = st.columns(3)
            for ci in range(3):
                i = rs + ci
                if i >= len(results):
                    break
                r = results[i]
                with cols[ci]:
                    av = r.get("avatar", "")
                    av_html = (f'<img src="{av}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;" />'
                               if av else '<div style="width:40px;height:40px;border-radius:50%;background:#334155;'
                               'display:flex;align-items:center;justify-content:center;color:#94a3b8;">?</div>')
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:0.8rem;padding:0.7rem;'
                        f'background:rgba(30,41,59,0.7);border:1px solid rgba(255,255,255,0.06);'
                        f'border-radius:12px;margin-bottom:0.2rem;">'
                        f'{av_html}<div><div style="color:#e2e8f0;font-weight:600;">{r["name"]}</div>'
                        f'<div style="color:#64748b;font-size:0.7rem;">{r["id"][:24]}</div></div>'
                        f'</div>', unsafe_allow_html=True)
                    if st.button("Seleccionar", key=f"sel_{i}", use_container_width=True):
                        select_user(i)
                        st.rerun()

# ──────────────────────────── Live Dashboard ─────────────────────────
elif st.session_state.user_id:
    metrics = get_metrics(st.session_state.user_id, st.session_state.platform_key)
    main_count = metrics.get("main", 0)
    prev_count = st.session_state.prev_count
    badge_class = platform_info["badge"]
    chart_color = platform_info["color"]

    # Record history
    st.session_state.history_times.append(datetime.now().strftime("%H:%M:%S"))
    st.session_state.history_values.append(main_count)
    if len(st.session_state.history_times) > 120:
        st.session_state.history_times = st.session_state.history_times[-120:]
        st.session_state.history_values = st.session_state.history_values[-120:]

    # EN VIVO
    st.markdown(
        '<div style="text-align:center;margin-bottom:0.2rem;">'
        '<span class="live-dot"></span>'
        '<span style="color:#ef4444;font-weight:600;font-size:0.8rem;letter-spacing:2px;">EN VIVO</span>'
        '</div>', unsafe_allow_html=True)

    avatar_html = f'<img src="{st.session_state.user_avatar}" class="avatar-img" />' if st.session_state.user_avatar else ""
    digits_html = render_digits(main_count, prev_count)

    st.markdown(
        f'<div class="counter-box">'
        f'<span class="platform-badge {badge_class}">{selected_platform.split("—")[0].strip()}</span>'
        f'{avatar_html}'
        f'<div class="user-name">{st.session_state.user_name}</div>'
        f'{digits_html}'
        f'<div class="counter-label">{metrics.get("label","")}</div>'
        f'</div>', unsafe_allow_html=True)

    st.session_state.prev_count = main_count

    # Metric cards
    extra = metrics.get("extra", {})
    if extra:
        cols = st.columns(len(extra))
        for i, (label, value) in enumerate(extra.items()):
            with cols[i]:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-value">{fmt(value)}</div>'
                    f'<div class="metric-label">{label}</div>'
                    f'</div>', unsafe_allow_html=True)

    # Real-time chart
    if len(st.session_state.history_values) >= 2:
        fig = build_chart(
            st.session_state.history_times,
            st.session_state.history_values,
            chart_color,
            metrics.get("label", "Contador"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if "error" in metrics:
        st.warning(f"⚠️ {metrics['error']}")

    if st.button("🔄 Cambiar Usuario", use_container_width=False):
        st.session_state.update(user_id=None, show_results=True, prev_count=0,
                                 history_times=[], history_values=[])
        st.rerun()

    time.sleep(2)
    st.rerun()

# ──────────────────────────── Welcome ────────────────────────────────
else:
    st.markdown(
        '<div style="text-align:center;padding:6rem 2rem;">'
        '<div style="font-size:4rem;margin-bottom:1rem;">📊</div>'
        '<div style="color:#94a3b8;font-size:1.3rem;font-weight:300;">'
        'Selecciona una plataforma y busca un usuario<br>para ver sus estadísticas en tiempo real.'
        '</div></div>', unsafe_allow_html=True)
