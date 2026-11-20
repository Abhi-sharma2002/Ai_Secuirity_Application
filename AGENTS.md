# Standing project scope

## Azure model switch, 20 November 2026

The user approved switching interactive answering to their existing Azure
gpt-5.4-mini deployment on trial credits, retaining the current interactive
allowance identity, ceiling, consumed reservations and stop flags. No new
capacity, paid use, benchmark execution, retries, fallback or resources are
authorized. Use the model-specific shared `none` reasoning setting for A/B/C;
retain historical gpt-5-mini settings and evaluation provenance.

## Current Azure trial selection, 26 October 2026

The user's latest instruction stops OpenRouter and selects their already
deployed Azure gpt-5-mini on their own Free Trial account. This supersedes the
temporary OpenRouter-only selection below. Remove OpenRouter credentials from
the active environment; preserve its historical code, receipts and accounting.
Use only the existing Azure deployment, with local embeddings, parsing,
retrieval, storage, evaluation tooling and UI. Do not create cloud resources,
upgrade the subscription, alter quota/tier or disable spending protection.
Trial credits only; no out-of-pocket use is authorized.

The private Azure endpoint, key and actual deployment name must be supplied
locally. No old expired/stopped Azure receipt authorizes this new account.
Keep live calls disabled until those settings and a current explicitly bounded
trial scope are complete. No provider calls, fallback, retries or benchmark
execution are authorized merely by entering a key. The user explicitly approved
the gpt-5-mini compatibility amendment: omit temperature identically for A/B/C.
The shared evaluation YAML records temperature as null; this is not authorization
to execute a live benchmark.

The earlier restrictions and records below remain historical where they
conflict with this selection; their no-upgrade, no-new-resource, secrecy and
history-preservation requirements continue to apply.

These instructions apply to all further work in this repository. They record the
user's restriction of 24 October 2026 and supersede older paid-use exceptions
for future execution. Preserve historical receipts/results as historical facts.

- Temporarily use only OpenRouter's fixed `nvidia/nemotron-3-ultra-550b-a55b:free`
  route for answering and screening when explicitly enabled with its bounded
  local allowance. Azure implementation and history remain intact but inactive.
  Do not provision or enable additional resources, deployments or paid features:
  no Azure AI Search, cloud embeddings, storage accounts, hosted apps, monitoring
  services or agents. Keep embeddings, parsing, retrieval, Chroma, SQLite,
  evaluation, charts and the UI local.
- Do not change resource SKU/tier, deployment type, subscription plan, spending
  protection or quota allocation. No Free Trial upgrade or out-of-pocket use.
- No paid provider route is authorized. The fixed `:free` alias and NVIDIA-only
  routing are required; verify current OpenRouter terms yourself because local
  code cannot guarantee account billing or provider pricing.
- Make provider calls only within a current explicitly authorized bounded scope.
  The temporary OpenRouter local receipt is limited to interactive Ask calls;
  evaluation remains disabled for this provider.
  No background requests, automatic retries, fallback models, or unnecessary LLM
  calls for health, grading, evaluation planning or chart generation.
- Preserve private settings, frozen datasets, saved results, approvals, original
  stop flags and cumulative accounting. Never reset/refund capacity or reactivate
  exhausted/stopped/expired authorizations. Historical paid receipts remain
  readable but cannot authorize new paid calls under this standing scope.
- Preserve Azure configuration and code; do not route requests to Azure while
  the temporary OpenRouter selection is active. Complete independent local work
  without adding cloud dependencies; do not make provider requests merely to
  diagnose billing.
- Never print credentials, key fragments, headers, private environment contents
  or raw sensitive request/response dumps.

## Explicit expiry amendment, 25 October 2026

The user authorized extending the current OpenRouter benign interactive allowance
to 25 October 2026, 13:00 IST (07:30 UTC). This specific amendment preserves its
identity, consumed reservations and stop flags, adds no capacity and authorizes
no benchmark execution. It is not permission for automatic renewal.

## Explicit new manual authorization, 26 October 2026

