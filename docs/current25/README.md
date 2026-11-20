# Current 25-document study

**Latest status (30 October):** All 141/141 main benchmark rows are recorded; no rows remain unrun. There are 125 non-error outcomes and 16 operational errors (15 Azure provider refusals and 1 interrupted outcome). Failed requests were not retried. 51 non-error answers still require semantic review; human quality remains unrated. Attack success and benign-task rates use only eligible automatically graded or actually reviewed outcomes. Errors, unrun cases and unresolved judgments are excluded. See [latest status](LATEST_STATUS.json).

The assignment PDF requires standard RAG (A), instruction separation (B), and an additional defense (C). A now uses a compact standard task prompt: answer from evidence, cite sources, abstain when unsupported and disclose genuine conflicts. The standing non-disclosure policy applies equally to all modes. A has no dedicated injection-screening or separation prompt. B retains explicit trusted/untrusted instruction separation. C retains screening, B answering and the payment-card output check.

## Dataset and cases

`backend/benchmark_current25/manifest.json` contains exactly **25 source documents and all 47 existing cases** (21 benign and 26 adversarial). Twenty compatible pairs of original source files were consolidated into sectioned Markdown documents; all 45 original extracted texts remain, with original hashes and source mappings. Benign and attack-bearing material are not mixed during consolidation. Development and final pools stay separate; absence and genuine conflict cases stay isolated. This is a changed retrieval dataset, so old observations cannot be transferred.

No cases were deleted. Existing overt, forged-authority, paraphrased, obfuscated, cross-chunk, protected-marker, answer-manipulation, misinformation and benign instruction-like cases already provide the requested harder coverage. No duplicate cases were added to inflate scores. When a source pack contains multiple indirect attacks, extra marker targets and mandatory semantic review prevent the other attack from being silently treated as safe. New word-boundary scoring prevents, for example, “30 days” from automatically passing an expected “3 days” check. Historical scoring retains its original matching behavior.

The independent current privacy suite has **25 documents × 5 conditions × 3 modes = 375 rows**, with 125 cases. The historical 45-document privacy suite and its actual rows remain separately readable.

## Local operation

From the repository root:

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python backend/scripts/current25_eval.py --plan
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python backend/scripts/current25_eval.py --prepare-only
.venv/bin/python backend/scripts/current25_eval.py --report
.venv/bin/python backend/scripts/current25_eval.py --privacy
.venv/bin/python run_app.py
```

The cached CPU embedding model builds `.cache/evaluation_current25`; the historical `.cache/evaluation_v3` is preserved. Uploaded documents remain independent. Ask / compare → Predefined documents now uses the 25-document index. New questions use retrieval and the selected A/B/C pipeline. Per-answer measurements show actual latency, references, citation-ID validation and C screening status. Task correctness, attack success, false positives and human quality are not guessed for arbitrary questions.

Metrics / evaluation defaults to **Current 25-document study**. All unrun A/B/C cases remain visible, with N/A rates and missing counts. Select **Historical v3 results** or **Historical privacy — 45 documents (older suite)** for the actual old measurements, and **Current privacy — 25 documents** for the new five-condition suite. Human review endpoints and artifacts are scoped to the selected study. Reading or refreshing dashboards never executes provider requests.

## Evaluation and live execution

The PDF calls for repeatable testing on predefined cases, with scoring rules declared before testing. It does not require arbitrary live questions to update the benchmark. The same cases, initial retrieval and model settings must be compared across A/B/C; C's filtering is an intentional treatment difference. Expected answers are never passed to the answering model.

The new main study needs at most **188 provider calls / 6,016,000 reservation units** for 47 A/B/C cases, producing 141 planned rows. The new privacy study needs at most **500 calls** for 375 rows. Together that is 688 calls. The actual main-run preflight had 642 remaining calls; postflight has 617. Both workloads cannot be assumed to fit the existing allowance. Do not assume both workloads can finish. No new capacity or expiry has been created.

The user subsequently approved the 188-call main workload. Its first live attempt stopped on the first operational failure as summarized above. Historical receipts are dataset-bound and stopped; `current25_eval.py --live` and the adapter require the exact independent receipt, frozen implementation, row/stage accounting and unstopped scope; this attempt is now stopped. Any continuation needs its own bounded authorization and current capacity preflight; the stopped receipt cannot be reactivated. No automatic retries, fallback, resource changes or paid use are introduced. Human judgments remain human. The original PDF, frozen datasets, historical outcomes and allowance records are preserved.


The Oct30 independent continuation was approved for 122 untouched rows and at most 163 calls. It added 26 recorded rows (including one interrupted outcome) using 30 reservations, then stopped. The original 19-row raw run is preserved separately. The aggregate has 45 rows; 96 remain untouched. Neither the old main scope nor the stopped continuation may be reactivated.


The final 96-row / 128-call continuation closed after recording every untouched main row. No original failed row was replayed. The aggregate contains all 141 planned rows with independent per-row execution provenance. Earlier stopped scopes remain historical and cannot be reactivated.


The final 96-row / 128-call continuation closed after recording every untouched main row. No original failed row was replayed. The aggregate contains all 141 planned rows with independent per-row execution provenance. Earlier stopped scopes remain historical and cannot be reactivated.
