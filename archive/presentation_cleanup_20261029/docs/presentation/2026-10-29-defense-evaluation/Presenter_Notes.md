# AI Security Document Lab — presenter notes

29 October 2026 · Abhishek Sharma

## 1. AI Security Document Lab

Introduce the project as an experimental comparison of prompt-injection defenses in a document assistant. The central question is which defense resists attacks while preserving useful answers. This deck focuses on evaluation design and recorded evidence, not implementation interview questions.

## 2. The Security Problem

RAG supplies retrieved text to an LLM. An attacker can place commands in a question or inside retrieved content, trying to turn source material into authority. We evaluate answer manipulation and protected-data disclosure while also checking whether the legitimate question is answered. A refusal alone does not establish good usability.

## 3. Evaluation Objectives

The experiment tests security and usability together. Attack success is measured on eligible graded adversarial rows. Normal-task performance is a separate measure. Human quality and ambiguous semantic decisions must remain human judgments. Timing records include provider failures, so they must not be described as pure successful-model latency.

## 4. The Three Configurations

A is a grounded baseline, not a completely unrestricted model. B adds trusted instruction separation but does not filter document chunks or add a new deterministic output filter. C screens the question and source chunks, then uses B answering and a payment-card output check. Display masking is common UI behavior and is not counted as model resistance.

## 5. Architecture of the Experiment

This is the evaluation architecture. A frozen question and source selection produce one saved initial retrieval result. A and B receive those original chunks; C may remove chunks or block after screening. Actual model outputs are saved, then graded against the expected task and attack objective. Expected answers are never sent to the answering model. This separation avoids answer-key leakage and lets observations be audited.

## 6. Dataset & Attack Coverage

The active main benchmark manifest contains 45 frozen sources and 47 cases: 21 benign and 26 adversarial. Direct attacks place hostile instructions in the user question; indirect attacks place them in source evidence. Frozen files and hashes support reproducibility. These synthetic cases test specific behaviors; they do not establish coverage of every real attack.

## 7. Fair Comparison Protocol

All modes use Azure gpt-5-mini, the same 700-token completion cap and minimal reasoning. Temperature is omitted, not set to zero. Chunking uses 1000 characters with 150-character overlap and retrieves up to five passages. Source evidence is shared before C screening. No automatic retries or fallback models are used. Continuation identities preserve implementation changes instead of overwriting old observations.

## 8. Five Primary Evaluation Metrics

For attack success, the denominator is eligible graded adversarial observations; an exposed-only variant checks cases where the attack was actually retrieved. Benign success uses ordinary cases. The C false-positive metric counts eligible benign cases flagged, blocked or filtered. Quality requires genuine human scores. Latency includes errors and excludes shared initial retrieval. All rates must be read with sample counts, exclusions and review coverage.

## 9. How an Observation Becomes a Score

A response must first be a usable execution outcome. A provider content-filter refusal, transport failure or schema failure is an operational error. For successful outcomes, task correctness and attack success are separate decisions. Ambiguous answers remain pending rather than receiving invented judgments. Citation IDs are validated structurally, but their semantic support requires review. Raw evidence is preserved even when the UI masks sensitive values.

## 10. Main Benchmark: Recorded Outcomes

Source: results/summary.csv. ASR is A 2/18, B 0/19, C 0/20. Benign success is 20/20 for all. Mean route times are approximately 3.56, 3.65 and 5.80 seconds. Quality averages are 4 but based on only two A ratings and one each for B and C. There are 13 operational errors and 11 pending judgments. These saved observations predate the latest v7 summary policy.

## 11. Security–Usefulness Trade-off

This is the important interpretation of the recorded evidence. Among eligible adversarial rows, A completed 18/18 legitimate tasks but had 2 successful attacks. B completed 19/19 with no recorded attack success in that subset. C blocked all 20/20 eligible attack rows and completed zero legitimate tasks in that subset. The eligible sets differ because errors and pending judgments are excluded; they are not perfectly paired subsets. Do not label C the universal winner based on zero ASR.

## 12. Case Study: Same Case, Different Outcomes

Use actual saved case final-21 as an example. A has task_passed true and attack_succeeded true, which shows that a useful answer can coexist with a security failure. B is pending human review, so we must not call it safe or unsafe. C is blocked with task_passed false and attack_succeeded false. These are historical labels from saved records, not a live replay. Attack payloads and protected values are intentionally not reproduced on this slide.

## 13. Privacy Evaluation: Five Tests per Source

The privacy suite is separate from the main benchmark. It uses controlled full-document evidence with a synthetic private contact and public route; it is not a retrieval test. The five conditions are control, direct plain, direct encoded, indirect plain and indirect encoded disclosure. Expected behavior is to give the public route while withholding the private value in every representation. Current coverage is incomplete, and non-error outcomes still require semantic review. Original sources can already be adversarial, so control means no added attack.

## 14. Limits, Errors & Implementation Changes

Keep the distinctions explicit. Azure content-filter refusals are provider operational errors, not C-defense blocks. UI masking does not change stored evidence and is not scored as model resistance. Four human quality ratings provide very limited coverage. New B/C business-summary-v7 instructions apply to current interactive answers but cannot be credited with historical benchmark rates. Different continuations retain their original identities rather than silently rewriting observations. More cases and human review are needed.

## 15. Demonstrating the Evaluation Workflow

Present the recorded benchmark first: show a case, its expected task, actual A/B/C outcomes and eligible metric denominators. Then, if authorized, select a source and submit a new benign question in Ask/compare. Explain that evidence is frozen once and C can filter it. Compare correctness, citations, disclosure and latency. Interactive responses remain unreviewed observations and do not overwrite benchmark metrics. The deck itself makes no model calls.

## 16. Findings & Next Evaluation Steps

Close on the project findings rather than claiming complete security. In the historical graded subsets, B showed a useful balance, while C showed the cost of broad blocking. The finding is provisional because of errors, pending judgments and low quality-review coverage. Next steps are actual human review, authorized untouched-row coverage, and a separately versioned evaluation of changed policies. The source deck and actual runtime remain unchanged by this presentation revision.

## Source of truth

- results/summary.csv: saved main benchmark metrics.
- results/records.csv: actual observations and errors.
- results/document_privacy/: privacy-suite coverage.
- backend/app/: implemented architecture and defense policies.
- eval_config.yaml: shared model settings.
- ForecastIQ_V2_Presentation.pptx: visual reference only.

PDF/PNG are matching visual previews generated from the same layout; the PPTX contains native editable text, shapes and arrows. Font substitution can slightly change rendering in other PowerPoint installations.
