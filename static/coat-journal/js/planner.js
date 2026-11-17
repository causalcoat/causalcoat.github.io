/* Planned commands only: no execution, upload, or credential collection. */
(function () {
  'use strict';
  const form = document.getElementById('planner');
  if (!form) return;
  const zh = form.dataset.locale === 'zh';
  const t = (en, cn) => zh ? cn : en;
  const el = name => form.elements.namedItem(name);
  const val = name => el(name).value.trim();
  const state = {main_provider: 'deepseek', decision_provider: 'deepseek', decision_kind: 'llm', reuse: 'yes', decision_model: 'jev', kev_size: '9b', service: 'local', method: 'mb', dataset: 'example'};
  const providers = JSON.parse(form.dataset.providers);
  const caches = {main: {}, decision: {}};
  const selected = {main: {}, decision: {}};
  const decisionModels = JSON.parse(form.dataset.decisionModels);
  const examples = JSON.parse(form.dataset.examples);
  const dmCache = Object.fromEntries(Object.entries(decisionModels).map(([name, spec]) => [name, {name: 'decision', address: spec.address, env: spec.api_key_env || ''}]));
  const outputs = Object.fromEntries(Array.from(form.querySelectorAll('[data-output]'), x => [x.dataset.output, x]));
  let tab = 'shell';
  const roundDefaults = JSON.parse(form.dataset.roundDefaults);
  const roundSelections = {};
  const sh = s => "'" + s.replace(/'/g, "'\\''") + "'";
  const py = s => JSON.stringify(s).replace(/[\u007f-\u009f\u2028\u2029]/g, c => '\\u' + c.charCodeAt(0).toString(16).padStart(4, '0'));
  const integer = s => /^[1-9]\d*$/.test(s) && Number.isSafeInteger(Number(s));
  const envValid = s => /^[A-Za-z_][A-Za-z0-9_]*$/.test(s);
  function current(prefix) {
    const provider = state[prefix + '_provider'];
    const model = selected[prefix][provider] || providers[provider].models[0] || 'custom';
    selected[prefix][provider] = model;
    const key = provider + ':' + model;
    if (!caches[prefix][key]) caches[prefix][key] = {name: prefix, custom: '', address: providers[provider].address, env: providers[provider].api_key_env || (provider === 'vllm' ? 'VLLM_API_KEY' : ''), effort: 'default'};
    return caches[prefix][key];
  }
  function save(prefix) { const c = current(prefix); ['name', 'custom', 'address', 'env'].forEach(k => { c[k] = el(prefix + '_' + k).value; }); }
  function load(prefix) { const c = current(prefix); ['name', 'custom', 'address', 'env'].forEach(k => { el(prefix + '_' + k).value = c[k]; }); }
  function buttons(container, options, active, callback) {
    const existing = new Map(Array.from(container.children, button => [button.dataset.value, button]));
    options.forEach(([value, label], index) => {
      let button = existing.get(value);
      if (!button) {
        button = document.createElement('button'); button.type = 'button'; button.dataset.value = value;
        button.addEventListener('click', () => button.onSelect(button.dataset.value));
      }
      button.onSelect = callback;
      button.textContent = label;
      button.setAttribute('aria-pressed', String(value === active));
      if (container.children[index] !== button) container.insertBefore(button, container.children[index] || null);
      existing.delete(value);
    });
    existing.forEach(button => button.remove());
  }
  function renderSide(prefix) {
    const provider = state[prefix + '_provider'], p = providers[provider], model = selected[prefix][provider], c = current(prefix);
    buttons(form.querySelector('[data-models="' + prefix + '"]'), [...p.models.map(x => [x, x]), ['custom', t('Custom', '自定义')]], model, value => { save(prefix); selected[prefix][provider] = value; load(prefix); render(); });
    form.querySelector('[data-custom-model="' + prefix + '"]').hidden = model !== 'custom';
    const supported = model !== 'custom' && p.efforts.length > 0;
    form.querySelector('[data-effort-wrap="' + prefix + '"]').hidden = !supported;
    form.querySelector('[data-effort-hint="' + prefix + '"]').hidden = supported;
    if (supported) {
      const efforts = p.efforts;
      buttons(form.querySelector('[data-efforts="' + prefix + '"]'), [['default', t('Service default', '服务默认')], ...efforts.map(x => [x, x])], c.effort, value => { c.effort = value; render(); });
    }
  }
  function validate(name, ok, message) {
    const input = el(name), error = form.querySelector('[data-error="' + name + '"]');
    input.setAttribute('aria-invalid', String(!ok)); error.textContent = ok ? '' : message;
    return !!ok;
  }
  const required = t('Required', '必填');
  function sideValid(prefix) {
    const p = providers[state[prefix + '_provider']], custom = selected[prefix][state[prefix + '_provider']] === 'custom';
    const a = validate(prefix + '_name', val(prefix + '_name'), required);
    const b = validate(prefix + '_address', val(prefix + '_address'), required);
    const c = validate(prefix + '_env', envValid(val(prefix + '_env')),  t('Enter a valid variable name', '填写有效的变量名'));
    const d = !custom || validate(prefix + '_custom', val(prefix + '_custom'), required);
    return a && b && c && d;
  }
  function sideCommand(prefix) {
    const provider = state[prefix + '_provider'], model = selected[prefix][provider], c = current(prefix), p = providers[provider];
    let cmd = 'coatlearn setup connection ' + sh(val(prefix + '_name')) + ' --backend ' + sh(p.backend) + ' --provider ' + sh(provider) + ' --model ' + sh(model === 'custom' ? val(prefix + '_custom') : model) + ' --address ' + sh(val(prefix + '_address'));
    if (val(prefix + '_env')) cmd += ' --api-key-env ' + sh(val(prefix + '_env'));
    if (model !== 'custom' && c.effort !== 'default') cmd += ' --effort ' + sh(c.effort);
    return cmd + ' --replace';
  }
  function render() {
    const {decision_kind, reuse, decision_model, kev_size, service, method, dataset} = state;
    renderSide('main'); renderSide('decision');
    if (integer(val('rounds'))) {
      el('rounds_slider').max = String(Math.max(10, Number(val('rounds'))));
      el('rounds_slider').value = val('rounds');
    }
    form.querySelector('[data-rounds-hint]').textContent = method === 'pag'
      ? t('Iteration limit per target and graph expansion stage; may stop early when unchanged.', '每个目标与图扩展阶段的迭代上限；结果不变时可能提前结束。')
      : t('Each iteration proposes factors, measures them and uses statistical feedback. More iterations may increase time and cost.', '每次提出候选因子、测量并获取统计反馈。次数越多，耗时和费用可能越高。');
    form.querySelector('[data-decision-llm]').hidden = decision_kind !== 'llm';
    form.querySelector('[data-independent]').hidden = reuse !== 'no';
    form.querySelector('[data-decision-model]').hidden = decision_kind !== 'model';
    form.querySelector('[data-kev]').hidden = decision_model !== 'kev';
    form.querySelector('[data-dm-env]').hidden = decision_model !== 'jev';
    form.querySelector('[data-custom]').hidden = dataset !== 'custom';
    const adjExample = method === 'adj' && dataset === 'example';
    form.querySelector('[data-adj-example]').hidden = !adjExample;
    form.querySelectorAll('[data-method]').forEach(x => { x.hidden = x.dataset.method !== method; });
    form.querySelector('[data-method-hint]').textContent = ({mb: t('Find factors around one target.', '寻找与一个目标有关的因素。'), pag: t('Refine a graph with known variables.', '用已有变量细化结构。'), adj: t('Find adjustment variables for an effect.', '为指定效应寻找调整变量。')})[method];
    let setupValid = sideValid('main');
    const setup = [sideCommand('main')];
    let decisionName = val('main_name');
    if (decision_kind === 'llm' && reuse === 'no') {
      const valid = sideValid('decision'); decisionName = val('decision_name');
      setupValid = setupValid && valid && decisionName !== val('main_name'); setup.push(sideCommand('decision'));
      if (decisionName === val('main_name')) validate('decision_name', false, t('Use a different name', '请使用不同名称'));
    } else if (decision_kind === 'model') {
      const a = validate('dm_name', val('dm_name') && val('dm_name') !== val('main_name'), t('Required; use a different name', '必填，且不能与主模型同名'));
      const b = validate('dm_address', val('dm_address'), required);
      const c = decision_model !== 'jev' || validate('dm_env', envValid(val('dm_env')), t('Enter a valid variable name', '填写有效的变量名'));
      setupValid = setupValid && a && b && c; decisionName = val('dm_name');
      const model = decision_model === 'jev' ? decisionModels.jev.models[0] : decisionModels.kev.models.find(name => name.includes('-' + kev_size + '-'));
      setup.push('coatlearn setup connection ' + sh(decisionName) + ' --backend ' + sh(decision_model) + ' --model ' + sh(model) + ' --address ' + sh(val('dm_address')) + (decision_model === 'jev' ? ' --api-key-env ' + sh(val('dm_env')) : '') + ' --replace');
      if (decision_model === 'kev' && service === 'local') setup.push('coatlearn setup local prepare --model ' + sh(model) + ' --address ' + sh(val('dm_address')) + ' --execute\n\n' + t('# Run in another terminal; this server stays in the foreground.', '# 请在另一个终端运行；服务会占用该终端。') + '\ncoatlearn setup local start --model ' + sh(model) + ' --address ' + sh(val('dm_address')));
    }
    const get = name => dataset === 'example' ? examples[method][name] : val(name);
    const requiredNames = ['data', 'text_col', ...(method === 'mb' ? ['target'] : method === 'pag' ? ['known'] : ['treatment', 'outcome'])];
    let dataValid = true;
    if (dataset === 'custom') requiredNames.forEach(name => { if (!validate(name, name === 'known' ? get(name).split(',').every(x => x.trim()) : get(name), required)) dataValid = false; });
    const known = method === 'pag' ? get('known').split(',').map(x => x.trim()) : [];
    const fields = method === 'mb' ? [['target', get('target')]] : method === 'pag' ? known.map(x => ['known-variable', x]) : [['treatment', get('treatment')], ['outcome', get('outcome')]];
    validate('output', true, '');
    const concurrencyValid = validate('concurrency', integer(val('concurrency')), t('Enter a positive integer', '填写正整数'));
    const roundsValid = validate('rounds', integer(val('rounds')), t('Enter a positive integer', '填写正整数'));
    const runValid = setupValid && dataValid && concurrencyValid && roundsValid;
    const args = [...(dataset === 'example' ? [['config', 'config/' + method + '.toml']] : []), ['data', get('data')], ['text-col', get('text_col')], ...fields, ['main-connection', val('main_name')], ['decision-kind', decision_kind === 'llm' ? 'llm' : 'model'], ['decision-connection', decisionName], ['rounds', val('rounds')], ['concurrency', val('concurrency')], ...(val('output') ? [['output', val('output')]] : [])];
    const prepareMethod = dataset === 'example' ? method : 'none';
    const shell = 'coatlearn setup prepare --method ' + prepareMethod + ' --directory . --decision-kind ' + decision_kind + '\n\ncoatlearn run ' + method + ' \\\n  ' + args.map(([k, v]) => '--' + k + ' ' + sh(v)).join(' \\\n  ') + ' \\\n  --execute';
    const pythonFields = method === 'pag' ? [['known_variables', '[' + known.map(py).join(', ') + ']']] : fields.map(([k, v]) => [k, py(v)]);
    const kwargs = [...(dataset === 'example' ? [['config', py('config/' + method + '.toml')]] : []), ['data', py(get('data'))], ['text_col', py(get('text_col'))], ...pythonFields, ['main_connection', py(val('main_name'))], ['decision_kind', py(decision_kind === 'llm' ? 'llm' : 'model')], ['decision_connection', py(decisionName)], ['rounds', val('rounds')], ['concurrency', val('concurrency')], ...(val('output') ? [['output', py(val('output'))]] : [])];
    const python = 'from coatlearn.preparation import prepare_resources\n\nprepare_resources(method=' + py(prepareMethod) + ', decision_kind=' + py(decision_kind) + ')\n\nfrom coatlearn.workspace import run_task\n\nresult = run_task(\n    ' + py(method) + ',\n    execute=True,\n' + kwargs.map(([k, v]) => '    ' + k + '=' + v + ',').join('\n') + '\n)';
    const error = t('Complete the required fields with valid values to see the preview.', '请填写必需字段和有效值，以显示预览。');
    for (const [kind, valid, text, language] of [['setup', setupValid, setup.join('\n\n'), 'bash'], ['run', runValid, tab === 'shell' ? shell : python, tab === 'shell' ? 'bash' : 'python']]) {
      const code = outputs[kind]; code.className = valid ? 'language-' + language : ''; code.textContent = valid ? text : error;
      form.querySelector('[data-copy-planner="' + kind + '"]').disabled = !valid;
      if (valid && window.Prism && Prism.languages[language]) { Prism.manual = true; Prism.highlightElement(code); }
    }
  }
  form.querySelectorAll('[data-group]').forEach(button => button.addEventListener('click', () => {
    const group = button.dataset.group, previous = state[group], next = button.dataset.value;
    if ((group === 'method' || group === 'dataset') && previous !== next) {
      roundSelections[state.method + ':' + state.dataset] = val('rounds');
      const nextMethod = group === 'method' ? next : state.method;
      const nextDataset = group === 'dataset' ? next : state.dataset;
      el('rounds').value = roundSelections[nextMethod + ':' + nextDataset] || (nextDataset === 'example' ? roundDefaults[nextMethod] : '2');
    }
    if (group.endsWith('_provider') && previous !== next) { const prefix = group.split('_')[0]; save(prefix); state[group] = next; load(prefix); }
    else if (group === 'decision_model' && previous !== next) { ['name', 'address', 'env'].forEach(k => { dmCache[previous][k] = el('dm_' + k).value; }); state[group] = next; ['name', 'address', 'env'].forEach(k => { el('dm_' + k).value = dmCache[next][k]; }); }
    else if (group === 'kev_size' && previous !== next) {
      const oldDefault = 'http://127.0.0.1:' + (previous === '4b' ? '8014' : '8019');
      if (el('dm_address').value === oldDefault) el('dm_address').value = 'http://127.0.0.1:' + (next === '4b' ? '8014' : '8019');
      state[group] = next;
    }
    else state[group] = next;
    form.querySelectorAll('[data-group="' + group + '"]').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.value === next)));
    render();
  }));
  form.addEventListener('input', event => { const name = event.target.name || ''; if (name === 'rounds_slider') el('rounds').value = event.target.value; if (name.startsWith('main_')) save('main'); if (name.startsWith('decision_')) save('decision'); render(); });
  form.addEventListener('change', render);
  form.querySelectorAll('[data-tab]').forEach(button => button.addEventListener('click', () => { tab = button.dataset.tab; form.querySelectorAll('[data-tab]').forEach(x => x.setAttribute('aria-pressed', String(x === button))); render(); }));
  form.querySelectorAll('[data-copy-planner]').forEach(button => button.addEventListener('click', async () => {
    const content = outputs[button.dataset.copyPlanner].textContent; let ok = false;
    try { if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(content); ok = true; } } catch (_) { /* Try fallback. */ }
    if (!ok) { const area = document.createElement('textarea'); area.value = content; area.readOnly = true; area.style.position = 'fixed'; area.style.left = '-9999px'; document.body.append(area); area.select(); try { ok = document.execCommand('copy'); } catch (_) { /* Manual selection remains available. */ } area.remove(); button.focus(); }
    form.querySelector('[data-copy-status="' + button.dataset.copyPlanner + '"]').textContent = ok ? t('Copied.', '已复制。') : t('Copy failed; select the code.', '复制失败，请选中代码。');
  }));
  form.addEventListener('submit', event => event.preventDefault());
  load('main'); load('decision'); render();
})();
