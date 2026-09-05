/* ==========================================================================
   VaultScreen 8K — main.js
   --------------------------------------------------------------------------
   Progressive enhancement only. The page is fully usable without this file;
   everything here adds polish: reveal-on-scroll, count-up numbers, card
   spotlight, hero tilt, mobile nav, FAQ accordion, contact form handling.
   No dependencies.
   ========================================================================== */
(() => {
  'use strict';

  const $  = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer  = window.matchMedia('(hover: hover) and (pointer: fine)');

  /* ------------------------------------------------------------------
     Header: frosted background once the page has scrolled
  ------------------------------------------------------------------ */
  const header = $('.header');
  const toTop  = $('.to-top');

  const onScroll = () => {
    const y = window.scrollY || document.documentElement.scrollTop;
    header?.classList.toggle('is-scrolled', y > 8);
    toTop?.classList.toggle('is-visible', y > 600);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ------------------------------------------------------------------
     Mobile navigation
  ------------------------------------------------------------------ */
  const navToggle = $('.nav-toggle');
  const nav       = $('#site-nav');

  const setNav = (open) => {
    if (!navToggle || !nav) return;
    navToggle.setAttribute('aria-expanded', String(open));
    navToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    nav.classList.toggle('is-open', open);
    document.body.classList.toggle('nav-locked', open);
  };

  navToggle?.addEventListener('click', () => {
    setNav(navToggle.getAttribute('aria-expanded') !== 'true');
  });
  nav?.addEventListener('click', (e) => {
    if (e.target.closest('a')) setNav(false);
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && nav?.classList.contains('is-open')) {
      setNav(false);
      navToggle?.focus();
    }
  });
  window.matchMedia('(min-width: 861px)').addEventListener('change', (e) => {
    if (e.matches) setNav(false);
  });

  /* ------------------------------------------------------------------
     Active nav link (scroll spy)
  ------------------------------------------------------------------ */
  const navLinks = $$('.nav-list a[href^="#"]');
  const sections = navLinks
    .map((a) => $(a.getAttribute('href')))
    .filter(Boolean);

  if ('IntersectionObserver' in window && sections.length) {
    const spy = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        navLinks.forEach((a) => {
          const active = a.getAttribute('href') === `#${entry.target.id}`;
          if (active) a.setAttribute('aria-current', 'true');
          else a.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    sections.forEach((s) => spy.observe(s));
  }

  /* ------------------------------------------------------------------
     Reveal on scroll
  ------------------------------------------------------------------ */
  const revealEls = $$('.reveal');
  if ('IntersectionObserver' in window && !reduceMotion.matches) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('is-visible'));
  }

  /* ------------------------------------------------------------------
     Count-up numbers  (<span data-count="250" data-suffix="K+">)
  ------------------------------------------------------------------ */
  const counters = $$('[data-count]');
  const formatNum = (n, decimals) =>
    decimals > 0 ? n.toFixed(decimals) : Math.round(n).toLocaleString();

  const runCounter = (el) => {
    const target   = parseFloat(el.dataset.count);
    const decimals = parseInt(el.dataset.decimals || '0', 10);
    const prefix   = el.dataset.prefix || '';
    const suffix   = el.dataset.suffix || '';
    if (Number.isNaN(target)) return;

    if (reduceMotion.matches) {
      el.textContent = prefix + formatNum(target, decimals) + suffix;
      return;
    }

    const duration = 1600;
    const start = performance.now();
    const easeOut = (t) => 1 - Math.pow(1 - t, 4);

    const tick = (now) => {
      const p = Math.min(1, (now - start) / duration);
      el.textContent = prefix + formatNum(target * easeOut(p), decimals) + suffix;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  if ('IntersectionObserver' in window && counters.length) {
    const cio = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        runCounter(entry.target);
        cio.unobserve(entry.target);
      });
    }, { threshold: 0.6 });
    counters.forEach((el) => cio.observe(el));
  }

  /* ------------------------------------------------------------------
     Card spotlight — pointer-tracked radial highlight
  ------------------------------------------------------------------ */
  if (finePointer.matches) {
    $$('[data-spotlight]').forEach((card) => {
      card.addEventListener('pointermove', (e) => {
        const r = card.getBoundingClientRect();
        card.style.setProperty('--mx', `${e.clientX - r.left}px`);
        card.style.setProperty('--my', `${e.clientY - r.top}px`);
      });
    });
  }

  /* ------------------------------------------------------------------
     Hero visual tilt
  ------------------------------------------------------------------ */
  const tilt = $('[data-tilt]');
  if (tilt && finePointer.matches && !reduceMotion.matches) {
    const zone = tilt.closest('.hero') || tilt;
    let raf = 0;

    zone.addEventListener('pointermove', (e) => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const r  = tilt.getBoundingClientRect();
        const dx = (e.clientX - (r.left + r.width  / 2)) / r.width;
        const dy = (e.clientY - (r.top  + r.height / 2)) / r.height;
        const rx = Math.max(-1, Math.min(1, dy)) * -7;
        const ry = Math.max(-1, Math.min(1, dx)) *  9;
        tilt.style.transform = `perspective(1200px) rotateX(${rx}deg) rotateY(${ry}deg)`;
      });
    });
    zone.addEventListener('pointerleave', () => {
      cancelAnimationFrame(raf);
      tilt.style.transform = '';
    });
  }

  /* ------------------------------------------------------------------
     FAQ accordion (one open at a time)
  ------------------------------------------------------------------ */
  const faqButtons = $$('.faq-q');
  faqButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const expanded = btn.getAttribute('aria-expanded') === 'true';
      faqButtons.forEach((b) => {
        b.setAttribute('aria-expanded', 'false');
        $(`#${b.getAttribute('aria-controls')}`)?.classList.remove('is-open');
      });
      if (!expanded) {
        btn.setAttribute('aria-expanded', 'true');
        $(`#${btn.getAttribute('aria-controls')}`)?.classList.add('is-open');
      }
    });
  });

  /* ------------------------------------------------------------------
     Contact form
     - Client-side validation with inline errors
     - POSTs to data-endpoint if set (e.g. Formspree), else mailto fallback
  ------------------------------------------------------------------ */
  const form = $('#contact-form');
  if (form) {
    const status = $('.form-status', form);
    const fields = $$('input:not([name="_gotcha"]), textarea', form);

    const showError = (input, msg) => {
      const err = input.parentElement?.querySelector('.field-error');
      input.setAttribute('aria-invalid', msg ? 'true' : 'false');
      if (err) err.textContent = msg;
    };

    const validate = (input) => {
      const v = input.value.trim();
      if (input.required && !v) return 'This field is required.';
      if (input.type === 'email' && v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return 'Enter a valid email address.';
      if (input.minLength > 0 && v && v.length < input.minLength) return `Please enter at least ${input.minLength} characters.`;
      return '';
    };

    fields.forEach((input) => {
      input.addEventListener('blur', () => showError(input, validate(input)));
      input.addEventListener('input', () => {
        if (input.getAttribute('aria-invalid') === 'true') showError(input, validate(input));
      });
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (form._gotcha?.value) return; // bot

      let firstInvalid = null;
      fields.forEach((input) => {
        const msg = validate(input);
        showError(input, msg);
        if (msg && !firstInvalid) firstInvalid = input;
      });
      if (firstInvalid) { firstInvalid.focus(); return; }

      const data = Object.fromEntries(new FormData(form).entries());
      const endpoint = form.dataset.endpoint;
      const submitBtn = $('button[type="submit"]', form);

      if (endpoint) {
        submitBtn.disabled = true;
        status.textContent = 'Sending…';
        try {
          const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
            body: JSON.stringify(data),
          });
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          status.textContent = 'Thanks — your message has been sent. We\u2019ll be in touch shortly.';
          form.reset();
        } catch (err) {
          status.textContent = 'Something went wrong. Please try again or email us directly.';
          console.error(err);
        } finally {
          submitBtn.disabled = false;
        }
      } else {
        // Mailto fallback — opens the visitor's mail client with the message pre-filled
        const to = form.dataset.mailto || '';
        const subject = encodeURIComponent(data.subject || `Website enquiry from ${data.name}`);
        const body = encodeURIComponent(`${data.message}\n\n— ${data.name} (${data.email})`);
        window.location.href = `mailto:${to}?subject=${subject}&body=${body}`;
        status.textContent = 'Opening your email app…';
      }
    });
  }

  /* ------------------------------------------------------------------
     Footer year
  ------------------------------------------------------------------ */
  $$('[data-year]').forEach((el) => { el.textContent = String(new Date().getFullYear()); });
})();
