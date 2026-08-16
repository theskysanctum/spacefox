(function () {
  'use strict';

  const FOCUSABLE_SELECTOR =
    'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"]), [role="button"], [role="link"]';

  function isVisible(el) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return false;
    const style = getComputedStyle(el);
    return style.visibility !== 'hidden' && style.display !== 'none';
  }

  function focusableCandidates() {
    return Array.from(document.querySelectorAll(FOCUSABLE_SELECTOR)).filter(
      (el) => !el.disabled && isVisible(el)
    );
  }

  function rectCenter(el) {
    const r = el.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  }

  function moveFocus(direction) {
    const candidates = focusableCandidates();
    if (candidates.length === 0) return;

    const current =
      document.activeElement && candidates.includes(document.activeElement)
        ? document.activeElement
        : null;

    if (!current) {
      candidates[0].focus();
      candidates[0].scrollIntoView({ block: 'nearest', inline: 'nearest' });
      return;
    }

    const from = rectCenter(current);
    let best = null;
    let bestScore = Infinity;

    for (const el of candidates) {
      if (el === current) continue;
      const to = rectCenter(el);
      const dx = to.x - from.x;
      const dy = to.y - from.y;

      let primary, perpendicular;
      if (direction === 'up') {
        primary = -dy;
        perpendicular = dx;
      } else if (direction === 'down') {
        primary = dy;
        perpendicular = dx;
      } else if (direction === 'left') {
        primary = -dx;
        perpendicular = dy;
      } else {
        primary = dx;
        perpendicular = dy;
      }

      if (primary <= 0) continue;
      const score = primary + Math.abs(perpendicular) * 2;
      if (score < bestScore) {
        bestScore = score;
        best = el;
      }
    }

    if (best) {
      best.focus();
      best.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    }
  }

  function activateFocused() {
    const el = document.activeElement;
    if (!el) return;
    if (el.tagName === 'A' || el.tagName === 'BUTTON' || el.getAttribute('role') === 'button') {
      el.click();
    }
  }

  window.__spacefoxOnMessage((msg) => {
    if (msg.action === 'nav') {
      moveFocus(msg.direction);
    } else if (msg.action === 'activate') {
      activateFocused();
    }
  });
})();
