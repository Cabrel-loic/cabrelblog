// static/js/input.js
// Consolidated site JS: replaces HTMX behaviors with vanilla JS

(function () {
  'use strict';

  // --- CSRF helpers (Django) ---
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }
  const csrftoken = getCookie('csrftoken');

  function fetchOptions(method, body, isFormData) {
    const opts = {
      method,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
      credentials: 'same-origin',
      body,
    };
    if (!isFormData && body) {
      // For JSON bodies (not used here), set content-type
      opts.headers['Content-Type'] = 'application/json';
    }
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method.toUpperCase()) && csrftoken) {
      opts.headers['X-CSRFToken'] = csrftoken;
    }
    return opts;
  }

  // --- Utility: swap an element by selector from an HTML string ---
  function swapFromHTML(responseHTML, selector, targetElement) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(responseHTML, 'text/html');
    const replacement = doc.querySelector(selector);
    if (replacement && targetElement) {
      targetElement.replaceWith(replacement);
      return true;
    }
    return false;
  }

  // --- Like button (replaces HTMX on core/partials/like_button.html) ---
  function onLikeSubmit(e) {
    const form = e.target.closest('form.js-like-form');
    if (!form) return;
    e.preventDefault();

    const action = form.getAttribute('action');
    const formData = new FormData(form);

    // Find the like button wrapper to swap (id="like-button-<post.id>")
    const wrapper = form.closest('[id^="like-button-"]');

    fetch(action, fetchOptions('POST', formData, true))
      .then(res => res.text())
      .then(html => {
        if (wrapper) {
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, 'text/html');
          const updated = doc.body.firstElementChild || doc.querySelector('[id^="like-button-"]');
          if (updated) wrapper.replaceWith(updated);
        }
      })
      .catch(err => console.error('Like toggle failed:', err));
  }

  // --- Inline edit form submit (replaces HTMX in core/partials/post_edit_form.html) ---
  function onInlineEditSubmit(e) {
    const form = e.target.closest('form.js-inline-edit-form');
    if (!form) return;
    e.preventDefault();

    const action = form.getAttribute('action');
    const formData = new FormData(form);

    fetch(action, fetchOptions('POST', formData, true))
      .then(res => res.text())
      .then(html => {
        const current = document.querySelector('#post-detail-body');
        if (!current) return;
        const swapped = swapFromHTML(html, '#post-detail-body', current);
        if (!swapped) {
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, 'text/html');
          const fallback = doc.querySelector('#post-detail-body') || doc.querySelector('main, body');
          if (fallback) current.replaceWith(fallback);
        }
      })
      .catch(err => console.error('Inline edit submit failed:', err));
  }

  // --- Inline edit loader (GET the partial and swap it) ---
  function onInlineEditTrigger(e) {
    const btn = e.target.closest('.js-inline-edit-trigger');
    if (!btn) return;
    e.preventDefault();
    const url = btn.getAttribute('data-edit-url');
    if (!url) return;

    fetch(url, fetchOptions('GET'))
      .then(res => res.text())
      .then(html => {
        const current = document.querySelector('#post-detail-body');
        if (!current) return;
        const swapped = swapFromHTML(html, '#post-detail-body', current);
        if (!swapped) {
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, 'text/html');
          const fallback = doc.querySelector('#post-detail-body');
          if (fallback) current.replaceWith(fallback);
        }
      })
      .catch(err => console.error('Load inline edit form failed:', err));
  }

  // --- Global listeners ---
  document.addEventListener('submit', function (e) {
    if (e.target && e.target.classList.contains('js-like-form')) {
      onLikeSubmit(e);
    } else if (e.target && e.target.classList.contains('js-inline-edit-form')) {
      onInlineEditSubmit(e);
    }
  });

  document.addEventListener('click', function (e) {
    if (e.target && e.target.classList.contains('js-inline-edit-trigger')) {
      onInlineEditTrigger(e);
    }
  });

})();