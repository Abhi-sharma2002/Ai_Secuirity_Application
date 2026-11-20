# PDF requirements and the current project

| PDF requirement | Current implementation |
|---|---|
| At least 20 documents and 30 cases | 25 documents and all 47 cases: 21 benign, 26 adversarial |
| Standard RAG baseline | A: grounded answers and references, no dedicated injection separation or screening |
| Instruction separation | B: trusted application rules distinguish untrusted retrieved content |
| Additional defense | C: input screening, evidence filtering, B answering and payment-card output checks |
| Same cases/model/evaluation criteria | Current manifest, shared initial retrieval and eval_config.yaml |
| Repeatable execution and five metrics | current25_eval.py; results/current25; task and attack grades remain separate |
| Findings and demo | current25/README.md, current25/LIVE_OUTCOME.json and DEMO.md |

The PDF requires predefined repeatable cases, not automatic benchmark updates from arbitrary live questions. Unsupported correctness or security judgments remain N/A.

Current main coverage is 19/141 rows after the first Azure refusal; the previous 141/141 comparison belongs to the historical 45-document experiment. The current privacy suite has 125 cases and 375 planned rows, all unrun.
