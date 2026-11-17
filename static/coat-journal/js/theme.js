/* Apply the saved or system theme before styles are painted. */
(function () {
  'use strict';
  var root = document.documentElement;
  var preference = null;
  try { preference = localStorage.getItem('coat-theme'); } catch (_) {}
  if (preference !== 'light' && preference !== 'dark') preference = null;
  var system = window.matchMedia('(prefers-color-scheme: dark)');
  function apply(theme) {
    root.setAttribute('data-theme', theme);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', theme === 'dark' ? '#171d19' : '#f6f5f0');
    var button = document.querySelector('.theme-toggle');
    if (button) {
      var label = theme === 'dark' ? button.dataset.lightLabel : button.dataset.darkLabel;
      button.setAttribute('aria-label', label);
      button.setAttribute('title', label);
    }
  }
  apply(preference || (system.matches ? 'dark' : 'light'));
  function initialize() {
    var button = document.querySelector('.theme-toggle');
    if (!button) return;
    button.hidden = false;
    apply(root.getAttribute('data-theme'));
    button.addEventListener('click', function () {
      preference = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('coat-theme', preference); } catch (_) {}
      apply(preference);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize);
  else initialize();
  function systemChanged(event) { if (!preference) apply(event.matches ? 'dark' : 'light'); }
  if (system.addEventListener) system.addEventListener('change', systemChanged);
  else if (system.addListener) system.addListener(systemChanged);
  window.addEventListener('storage', function (event) {
    if (event.key !== 'coat-theme' && event.key !== null) return;
    preference = event.newValue === 'dark' || event.newValue === 'light' ? event.newValue : null;
    apply(preference || (system.matches ? 'dark' : 'light'));
  });
})();
