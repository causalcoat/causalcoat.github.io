#!/usr/bin/env python3
"""Build the bilingual COAT homepage from a sibling COAT-Learn checkout.

Run: python3 build.py [--project-source ../COAT-Learn]
The source checkout owns software docs; this repository owns website content.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess

from content import AUTHORS, BIBTEX, CONTENT, DEMOS, PAPER, PDF, TITLE

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent / "COAT-Learn"
ASSETS = "static/coat-journal/"
SOURCE = "https://github.com/causalcoat/COAT-Learn/tree/main"
PAGES = {"en": "index.html", "zh": "index-zh.html"}


def e(value):
    return html.escape(str(value), quote=True)


def doc(c, page="README"):
    return "docs/#/" + c["docpath"] + ("" if page == "README" else page + ".md")


def link(url, label, cls=""):
    return f'<a class="{cls}" href="{e(url)}">{label}</a>'


def button(url, label, primary=False):
    arrow = '↓' if url.startswith('#') else '↗'
    return link(url, e(label) + f'<span aria-hidden="true">{arrow}</span>', "button primary" if primary else "button secondary")


def code_block(identifier, title, code, c, language="bash"):
    return f'''<div class="code-block"><div class="code-heading"><h3>{e(title)}</h3><button type="button" class="js-only" data-copy="{identifier}">{e(c['copy'])}</button></div><pre id="{identifier}" tabindex="0"><code class="language-{language}">{e(code)}</code></pre></div>'''


def text_source(sample, factor):
    return "".join(f'<mark class="active-evidence">{e(text)}</mark>' if key == factor["key"] else e(text) for text, key in sample["parts"])


def demo_panel(key, data, c):
    sample = data["samples"][0]
    factor = data["factors"][0]
    picker = "".join(f'<button type="button" data-sample="{i}" aria-pressed="{str(i == 0).lower()}">{e(s["id"])}</button>' for i, s in enumerate(data["samples"]))
    factors = "".join(f'<button type="button" data-factor="{i}" aria-pressed="{str(i == 0).lower()}">{e(f["name"])}</button>' for i, f in enumerate(data["factors"]))
    if data["kind"] == "image":
        x, y, w, h = sample["regions"][0]
        source = f'''<div class="image-stage" data-image-stage><img data-source-image src="{ASSETS}images/{e(sample['image'])}" alt="{e(data['note'])}" width="308" height="308" loading="lazy"><span data-roi class="roi" style="left:{x}%;top:{y}%;width:{w}%;height:{h}%"></span></div><button type="button" class="text-button js-only" data-zoom>{e(c['zoom'])}</button>'''
    else:
        source = f'<blockquote class="raw-text" data-source-text>{text_source(sample, factor)}</blockquote>'
    rules = "".join(f'<dt>{e(n)}</dt><dd>{e(rule)}</dd>' for n, rule in factor["rules"])
    table_head = f'<th scope="col">{e(c["sample"])}</th>' + "".join(f'<th scope="col">{e(f["name"])}</th>' for f in data["factors"])
    rows = []
    for r, item in enumerate(data["samples"]):
        cells = "".join(f'<td><button type="button" data-cell="{r},{f}" aria-pressed="{str(r == 0 and f == 0).lower()}" aria-label="{e(item["id"] + ", " + data["factors"][f]["name"] + ", " + str(value if value is not None else c["missing"]))}">{e(value if value is not None else c["missing"])}</button></td>' for f, value in enumerate(item["values"]))
        rows.append(f'<tr><th scope="row">{e(item["id"])}</th>{cells}</tr>')
    reason = data.get("note", c["rule_match"])
    return f'''<section class="demo-panel" id="demo-{key}" data-demo="{key}" aria-labelledby="tab-{key}">
    <div class="evidence-grid"><div class="source-pane"><div class="pane-label"><h3>{e(c['source'])}</h3><span data-context>{e(sample['context'])}</span></div><div class="sample-picker" aria-label="{e(c['sample'])}">{picker}</div>{source}</div>
    <div class="rule-pane"><button type="button" class="reset-example js-only" data-reset>{e(c['reset'])}</button><h3>{e(c['definition'])}</h3><div class="factor-picker" aria-label="{e(c['factor'])}">{factors}</div><div class="definition-title"><h4 data-factor-title>{e(factor['name'])}</h4><span class="value-chip" data-value>{sample['values'][0]}</span></div><p data-summary>{e(factor['summary'])}</p><dl class="rule-list" data-rules>{rules}</dl><p class="measurement-reason" data-reason role="status" aria-live="polite">{e(reason)}</p></div></div>
    <details class="measurement-table" open><summary>{e(c['detail'])}</summary><p>{e(c['table_hint'])} {e(c['example_prompt']) if key == "reviews" else ""}</p><div class="table-scroll" tabindex="0" role="region" aria-label="{e(c['table_title'])}"><table><caption class="visually-hidden">{e(c['table_title'])}</caption><thead><tr>{table_head}</tr></thead><tbody>{''.join(rows)}</tbody></table></div></details></section>'''


def climate_panel(data, c):
    code = 'field = archive["air_temperature"].sel(\n    latitude=slice(-5, 5),\n    longitude=slice(210, 270),\n)\nfactor = field.mean(("latitude", "longitude"))'
    headings = "".join(f'<th scope="col">{e(m)}</th>' for m in data["months"])
    values = "".join(f'<td>{n:.1f}</td>' for n in data["values"])
    return f'''<section class="demo-panel climate-panel" id="demo-climate" data-demo="climate" aria-labelledby="tab-climate"><p class="climate-intro">{e(c['climate_intro'])}</p><div class="climate-grid"><div class="climate-definition"><dl class="climate-spec"><dt>{e(c['quantity'])}</dt><dd>{e(data['quantity'])}</dd><dt>{e(c['region'])}</dt><dd>{e(data['region'])}</dd></dl><h3 class="code-label">{e(c['climate_code'])}</h3><pre tabindex="0"><code>{e(code)}</code></pre></div><figure class="map-figure"><svg viewBox="0 0 480 240" role="img" aria-labelledby="climate-map-title"><title id="climate-map-title">{e(c['climate_map'])}</title><rect width="480" height="240" fill="#e4edf0"/><image href="{ASSETS}images/review-pacific-base.svg" width="480" height="240" preserveAspectRatio="none"/><path d="M0 120H480" stroke="#6c8f99" stroke-dasharray="3 4"/><rect x="120" y="113.3" width="80" height="13.4" fill="#a93f2533" stroke="#a93f25"/><text x="123" y="104" fill="#873f29" font-family="sans-serif" font-size="14">Niño3</text></svg><figcaption>{e(c['climate_map'])}</figcaption></figure></div><div class="table-scroll" tabindex="0" role="region" aria-label="{e(c['climate_output'])}"><table><caption>{e(c['climate_output'])} / °C</caption><thead><tr>{headings}</tr></thead><tbody><tr>{values}</tr></tbody></table></div><p class="demo-disclosure">{e(c['climate_note'])}</p></section>'''


def render(locale):
    c = CONTENT[locale]
    data = DEMOS[locale]
    nav = "".join(link("#" + key, e(label)) for key, label in c["nav"])
    cols = "".join(f'<div><span>{e(label)}</span><strong>{e(value)}</strong><small>{e(meaning)}</small></div>' for label, value, meaning in zip(c["hero_columns"], c["hero_values"], c["hero_meanings"]))
    tabs = "".join(f'<a id="tab-{key}" href="#demo-{key}" data-dataset="{key}"><strong>{e(title)}</strong><span>{e(subtitle)}</span></a>' for key, title, subtitle in c["datasets"])
    demos = "".join(demo_panel(key, data[key], c) for key in ("reviews", "medical", "news")) + climate_panel(data["climate"], c)
    loop = "".join(f'<li><span class="step-index">0{i+1}</span><h3>{e(title)}</h3><p>{e(body)}</p></li>' for i, (title, body) in enumerate(c["loop"]))
    tasks = "".join(f'''<article class="task"><div class="task-label">COAT-{t['id'].upper()}</div><h3>{e(t['question'])}</h3><h4>{e(t['term'])}</h4><p>{e(t['text'])}</p><dl><dt>{e(c['input_label'])}</dt><dd>{e(t['input'])}</dd><dt>{e(c['output_label'])}</dt><dd>{e(t['output'])}</dd></dl>{link(doc(c,'discovery') + '?id=' + ({'mb':'mb-seek-information-about-one-target','pag':'pag-refine-structure-with-new-variables','adj':'adj-seek-adjustment-variables-for-a-specified-effect'} if locale == 'en' else {'mb':'mb：寻找关于一个目标的信息','pag':'pag：用新变量细化结构','adj':'adj：为指定效应寻找调整变量'})[t['id']], e(c['task_link']) + ' <span aria-hidden="true">↗</span>', 'text-link')}</article>''' for t in c["tasks"])
    cases = "".join(f'''<article class="research-case"><p class="eyebrow">{e(case['name'])}</p><h3>{e(case['title'])}</h3><p>{e(case['body'])}</p><details><summary>{e(c['paper_figure'])}</summary><figure><img src="{ASSETS}images/{case['image']}" alt="{e(case['alt'])}" loading="lazy"><figcaption>{link(PDF,e(c['read_paper']))}</figcaption></figure></details></article>''' for case in c["cases"])
    manifest = {"ui": {k:c[k] for k in ["missing","no_mention","rule_match","copied","copy_failed","close"]}, "demos": data}
    manifest_json = json.dumps(manifest, ensure_ascii=False).replace('</', r'<\/')
    return f'''<!doctype html>
<!-- Generated by build.py from content.py and COAT-Learn/docs/. -->
<html lang="{c['lang']}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#f6f5f0">
<title>{e(c['title'])}</title><meta name="description" content="{e(c['description'])}">
<link rel="canonical" href="https://causalcoat.github.io/{'' if locale=='en' else 'index-zh.html'}">
<link rel="alternate" hreflang="en" href="https://causalcoat.github.io/"><link rel="alternate" hreflang="zh-CN" href="https://causalcoat.github.io/index-zh.html">
<meta property="og:type" content="website"><meta property="og:title" content="{e(c['title'])}"><meta property="og:description" content="{e(c['description'])}">
<link rel="icon" href="{ASSETS}images/favicon.svg" type="image/svg+xml"><link rel="preload" href="{ASSETS}fonts/manrope-latin-variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{ASSETS}css/style.css"><script src="{ASSETS}js/main.js" defer></script>
</head><body>
<a class="skip-link" href="#main">{e(c['skip'])}</a>
<header class="site-header"><div class="container header-inner"><a class="brand" href="#top"><span class="brand-name">COAT<span class="brand-dot" aria-hidden="true">.</span></span><span class="brand-subtitle">{e(c['brand'])}</span></a><button class="menu-toggle" type="button" aria-controls="site-nav" aria-expanded="false">{e(c['menu'])}<span aria-hidden="true">＋</span></button><nav id="site-nav" aria-label="{e(c['menu'])}">{nav}{link(doc(c),e(c['docs']),'nav-docs')}<a class="language-link" lang="{c['other_lang']}" hreflang="{c['other_lang']}" href="{c['other_file']}">{e(c['other'])}</a></nav></div></header>
<main id="main">
<section class="hero" id="top" aria-labelledby="hero-title"><div class="container"><a class="publication-link" href="{PAPER}">{e(c['publication'])}<span aria-hidden="true">↗</span></a><div class="hero-grid"><div class="hero-copy"><p class="eyebrow">{e(c['eyebrow'])}</p><h1 id="hero-title">{c['headline']}</h1><p class="hero-intro">{e(c['intro'])}</p><p class="hero-answer">{e(c['answer'])}</p><div class="button-row">{button('#variables',c['primary'],True)}{button(doc(c,'quickstart'),c['secondary'])}</div><p class="hero-note">{e(c['hero_note'])}</p></div><figure class="hero-example"><div class="example-label">{e(c['hero_label'])}<span aria-hidden="true">↙</span></div><blockquote>{c['quote']}</blockquote><p class="example-bridge">{e(c['hero_bridge'])}</p><div class="mini-table category-table">{cols}</div><figcaption>{e(c['hero_caption'])}</figcaption></figure></div><nav class="page-outline" aria-label="{e(c['menu'])}">{link("#variables",e(c["variables_kicker"]))}{link("#questions",e(c["questions_kicker"]))}{link("#use",e(c["use_kicker"]))}{link("#research",e(c["research_jump"]))}</nav></div></section>
<section class="section" id="variables" aria-labelledby="variables-title"><div class="container"><div class="section-heading"><div><p class="eyebrow">{e(c['variables_kicker'])}</p><h2 id="variables-title">{c['variables_title']}</h2></div><p>{e(c['variables_intro'])}</p></div><p class="example-notice">{e(c['example_badge'])}</p><div class="dataset-tabs" aria-label="{e(c['variables_kicker'])}">{tabs}</div><div class="demo-panels">{demos}</div><div class="demo-notes"><p>{e(c['encoding_note'])}</p><p>{e(c['demo_note'])} {e(c['data_scope'])}</p></div></div></section>
<section class="section discovery-section" id="discovery" aria-labelledby="discovery-title"><div class="container"><div class="section-heading"><div><p class="eyebrow">{e(c['discovery_kicker'])}</p><h2 id="discovery-title">{c['discovery_title']}</h2></div><p>{e(c['discovery_intro'])}</p></div><ol class="discovery-loop">{loop}</ol><div class="feedback-line"><span>{e(c['feedback_label'])}</span><p>“{e(c['feedback'])}”</p><span aria-hidden="true">↶</span></div><p class="division-note">{e(c['division'])}</p><details class="framework-detail"><summary>{e(c['framework'])}</summary><figure><img src="{ASSETS}images/coat_illustration.png" width="2006" height="1081" alt="{e(c['framework_alt'])}" loading="lazy"></figure></details></div></section>
<section class="section" id="questions" aria-labelledby="questions-title"><div class="container"><div class="section-heading"><div><p class="eyebrow">{e(c['questions_kicker'])}</p><h2 id="questions-title">{c['questions_title']}</h2></div><p>{e(c['questions_intro'])}</p></div><div class="task-grid">{tasks}</div><div class="independent-path"><p>{e(c['independent'])}</p><div>{link(doc(c,'annotation'),e(c['annotation_link']),'text-link')}{link(doc(c,'causality'),e(c['causality_link']),'text-link')}</div></div></div></section>
<section class="section use-section" id="use" aria-labelledby="use-title"><div class="container"><div class="section-heading"><div><p class="eyebrow">{e(c['use_kicker'])}</p><h2 id="use-title">{c['use_title']}</h2></div><p>{e(c['use_intro'])}</p></div><div class="source-prerequisite"><strong>{e(c['source_step'])}</strong><p>{e(c['source_help'])}</p>{link(SOURCE,e(c['source_link']),"text-link")}</div><div class="quickstart-grid"><div class="start-steps">{code_block('inspect-command',c['inspect_title'],c['inspect_code'],c)}<p>{e(c['inspect_note'])}</p><div class="run-prerequisite"><p>{e(c['run_note'])}</p>{link(doc(c,'models'),e(c['setup_link']),"text-link")}</div>{code_block('run-command',c['run_title'],c['run_code'],c)}</div><div class="result-step">{code_block('result-code',c['result_title'],c['result_code'],c,'python')}<p>{e(c['result_note'])}</p>{button(doc(c,'quickstart'),c['guide'],True)}<div class="next-links">{link(doc(c,'models'),e(c['model_guide']),'text-link')}{link(doc(c,'configuration'),e(c['config_guide']),'text-link')}</div></div></div><div class="release-notes"><p>{e(c['example_scope'])}</p><p>{e(c['license'])} {link(SOURCE,e(c['source_link']))}</p></div></div></section>
<section class="section" id="research" aria-labelledby="cases-title"><div class="container"><div class="section-heading"><div><p class="eyebrow">{e(c['cases_kicker'])}</p><h2 id="cases-title">{c['cases_title']}</h2></div><p>{e(c['cases_intro'])}</p></div><div class="research-grid">{cases}</div><p class="research-scope">{e(c['paper_scope'])}</p></div></section>
<section class="section paper-section" id="paper" aria-labelledby="paper-title"><div class="container paper-grid"><div><p class="eyebrow">{e(c['research_title'])}</p><h2 id="paper-title">{TITLE}</h2><p class="authors">{AUTHORS}</p><p class="author-note">{'Chenxi Liu and Yongqiang Chen contributed equally. Corresponding author: Bo Han.' if locale == 'en' else 'Chenxi Liu 与 Yongqiang Chen 共同第一作者。通讯作者：Bo Han。'}</p><p>Journal of Machine Learning Research<br>27(229):1–95, 2026</p><p class="research-note">{e(c['research_note'])}</p><div class="button-row">{button(PDF,c['read_paper'],True)}</div><div class="paper-links">{link(PAPER,e(c['publisher']))}{link('https://arxiv.org/abs/2402.03941','arXiv')}{link('neurips-24/',e(c['conference']))}</div></div><div><details class="citation" open><summary>{e(c['citation'])}</summary><div class="citation-actions"><a href="https://www.jmlr.org/papers/v27/25-2137.bib">.bib <span aria-hidden="true">↗</span></a><button type="button" class="js-only" data-copy="bibtex">{e(c['copy'])}</button></div><pre id="bibtex" tabindex="0"><code>{e(BIBTEX)}</code></pre></details></div></div></section>
</main><footer class="site-footer"><div class="container"><div class="footer-main"><a href="#top" class="footer-wordmark">COAT.</a><p>{e(c['footer']).replace(chr(10),'<br>')}</p></div><div class="footer-bottom"><p>{e(c['footer_note'])}</p><div>{link(doc(c),e(c['docs']))}{link(doc(c,'agents'),e(c['agent']))}{link('mailto:cscxliu@comp.hkbu.edu.hk',e(c['contact']))}</div></div></div></footer>
<dialog id="image-dialog" aria-label="{e(c['zoom'])}"><button type="button" data-close-dialog>{e(c['close'])} ×</button><div data-dialog-image></div></dialog><div class="visually-hidden" id="page-status" role="status" aria-live="polite"></div>
<script type="application/json" id="page-data">{manifest_json}</script>
</body></html>
'''


def write_generated(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_docs():
    """Publish Markdown from COAT-Learn without a second edited copy."""
    source_prefix = SOURCE + "/"
    for source in sorted((PROJECT / "docs").rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(PROJECT / "docs")
        destination = ROOT / "docs" / relative
        if source.suffix == ".md":
            text = source.read_text(encoding="utf-8")
            def rewrite(match):
                target = match.group(1)
                if re.match(r"https?://|mailto:|#|/", target):
                    return match.group(0)
                name, sep, fragment = target.partition("#")
                resolved = (source.parent / name).resolve()
                if not resolved.is_relative_to(PROJECT / "docs"):
                    path = resolved.relative_to(PROJECT)
                    return "](<" + source_prefix + path.as_posix() + (sep + fragment if sep else "") + ">)"
                return match.group(0)
            text = re.sub(r"\]\(<([^>]+)>\)", rewrite, text)
            write_generated(destination, "<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->\n\n" + text)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())


def build_companions():
    """Keep discovery metadata factual; delegate detailed procedures to the public skill."""
    try:
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        revision = None
    paths = [PROJECT / name for name in ("README.md", "README.zh-cn.md", "CITATION.cff", "LICENSE", "NOTICE", "data/README.md", "data/LICENSE")]
    paths += sorted((PROJECT / "docs").rglob("*.md")) + sorted((PROJECT / "skills/coatlearn").rglob("*.md"))
    digest = hashlib.sha256()
    for p in paths:
        digest.update(p.relative_to(PROJECT).as_posix().encode())
        digest.update(p.read_bytes())
    payload = {
        "name": "coatlearn", "description": "Discover and measure factors in unstructured data; ready-to-use discovery interfaces accept text columns.",
        "source_revision": revision, "documentation_sha256": digest.hexdigest(),
        "publication": {"title": TITLE, "journal": "Journal of Machine Learning Research", "year": 2026, "volume": 27, "issue": 229, "pages": "1--95", "url": PAPER, "bibtex_url": "https://www.jmlr.org/papers/v27/25-2137.bib"},
        "interfaces": {
            "annotation": "coatlearn.annotation.annotate(texts, definitions, *, model, concurrency=16, batch_size=8)",
            "mb": "coatlearn.run_mb(data, target, *, text_col='X', main_model, annotation_model, config=None)",
            "pag": "coatlearn.run_pag(data, known_variables, *, text_col='X', main_model, annotation_model, config=None)",
            "adj": "coatlearn.run_adj(data, treatment, outcome, *, text_col='X', main_model, annotation_model, config=None)",
        },
        "result_fields": ["method", "status", "factors", "graph", "adjustment_sets", "estimates", "diagnostics", "provenance"],
        "models": {"chat": "OpenAI-compatible hosted or separately served endpoints, including vLLM", "decision": "Hosted Jev or local Kev through native POST /v1/systemone HTTP, without TypeSafe SDK"},
        "measurement": {"score": "Probability-weighted declared original values", "choice": "Selected option's declared numeric code", "mention": "General-format mention probability below 0.5 records a missing measurement", "confidence": "Separate metadata, not factor value"},
        "adjustment": "Generalized adjustment on the supplied graph; effect estimation uses per-set complete-case IPW. Explicit researcher exemptions or cycle-deletion hypotheses must accompany interpretation.",
        "release": {"distribution": "Source checkout; no PyPI release asserted", "licensing": {"software": "Apache-2.0", "example_csv_files": "CC-BY-4.0"}},
        "links": {"documentation": "../../docs/", "agent_guide": "agent.md", "public_skill": "skill/SKILL.md", "source": SOURCE},
        "site": {"model_calls": False, "data_upload": False, "credential_collection": False},
    }
    write_generated(ROOT / ASSETS / "api.json", json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    for p in (PROJECT / "skills/coatlearn").rglob("*"):
        if p.is_file():
            dest = ROOT / ASSETS / "skill" / p.relative_to(PROJECT / "skills/coatlearn")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(p.read_bytes())
    write_generated(ROOT / ASSETS / "agent.md", """# Use coatlearn with an agent

