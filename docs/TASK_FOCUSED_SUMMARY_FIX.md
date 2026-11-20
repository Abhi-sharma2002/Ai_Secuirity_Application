# Task-focused B/C summaries

Instruction-separation revision `instruction-separation-business-summary-v7`
limits ordinary business answers and broad document summaries to relevant business
facts. It directs the model to omit planted assistant instructions, replacement
answers/amounts, demands to include codes, and commentary about ignoring them.
Genuine business-policy conflicts must still be disclosed. Explicit security
analysis may describe manipulation at a high level without reproducing payloads.

B and C share this separation instruction; A remains unchanged. This is a prompt
policy amendment, not a new deterministic B output filter or a confidentiality
guarantee. Original evidence is unchanged. Historical observations and reviews
remain associated with their original prompt hashes and must not be rewritten.
New interactive responses carry the revised defense version and prompt hash.
The readiness API reports the loaded version; Ask and comparison show the policy
version that produced each saved answer and warn when it differs from the loaded
version. Refreshing or restarting does not regenerate saved responses.
The v7 wording explicitly resolves the grounding policy's conflict-reporting
instruction: assistant-directed replacement answers are not business policies.
It applies to every evidence source without document-specific answer rules.
Existing benchmark artifacts may require their normal compatibility review;
this change does not authorize rerunning them or replacing the frozen index.

No live model verification was performed for this change. Human review of new
outputs is required before claiming the behavior has been demonstrated.
