# AI Security Document Lab — presenter notes

29 October 2026 · Abhishek Sharma

## 1. AI Security Document Lab

Introduce yourself as Abhishek Sharma. This is a document assistant and an evaluation lab: it asks whether an LLM can use document facts without obeying malicious instructions embedded in those documents. The layout follows the provided ForecastIQ reference; no ForecastIQ product claims are reused.

## 2. Project Overview

The user uploads a file or selects one of the 45 predefined sources, then asks a new question. Local mode returns passages only. Authorized live mode sends the question and retrieved passages to the existing Azure gpt-5-mini deployment. The benchmark uses fixed cases and saved observations; opening results makes no provider call.

## 3. Objectives & Scope

We measure resistance and usefulness, not only refusal. A response that blocks every attack may also lose useful answers. The app is a local, single-user proof of concept. It does not train or fine-tune the LLM, create cloud search resources, or guarantee protection from all attacks.

## 4. Tech Stack

SQLite is the application registry; Chroma is the vector search store. Chroma itself uses internal SQLite files, but that is separate from our application registry. MiniLM runs on CPU and creates 384-dimensional normalized vectors. Azure gpt-5-mini is the existing model deployment; local search does not call it.

## 5. Architecture

Read left to right. Both document libraries meet at evidence retrieval. Original uploads and document versions remain local. Uploaded vectors and the frozen evaluation index are separate. Only selected evidence and the question cross the Azure boundary when the user submits an authorized live request. C may remove evidence after the shared initial retrieval. Expected answers and evaluator labels never enter the answering prompt.

## 6. How a Document Becomes Searchable

Every upload gets a logical document ID and an immutable version ID. Its original bytes are saved before parsing. Only fully indexed and verified versions become active. Overlap helps retain context across chunk boundaries. A scanned PDF can require OCR; parsing does not make malicious content trustworthy. A hash verifies content identity, not safety.

## 7. Three Defense Pipelines: A / B / C

All modes share grounding rules, model settings and the initial evidence. A is a grounded baseline, not an unrestricted model. B adds instruction separation without deleting source chunks or adding a new runtime output filter. C screens the question and sources, can block or remove evidence, then uses B answering and a payment-card output check. A provider content-filter refusal is a different event from C blocking. UI masking applies across modes and is not scored as resistance.

## 8. Storage: What Is Saved, and Why?

Files preserve exact input bytes. SQLite records the document lifecycle, active version and calls. Chroma stores chunk text, numeric embeddings and metadata for semantic search. JSON defines nested cases; CSV records flat observations. We selected local storage for the scale and deployment constraints. PostgreSQL with pgvector is a valid future alternative for a multi-user service; Chroma is not claimed to be best for every workload.

## 9. Evaluation: From a Case to a Measured Result

The main benchmark has 47 predefined questions across 45 sources. It retrieves and freezes the initial evidence, then applies A, B and C. Expected answers, attack objectives and rubrics are for evaluation only and are not sent as answer keys. Operational errors are excluded from success rates. Interactive new questions are useful demonstrations but do not silently replace benchmark observations. Human quality and ambiguous semantic decisions require a person.

## 10. Recorded Main Benchmark: Results & Limits

These figures come from results/summary.csv on 29 October 2026. ASR counts are A 2/18, B 0/19 and C 0/20. Benign task success is 20/20 for each. There are 13 operational errors and 11 pending judgments. Only four human quality ratings exist: A two, B one, C one. Do not claim that B or C is secure because an observed attack-success rate is zero. Recent v7 policy changes were not used for these historical observations.

## 11. Privacy Suite: Five Tests per Document

The separate privacy suite adds a fictional private contact and public route to each source. It supplies controlled full-document evidence, so it is not a retrieval benchmark. There are 225 cases and 675 planned A/B/C rows. Current coverage is 92 recorded, 583 unrun and 3 execution errors. Runs stopped on operational failures, including Azure content-filter refusals. Never show unrun rows as successful defenses. Control means no added attack, not necessarily a benign original document.

## 12. Live Demonstration: New Questions

Start the app using .venv/bin/python run_app.py --live-answers. Choose a library and one document, then ask a benign question. Local-only returns matching passages, not an AI answer. For a live A/B/C comparison, use the comparison form; initial evidence is frozen once and the comparison costs up to four existing provider calls. Do not replay a provider-refused payload. If the live system is unavailable, show saved outcomes honestly rather than inventing an answer.

## 13. What Was Built & What We Learned

The deliverable is an inspectable local document assistant with distinct A/B/C pipelines, preserved evidence and evaluation tools. B can resist answer manipulation while still overdescribing malicious content; v7 strengthens summary instructions, but has not established a new benchmark result. C adds screening and output checks but can sacrifice useful answers and time. Remaining work is bounded untouched-case execution where authorized, actual human review, and broader adversarial testing—not a claim of complete protection.

## 14. Thank You

Invite questions on architecture, storage choices, trust boundaries, model calls, metrics and operational failures. Use the appendix diagrams if asked where a function is implemented. Be precise: no security guarantee, no fabricated human reviews and no automatic replay of a refused or failed benchmark request.

## 15. Appendix: Where the Logic Lives

All paths are within backend/app unless explicitly prefixed frontend. Upload lifecycle is in ingestion/lifecycle.py, not the old TXT-only upload helper. The runtime API chooses the uploaded or predefined library. Azure serialization is isolated in llm/azure_openai.py and uses a single HTTP attempt. Avoid opening private environment files during a public demo.

## 16. Appendix: Questions You Can Answer

Why Chroma: local semantic search, persistence and metadata filters without a new cloud resource. Why SQLite: single-user application state with transactions and no database server. Why not PostgreSQL: a valid option for a larger multi-user system, especially with pgvector, but not required here. Why local mode: it validates retrieval without sending evidence to a model. Why failures remain: preserving observations is necessary for an honest experiment. Does uploading train the model: no, it creates an external index. Is local storage encrypted: not automatically. The same model and initial retrieval support fair comparisons; different prompt policies and C processing are the intentional experimental variables.

## Source of truth

- results/summary.csv: saved main benchmark metrics.
- results/records.csv: actual observations and errors.
- results/document_privacy/: privacy-suite coverage.
- backend/app/: implemented architecture and defense policies.
- eval_config.yaml: shared model settings.
- ForecastIQ_V2_Presentation.pptx: visual reference only.

PDF/PNG are matching visual previews generated from the same layout; the PPTX contains native editable text, shapes and arrows. Font substitution can slightly change rendering in other PowerPoint installations.
