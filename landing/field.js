const CFG = {
  accent: "#22b573",
  count: 150,
  link: 108,
  speed: 60,
  mode: "attract"
};
const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const BOOTED = true;

(function chrome() {
  const pad = (n) => String(n).padStart(2, "0");
  const clock = document.getElementById("clock");
  const uptime = document.getElementById("uptime");
  const year = document.getElementById("year");
  const start = performance.now();
  if (year) year.textContent = String(new Date().getFullYear());
  function tick() {
    const d = new Date();
    if (clock) {
      clock.textContent =
        pad(d.getUTCHours()) + ":" + pad(d.getUTCMinutes()) + ":" + pad(d.getUTCSeconds()) + " UTC";
    }
    if (uptime) {
      const s = Math.floor((performance.now() - start) / 1000);
      const h = Math.floor(s / 3600);
      const m = Math.floor((s % 3600) / 60);
      const sec = s % 60;
      uptime.textContent = h ? h + "h " + m + "m" : m ? m + "m " + sec + "s" : sec + "s";
    }
  }
  tick();
  setInterval(tick, 1000);
})();

(function field() {
  const canvas = document.getElementById("field");
  if (!canvas) return;
  const ctx = canvas.getContext("2d", { alpha: true });
  let W = 0;
  let H = 0;
  const DPR = Math.min(window.devicePixelRatio || 1, 2);
  const mouse = { x: -9999, y: -9999, active: false };
  let particles = [];
  let pulses = [];
  let rafId = null;
  let lastT = 0;
  let lastSpawn = 0;
  const linkDist = CFG.link;
  const linkSq = linkDist * linkDist;

  function resize() {
    W = canvas.clientWidth = window.innerWidth;
    H = canvas.clientHeight = window.innerHeight;
    canvas.width = Math.floor(W * DPR);
    canvas.height = Math.floor(H * DPR);
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    seed();
  }

  function seed() {
    const n = Math.round(CFG.count);
    particles = new Array(n).fill(0).map(() => ({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      r: 0.6 + Math.random() * 1.4,
      l: 0.35 + Math.random() * 0.55,
      flash: 0
    }));
    pulses = [];
  }

  function hexToRgb(h) {
    const m = h.replace("#", "");
    const n = m.length === 3 ? m.split("").map((c) => c + c).join("") : m;
    const v = parseInt(n, 16);
    return [(v >> 16) & 255, (v >> 8) & 255, v & 255];
  }

  function nearest(i) {
    const a = particles[i];
    let best = -1;
    let bd = linkSq;
    for (let j = 0; j < particles.length; j++) {
      if (j === i) continue;
      const dx = a.x - particles[j].x;
      const dy = a.y - particles[j].y;
      const d = dx * dx + dy * dy;
      if (d < bd) {
        bd = d;
        best = j;
      }
    }
    return best;
  }

  function step(t) {
    rafId = requestAnimationFrame(step);
    const dt = Math.min(0.05, (t - lastT) / 1000 || 0.016);
    lastT = t;
    ctx.clearRect(0, 0, W, H);
    const speedK = CFG.speed / 60;
    const mode = CFG.mode;
    const [ar, ag, ab] = hexToRgb(CFG.accent);

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      if (mouse.active && mode !== "off") {
        const dx = mouse.x - p.x;
        const dy = mouse.y - p.y;
        const d2 = dx * dx + dy * dy;
        const R = 180;
        const R2 = R * R;
        if (d2 < R2 && d2 > 0.01) {
          const d = Math.sqrt(d2);
          const falloff = 1 - d / R;
          const f = falloff * falloff * 90;
          const nx = dx / d;
          const ny = dy / d;
          if (mode === "attract") {
            p.vx += nx * f * dt;
            p.vy += ny * f * dt;
          } else if (mode === "repel") {
            p.vx -= nx * f * dt;
            p.vy -= ny * f * dt;
          } else if (mode === "orbit") {
            p.vx += (-ny * f * 1.2 + nx * f * 0.15) * dt;
            p.vy += (nx * f * 1.2 + ny * f * 0.15) * dt;
          }
        }
      }
      p.x += p.vx * speedK;
      p.y += p.vy * speedK;
      p.vx *= 0.985;
      p.vy *= 0.985;
      if (p.x < -10) p.x = W + 10;
      else if (p.x > W + 10) p.x = -10;
      if (p.y < -10) p.y = H + 10;
      else if (p.y > H + 10) p.y = -10;
    }

    if (linkDist > 0) {
      for (let i = 0; i < particles.length; i++) {
        const a = particles[i];
        for (let j = i + 1; j < particles.length; j++) {
          const b = particles[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const d2 = dx * dx + dy * dy;
          if (d2 < linkSq) {
            const tt = 1 - Math.sqrt(d2) / linkDist;
            const alpha = tt * 0.18;
            ctx.strokeStyle = "rgba(" + ar + "," + ag + "," + ab + "," + alpha + ")";
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
      }
    }

    if (BOOTED && t - lastSpawn > 3400 && pulses.length < 2) {
      lastSpawn = t;
      const i = (Math.random() * particles.length) | 0;
      const j = nearest(i);
      if (j >= 0) pulses.push({ i, j, t0: t });
    }
    for (let k = pulses.length - 1; k >= 0; k--) {
      const pu = pulses[k];
      const pr = (t - pu.t0) / 950;
      if (pr >= 1) {
        particles[pu.j].flash = t;
        pulses.splice(k, 1);
        continue;
      }
      const a = particles[pu.i];
      const b = particles[pu.j];
      const e = pr * pr * (3 - 2 * pr);
      for (let s = 0; s < 4; s++) {
        const bp = Math.max(0, e - s * 0.05);
        const bx = a.x + (b.x - a.x) * bp;
        const by = a.y + (b.y - a.y) * bp;
        ctx.beginPath();
        ctx.arc(bx, by, 2.0 - s * 0.4, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(" + ar + "," + ag + "," + ab + "," + (0.8 - s * 0.2) + ")";
        ctx.fill();
      }
    }

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      const fl = p.flash ? Math.max(0, 1 - (t - p.flash) / 500) : 0;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r + fl * 2, 0, Math.PI * 2);
      ctx.fillStyle =
        fl > 0
          ? "rgba(" + ar + "," + ag + "," + ab + "," + (p.l + fl * 0.5) + ")"
          : "rgba(230,230,230," + p.l + ")";
      ctx.fill();
    }

    if (mouse.active && mode !== "off") {
      const g = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, 180);
      g.addColorStop(0, "rgba(" + ar + "," + ag + "," + ab + ",0.10)");
      g.addColorStop(1, "rgba(" + ar + "," + ag + "," + ab + ",0)");
      ctx.fillStyle = g;
      ctx.fillRect(mouse.x - 180, mouse.y - 180, 360, 360);
    }
  }

  window.addEventListener("resize", resize, { passive: true });
  window.addEventListener(
    "pointermove",
    (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
      mouse.active = true;
    },
    { passive: true }
  );
  window.addEventListener("pointerleave", () => {
    mouse.active = false;
  });
  window.addEventListener("blur", () => {
    mouse.active = false;
  });

  resize();
  if (REDUCED) {
    step(0);
    cancelAnimationFrame(rafId);
  } else {
    rafId = requestAnimationFrame(step);
  }
})();
