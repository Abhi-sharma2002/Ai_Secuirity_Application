# Current dataset: 25 documents and 47 cases

Current source of truth: `backend/benchmark_current25/manifest.json` and `results/current25/`. The 42-document and 45-document datasets are historical; their measurements do not transfer to this study.

- 25 versioned Markdown source packs preserve all 45 original extracted source texts and their provenance.
- All 47 existing cases are retained: 21 benign and 26 adversarial.
- A/B/C produce 141 planned rows. The same initial retrieval and model settings are compared.
- Existing coverage includes direct and indirect injection, forged authority, obfuscation, cross-chunk attacks, misinformation, mixed content and benign instruction-like controls.
- Expected answers are evaluator inputs only, never model answer keys.

The independent current privacy suite has 25 documents, 125 cases and 375 planned rows. It remains unrun.

Validate locally with `backend/scripts/build_current25.py`; use `backend/scripts/current25_eval.py --plan` for the main workload. Historical fixtures and observations remain preserved.
