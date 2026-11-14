/* Progressive enhancement: local teaching material only; no fetch, models or telemetry. */
(function () {
  'use strict';
  var manifest = document.getElementById('page-data');
  if (!manifest) return;
  var data;
  try { data = JSON.parse(manifest.textContent); } catch (_) { return; }
  document.documentElement.classList.add('js');
  var ui = data.ui;
  var state = { reviews: { sample: 0, factor: 0 }, medical: { sample: 0, factor: 0 }, news: { sample: 0, factor: 0 } };
  function node(tag, text, className) {
    var el = document.createElement(tag);
    if (text !== undefined) el.textContent = text;
    if (className) el.className = className;
    return el;
  }
  function valueText(value) { return value === null ? ui.missing : String(value); }
  function paint(key) {
    var panel = document.getElementById('demo-' + key);
    var example = data.demos[key], current = state[key];
    var sample = example.samples[current.sample], factor = example.factors[current.factor];
    var value = sample.values[current.factor];
    panel.querySelector('[data-context]').textContent = sample.context;
    panel.querySelector('[data-factor-title]').textContent = factor.name;
    panel.querySelector('[data-summary]').textContent = factor.summary;
    panel.querySelector('[data-value]').textContent = valueText(value);
    panel.querySelectorAll('[data-sample]').forEach(function (button) { button.setAttribute('aria-pressed', String(Number(button.dataset.sample) === current.sample)); });
    panel.querySelectorAll('[data-factor]').forEach(function (button) { button.setAttribute('aria-pressed', String(Number(button.dataset.factor) === current.factor)); });
    panel.querySelectorAll('[data-cell]').forEach(function (button) { button.setAttribute('aria-pressed', String(button.dataset.cell === current.sample + ',' + current.factor)); });
    var rules = panel.querySelector('[data-rules]');
    rules.replaceChildren();
    factor.rules.forEach(function (rule) {
      var cls = value !== null && Number(rule[0]) === value ? 'selected-rule' : '';
      rules.append(node('dt', rule[0], cls), node('dd', rule[1], cls));
    });
    var reason = value === null ? ui.no_mention : ui.rule_match;
    if (example.kind === 'text') {
      var source = panel.querySelector('[data-source-text]');
      source.replaceChildren();
      sample.parts.forEach(function (part) {
        source.appendChild(part[1] === factor.key ? node('mark', part[0], 'active-evidence') : document.createTextNode(part[0]));
      });
    } else {
      var image = panel.querySelector('[data-source-image]');
      image.src = 'static/coat-journal/images/' + sample.image;
      var box = panel.querySelector('[data-roi]'), region = sample.regions[current.factor];
      box.hidden = !region;
      if (region) {
        box.style.left = region[0] + '%'; box.style.top = region[1] + '%';
        box.style.width = region[2] + '%'; box.style.height = region[3] + '%';
      }
      reason = example.note;
    }
    panel.querySelector('[data-reason]').textContent = reason;
    panel.dataset.selectedSample = sample.id;
    panel.dataset.selectedFactor = factor.key;
    panel.dataset.selectedValue = valueText(value);
  }
  Object.keys(state).forEach(function (key) {
    var panel = document.getElementById('demo-' + key);
    panel.addEventListener('click', function (event) {
      var control = event.target.closest('button');
      if (!control) return;
      if (control.hasAttribute('data-reset')) { state[key].sample = 0; state[key].factor = 0; }
      else if (control.hasAttribute('data-cell')) {
        var indices = control.dataset.cell.split(',').map(Number);
        state[key].sample = indices[0]; state[key].factor = indices[1];
      } else if (control.hasAttribute('data-sample')) state[key].sample = Number(control.dataset.sample);
      else if (control.hasAttribute('data-factor')) state[key].factor = Number(control.dataset.factor);
      else return;
      paint(key);
    });
    paint(key);
  });
  var tabs = Array.from(document.querySelectorAll('[data-dataset]'));
  var tablist = document.querySelector('.dataset-tabs');
  tablist.setAttribute('role', 'tablist');
  function selectDataset(key, focus) {
    tabs.forEach(function (tab) {
      var selected = tab.dataset.dataset === key;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      document.getElementById('demo-' + tab.dataset.dataset).hidden = !selected;
      if (selected && focus) tab.focus();
    });
  }
  tabs.forEach(function (tab, index) {
    var panel = document.getElementById('demo-' + tab.dataset.dataset);
    tab.setAttribute('role', 'tab'); tab.setAttribute('aria-controls', panel.id);
    panel.setAttribute('role', 'tabpanel'); panel.tabIndex = 0;
    tab.addEventListener('click', function (event) { event.preventDefault(); selectDataset(tab.dataset.dataset, false); });
    tab.addEventListener('keydown', function (event) {
      var next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      else return;
      event.preventDefault(); selectDataset(tabs[next].dataset.dataset, true);
    });
  });
  selectDataset('reviews', false);
  var menu = document.querySelector('.menu-toggle'), navigation = document.getElementById('site-nav');
  var mobile = window.matchMedia('(max-width: 700px)');
  function closeMenu(focus) {
    navigation.classList.remove('is-open'); menu.setAttribute('aria-expanded', 'false');
    if (focus) menu.focus();
  }
  menu.addEventListener('click', function () {
    var open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open)); navigation.classList.toggle('is-open', open);
  });
  navigation.addEventListener('click', function (event) { if (event.target.closest('a')) closeMenu(false); });
  document.addEventListener('keydown', function (event) { if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') closeMenu(true); });
  document.addEventListener('click', function (event) { if (mobile.matches && !event.target.closest('.site-header')) closeMenu(false); });
  mobile.addEventListener('change', function () { if (!mobile.matches) closeMenu(false); });
  function revealHash() {
    var hash;
    try { hash = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    var target = document.getElementById(hash);
    if (!target) return;
    var panel = target.closest('[data-demo]');
    if (panel) selectDataset(panel.dataset.demo, false);
    var parent = target;
    while (parent) { if (parent.tagName === 'DETAILS') parent.open = true; parent = parent.parentElement; }
    requestAnimationFrame(function () { target.scrollIntoView({ block: 'start' }); });
  }
  window.addEventListener('hashchange', revealHash);
  if (location.hash) revealHash();
  // Keep language switches at the same section where possible.
  document.querySelectorAll('.language-link').forEach(function (a) {
    a.addEventListener('click', function () { if (location.hash) a.href = a.getAttribute('href').split('#')[0] + location.hash; });
  });
  if ('IntersectionObserver' in window) {
    var anchors = Array.from(navigation.querySelectorAll('a[href^="#"]'));
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        anchors.forEach(function (a) { if (a.hash === '#' + entry.target.id) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current'); });
      });
    }, { rootMargin: '-10% 0px -65% 0px' });
    anchors.forEach(function (a) { var section = document.getElementById(a.hash.slice(1)); if (section) observer.observe(section); });
  }
  var dialog = document.getElementById('image-dialog');
  if (typeof dialog.showModal === 'function') {
    document.querySelector('[data-zoom]').addEventListener('click', function () {
      dialog.querySelector('[data-dialog-image]').replaceChildren(document.querySelector('[data-image-stage]').cloneNode(true));
      dialog.showModal();
    });
    dialog.querySelector('[data-close-dialog]').addEventListener('click', function () { dialog.close(); });
    dialog.addEventListener('click', function (event) {
      var rect = dialog.getBoundingClientRect();
      if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
    });
  }
  function fallbackCopy(text) {
    var prior = document.activeElement, field = node('textarea');
    field.value = text; field.readOnly = true; field.style.position = 'fixed'; field.style.left = '-9999px';
    document.body.appendChild(field); field.select();
    var success = false;
    try { success = document.execCommand('copy'); } catch (_) { /* Manual copy remains available. */ }
    field.remove(); if (prior) prior.focus({ preventScroll: true });
    return success;
  }
  document.querySelectorAll('[data-copy]').forEach(function (button) {
    button.addEventListener('click', async function () {
      var text = document.getElementById(button.dataset.copy).textContent.trim();
      var success = false;
      try { if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(text); success = true; } else success = fallbackCopy(text); }
      catch (_) { success = fallbackCopy(text); }
      var prior = button.textContent;
      button.textContent = success ? ui.copied : ui.copy_failed;
      document.getElementById('page-status').textContent = button.textContent;
      window.setTimeout(function () { button.textContent = prior; document.getElementById('page-status').textContent = ''; }, 1800);
    });
  });
})();
