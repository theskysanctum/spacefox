(function () {
  'use strict';
  const TILE_DATA_URI = "__CRT_TILE_DATA_URI__";

  function inject() {
    const overlay = document.createElement('div');
    overlay.id = 'spacefox-crt-overlay';
    Object.assign(overlay.style, {
      position: 'fixed',
      inset: '0',
      backgroundImage: `url(${TILE_DATA_URI})`,
      backgroundRepeat: 'repeat',
      pointerEvents: 'none',
      zIndex: '2147483647',
    });
    document.documentElement.appendChild(overlay);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
