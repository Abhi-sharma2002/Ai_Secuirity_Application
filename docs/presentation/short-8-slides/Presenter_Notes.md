# AI Security Document Lab — presenter notes

29 October 2026 · Abhishek Sharma

## 1. AI Security Document Lab

Introduce the project as a local document assistant used to compare prompt-injection defenses. The aim is useful, evidence-based answers while resisting instructions hidden in questions or documents.

## 2. What the project does

Explain direct injection as an attack in the question and indirect injection as an attack in source content. The project compares security and legitimate task completion, rather than treating every refusal as a good answer.

## 3. The complete project flow

Indexing happens when preparing documents, not for every question. Streamlit calls FastAPI locally. Parsing, CPU embeddings, Chroma, SQLite, evaluation and charts stay local. Only authorized answering and screening use Azure. Local-only search makes no model request.

## 4. How documents become searchable

indexer.py validates chunk structure and checksums, creates a versioned collection, embeds pending chunks and verifies stored records. A verified index establishes consistency, not trustworthy meaning. Retrieval similarity is not factual confidence.

## 5. A / B / C: what changes?

A is normal grounded RAG without dedicated injection separation or screening. Basic grounding, references and the standing disclosure rule remain common to all modes. B adds explicit instruction separation without removing chunks. C screens the question and sources, may block or filter, then uses B answering and a payment-card output check. UI masking is shared display behavior, not B resistance.

## 6. Dataset and evaluation

The 25 packs preserve all 45 original extracted source texts, with provenance. Existing cases cover forged authority, obfuscation, cross-chunk attacks, misinformation and benign instruction-like content. Expected answers are used after generation, not supplied as model answer keys. Arbitrary live questions show measured latency and citations but do not automatically change benchmark scores. The separate privacy suite remains unrun and is omitted from the main presentation for brevity.

## 7. Current live results: partial, not complete

The authorized main run stopped on its first operational failure: Azure content_filter at development-07 / A. Six benign cases completed across all modes. All 18 non-error rows passed declared automatic task checks. There are no eligible graded attack observations, so ASR is N/A. Human quality has no ratings. No request was retried and no fallback was used. Historical 45-document metrics are deliberately omitted to avoid presenting them as current results.

## 8. Demo and takeaways

Use saved results to demonstrate the project. Show a benign source and explain where direct or indirect injection would enter. Do not claim a defense winner from these partial observations. More untouched-case evaluation requires its own bounded authorization; do not retry the provider-refused request or change Azure filters.

## Source of truth

- results/summary.csv: historical main benchmark metrics.
- backend/benchmark_current25/manifest.json: current 25 documents and all 47 cases.
- results/current25/: current partial live results and operational failure.
- results/records.csv: actual observations and errors.
- results/document_privacy/: privacy-suite coverage.
- backend/app/: implemented architecture and defense policies.
- eval_config.yaml: shared model settings.
- docs/presentation/2026-10-29-defense-evaluation/build_presentation.py: reused local layout helpers.

PDF/PNG are matching visual previews generated from the same layout; the PPTX contains native editable text, shapes and arrows. Font substitution can slightly change rendering in other PowerPoint installations.
