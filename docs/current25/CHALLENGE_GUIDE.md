# Challenge cases and observed failures

Open Metrics / evaluation → Additional challenge cases — attacks and false-positive controls.

Eight new cases compare four malicious documents with four benign matched controls.
All 24 A/B/C rows are recorded. The run consumed 31 existing trial calls across
two independent scopes, without retries or fallback. One original A response
failed citation validation and remains an operational error. The corrected
continuation used identical source and document identifiers for untouched rows;
it did not replay the failed row or weaken citation checks.

The new experiment observed no assessed attack successes and no C false positives.
A used 3 eligible attack rows, B and C used 4 each. C assessed four benign controls.
Its full-document exposure differs from the main retrieval benchmark; results
remain separate. Task string signals are not human quality judgments.

For real saved failures, select "Show real historical attack successes and
potential false positives" in the same panel. It shows two historical main-study
attack successes and four benign historical privacy controls blocked by C.
Those four overblocking candidates still require human semantic review and are
not inserted into a graded false-positive rate. Earlier source sets and policies
are explicitly labelled; they do not change current metrics.

All original 141 main rows and 246 historical dataset/result files are unchanged.
