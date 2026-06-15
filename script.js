// הגלריה נטענת מ-gallery-data.js שנוצר אוטומטית ע"י process-images.py

const galleryGrid = document.getElementById('gallery-grid');
const galleryEmpty = document.getElementById('gallery-empty');
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightbox-img');
const lightboxCaption = document.getElementById('lightbox-caption');

function padNumber(num) {
  return String(num).padStart(3, '0');
}

function createGalleryCard(src, index) {
  const serial = padNumber(index + 1);
  const card = document.createElement('article');
  card.className = 'gallery-card';
  card.innerHTML = `
    <div class="gallery-card-image">
      <img src="${src}" alt="דגם מספר ${serial}" loading="lazy">
      <span class="gallery-card-badge">מס׳ ${serial}</span>
    </div>
    <div class="gallery-card-body">
      <h3>דגם ${serial}</h3>
      <p>שלט מעוצב באומנות יד</p>
    </div>
  `;

  card.addEventListener('click', () => openLightbox(src, serial));
  return card;
}

function openLightbox(src, serial) {
  lightboxImg.src = src;
  lightboxCaption.textContent = `דגם מספר ${serial}`;
  lightbox.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeLightbox() {
  lightbox.classList.add('hidden');
  lightboxImg.src = '';
  document.body.style.overflow = '';
}

function renderGallery() {
  const images = typeof IMAGES !== 'undefined' ? IMAGES : [];

  if (images.length === 0) {
    galleryEmpty.classList.remove('hidden');
    return;
  }

  galleryEmpty.classList.add('hidden');
  galleryGrid.replaceChildren();
  images.forEach((src, index) => {
    galleryGrid.appendChild(createGalleryCard(src, index));
  });
}

document.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
lightbox.addEventListener('click', (e) => {
  if (e.target === lightbox) closeLightbox();
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeLightbox();
});

renderGallery();
