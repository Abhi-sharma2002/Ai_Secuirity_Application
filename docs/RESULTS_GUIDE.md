# Reading the current results

All 141/141 main benchmark rows are recorded; no rows remain unrun. There are 125 non-error outcomes and 16 operational errors (15 Azure provider refusals and 1 interrupted outcome). Failed requests were not retried.

| Mode | Recorded | Benign task checks | Successful attacks / eligible attacks | Errors |
|---|---|---|---|---|
| A | 47/47 | 19/19 | 0/4 | 5 |
| B | 47/47 | 19/19 | 0/4 | 5 |
| C | 47/47 | 19/19 | 0/9 | 6 |

51 non-error answers still require semantic review; human quality remains unrated. Attack success and benign-task rates use only eligible automatically graded or actually reviewed outcomes. Errors, unrun cases and unresolved judgments are excluded.

Coverage distinguishes non-error outcomes from operational errors. Metric figures label actual eligible sample counts beside percentages. Missing human quality stays unavailable. Read the collapsed coverage, review, source evidence and diagnostic sections for the complete record.

The source of truth is `results/current25/records.csv` with its computed `summary.csv`. `coverage.png` and `metrics.png` are bound to the current raw CSV by `visualization_binding.json`. Historical 45-document rates are not mixed into the current study.

Uploaded-document charts use saved responses whose evidence belongs to current active upload versions. They are observations, not a controlled attack evaluation. The separate current five-test study remains unrun.


Metrics opens the saved 47-case / 141-row main benchmark with a table by default; Graphs remains optional. ASR is explicitly provisional while judgments remain pending. C false positives mean normal questions or genuine supporting evidence incorrectly flagged, filtered or blocked. The separate unrun five-test view links back to the completed main benchmark. The user selected no additional live calls for this correction.


To show the earlier nonzero rate, select Metrics / evaluation → Historical v3 results — 45 documents (older prompts), or use http://127.0.0.1:8501/?view=metrics&study=historical . Saved ASR is A 2/18 (11.1%), B 0/19 and C 0/20. The current 25-document experiment remains separate; no scores are rewritten.


Denominator explanation (historical main): each mode received the same 26 attacks. A excludes 4 errors and 4 pending judgments (18 assessed); B excludes 4 errors and 3 pending (19); C excludes 5 errors and 1 pending (20). These count assessed responses, not different questions or provider calls.

The historical results page also shows a separate automatically measured C benign-control flag/block rate: 4/4 usable controls (100%), with 1 error and 14 unrun controls excluded. This small historical privacy-control subset is distinct from the main benchmark and human-reviewed FPR. No human judgments or saved grades were changed.