For analysis requests, load the public [coatlearn skill](skill/SKILL.md) and keep its references directory alongside it. The skill is copied from the package source when this site is built.

Use the [current documentation](../../docs/) to select annotation, MB, PAG or ADJ, configure models and interpret results. Read [api.json](api.json) for a compact interface inventory, not an execution service.

Before model execution, agree on the data columns, mappings, model endpoints, assumptions and output directory. Explain where text will be sent and obtain permission for that plan. Local CLI inspection without `--run` does not call models. Keep keys in named environment variables or an explicitly selected private dotenv file.

Report factor values separately from confidence and missingness. Interpret graphs and adjustment sets relative to their assumptions. A completed run does not establish causal correctness; no estimate is not a zero effect. Use per-set records for effect estimates and identify researcher-supplied priors, exemptions or graph-processing hypotheses.

The website is static. It neither receives datasets nor runs models. Software is licensed under Apache-2.0; the two example CSV files use CC BY 4.0. See the source repository for attribution and license terms.
""")


def redirect(target, locale="en"):
    canonical = "https://causalcoat.github.io/" + ("" if target == "index.html" else target)
    label = "Open the current COAT project" if locale == "en" else "打开当前 COAT 项目页"
    return f'''<!doctype html>
<html lang="{'en' if locale == 'en' else 'zh-CN'}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>COAT · Moved</title><link rel="canonical" href="{canonical}">
<meta http-equiv="refresh" content="0;url={target}">
<script>location.replace({json.dumps(target)} + location.search + location.hash);</script>
</head><body><p><a href="{target}">{label}</a></p></body></html>
'''


def main():
    global PROJECT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-source", type=Path, default=PROJECT,
                        help="COAT-Learn source checkout (default: sibling directory)")
    args = parser.parse_args()
    PROJECT = args.project_source.resolve()
    for name in ("pyproject.toml", "coatlearn/__init__.py", "docs/README.md", "skills/coatlearn/SKILL.md", "LICENSE", "data/LICENSE"):
        if not (PROJECT / name).is_file():
            parser.error("Missing COAT-Learn source file: " + name)
    for locale, filename in PAGES.items():
        write_generated(ROOT / filename, render(locale))
    for locale, suffix in (("en", ""), ("zh", "-zh")):
        write_generated(ROOT / ("discovering-and-reasoning" + suffix + ".html"), redirect(PAGES[locale], locale))
    build_docs()
    build_companions()
    print("Built bilingual homepage, legacy redirects, documentation and interface companions.")


if __name__ == "__main__":
    main()
