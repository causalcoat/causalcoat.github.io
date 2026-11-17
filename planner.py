"""Bilingual markup for the browser-only command preview."""
from html import escape
import json


def render_planner(locale, doc, project, catalog):
    rounds = {method: spec['example_rounds'] for method, spec in catalog['methods'].items()}
    defaults = escape(json.dumps(rounds), quote=True)
    zh = locale == 'zh'
    def t(en, cn):
        return cn if zh else en
    def field(name, label, value='', placeholder='', attrs=''):
        return f'<label>{escape(label)}<input name="{name}" value="{escape(value, quote=True)}" placeholder="{escape(placeholder, quote=True)}" {attrs}><small class="planner-error" data-error="{name}"></small></label>'
    def chips(group, options, selected):
        return '<div class="planner-chips" role="group" aria-label="' + escape(group, quote=True) + '">' + ''.join(f'<button type="button" data-group="{group}" data-value="{value}" aria-pressed="{str(value == selected).lower()}">{label}</button>' for value, label in options) + '</div>'
    provider_data = escape(json.dumps(catalog['providers']), quote=True)
    decision_data = escape(json.dumps(catalog['decision_models']), quote=True)
    examples = {}
    for method, spec in catalog['methods'].items():
        task = dict(spec['example'])
        # Example files are prepared under config/ and data/ in the user's workspace.
        task['data'] = (project / 'config' / task['data']).resolve().relative_to(project.resolve()).as_posix()
        if 'known_variables' in task:
            task['known'] = ', '.join(task.pop('known_variables'))
        examples[method] = task
    example_data = escape(json.dumps(examples), quote=True)
    labels = {'deepseek': 'DeepSeek', 'openrouter': 'OpenRouter', 'opencode': 'OpenCode', 'vllm': 'vLLM'}
    providers = [(name, labels.get(name, name)) for name in catalog['providers']]
    def model_side(prefix):
        return f'''<p class="planner-label">{t('Model source', '模型来源')}</p>{chips(prefix + '_provider', providers, 'deepseek')}
        <p class="planner-label">{t('Model', '模型')}</p><div class="planner-chips" role="group" aria-label="{t('Model', '模型')}" data-models="{prefix}"></div>
        <div data-custom-model="{prefix}" hidden>{field(prefix + '_custom', t('Custom model name', '自定义模型名称'), placeholder=t('Enter a model name', '填写模型名称'))}</div>
        <div data-effort-wrap="{prefix}"><p class="planner-label">{t('Reasoning effort', '推理强度')}</p><div class="planner-chips" role="group" aria-label="{t('Reasoning effort', '推理强度')}" data-efforts="{prefix}"></div></div>
        <p class="planner-hint" data-effort-hint="{prefix}" hidden>{t('Reasoning options depend on the deployed model.', '推理选项取决于部署的模型。')}</p>
        <details><summary>{t('Connection settings', '连接设置')}</summary><div class="planner-detail">{field(prefix + '_name', t('Connection name', '连接名称'))}{field(prefix + '_address', t('Endpoint', '服务地址'))}{field(prefix + '_env', t('API key environment variable', '密钥环境变量名'), attrs='autocomplete="off" spellcheck="false"')}</div></details>'''
    def code(kind, title, tabs=''):
        return f'''<div class="planner-code"><div class="planner-code-head"><div class="planner-code-title"><strong>{title}</strong>{tabs}</div><div class="planner-copy"><span role="status" aria-live="polite" data-copy-status="{kind}"></span><button type="button" data-copy-planner="{kind}">{t('Copy', '复制')}</button></div></div><pre tabindex="0"><code data-output="{kind}"></code></pre></div>'''
    tabs = f'''<div class="planner-tabs" role="group" aria-label="{t('Code language', '代码语言')}"><button type="button" data-tab="shell" aria-pressed="true">Shell</button><button type="button" data-tab="python" aria-pressed="false">Python</button></div>'''
    return f'''<section class="section use-section" id="use" aria-labelledby="use-title"><div class="container">
    <div class="section-heading"><div><p class="eyebrow">{t('Get started', '开始使用')}</p><h2 id="use-title">{t('Configure models. Run an analysis.', '配好模型，开始分析。')}</h2></div></div>
    <noscript><p>{t('Enable JavaScript to update the preview.', '请启用 JavaScript 以更新预览。')}</p></noscript>
    <form id="planner" data-locale="{locale}" data-round-defaults="{defaults}" data-providers="{provider_data}" data-decision-models="{decision_data}" data-examples="{example_data}" novalidate><article class="planner-panel"><header><span>01 / {t('MODELS', '模型')}</span><h3>{t('Configure models', '配置模型')}</h3></header>
    <div class="planner-models"><section class="planner-card"><h4>{t('Main model', '主模型')}</h4>{model_side('main')}</section>
    <section class="planner-card"><h4>{t('Annotation model', '标注模型（Annotation）')}</h4><p class="planner-label">{t('Model type', '模型类型')}</p>{chips('decision_kind', [('llm', 'LLM'), ('model', 'Decision Model')], 'llm')}
    <div data-decision-llm><p class="planner-label">{t('LLM connection', 'LLM 连接')}</p>{chips('reuse', [('yes', t('Reuse main model', '复用主模型')), ('no', t('Choose separately', '单独选择'))], 'yes')}<div data-independent hidden>{model_side('decision')}</div></div>
    <div data-decision-model hidden><p class="planner-label">{t('Decision model', '决策模型')}</p>{chips('decision_model', [('jev', 'Jev'), ('kev', 'Kev')], 'jev')}<div data-kev hidden><p class="planner-label">{t('Size', '模型规模')}</p>{chips('kev_size', [('9b', '9B'), ('4b', '4B')], '9b')}<p class="planner-label">{t('Service', '服务')}</p>{chips('service', [('local', t('New service', '新建服务')), ('existing', t('Existing service', '已有服务'))], 'local')}</div><details><summary>{t('Connection settings', '连接设置')}</summary><div class="planner-detail">{field('dm_name', t('Connection name', '连接名称'), 'decision')}{field('dm_address', t('Endpoint', '服务地址'), 'https://api.typesafe.ai')}<div data-dm-env>{field('dm_env', t('API key environment variable', '密钥环境变量名'), 'TYPESAFE_API_KEY')}</div></div></details></div></section></div>
    {code('setup', t('Save model connections · Shell', '保存模型连接 · Shell'))}</article>
    <article class="planner-panel"><header><span>02 / {t('ANALYSIS', '分析')}</span><h3>{t('Run an analysis', '运行分析')}</h3></header><div class="planner-run-fields"><div><p class="planner-label">{t('Goal', '分析目标')}</p>{chips('method', [('mb','MB'),('pag','PAG'),('adj','ADJ')], 'mb')}<p class="planner-hint" data-method-hint></p></div><div><p class="planner-label">{t('Data', '数据')}</p>{chips('dataset', [('example',t('Example','示例数据')),('custom',t('My data','自有数据'))], 'example')}</div><div class="planner-iterations"><label class="planner-label" for="planner-rounds">{t('Factor discovery iterations', '因子发现迭代次数')}</label><div class="planner-range"><input type="range" name="rounds_slider" min="1" max="10" step="1" value="{rounds['mb']}" aria-label="{t('Factor discovery iterations slider', '因子发现迭代次数滑动条')}" aria-describedby="planner-rounds-hint"><input id="planner-rounds" name="rounds" type="number" min="1" step="1" value="{rounds['mb']}" aria-describedby="planner-rounds-hint"><small class="planner-error" data-error="rounds"></small></div><p id="planner-rounds-hint" class="planner-hint" data-rounds-hint></p></div>
    <div class="planner-custom" data-custom hidden>{field('data', t('Data path', '数据路径'), placeholder='./data/reviews.csv')}{field('text_col', t('Text column', '文本列'), placeholder='Review')}<div data-method="mb">{field('target', t('Target column', '目标列'), placeholder='Score')}</div><div data-method="pag" hidden>{field('known', t('Known variables, comma-separated', '已有变量，用逗号分隔'), placeholder='Taste, Score')}</div><div data-method="adj" hidden>{field('treatment', t('Treatment column', '处理列'), placeholder='email_type')}{field('outcome', t('Outcome column', '结果列'), placeholder='visit')}</div></div>
    <div data-adj-example hidden><p class="planner-hint">{t('Synthetic email / visit example · post → email_type / visit · 2 rounds. The run code prepares the example files.', '合成邮件 / 访问示例 · 文本 post，处理 email_type，结果 visit · 默认 2 轮。运行代码会先准备示例文件。')}</p><details><summary>{t('ADJ example settings and assumptions', 'ADJ 示例设置与研究假设')}</summary><p class="planner-hint">{t('The example configuration uses treatment Yes/missing → 1/0; outcome Yes/No → 1/0; mv_fisherz, alpha 0.001, seed 42, FCI depth 2.', '示例配置：处理列 Yes/缺失 → 1/0；结果列 Yes/No → 1/0；检验 mv_fisherz，显著性水平 0.001，随机种子 42，FCI 深度 2。')}</p><p class="planner-hint">{t('This synthetic example assumes treatment precedes outcome and factors precede treatment. It enables cycle breaking and an explicit researcher exemption for adjustment amenability.', '该合成示例假定处理影响结果、因子先于处理，并启用环处理和带理由的调整可行性豁免。')}</p></details></div><details class="planner-advanced"><summary>{t('Advanced settings', '高级设置')}</summary><div class="planner-detail">{field('concurrency', t('Annotation concurrency', '标注并行数'), '16', attrs='type="number" min="1" step="1"')}{field('output', t('Output directory', '输出目录'), placeholder=t('Create a run directory automatically', '自动创建运行目录'))}</div><p class="planner-hint">{t('Number of annotation tasks processed at once; actual request counts are also affected by model connection rate limits.', '同时处理的标注任务数；实际请求数量还受模型连接限流影响。')}</p></details></div>{code('run', t('Run analysis', '运行分析'), tabs)}</article></form></div></section>'''