The user explicitly requested enabling twenty live provider calls for their
manual checking now. This authorizes a new, independent interactive scope
on the fixed NVIDIA-only Nemotron free route, capped at 20 provider calls
and 640000 local reservation units. It does not authorize benchmark execution,
background inference, retries, paid routes, or automatic renewal.

Activation: 2026-10-25T22:59:48.248634+00:00. Expiry: 2026-10-25T23:59:48.248634+00:00
(2026-10-26T05:29:48.248634+05:30 IST). The existing API key authenticated and
the account reported sufficient free-request capacity during preflight.
Old receipts, consumed reservations and stop flags remain intact. This is
a separately authorized scope, not reactivation of any old authorization.

## Explicit restriction to ten calls, 26 October 2026

The user reduced the active manual scope to ten provider calls for twenty
minutes and asked to keep the other ten inactive until they ask later.
The current receipt retains its allowance identity and consumed accounting;
its cap is now 10 calls / 320000 local reservation units. The original
receipt is preserved privately. This supersedes the prior active twenty-call
cap and one-hour expiry; it does not clear any stop or consumed capacity.

Restriction applied: 2026-10-25T23:02:33.605033+00:00. Expiry: 2026-10-25T23:22:33.605033+00:00
(2026-10-26T04:52:33.605033+05:30 IST). The deferred ten calls remain inactive.
Do not activate them, extend expiry, or renew automatically. Benchmark
execution remains disabled; the fixed free route and all other limits remain.

## Explicit ten-minute manual expiry extension, 26 October 2026

The user explicitly requested ten additional minutes for the currently
active ten-call manual scope. Its new expiry is 2026-10-25T23:32:33.605033+00:00
(2026-10-26T05:02:33.605033+05:30 IST). Keep the same allowance identity, ten-call
cap, consumed reservations and stop flags. The deferred ten calls remain
inactive. This adds time only, not calls or permission for any automatic
renewal, background inference or benchmark execution.


## Explicit Azure request ceiling, 26 October 2026

The user explicitly authorized up to 1000 requests on their personal Azure
account in response to the prepared one-hour live-check question. Use the
existing gpt-5-mini deployment and confirmed trial credits only. This is an
upper bound, not a target or an independently verified provider quota.
Authorization begins 2026-10-26T10:15:47.749409+00:00 and expires
2026-10-26T11:15:47.749409+00:00. No automatic renewal is authorized.

Allocate at most four calls to the synthetic A/B/C smoke test. After success,
the remaining allocation may fund user-initiated benign interactive requests.
All allocations together must remain within the 1000-request ceiling. Preserve
all prior receipts, stop flags and consumed reservations; no historical scope
is reactivated. Stop the smoke test on its first failure, with no retries or
fallback. Benchmark execution remains disabled; this authorization does not
verify Azure's deployment quotas or approve a full evaluation run.


## Explicit removal of current Azure time expiry, 26 October 2026

The user explicitly instructed: "dont set any expriy". This supersedes the
one-hour expiry for the current ordinary Azure interactive allocation. Its
expires_at is null. Preserve the same allowance identity, request ceiling,
consumed reservations and stop flags; no additional capacity is granted.
The aggregate ceiling remains 1000 requests, including the four completed
synthetic smoke requests. Historical receipts and their expiries remain intact.
No time limit should be reintroduced without a new user instruction. Trial
credits only, no new resources/upgrades, no automatic retries/fallback, and no
benchmark execution remain the active scope.


## Azure token-efficiency fix, 26 October 2026

After diagnosis of an empty answer at the completion cap, the user explicitly
requested fixing excessive token use. The shared Azure configuration now adds
reasoning_effort: minimal to the original eight-key configuration as a recorded
compatibility amendment. The completion cap stays 700 and temperature stays
omitted. Apply identical answering settings to A/B/C and minimal reasoning to
screening. Read these settings from eval_config.yaml and record their revised
identity. Preserve historical configuration receipts and results.

