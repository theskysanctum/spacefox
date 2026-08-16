(function () {
  'use strict';

  function isEditable(el) {
    if (!el) return false;
    if (el.isContentEditable) return true;
    const tag = el.tagName;
    if (tag === 'TEXTAREA') return true;
    if (tag === 'INPUT') {
      const type = (el.getAttribute('type') || 'text').toLowerCase();
      return !['button', 'submit', 'checkbox', 'radio', 'range', 'color', 'file', 'reset', 'image'].includes(type);
    }
    return false;
  }

  document.addEventListener('focusin', (event) => {
    if (isEditable(event.target)) {
      window.__spacefoxSend({ action: 'show' });
    }
  });

  document.addEventListener('focusout', (event) => {
    if (isEditable(event.target)) {
      window.__spacefoxSend({ action: 'hide' });
    }
  });
})();
