# Home.py — BloodAI Landing Page
# This is the ENTRY POINT. blood_ai.py stays in pages/ folder.
# Run: streamlit run Home.py

import streamlit as st

st.set_page_config(
    page_title="BloodAI — Advanced Haematology Insights",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide all streamlit chrome completely
st.markdown("""
<style>
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],.stDeployButton{display:none !important}
.block-container{padding:0 !important;max-width:100% !important}
section[data-testid="stSidebar"]{display:none !important}
html,body,.stApp{background:#020c14 !important;overflow:hidden !important}
iframe{border:none !important}

/* The one real button we need */
#launch-wrap{
    position:fixed;bottom:38px;left:50%;transform:translateX(-50%);
    z-index:9999;display:flex;flex-direction:column;align-items:center;gap:0.5rem;
}
.stButton>button{
    background:transparent !important;
    border:2px solid rgba(0,229,255,0.75) !important;
    color:#00e5ff !important;
    font-family:'Orbitron',monospace !important;
    font-size:0.88rem !important;
    font-weight:700 !important;
    letter-spacing:0.25em !important;
    padding:1rem 3.5rem !important;
    border-radius:6px !important;
    box-shadow:0 0 25px rgba(0,229,255,0.2),inset 0 0 20px rgba(0,229,255,0.05) !important;
    transition:all 0.3s ease !important;
    text-transform:uppercase !important;
}
.stButton>button:hover{
    background:rgba(0,229,255,0.12) !important;
    border-color:rgba(0,229,255,1) !important;
    box-shadow:0 0 50px rgba(0,229,255,0.5),0 0 80px rgba(0,229,255,0.2),inset 0 0 30px rgba(0,229,255,0.1) !important;
    color:#fff !important;
    transform:translateY(-3px) !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# ANIMATED 3D LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════
LANDING_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100vh;overflow:hidden;background:#020c14}
body{display:flex;align-items:center;justify-content:center}

canvas{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none}

.overlay{
    position:fixed;top:0;left:0;width:100%;height:100%;z-index:1;pointer-events:none;
    background:radial-gradient(ellipse at 50% 50%,
        rgba(2,12,20,0.05) 0%,
        rgba(2,12,20,0.5) 55%,
        rgba(2,12,20,0.92) 100%);
}

.content{
    position:relative;z-index:2;text-align:center;padding:1.5rem 1rem;
    opacity:0;animation:fadeUp 1.6s cubic-bezier(.22,1,.36,1) 0.3s forwards;
}
@keyframes fadeUp{from{opacity:0;transform:translateY(35px)}to{opacity:1;transform:translateY(0)}}

.icon-wrap{
    margin-bottom:1.4rem;
    animation:floatY 3.5s ease-in-out infinite;
}
@keyframes floatY{0%,100%{transform:translateY(0)}50%{transform:translateY(-14px)}}

.title{
    font-family:'Orbitron',monospace;
    font-size:clamp(3rem,8vw,6rem);
    font-weight:900;
    letter-spacing:0.3em;
    color:#fff;
    line-height:1.05;
    margin-bottom:0.5rem;
    text-shadow:
        0 0 25px rgba(0,229,255,1),
        0 0 55px rgba(0,229,255,0.7),
        0 0 100px rgba(0,229,255,0.4),
        0 0 150px rgba(0,229,255,0.2);
    animation:titleGlow 3.5s ease-in-out infinite;
}
@keyframes titleGlow{
    0%,100%{text-shadow:0 0 25px rgba(0,229,255,1),0 0 55px rgba(0,229,255,0.7),0 0 100px rgba(0,229,255,0.4)}
    50%{text-shadow:0 0 35px rgba(0,229,255,1),0 0 75px rgba(0,229,255,0.9),0 0 130px rgba(0,229,255,0.6),0 0 200px rgba(0,229,255,0.25)}
}

.subtitle{
    font-family:'Orbitron',monospace;
    font-size:clamp(0.6rem,1.3vw,0.85rem);
    letter-spacing:0.38em;
    color:#00b8d9;
    margin-bottom:0.9rem;
    text-shadow:0 0 14px rgba(0,184,217,0.65);
    animation:fadeUp 1.6s cubic-bezier(.22,1,.36,1) 0.6s both;
    opacity:0;
}

.tagline{
    font-family:'Rajdhani',sans-serif;
    font-size:clamp(0.88rem,1.5vw,1.05rem);
    color:rgba(200,235,242,0.7);
    letter-spacing:0.04em;
    line-height:1.7;
    max-width:560px;
    margin:0 auto 1.4rem auto;
    animation:fadeUp 1.6s cubic-bezier(.22,1,.36,1) 0.8s both;
    opacity:0;
}

.stats-row{
    display:flex;gap:2.2rem;justify-content:center;margin-bottom:2.8rem;
    flex-wrap:wrap;
    animation:fadeUp 1.6s cubic-bezier(.22,1,.36,1) 1s both;
    opacity:0;
}
.stat{text-align:center}
.stat-num{
    font-family:'Orbitron',monospace;font-size:1.5rem;font-weight:700;
    color:#00e5ff;
    text-shadow:0 0 14px rgba(0,229,255,0.7);
    animation:countUp 1s ease-out 1.5s both;
}
@keyframes countUp{from{opacity:0;transform:scale(0.7)}to{opacity:1;transform:scale(1)}}
.stat-lbl{
    font-size:0.62rem;color:rgba(128,222,234,0.5);
    text-transform:uppercase;letter-spacing:1.5px;margin-top:3px;
    font-family:'Orbitron',monospace;
}

/* Scan line effect */
.scanline{
    position:fixed;top:0;left:0;width:100%;height:3px;z-index:10;pointer-events:none;
    background:linear-gradient(90deg,transparent,rgba(0,229,255,0.4),transparent);
    animation:scanMove 4s linear infinite;
    opacity:0.4;
}
@keyframes scanMove{from{top:0}to{top:100%}}

/* Corner accents */
.corner{position:fixed;width:40px;height:40px;z-index:10;pointer-events:none}
.corner-tl{top:16px;left:16px;border-top:2px solid rgba(0,229,255,0.5);border-left:2px solid rgba(0,229,255,0.5)}
.corner-tr{top:16px;right:16px;border-top:2px solid rgba(0,229,255,0.5);border-right:2px solid rgba(0,229,255,0.5)}
.corner-bl{bottom:16px;left:16px;border-bottom:2px solid rgba(0,229,255,0.5);border-left:2px solid rgba(0,229,255,0.5)}
.corner-br{bottom:16px;right:16px;border-bottom:2px solid rgba(0,229,255,0.5);border-right:2px solid rgba(0,229,255,0.5)}
</style>
</head>
<body>

<canvas id="dna-canvas"></canvas>
<div class="overlay"></div>
<div class="scanline"></div>
<div class="corner corner-tl"></div>
<div class="corner corner-tr"></div>
<div class="corner corner-bl"></div>
<div class="corner corner-br"></div>

<div class="content">

    <!-- Stethoscope SVG icon -->
    <div class="icon-wrap">
        <svg width="78" height="78" viewBox="0 0 78 78" fill="none" xmlns="http://www.w3.org/2000/svg"
             style="filter:drop-shadow(0 0 22px rgba(0,229,255,0.9)) drop-shadow(0 0 45px rgba(0,229,255,0.4))">
            <circle cx="21" cy="16" r="6.5" stroke="#00e5ff" stroke-width="2.2"/>
            <circle cx="57" cy="16" r="6.5" stroke="#00e5ff" stroke-width="2.2"/>
            <path d="M21 22.5 Q21 52 39 52 Q57 52 57 22.5" stroke="#00e5ff" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="39" y1="52" x2="39" y2="53" stroke="#00e5ff" stroke-width="2.5"/>
            <circle cx="39" cy="62" r="11.5" stroke="#00e5ff" stroke-width="2.2" fill="rgba(0,229,255,0.07)"/>
            <text x="39" y="67" text-anchor="middle" fill="#00e5ff" font-size="9.5" font-family="Orbitron,monospace" font-weight="700">AI</text>
        </svg>
    </div>

    <div class="title">BLOOD AI</div>
    <div class="subtitle">Advanced Haematology Insights</div>
    <div class="tagline">
        Powered by cutting-edge AI technology for precision blood analysis<br>
        and personalised genetic health insights
    </div>

    <div class="stats-row">
        <div class="stat"><div class="stat-num">48</div><div class="stat-lbl">Parameters</div></div>
        <div class="stat"><div class="stat-num">7</div><div class="stat-lbl">Patterns</div></div>
        <div class="stat"><div class="stat-num">4</div><div class="stat-lbl">Risk Scores</div></div>
        <div class="stat"><div class="stat-num">3</div><div class="stat-lbl">AI Models</div></div>
    </div>

</div>

<script>
/* ════════════════════════════════════════════════
   ANIMATED 3D DNA PARTICLE SYSTEM
   ════════════════════════════════════════════════ */
const canvas = document.getElementById('dna-canvas');
const ctx    = canvas.getContext('2d');
let W, H, t = 0, mx = W/2, my = H/2;

function resize(){
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);
window.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });

/* ── Floating particles ── */
const PARTICLE_COUNT = 200;
const particles = Array.from({length: PARTICLE_COUNT}, () => ({
    x: Math.random() * (window.innerWidth  || 1400),
    y: Math.random() * (window.innerHeight || 800),
    r: Math.random() * 1.8 + 0.3,
    vx: (Math.random() - 0.5) * 0.4,
    vy: (Math.random() - 0.5) * 0.4,
    a: Math.random() * 0.55 + 0.15,
    phase: Math.random() * Math.PI * 2,
}));

function drawParticles() {
    particles.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
        if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
        p.phase += 0.022;
        const a = p.a * (0.65 + 0.35 * Math.sin(p.phase));
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0,185,220,${a})`;
        ctx.fill();
    });

    // Connection web
    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const d  = Math.sqrt(dx*dx + dy*dy);
            if (d < 85) {
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.strokeStyle = `rgba(0,150,200,${0.1 * (1 - d/85)})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
            }
        }
    }
}

/* ── DNA Helix ── */
const STRANDS = [
    { cx: 0.13, amp: 85, pitchH: 2.8, phase: 0,    speed: 0.007, scale: 0.9 },
    { cx: 0.87, amp: 80, pitchH: 2.6, phase: 1.2,  speed: 0.008, scale: 0.85 },
    { cx: 0.5,  amp: 100,pitchH: 3.0, phase: 0.6,  speed: 0.006, scale: 1.05 },
];

function drawDNAStrand(s) {
    const cx   = s.cx * W;
    const amp  = s.amp * s.scale;
    const pitch= H / s.pitchH;
    const steps= 56;
    const parX = (mx / W - 0.5) * 28 * s.scale;
    const parY = (my / H - 0.5) * 16 * s.scale;

    ctx.lineWidth = 1.5;

    for (let i = 0; i < steps; i++) {
        const y0 = (i / steps)   * H * 1.25 - H * 0.125;
        const y1 = ((i+1)/steps) * H * 1.25 - H * 0.125;
        const a0 = (y0 / pitch) * Math.PI * 2 + t * s.speed + s.phase;
        const a1 = (y1 / pitch) * Math.PI * 2 + t * s.speed + s.phase;

        const x0L = cx + parX + Math.cos(a0) * amp;
        const x0R = cx + parX - Math.cos(a0) * amp;
        const x1L = cx + parX + Math.cos(a1) * amp;
        const x1R = cx + parX - Math.cos(a1) * amp;
        const y0p = y0 + parY;
        const y1p = y1 + parY;

        const alpha = 0.12 + 0.2 * Math.abs(Math.cos(a0));

        // Left backbone
        ctx.beginPath(); ctx.moveTo(x0L, y0p); ctx.lineTo(x1L, y1p);
        ctx.strokeStyle = `rgba(0,160,210,${alpha})`; ctx.stroke();
        // Right backbone
        ctx.beginPath(); ctx.moveTo(x0R, y0p); ctx.lineTo(x1R, y1p);
        ctx.strokeStyle = `rgba(0,130,190,${alpha})`; ctx.stroke();

        // Rungs every 4 steps
        if (i % 4 === 0) {
            const ym  = (y0p + y1p) / 2;
            const xmL = (x0L + x1L) / 2;
            const xmR = (x0R + x1R) / 2;
            const ra  = 0.08 + 0.22 * Math.abs(Math.cos(a0));
            ctx.beginPath(); ctx.moveTo(xmL, ym); ctx.lineTo(xmR, ym);
            ctx.strokeStyle = `rgba(0,229,255,${ra})`; ctx.lineWidth = 0.9; ctx.stroke();
            ctx.lineWidth = 1.5;

            // Glowing node dots
            const nr = 2.8 * s.scale;
            ctx.beginPath(); ctx.arc(xmL, ym, nr, 0, Math.PI*2);
            ctx.fillStyle = `rgba(0,210,240,${ra * 1.6})`; ctx.fill();
            ctx.beginPath(); ctx.arc(xmR, ym, nr, 0, Math.PI*2);
            ctx.fillStyle = `rgba(0,190,225,${ra * 1.6})`; ctx.fill();
        }

        // Backbone dots
        const bd = 2.2 * s.scale;
        ctx.beginPath(); ctx.arc(x0L, y0p, bd, 0, Math.PI*2);
        ctx.fillStyle = `rgba(0,195,230,${alpha * 0.9})`; ctx.fill();
        ctx.beginPath(); ctx.arc(x0R, y0p, bd, 0, Math.PI*2);
        ctx.fillStyle = `rgba(0,175,215,${alpha * 0.9})`; ctx.fill();
    }
}

/* ── Sweep scan ring ── */
let sweep = 0;
function drawSweep() {
    const cx = W / 2, cy = H / 2;
    const r1 = Math.min(W, H) * 0.42;
    const r2 = Math.min(W, H) * 0.46;

    ctx.beginPath();
    ctx.arc(cx, cy, r1, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(0,229,255,0.03)';
    ctx.lineWidth = 1; ctx.stroke();

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(sweep);
    const g = ctx.createLinearGradient(0, -r2, 0, r2);
    g.addColorStop(0, 'rgba(0,229,255,0)');
    g.addColorStop(0.6, 'rgba(0,229,255,0.035)');
    g.addColorStop(1, 'rgba(0,229,255,0.07)');
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, r2, -0.6, 0.6);
    ctx.closePath();
    ctx.fillStyle = g;
    ctx.fill();
    ctx.restore();

    sweep -= 0.005;
}

/* ── Glowing center pulse ── */
function drawCenterGlow() {
    const cx = W/2, cy = H/2;
    const pulse = 0.5 + 0.5 * Math.sin(t * 0.04);
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.min(W,H)*0.3);
    g.addColorStop(0, `rgba(0,229,255,${0.018 * pulse})`);
    g.addColorStop(1, 'rgba(0,229,255,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
}

/* ── Main render loop ── */
function loop() {
    ctx.clearRect(0, 0, W, H);

    // Deep background
    const bg = ctx.createRadialGradient(W/2, H/2, 0, W/2, H/2, Math.max(W,H)*0.65);
    bg.addColorStop(0, 'rgba(0,22,48,0.3)');
    bg.addColorStop(1, 'rgba(2,12,20,0)');
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);

    drawCenterGlow();
    drawSweep();
    STRANDS.forEach(drawDNAStrand);
    drawParticles();

    t++;
    requestAnimationFrame(loop);
}
loop();
</script>
</body>
</html>
"""

# Render the full-screen animated canvas
st.components.v1.html(LANDING_HTML, height=650, scrolling=False)

# ── GET STARTED button (native Streamlit — always visible and works) ───────
st.markdown("""
<style>
div[data-testid="stVerticalBlock"] > div:last-child > div{
    display:flex;justify-content:center;align-items:center;
    flex-direction:column;padding-bottom:1rem;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("⚡  GET STARTED", key="gs_btn", use_container_width=True):
        st.switch_page("pages/blood_ai.py")