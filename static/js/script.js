document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const hash = this.getAttribute('href');
    if (!hash || hash === '#') return;

    const target = document.querySelector(hash);
    if (!target) return;

    e.preventDefault();

    const header = document.querySelector('header');
    const headerHeight = header ? header.offsetHeight : 0;
    const elementPosition = target.getBoundingClientRect().top + window.scrollY;
    const offsetPosition = elementPosition - headerHeight;

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });
  });
});

const sections = document.querySelectorAll('[class$="section"]');
const navLinks = document.querySelectorAll('.nav-link');

if (sections.length && navLinks.length && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          navLinks.forEach(link => {
            link.classList.remove('active');
            const href = link.getAttribute('href') || '';
            const hash = href.includes('#') ? href.substring(href.indexOf('#')) : '';
            if (hash === `#${entry.target.id}`) {
              link.classList.add('active');
            }
          });
        }
      });
    },
    { rootMargin: '-50% 0px -40% 0px', threshold: 0 }
  );

  sections.forEach(section => observer.observe(section));
}

function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.style.display = 'block';
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.style.display = 'none';
}

window.addEventListener('click', event => {
  document.querySelectorAll('.modal').forEach(modal => {
    if (event.target === modal) modal.style.display = 'none';
  });
});
