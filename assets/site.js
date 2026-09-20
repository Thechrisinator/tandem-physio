const menuToggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('#site-nav');
const navLinks = document.querySelectorAll('#site-nav a');

if (menuToggle && nav) {
  const mobile = window.matchMedia('(max-width: 880px)');
  let lastFocus = document.activeElement;
  document.addEventListener('focusin', (event) => { lastFocus = event.target; });
  document.addEventListener('pointerdown', () => { lastFocus = null; });
  const setMenu = (open, restoreFocus = false) => {
    nav.classList.toggle('is-open', open);
    menuToggle.setAttribute('aria-expanded', String(open));
    menuToggle.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    menuToggle.textContent = open ? '×' : '☰';
    if (restoreFocus) menuToggle.focus();
  };

  menuToggle.addEventListener('click', () => {
    setMenu(menuToggle.getAttribute('aria-expanded') !== 'true');
  });

  navLinks.forEach((link) => {
    link.addEventListener('click', () => {
      if (mobile.matches) setMenu(false, nav.contains(document.activeElement));
    });
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menuToggle.getAttribute('aria-expanded') === 'true') {
      setMenu(false, true);
    }
  });
  nav.addEventListener('focusout', (event) => {
    if (!nav.contains(event.relatedTarget) && event.relatedTarget !== menuToggle) setMenu(false);
  });
  mobile.addEventListener('change', () => {
    // CSS can hide the focused control before the media-query event fires.
    const active = document.activeElement === document.body ? lastFocus : document.activeElement;
    setMenu(false);
    if (mobile.matches && nav.contains(active)) menuToggle.focus();
    if (!mobile.matches && active === menuToggle) navLinks[0].focus();
  });

  setMenu(false);
  // Hide mobile navigation only after its controls have been wired successfully.
  document.documentElement.classList.add('nav-ready');
}

const revealItems = document.querySelectorAll('[data-reveal]');
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (revealItems.length && !reduceMotion && 'IntersectionObserver' in window) {
  document.body.classList.add('reveal-ready');

  const observer = new IntersectionObserver((entries, activeObserver) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        activeObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  revealItems.forEach((item) => observer.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add('is-visible'));
}
