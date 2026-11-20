> Dataset version note: the current predefined study is **25 documents / 47 cases**. Earlier dataset counts, execution logs and measured rates below describe their historical versions. For current status, use [the current study guide](current25/README.md).

# Document privacy live run — 27 October 2026

The user approved all cases within the existing remaining Azure trial allowance.
A separate scope capped this attempt at 758 calls; it added no aggregate capacity.

- Live backend answering was enabled and real Azure responses were recorded.
- 63 provider calls were reserved and 63 of 675 rows were saved.
- 62 rows contain non-operational-error outcomes; all require semantic review.
- One operational error: development-05--control, mode C.
- The screener returned `none` together with another reason code. The existing
  schema correctly rejected that contradictory metadata.
- The run stopped immediately, preserving its stop flag, journal, raw private
  response and every saved row. No request was retried.
- 612 rows remain unrun. The first four documents have all fifteen A/B/C rows.
- The shared allowance had 695 calls remaining at the post-run check. Interactive
  live answering remained enabled; the privacy benchmark scope remained stopped.
- Zero automatically matched leakage candidates is not a reviewed security rate.

Inspect Metrics / evaluation → Five tests per document. Do not clear the stop flag
or reuse this scope. Any continuation needs a concrete correction and a separately
approved untouched-row scope, retaining prior provenance and consumed capacity.

## Reason-consistency continuation — 28 October 2026

The user approved a separate untouched-row continuation capped at 695 existing
calls. The C screening prompt clarified that `none` is an exclusive overall
reason, not a per-source label; strict contradictory-metadata validation remained.

- 28 continuation calls produced 28 additional saved rows: 27 non-error outcomes
  and one provider error.
- Azure returned `content_filter` for development-07--control / A generation.
  The client category was `invalid_request_or_unsupported_parameters`; the saved
  provider code identifies the refusal. It is not a defense success.
- The continuation stopped immediately; no retry or filter adjustment was made.
- Total: 91/675 rows, 89 non-error outcomes requiring review, two errors and 584
  untouched rows. The original 63 record hashes were verified unchanged.
- Remaining shared allowance at post-run check: 667 calls. Interactive answering
  remained enabled, while both benchmark stop flags remained preserved.

A further continuation requires a separate explicit approval. A provider-filter
exception, if approved, may advance only to distinct untouched requests; it must
not retry the refused prompt or weaken provider filters.

## Business-summary-v7 continuation — 29 October 2026

The user approved 584 untouched rows within at most 650 remaining existing Azure
trial calls. A new independent `continuation-business-summary-v7` scope preserved
all 91 prior record hashes and all prior stop flags. New requests use the revised
B/C summary policy; older rows retain their original implementation identities.

The first untouched row, `development-07--control / B`, received Azure
`content_filter` during generation. One call was consumed; the outcome and new
stop flag were saved, and execution stopped immediately without retry or fallback.
The client's generic category is `invalid_request_or_unsupported_parameters`;
the recorded provider code identifies this as a content-filter refusal.

Coverage is now 92/675 rows: 89 non-error outcomes awaiting human review,
three operational errors, and 583 untouched rows. Remaining cumulative allowance
at post-run check: 649 calls. All 91 prior records and old stop flags were verified
unchanged. No new capacity or expiry was created. No later row was attempted.
This continuation is stopped and must not be silently resumed. Provider refusals
are operational failures, not defense successes. The public continuation receipt
and sanitized outcome are in
`DOCUMENT_PRIVACY_BUSINESS_SUMMARY_V7_CONTINUATION.json`.
