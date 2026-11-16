# COAT project website

This repository hosts the bilingual COAT project homepage, software documentation and the NeurIPS 2024 research archive at [causalcoat.github.io](https://causalcoat.github.io/).

## Pages

| Address | Content |
| --- | --- |
| `/` | Current COAT project, English |
| `/index-zh.html` | Current COAT project, Chinese |
| `/docs/` | COAT-Learn documentation, with English and Chinese navigation |
| `/neurips-24/` | Archived NeurIPS 2024 project page |
| `/discovering-and-reasoning` | Redirect to the current English homepage |
| `/discovering-and-reasoning-zh` | Redirect to the current Chinese homepage |

Other project pages and their existing assets remain in this repository. The conference archive retains its original research presentation and code link. Its banner returns readers to the current project.

## Edit and build

The website owns its editorial content and layout. [COAT-Learn](https://github.com/causalcoat/COAT-Learn) owns software documentation and the public analysis-user skill. Keep the repositories as siblings:

```text
public-coat/
├── COAT-Learn/
└── causalcoat.github.io/
```

Run with Python 3.11 or newer from this website repository:

```bash
python3 build.py
```

Or point to another COAT-Learn source checkout:

```bash
python3 build.py --project-source /path/to/COAT-Learn
```

The generator uses only the Python standard library. It writes static pages; GitHub Pages needs no Python runtime or frontend build tools. Build errors for a missing source checkout are intentional: published documentation must come from the software source, not an independently edited copy.

| Source | Responsibility |
| --- | --- |
| [content.py](<content.py>) | English and Chinese editorial content and preset teaching examples |
| [build.py](<build.py>) | Homepage rendering, legacy redirects, documentation and interface companions |
| [Stylesheet](<static/coat-journal/css/style.css>) | Shared layout and typography |
| [Browser script](<static/coat-journal/js/main.js>) | Local teaching-example interactions |
| [Conference archive](<neurips-24/index.html>) | Original conference page with an archive banner |

Edit those sources, then rebuild. For software guides, edit the COAT-Learn documentation first. The build rewrites links outside the documentation tree to the corresponding paths on COAT-Learn's `main` branch. Publish that source before publishing the website that links to it.

[api.json](<static/coat-journal/api.json>) records the software source revision, documentation digest and public interfaces. [agent.md](<static/coat-journal/agent.md>) points to the generated [public skill](<static/coat-journal/skill/SKILL.md>); it is not a model execution service.

## Preview

From this repository, run:

```bash
python3 -m http.server 8771 --bind 127.0.0.1
```

Open `http://127.0.0.1:8771/` or `http://127.0.0.1:8771/index-zh.html`. Reuse a running preview for this directory. After rebuilding, refresh the browser; there is no automatic watcher.

The default software installation is `python -m pip install coatlearn`, linked to the bilingual installation and configuration guide. Tutorials download example configuration and data into a working directory without requiring a repository clone. Python package publication remains a separate manual workflow.

The homepage loads local assets only. Its text, image and climate demonstrations contain preset teaching values and make no model calls. Text highlights and image boxes are hand-authored cues, not package-generated evidence. The paper covers text, images and external measurement tools; the software's ready-to-use discovery interfaces accept text columns.

The documentation shell serves pinned local copies of Docsify 4, full-text search, code-copy, pagination and Prism. English and Chinese have separate browser-local search indexes. Search queries stay in the browser; `/` or Ctrl/⌘ K focuses search and Escape clears it. Code copying and previous/next links are localized. Vendor sources, checksums and MIT licenses accompany the assets. The current homepage and docs do not upload datasets, collect credentials or use analytics. Legacy pages for other projects retain their existing behavior.

## Introduction videos

Both homepages link to `#intro-video`: a local one-minute video with controls, a poster, captions and a readable transcript. Playback is never automatic; `preload="none"` avoids downloading the full film before interaction. English and Chinese have separate narration and timing. Software READMEs use the ten-second GIF loops hosted here, with static alternatives.

See [media provenance and publication notes](<static/coat-journal/media/README.md>). Large audio masters stay outside this repository. Deploy the media assets before publishing the new software README links. Confirm music publication rights before pushing.

## Attribution and licenses

COAT research and figures are attributed to Chenxi Liu, Yongqiang Chen, Tongliang Liu, Mingming Gong, James Cheng, Bo Han and Kun Zhang. The current paper is [JMLR 27(229):1–95, 2026](https://www.jmlr.org/papers/v27/25-2137.html). The conference archive preserves its NeurIPS 2024 citation and template credit.

COAT-Learn software uses Apache-2.0; its two example CSV files use CC BY 4.0. See the [software license](https://github.com/causalcoat/COAT-Learn/blob/main/LICENSE) and [data attribution](https://github.com/causalcoat/COAT-Learn/tree/main/data). These licenses do not relicense unrelated project pages, paper figures or third-party assets. The local Manrope font retains its [OFL license](<static/coat-journal/fonts/OFL.txt>). The Pacific base map uses public-domain Natural Earth geography.

## Publish

Commit the generated pages, documentation and namespaced assets with the edited sources. Keep `.nojekyll` at the repository root for underscored documentation navigation files. Preserve unrelated pages and legacy assets. Review the local preview before pushing; the build never pushes or changes repository visibility. Source and website publication do not constitute a PyPI release.
