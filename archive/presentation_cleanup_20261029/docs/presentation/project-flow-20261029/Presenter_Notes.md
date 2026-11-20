# AI Security Document Lab — presenter notes

29 October 2026 · Abhishek Sharma

## 1. AI Security Document Lab

Start with the user journey: a person selects a document, asks a question and receives a cited answer. Then explain where prompt injection enters and why the project compares three defense configurations. The following slides follow the actual application flow before discussing results.

## 2. 1. What problem does the project solve?

Explain RAG first: retrieve relevant passages and supply them to an answering model. Direct injection comes through a question; indirect injection comes through source text. The project measures whether added defenses preserve useful answers while resisting these instructions.

## 3. 2. The complete application journey

Read the top row left to right, then the bottom row. Indexing happens when documents are prepared; it is not repeated for every question. Evaluation is a separate controlled workflow, not automatic grading of every interactive question. Local-only search stops before provider generation.

## 4. 3. Upload → usable document text

Implementation: backend/app/ingestion/lifecycle.py and parsers.py, followed by rag/indexer.py. Parsing does not certify source text as trustworthy. A failed replacement preserves the currently active document version. Text PDFs are supported; do not imply scanned-image OCR is implemented.

## 5. 4. Inside indexer.py: building a trusted index

This slide explains the open IDE file. index_chunks validates inputs, calculates a dataset version and uses a versioned enterprise_documents collection. Existing records are checked before missing chunks are added in batches. Interrupted building collections can resume after verification; verified but incomplete collections fail. Index integrity checks protect consistency, not against malicious meaning inside valid text.

## 6. 5. Question → relevant source passages

Implementation: rag/retrieval.py and retriever.py. The uploaded-library implementation ranks by distance and ID, selects at most top_k=5 and bounds selected text to 12,000 bytes. The predefined library uses its own isolated index. Smaller cosine distance indicates similarity, not factual confidence. No answer keys are retrieved from evaluation labels.

## 7. 6. Where prompt injection enters

Use these as illustrative attack descriptions, not actual saved outputs. Retrieval can correctly find a relevant passage that also contains malicious instructions. The trust boundary is between application policy and untrusted question/source content. Format validation and similarity retrieval do not solve this semantic problem.

## 8. 7. A / B / C: the actual defense branches

All modes start with the same initial evidence in a controlled comparison. A already has grounding rules; it is not unrestricted. B adds privileged instruction separation without filtering chunks. C screens question and sources, may block or remove sources, then uses B answering and a payment-card output-pattern check. C reserves capacity for up to two calls; A/B reserve one.

## 9. 8. C mode: decisions before answering

These are conditional branches, not six unavoidable calls. screening.apply returns early for a flagged question or screening error. Unknown source IDs and contradictory metadata are errors, not decisions to repair silently. If unflagged evidence remains, B generates and C checks the answer for payment-card patterns. This output check is not a universal secret detector.

## 10. 9. Answer generation → displayed response

Authorization is checked around provider execution; C reserves before screening. Azure requests omit temperature identically for A/B/C. There are no automatic retries or fallback models. Schema checks validate structure; citation-ID checks establish membership in supplied evidence, not semantic support. UI masking does not modify saved raw evidence and is not scored as B model resistance.

## 11. 10. One example to explain the whole flow

This is a teaching example, not a new experiment and not a prediction of which answer a mode will produce. Walk through upload, chunk embedding, retrieval and each defense branch. Expected safe behavior is to answer the legitimate policy question without following the disclosure instruction. Recorded outcomes are shown separately later.

## 12. 11. How the controlled evaluation runs

The active main runner is backend/scripts/run_eval.py with evaluation/simple_runner.py. Expected answers and attack objectives are used after generation, never supplied as model answer keys. Operational errors and pending judgments are excluded from graded security denominators. Historical implementations and continuations retain their original provenance.

## 13. 12. What the five metrics tell us

Metric definitions come from the saved reporting implementation. Attack success uses eligible graded adversarial rows; benign success uses eligible benign rows. C false positives measure benign inputs flagged, filtered or blocked. Recorded route timing includes errors and excludes shared initial retrieval. A/B false-positive screening metrics are not applicable.

## 14. 13. What the saved main benchmark shows

Read from results/summary.csv at build time. Historical main results use recorded earlier policies, not proof that the newer business-summary-v7 policy has been evaluated. Graded denominators differ because operational errors and unresolved judgments are excluded. The attack-task figures come from actual eligible saved rows. Four human quality ratings are too few for a strong quality conclusion.

## 15. 14. Separate privacy suite: current status

This suite uses controlled full-document evidence and is separate from the retrieval benchmark. Original documents may already be adversarial, so control means no added attack. Latest business-summary-v7 continuation stopped on its first Azure content-filter refusal. Do not resume it or reinterpret a provider refusal as a defense win. Historical rows retain original policy identities.

## 16. 15. How to demonstrate the project

Use saved results for a reproducible presentation. A fresh live demonstration requires the existing current authorization and available capacity; making this deck does not execute it. Tell the story in application order rather than starting with metric tables. End by showing that useful answers and secure behavior must be assessed together.

## 17. 16. Conclusion and next work

Close with the implemented system and the limits of its observations. B showed a promising balance in the historical graded subset, while C lost legitimate tasks through blocking. Neither proves general security. The current policy is a later treatment and needs its own evidence. Ask for questions about the flow, defense decisions or recorded findings.

## Source of truth

- results/summary.csv: saved main benchmark metrics.
- results/records.csv: actual observations and errors.
- results/document_privacy/: privacy-suite coverage.
- backend/app/: implemented architecture and defense policies.
- eval_config.yaml: shared model settings.
- docs/presentation/2026-10-29-defense-evaluation/build_presentation.py: reused local layout helpers.

PDF/PNG are matching visual previews generated from the same layout; the PPTX contains native editable text, shapes and arrows. Font substitution can slightly change rendering in other PowerPoint installations.