A small synthetic A/B/C verification may consume at most four calls from the
existing current request allocation in response to this fix request. It must
not resend the user's failed question, create new capacity, clear stop flags,
add expiry, retry automatically or execute the full benchmark.


## Full-card disclosure rule, 26 October 2026

The user rejected repeated B-mode disclosure of the published sandbox card list.
Remove the active public-test disclosure exception. Shared grounding and B
separation prohibit full payment-card numbers, including sandbox values. C
screening and C's output check apply the same no-exception disclosure policy.
Mask recognized full card numbers in UI previews across modes. Keep A/B/C's
underlying pipelines distinct: UI masking is not a new B runtime defense.
Preserve raw evidence and historical answers; do not score display masking as
model resistance or rewrite historical benchmark observations.

## Explicit bounded current benchmark authorization, 26 October 2026

The user explicitly approved the prepared workload and confirmed current trial
credits and adequate deployment quota: five new-case A checks followed by the
47-case A/B/C comparison, at most 193 provider calls in total. These calls must
consume the existing current 1000-request allocation, not create new capacity.
No expiry, retries, fallback, paid use, new resources or upgrades are authorized.
Stop this benchmark on its first operational failure and preserve every result,
reservation and stop flag. Human judgments must remain actual human judgments.
This amendment supersedes the benchmark prohibition only for this workload.

## Explicit live completion continuation, 26 October 2026

After the first bounded run stopped on a C screening-contract error, the user
explicitly requested fixing it live and completing all remaining project work.
Preserve that failed run, its 11 consumed reservations and its benchmark stop flag.
A new independent corrected run may use at most 193 calls from the existing
remaining Azure allocation (957 at continuation preflight), with the same trial-only
settings, no expiry and no automatic retries/fallback. This adds no capacity to
the aggregate 1000-request ceiling. Preserve all outcomes and stop the corrected
run on its first operational failure. No false human reviews or invented results.

## Explicit provider-filter continuation, 26 October 2026

The user explicitly approved: continue only untouched A/B/C rows, at most 163
further calls from the existing allocation. Preserve every completed/failed row,
all previous scope identities, accounting and stop flags. Azure content-filter
refusals remain operational errors and may advance to distinct untouched requests;
never retry a refused request or change Azure filters. Stop on authentication,
quota, transport, schema or other application failures. This exception changes
the first-error rule only for provider content-filter refusals. The completed
five A smoke checks and successful rows retain their original implementation
provenance; an explicit continuation history records the error-handling-only
revision. Settings, dataset, evidence and defense policies remain identical.


## Explicit PDF-aligned continuation, 27 October 2026

The user approved the prepared continuation of exactly 108 untouched evaluation
rows (36 A, 36 B, 36 C), capped at 144 provider calls from the existing Azure
trial allocation. Preserve previous results, consumed reservations and all old
stop flags. Create an independent continuation identity; add no capacity or
expiry, retry no prior request, and use no fallback. Retain content-filter
refusals as operational errors and advance only to distinct untouched rows.
Stop on any other operational failure. Record the PDF-alignment implementation
revision and prior-row provenance; do not silently rewrite past observations.
Human quality and semantic judgments must remain actual human input.

## Explicit document privacy suite authorization, 27 October 2026

The user explicitly instructed "allow for all the tes case live call" after the
225-case / 675-row scope and existing allowance were explained. Execute all five
privacy cases for each of the 45 documents across A/B/C, capped at the 758 calls
remaining at preflight and 24,256,000 reservation units from the existing Azure
trial allocation. This grants no additional aggregate capacity and no expiry.
The worst-case workload is 900 calls, so this approval does not guarantee all rows
can finish. Preserve unfinished rows if capacity is exhausted. Use a separate
privacy-scope identity, preserve all previous receipts/results/stops, stop on the
first operational failure, and make no automatic retries or fallback. Actual human
reviews remain human. Live interactive answering was also requested; it shares
this same cumulative allowance and never increases the ceiling.

## Explicit privacy reason-consistency continuation, 28 October 2026

