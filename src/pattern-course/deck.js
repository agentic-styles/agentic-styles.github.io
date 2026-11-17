const slides = [...document.querySelectorAll('.slide')];
const counter = document.querySelector('#slide-counter');
const progress = document.querySelector('.progress');
let current = 0;

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function show(index, updateHash = true) {
  current = clamp(index, 0, slides.length - 1);
  slides.forEach((slide, i) => {
    slide.classList.toggle('active', i === current);
    slide.setAttribute('aria-hidden', i === current ? 'false' : 'true');
  });
  counter.value = `${String(current + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
  progress.style.width = `${((current + 1) / slides.length) * 100}%`;
  document.title = `${slides[current].dataset.title || 'Agentic Patterns'} · ${current + 1}/${slides.length}`;
  if (updateHash) history.replaceState(null, '', `#${current + 1}`);
}

function move(delta) { show(current + delta); }

document.querySelector('#prev').addEventListener('click', () => move(-1));
document.querySelector('#next').addEventListener('click', () => move(1));
document.querySelector('#fullscreen').addEventListener('click', () => {
  if (!document.fullscreenElement) document.documentElement.requestFullscreen?.();
  else document.exitFullscreen?.();
});

document.addEventListener('keydown', (event) => {
  if (document.body.classList.contains('overview')) {
    if (event.key === 'Escape' || event.key.toLowerCase() === 'o') document.body.classList.remove('overview');
    return;
  }
  if (['ArrowRight', 'ArrowDown', 'PageDown', ' ', 'Enter'].includes(event.key)) {
    event.preventDefault(); move(1);
  } else if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'].includes(event.key)) {
    event.preventDefault(); move(-1);
  } else if (event.key === 'Home') {
    event.preventDefault(); show(0);
  } else if (event.key === 'End') {
    event.preventDefault(); show(slides.length - 1);
  } else if (event.key.toLowerCase() === 'f') {
    document.querySelector('#fullscreen').click();
  } else if (event.key.toLowerCase() === 'o') {
    document.body.classList.add('overview');
  }
});

document.querySelector('.deck').addEventListener('click', (event) => {
  if (!document.body.classList.contains('overview')) return;
  const slide = event.target.closest('.slide');
  if (!slide) return;
  current = slides.indexOf(slide);
  document.body.classList.remove('overview');
  show(current);
});

window.addEventListener('hashchange', () => {
  const requested = Number(location.hash.slice(1));
  if (Number.isFinite(requested) && requested > 0) show(requested - 1, false);
});

slides.forEach((slide, i) => slide.dataset.index = String(i + 1).padStart(2, '0'));
const initial = Number(location.hash.slice(1));
show(Number.isFinite(initial) && initial > 0 ? initial - 1 : 0, false);
