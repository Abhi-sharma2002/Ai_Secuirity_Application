# AI Security Document Lab

The current predefined study has **25 documents and 47 cases** (21 benign, 26 adversarial), giving 141 planned A/B/C observations. The current manifest is `backend/benchmark_current25/manifest.json`.

A is standard grounded RAG. B adds instruction separation. C adds question/source screening, evidence filtering and a payment-card output check. Parsing, CPU embeddings, Chroma, SQLite, UI and reporting run locally. Authorized answering/screening uses the existing Azure gpt-5-mini trial deployment.

## Start the application

Microsoft organizational sign-in and application roles are required. Complete
[Entra setup](docs/AUTHENTICATION.md) and local configuration first. Assigned
users share uploaded documents; management, evaluations/reviews and live calls
are controlled by backend permissions. Use http://localhost:8501 for the configured
development sign-in callback.

From the configured main checkout:

```bash
.venv/bin/python run_app.py --check
.venv/bin/python run_app.py
```

Open http://127.0.0.1:8501. The default launcher is local-only. `--live-answers` enables interactive answering only under the existing valid allowance; it does not authorize a benchmark. Private settings stay local and capacity is never reset.

For single-user access on this computer without Microsoft sign-in, start instead with `.venv/bin/python run_app.py --local-access`. Both services bind to loopback. Anyone who can access the local browser session can use the workspace, so use Microsoft sign-in for shared access. The sidebar's Provider setup explains the existing Azure settings; entering a key does not enable or authorize live calls.

Ask / compare defaults to **Uploaded documents**, selecting the newest active file. The **Predefined documents (25)** library is an explicit separate choice. Local evidence search is available within Ask / compare. Uploaded documents are a separate user-managed library and do not change the frozen 25-document study.

## Current evaluation

All 141/141 main benchmark rows are recorded; no rows remain unrun. There are 125 non-error outcomes and 16 operational errors (15 Azure provider refusals and 1 interrupted outcome). Failed requests were not retried.

| Mode | Recorded | Benign task checks | Successful attacks / eligible attacks | Errors |
|---|---|---|---|---|
| A | 47/47 | 19/19 | 0/4 | 5 |
| B | 47/47 | 19/19 | 0/4 | 5 |
| C | 47/47 | 19/19 | 0/9 | 6 |

51 non-error answers still require semantic review; human quality remains unrated. Attack success and benign-task rates use only eligible automatically graded or actually reviewed outcomes. Errors, unrun cases and unresolved judgments are excluded.

The main results combine three explicitly identified executions; original raw files, stop flags and implementation snapshots are preserved.

The separate five-test privacy suite retains **25 documents, 125 cases and 375 planned A/B/C rows**. It remains unrun because the latest approvals covered the main benchmark only. Uploaded-document observations remain separate.

## Local validation and reports

```bash
.venv/bin/python backend/scripts/build_current25.py
.venv/bin/python backend/scripts/current25_eval.py --plan
.venv/bin/python backend/scripts/current25_eval.py --report
```

These commands make no provider calls. The existing index is preserved; fresh setup can use `--prepare-only` with cached CPU weights and offline environment flags. Completed and failed benchmark scopes remain closed or stopped; no retry, fallback, expiry, new capacity or cloud resource change is introduced.

[Current study guide](docs/current25/README.md) · [Dataset](docs/DATASET.md) · [Current status](docs/COMPLETION_STATUS.md) · [Demo](docs/DEMO.md) · [Eight-page PDF](docs/presentation/short-8-slides/AI_Security_Short_8_Slides.pdf)

Previous 42- and 45-document datasets and their actual observations remain preserved as history. They are not the active predefined library.


Metrics opens the saved 47-case / 141-row main benchmark with a table by default; Graphs remains optional. ASR is explicitly provisional while judgments remain pending. C false positives mean normal questions or genuine supporting evidence incorrectly flagged, filtered or blocked. The separate unrun five-test view links back to the completed main benchmark. The user selected no additional live calls for this correction.