The user approved the prepared continuation by instructing "next step do it".
Run only the 612 untouched privacy rows, capped at 695 provider calls from the
existing remaining trial allocation. Preserve the 63 original rows, old scope,
journal, consumed reservations and stop flag. Use the separate
continuation-reason-consistency-v2 receipt with the recorded screening-prompt
clarification and frozen prior-record hashes. Add no capacity or expiry, make no
retries or fallback, and stop on the first operational failure. Worst-case demand
exceeds this cap; leave unfinished rows unrun if capacity is exhausted.

## Explicit untouched privacy continuation, 29 October 2026

The user approved the explained continuation with "okay do it": only the 584
untouched privacy rows, capped at 650 calls / 20,800,000 reservation units from
the existing Azure trial allocation. Use the independent
continuation-business-summary-v7 receipt. Preserve all 91 previous rows, prior
scope identities, consumed accounting and stop flags. Record the revised B/C
business-summary-v7 policy and original per-row implementation provenance;
these revisions must not be presented as one unchanged experiment. No new
capacity, expiry, retries, fallback, paid use, resource changes or automatic
renewal. Stop on the first operational failure, including Azure refusals.
If capacity cannot fund a row's maximum stages, leave that row and later rows
unrun. Human reviews remain actual human input.

## Explicit 25-document PDF-aligned revision, 29 October 2026

The user confirmed A is standard RAG without dedicated injection defenses,
B retains the PDF-required instruction separation, and C retains added screening
and output checks. The standing shared disclosure rule still applies to all modes.
The current dataset is `backend/benchmark_current25`: exactly 25 source packs,
all 45 original extracted source texts and all 47 cases preserved with provenance.
The current privacy suite contains 25 documents and 125 cases (375 A/B/C rows).
Historical datasets, 141 v3 rows, 92 privacy rows, receipts and stops remain intact.

Current-suite reports live under `results/current25`; they must not inherit old
scores. Live questions show observed latency, references and statuses, while
unsupported semantic/security/quality judgments remain N/A. The PDF requires
predefined repeatable evaluation, not automatic benchmark updates for arbitrary
live questions. This revision authorizes local implementation and verification,
not a new live benchmark scope. The prepared main workload is at most 188 calls;
main plus the new privacy suite could require 688 calls and cannot be assumed to
fit the existing remaining allowance. No new capacity, expiry, retries or fallback.

## Explicit current25 main benchmark authorization, 29 October 2026

The user approved the prepared 47-case A/B/C main benchmark with “do it” in
response to the 188-call trial-credit/quota confirmation question. Execute only
these 141 planned rows, at most 188 calls / 6,016,000 reservation units, consuming
the existing aggregate Azure trial allocation. Use independent
`user-approved-current25-main-20261029-v1`; preserve all historical receipts,
rows, consumed accounting and stop flags. No expiry, new capacity, retries,
fallback, paid use or cloud resource changes. Stop on the first operational
failure, including provider refusals. Human judgments remain actual human input.
This authorization does not include the separate 125-case current privacy suite.


## Explicit untouched main benchmark continuation, 30 October 2026

The user approved "Remaining main benchmark only: 122 rows, at most 163 calls".
Use an independent continuation identity and only the existing Azure trial
allocation, without adding capacity or expiry. Preserve all 19 previous main
rows, original receipt, stop flags, accounting and implementation provenance.
Provider content-filter refusals remain operational errors and may advance only
to distinct untouched rows. Never retry a prior request or alter Azure filters.
Stop on any other operational failure. No fallback, paid use or resource changes.
This does not authorize the separate five-tests-per-document privacy workload.
Human judgments remain actual human input. Keep the main 25-document study,
five-tests-per-document study and uploaded documents available in the UI.


## Explicit remaining main continuation, 30 October 2026

