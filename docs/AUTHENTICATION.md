# Microsoft sign-in and roles

Authentication is required on every API route except `/health`. Until local
configuration and Entra role assignment are complete, the workspace stays closed.
Use the existing organization tenant. Do not upgrade, deploy cloud resources,
change model quotas or submit LLM calls to test sign-in.

## Register the API

At https://entra.microsoft.com open **Entra ID → App registrations → New
registration**. Name it **AI Security Lab API**, choose **Accounts in this
organizational directory only**, and leave the redirect URI blank. Save its
Directory (tenant) ID and Application (client) ID locally.

Under **Expose an API**, set the Application ID URI to `api://<API-CLIENT-ID>`.
Add an enabled scope named `access_as_user`, consent **Admins only**, display
name **Access AI Security Lab**, description **Allow the web application to
access AI Security Lab on behalf of the signed-in user.**

In **Manifest**, set `api.requestedAccessTokenVersion` to `2`, preserving other
fields. The API accepts v2 delegated access tokens for this API only, not ID,
Graph, app-only, other-tenant or other-client tokens.

## Define roles and assign people

On the API registration's **App roles** page create enabled roles with member
type **Users/Groups**. Values are case-sensitive:

| Name | Value | Access |
|---|---|---|
| User | `Lab.User` | Shared uploads, predefined documents, upload and local search |
| Reviewer | `Lab.Reviewer` | User access plus evaluations, evidence, downloads and human reviews |
| Administrator | `Lab.Admin` | Reviewer access plus replace/delete/partial activation and diagnostics |
| Live caller | `Lab.LiveCaller` | Additional live Ask/compare permission; a base role is also required |

Administrator does not implicitly grant live access. Roles never increase the
existing trial allowance or authorize a benchmark. Existing scope, stop and
accounting checks remain in effect.

Under **Enterprise applications → AI Security Lab API → Users and groups**,
assign your account `Lab.Admin`. Assign `Lab.LiveCaller` separately only to people
permitted to consume the existing live allocation. Assign others `Lab.User` or
`Lab.Reviewer`. Use direct user assignments; paid group features are unnecessary.
These are app roles, not Azure subscription Owner/Contributor roles.

## Register the web client

Create a second single-tenant registration **AI Security Lab Web**. Select the
**Web** platform with redirect URI `http://localhost:8501/oauth2callback`.
Save its Application (client) ID locally. Under **Certificates & secrets** create
a client secret and save its **Value**, not Secret ID, locally. The API
registration needs no secret. Do not enable implicit grants or public-client flows.

Under the Web app's **API permissions → Add a permission → My APIs**, select
**AI Security Lab API → Delegated permissions → access_as_user**, then grant
administrator consent. Do not add Graph or application permissions for this flow.

For both enterprise applications set **Properties → Assignment required? → Yes**
where available. Assign permitted people to the Web enterprise application too
(default access role is sufficient). API roles belong on the API enterprise app.
If the tenant disallows registration, consent or assignment, its administrator
must complete those steps; do not create another tenant or upgrade to bypass it.

## Configure locally

Add the IDs to the existing root `.env`, preserving provider/allowance settings:

```dotenv
ENTRA_TENANT_ID=<directory-tenant-id>
ENTRA_API_CLIENT_ID=<API-application-client-id>
ENTRA_WEB_CLIENT_ID=<Web-application-client-id>
```

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`. Replace its
tenant/API/Web ID and Web secret placeholders. Keep the custom API scope and
`expose_tokens = ["access"]`. Generate a cookie secret without printing it:

```bash
.venv/bin/python -c 'from pathlib import Path; import secrets; p=Path(".streamlit/secrets.toml"); p.write_text(p.read_text().replace("REPLACE_WITH_A_LONG_RANDOM_SECRET", secrets.token_urlsafe(64))); p.chmod(0o600)'
```

The secrets file is ignored by Git. Never share it, tokens or provider keys in
chat, logs, screenshots or commits. Backend configuration needs no client secret.

## Test sign-in without model calls

```bash
.venv/bin/python -m pip install 'PyJWT[crypto]==2.15.0' 'Authlib==1.9.3'
.venv/bin/python run_app.py
```

Open **http://localhost:8501**, select **Sign in with Microsoft**. Login contacts
Microsoft identity endpoints, not the model. The launcher keeps model calls
disabled. Verify users cannot manage documents, inspect evaluations or submit
reviews; reviewers can inspect/review but cannot manage documents or diagnostics.
Live permission additionally requires `Lab.LiveCaller` and `--live-answers`;
do not submit model calls just to test authentication.

Offline security tests use temporary storage, synthetic RSA signing keys and no
Microsoft/provider requests:

```bash
PYTHONPATH=backend HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python -m pytest backend/tests/api/test_authentication.py -q
```

## Boundaries

Assigned users intentionally share uploads. Cached question IDs are scoped to
the verified tenant/user identity; human review records use that identity rather
than an editable reviewer label. Existing historical records stay intact.
The CLI evaluator remains a trusted local operator tool under its existing
bounded authorizations; HTTP roles do not authorize CLI benchmark execution.

Tokens are verified per request for signature, expiry, issuer, tenant, API
audience, delegated scope, allowed Web client and roles. Microsoft public signing
keys are fetched from the configured authority as needed and cached. Expired API
tokens require sign-out/sign-in; the Streamlit identity cookie can last longer.
Role changes/revocation may take until issued tokens expire. No immediate
revocation or encrypted-storage guarantee is claimed. In-flight requests use
permissions checked at request start.

Hosting is not deployed. Keep services on loopback. Later deployment needs an
approved host, HTTPS/WebSocket support, an exact HTTPS callback, private persistent
storage and the existing one-backend-worker constraint. Do not expose an old
unauthenticated backend. This change adds no provider retries or fallback.

## Official references

- [Client and API registration](https://learn.microsoft.com/en-us/entra/identity-platform/web-api-tutorial-01-register-app)
- [User/app-role assignment](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/assign-user-or-group-access-portal)
- [Token claim validation](https://learn.microsoft.com/en-us/entra/identity-platform/claims-validation)
- [Streamlit OIDC settings](https://docs.streamlit.io/develop/api-reference/user/st.login)
- [Streamlit token access](https://docs.streamlit.io/develop/api-reference/user/st.user)
