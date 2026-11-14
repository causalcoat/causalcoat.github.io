<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Local documentation dependencies

These pinned files are served locally so reading and searching documentation does not require a CDN. They are copied from upstream npm distributions. The Vue stylesheet has one documented modification: its Google Fonts import is removed so the browser uses system fonts without external font requests. The [manifest](<manifest.json>) records source URLs and original SHA-256 digests, plus the local digest for that modified stylesheet.

| Component | Version | License |
| --- | --- | --- |
| Docsify, Vue theme and full-text search | 4.13.1 | [MIT](<LICENSE-docsify>) |
| docsify-copy-code | 3.0.2 | [MIT](<LICENSE-docsify-copy-code>) |
| docsify-pagination | 2.10.1 | [MIT](<LICENSE-docsify-pagination>) |
| Prism language components | 1.30.0 | [MIT](<LICENSE-prismjs>) |

The search configuration uses the current sidebar as its page list and keeps English and Chinese indexes separate. It searches local documentation in the browser, including Chinese text and API identifiers. No search query is sent to a hosted search service.

When updating a dependency, replace its distribution files and license, update its manifest entries, and inspect both languages in the browser. Keep the Docsify core, theme and search plugin on the same version. The docs currently target Docsify 4; do not copy Docsify 5-only configuration options into this shell.