After the interrupted Oct30 attempt was preserved and stopped with 45 recorded
rows, the user approved "Complete the remaining 96 rows (128-call cap)".
Use only those 96 untouched main rows (32 per mode), with an independent scope,
maximum 128 provider calls / 4096000 reservation units from the existing trial
allowance. No added capacity, expiry, retries, fallback or resource changes.
Retain provider-filter refusals as errors and advance only to distinct untouched
rows; stop on any other operational failure. Preserve all 45 previous rows,
original stop flags, scope identities and implementation provenance. This does
not authorize privacy execution or fabricated human reviews.


## Saved-benchmark selection, 30 October 2026

The user selected "Use the completed 47-case benchmark; no more live calls".
For this presentation correction use the saved current 141-row main benchmark;
do not execute the unrun current privacy suite or send additional provider calls.
Restore the metric table by default, retain optional graphs, and explain zero
assessed ASR, pending judgments and C-only false positives without changing grades.


## Explicit matched challenge authorization, 30 October 2026

The user approved "Run the 8 new cases, capped at 32 calls" after the separate
24-row A/B/C workload and first-error stop rule were explained. This supersedes
the no-more-calls choice only for this new workload. Use an independent scope,
at most 32 calls / 1024000 reservation units from existing Azure trial capacity.
No added capacity, expiry, retries, fallback or resource changes. Stop on the
first operational failure, including provider refusals. Preserve all prior
records, stop flags and implementation provenance. Keep challenge observations
separate from the frozen 47-case benchmark. Do not prefill successes, false
positives or human reviews; cases may yield zero observed failures.


## Explicit untouched matched-challenge continuation, 30 October 2026

The user approved "Continue the 23 untouched rows, capped at 31 calls" after
one correct answer failed citation validation. Preserve that failed A row and
the stopped 1-call scope; never replay it. Use a new independent scope, cap 31
calls / 992000 reservation units from existing Azure trial capacity, no added
capacity or expiry. Align source ID and document ID to remove identifier
ambiguity; preserve citation validation, facts, model settings and defenses.
Stop on first operational failure. No retries, fallback or fabricated outcomes.


## Explicit all-upload validation, 30 October 2026

The user approved the prepared 23-question / 69-row workload across all 10
frozen uploaded documents and A/B/C, capped at 92 existing Azure trial calls /
2944000 reservation units. They explicitly approved sending retrieved passages
including full payment-card numbers and personal/sensitive information to the
existing gpt-5-mini deployment. Answers must withhold protected values. No added
capacity, expiry, retry, fallback or resource changes. Record provider-filter
refusals as errors and advance only to untouched rows; stop on any other
operational failure. Freeze document versions, retrieval and implementation;
preserve all prior results, scopes and accounting. Human quality remains human.


## Explicit all-upload untouched continuation, 30 October 2026

User approved only the 59 untouched all-upload A/B/C rows, capped at 79 existing trial calls / 2,528,000 reservation units. The original 10 rows and stopped scope stay preserved. The same explicitly approved sensitive passages may be sent to existing Azure. Use the shared concise-answer revision and citation enum. No new capacity, expiry, retries or fallback. Advance only provider-filter refusals and stop on other operational failures. Human quality stays unrated.


## Explicit shared 2000-token cap and final upload continuation, 30 October 2026

User approved raising the shared Azure A/B/C completion cap from 700 to 2000 tokens, superseding the earlier fixed-700 rule. Keep identical settings for all modes and record a new settings identity. Only the 27 untouched all-upload rows may run, capped at 36 existing trial calls / 1,152,000 reservation units. Previously approved sensitive passages remain approved. Preserve both prior stopped runs and all 42 records. No retries, fallback, new capacity, expiry or resource changes. Advance provider-filter refusals; stop on any other operational failure. Human judgments remain unrated.


## Explicit final nine upload rows, 30 October 2026

User approved only the final 9 untouched all-upload rows, capped at 12 existing Azure trial calls / 384,000 reservation units. Retain shared 2000-token cap and required-citation schema. Previously approved sensitive passages remain approved. Preserve all 60 prior rows, including the B disclosure and three stopped scopes. No retries, fallback, new capacity, expiry or resources. Advance filter refusals; stop on other operational failures. Human quality remains unrated.
