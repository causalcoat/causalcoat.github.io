/* Local accessibility and navigation enhancements around pinned Docsify plugins. */
(function () {
  'use strict';
  var input, clear, status, help, panel, currentLanguage, observer;
  var messages = {
    en: {search: 'Search English documentation', clear: 'Clear search', help: 'Search this language · / or Ctrl/⌘ K · Esc to clear', results: ' results', none: 'No results. Try a shorter term or a function name.', source: 'View this page on GitHub'},
    zh: {search: '搜索中文文档', clear: '清除搜索', help: '搜索当前语言 · / 或 Ctrl/⌘ K · Esc 清除', results: ' 条结果', none: '没有找到结果。试试更短的词语或函数名。', source: '在 GitHub 查看本页源码'}
  };
  function language() { return location.hash.indexOf('#/zh-cn/') === 0 ? 'zh' : 'en'; }
  function announce() {
    if (!input || !status) return;
    var count = panel.querySelectorAll('.matching-post').length;
    status.textContent = input.value.trim() ? (count ? count + messages[language()].results : messages[language()].none) : '';
  }
  function clearSearch() {
    if (!input) return;
    input.value = '';
    if (clear) clear.click();
    input.dispatchEvent(new Event('input', {bubbles: true}));
  }
  function enhanceSearch() {
    input = document.querySelector('.search input');
    if (!input) return;
    var box = input.closest('.search');
    panel = box.querySelector('.results-panel');
    clear = box.querySelector('.clear-button');
    if (!box.dataset.enhanced) {
      box.dataset.enhanced = 'true';
      box.setAttribute('role', 'search');
      help = document.createElement('p');help.className = 'search-help';help.id = 'docs-search-help';
      status = document.createElement('p');status.className = 'search-status';status.setAttribute('role', 'status');status.setAttribute('aria-live', 'polite');
      box.insertBefore(help, panel);box.insertBefore(status, panel);
      input.setAttribute('aria-describedby', help.id);
      input.setAttribute('autocomplete', 'off');
      clear.setAttribute('role', 'button');clear.setAttribute('tabindex', '0');
      clear.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault();clear.click();input.focus(); }
      });
      input.addEventListener('keydown', function (event) {
        if (event.key === 'ArrowDown') {
          var first = panel.querySelector('a');
          if (first) { event.preventDefault();first.focus(); }
        } else if (event.key === 'Enter') {
          var result = panel.querySelector('a');
          if (result) { event.preventDefault();result.click(); }
        }
      });
      panel.addEventListener('keydown', function (event) {
        var links = Array.from(panel.querySelectorAll('a'));
        var index = links.indexOf(document.activeElement);
        if (event.key === 'ArrowDown' && links[index + 1]) {event.preventDefault();links[index + 1].focus();}
        if (event.key === 'ArrowUp') {event.preventDefault();if (index > 0) links[index - 1].focus();else input.focus();}
      });
      observer = new MutationObserver(announce);observer.observe(panel, {childList: true});
    }
    var lang = language(), text = messages[lang];
    if (currentLanguage && currentLanguage !== lang) clearSearch();
    currentLanguage = lang;
    input.setAttribute('aria-label', text.search);clear.setAttribute('aria-label', text.clear);help.textContent = text.help;
    box.setAttribute('aria-label', text.search);announce();
  }
  document.addEventListener('keydown', function (event) {
    var element = document.activeElement;
    var editing = element && (element.matches('input,textarea,select') || element.isContentEditable);
    if (((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') || (event.key === '/' && !editing && !event.ctrlKey && !event.metaKey && !event.altKey)) {
      if (!input) return;
      event.preventDefault();
      document.body.classList.toggle('close', innerWidth <= 768);
      input.focus();input.select();
    } else if (event.key === 'Escape' && input && input.closest('.search').contains(element)) {
      clearSearch();input.focus();
    }
  });
  window.$docsify.plugins = [].concat(window.$docsify.plugins || [], function (hook, vm) {
    hook.afterEach(function (html) {
      var route = vm.route.path;
      var source = route.replace(/^\//, '');
      if (!source || source.endsWith('/')) source += 'README.md';
      if (!source.endsWith('.md')) source += '.md';
      return html + '<footer class="doc-source"><a target="_blank" rel="noopener" href="https://github.com/causalcoat/COAT-Learn/blob/main/docs/' + source + '">' + messages[language()].source + ' ↗</a></footer>';
    });
    hook.doneEach(enhanceSearch);
  });
}());
