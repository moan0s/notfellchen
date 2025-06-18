import PhotoSwipeLightbox from './photoswipe-lightbox.esm.js';

const lightbox = new PhotoSwipeLightbox({
  gallery: '.gallery',
  children: 'a',
  pswpModule: () => import('https://unpkg.com/photoswipe'),
});

lightbox.init();


