document.getElementById('year').textContent = new Date().getFullYear();

const navToggle = document.getElementById('navToggle');
const primaryNav = document.getElementById('primaryNav');

navToggle.addEventListener('click', () => {
    const isOpen = primaryNav.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', isOpen);
});

primaryNav.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
        primaryNav.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
    });
});

const header = document.getElementById('siteHeader');
const backToTop = document.getElementById('backToTop');

window.addEventListener('scroll', () => {
    const scrolled = window.scrollY > 40;
    header.style.boxShadow = scrolled ? '0 6px 20px -14px rgba(15,42,61,.4)' : 'none';
    backToTop.classList.toggle('visible', window.scrollY > 500);
});

backToTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

const starfield = document.getElementById('starfield');
if (starfield) {
    const ctx = starfield.getContext('2d');
    const heroEl = starfield.closest('.hero');
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let stars = [];
    let width, height;

    function resize() {
        width = starfield.width = heroEl.offsetWidth;
        height = starfield.height = heroEl.offsetHeight;
        const count = Math.round((width * height) / 9000);
        stars = Array.from({ length: count }, () => ({
            x: Math.random() * width,
            y: Math.random() * height,
            r: Math.random() * 1.3 + 0.3,
            baseAlpha: Math.random() * 0.5 + 0.25,
            phase: Math.random() * Math.PI * 2,
            speed: Math.random() * 0.015 + 0.005,
        }));
    }

    function drawStatic() {
        ctx.clearRect(0, 0, width, height);
        stars.forEach((s) => {
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255,255,255,${s.baseAlpha})`;
            ctx.fill();
        });
    }

    let frame = 0;
    function animate() {
        frame++;
        ctx.clearRect(0, 0, width, height);
        stars.forEach((s) => {
            const twinkle = Math.sin(frame * s.speed + s.phase) * 0.35;
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255,255,255,${Math.max(0.1, s.baseAlpha + twinkle)})`;
            ctx.fill();
        });
        requestAnimationFrame(animate);
    }

    resize();
    if (reduceMotion) {
        drawStatic();
    } else {
        animate();
    }
    window.addEventListener('resize', () => {
        resize();
        if (reduceMotion) drawStatic();
    });
}
