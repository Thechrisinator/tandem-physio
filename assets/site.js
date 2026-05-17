const menuToggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('#site-nav');
const navLinks = document.querySelectorAll('#site-nav a');

if (menuToggle && nav) {
  menuToggle.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('is-open');
    menuToggle.setAttribute('aria-expanded', String(isOpen));
    menuToggle.textContent = isOpen ? '×' : '☰';
  });

  navLinks.forEach((link) => {
    link.addEventListener('click', () => {
      nav.classList.remove('is-open');
      menuToggle.setAttribute('aria-expanded', 'false');
      menuToggle.textContent = '☰';
    });
  });
}
