"""Single-tenant Entra delegated access tokens and deny-by-default API permissions.

No role/email supplied by a browser is trusted. The CLI evaluator remains a
local operator tool, outside HTTP authentication and inside its existing scopes.
"""
from contextvars import ContextVar
from dataclasses import dataclass
from functools import lru_cache
import os
import hmac
from uuid import UUID

from fastapi import HTTPException, Request
from starlette.concurrency import run_in_threadpool


ROLE_PERMISSIONS = {
    'Lab.User': frozenset({'documents.read', 'documents.upload', 'search'}),
    'Lab.Reviewer': frozenset({'documents.read', 'documents.upload', 'search', 'evaluation.read', 'evaluation.review'}),
    'Lab.Admin': frozenset({'documents.read', 'documents.upload', 'documents.manage', 'search',
                            'evaluation.read', 'evaluation.review', 'operations.read'}),
}
LIVE_ROLE = 'Lab.LiveCaller'

# Use matched route templates, not loose prefixes. New endpoints have no access
# until a permission is deliberately assigned here.
ROUTE_PERMISSIONS = {
    ('GET', '/auth/me'): 'authenticated',
    ('GET', '/ready'): 'authenticated',
    ('GET', '/predefined-documents'): 'documents.read',
    ('GET', '/documents'): 'documents.read',
    ('GET', '/versions/{version_id}'): 'documents.read',
    ('POST', '/documents'): 'documents.upload',
    ('POST', '/documents/{document_id}/replace'): 'documents.manage',
    ('POST', '/versions/{version_id}/accept-partial'): 'documents.manage',
    ('DELETE', '/documents/{document_id}'): 'documents.manage',
    ('POST', '/search'): 'search',
    ('POST', '/chat'): 'live.call',
    ('POST', '/compare'): 'live.call',
    ('GET', '/results'): 'evaluation.read',
    ('GET', '/results/{run_id}'): 'evaluation.read',
    ('GET', '/results/{run_id}/artifacts/{artifact}'): 'evaluation.read',
    ('GET', '/diagnostics'): 'operations.read',
    ('GET', '/diagnostics/{diagnostic_id}'): 'operations.read',
}
for _suite in ('evaluation-v3', 'evaluation-current25'):
    ROUTE_PERMISSIONS.update({
        ('GET', f'/{_suite}'): 'evaluation.read',
        ('GET', f'/{_suite}/artifacts/{{artifact}}'): 'evaluation.read',
        ('GET', f'/{_suite}/evidence/{{case_id}}'): 'evaluation.read',
        ('POST', f'/{_suite}/quality-review'): 'evaluation.review',
        ('POST', f'/{_suite}/case-review'): 'evaluation.review',
    })
for _suite in ('evaluation-document-privacy', 'evaluation-current25-privacy'):
    ROUTE_PERMISSIONS[('GET', f'/{_suite}')] = 'evaluation.read'
    ROUTE_PERMISSIONS[('POST', f'/{_suite}/review')] = 'evaluation.review'
for _suite in ('evaluation-uploads', 'evaluation-challenges'):
    ROUTE_PERMISSIONS[('GET', f'/{_suite}')] = 'evaluation.read'


@dataclass(frozen=True)
class IdentityConfig:
    tenant_id: str
    api_client_id: str
    web_client_id: str

    @property
    def issuer(self):
        return f'https://login.microsoftonline.com/{self.tenant_id}/v2.0'


def configuration():
    try:
        values = [str(UUID(os.environ[name].strip())) for name in
                  ('ENTRA_TENANT_ID', 'ENTRA_API_CLIENT_ID', 'ENTRA_WEB_CLIENT_ID')]
        if values[1] == values[2]:
            raise ValueError('Separate API and web registrations required')
        return IdentityConfig(*values)
    except (KeyError, ValueError, AttributeError):
        raise HTTPException(503, 'Microsoft sign-in is not configured. Configure the existing tenant and API/web application IDs locally.') from None


@dataclass(frozen=True)
class Principal:
    tenant_id: str
    object_id: str
    roles: frozenset[str]

    @property
    def subject(self):
        # Stable, tenant-scoped identity; never an editable display name/email.
        return f'{self.tenant_id}:{self.object_id}'

    @property
    def permissions(self):
        permissions = frozenset().union(*(ROLE_PERMISSIONS.get(role, frozenset()) for role in self.roles))
        if permissions and LIVE_ROLE in self.roles:
            permissions |= {'live.call'}
        return permissions


_principal = ContextVar('authenticated_principal', default=None)


def current_principal():
    principal = _principal.get()
    if principal is None:
        raise HTTPException(401, 'Microsoft sign-in required', headers={'WWW-Authenticate': 'Bearer'})
    return principal


@lru_cache(maxsize=4)
def signing_keys(tenant_id):
    import jwt
    # Trusted static authority only: never follow jku/x5u from a submitted JWT.
    return jwt.PyJWKClient(f'https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys',
                           cache_jwk_set=True, lifespan=300, timeout=5)


def validate_token(token):
    config = configuration()
    try:
        import jwt
    except ImportError:
        raise HTTPException(503, 'Microsoft sign-in dependencies are not installed.') from None
    try:
        header = jwt.get_unverified_header(token)
        if header.get('alg') != 'RS256' or not isinstance(header.get('kid'), str) or len(header['kid']) > 200:
            raise jwt.InvalidTokenError()
        key = signing_keys(config.tenant_id).get_signing_key_from_jwt(token)
        claims = jwt.decode(token, key.key, algorithms=['RS256'], audience=config.api_client_id,
                            issuer=config.issuer, options={'require': ['exp', 'iat', 'nbf', 'iss', 'aud', 'tid', 'oid', 'sub', 'azp', 'scp', 'ver']})
        if (claims['ver'] != '2.0' or claims['tid'] != config.tenant_id
                or claims['azp'] != config.web_client_id or claims.get('idtyp') == 'app'
                or not isinstance(claims['scp'], str) or 'access_as_user' not in claims['scp'].split()):
            raise jwt.InvalidTokenError()
        oid = str(UUID(claims['oid']))
        roles = claims.get('roles', [])
        if not isinstance(roles, list) or any(not isinstance(role, str) for role in roles):
            raise jwt.InvalidTokenError()
        principal = Principal(config.tenant_id, oid, frozenset(roles))
    except jwt.PyJWKClientConnectionError:
        raise HTTPException(503, 'Microsoft signing keys are temporarily unavailable. No provider request was made.') from None
    except (jwt.PyJWTError, ValueError, TypeError, KeyError):
        raise HTTPException(401, 'Invalid or expired Microsoft API access token. Sign in again.',
                            headers={'WWW-Authenticate': 'Bearer'}) from None
    if not principal.permissions:
        raise HTTPException(403, 'An application role must be assigned by your administrator.')
    return principal


async def require_access(request: Request):
    route = request.scope.get('route')
    template = getattr(route, 'path', '')
    if request.method == 'GET' and template == '/health':
        yield
        return
    header = request.headers.get('authorization', '')
    scheme, _, token = header.partition(' ')
    if scheme.lower() != 'bearer' or not token or len(token) > 16_384:
        raise HTTPException(401, 'Microsoft sign-in required', headers={'WWW-Authenticate': 'Bearer'})
    local_token = os.environ.get('LOCAL_ACCESS_TOKEN')
    if local_token and token.isascii() and hmac.compare_digest(token, local_token):
        principal = Principal('local', 'operator', frozenset({'Lab.Admin', LIVE_ROLE}))
    else:
        principal = await run_in_threadpool(validate_token, token)
    permission = ROUTE_PERMISSIONS.get((request.method, template))
    if permission != 'authenticated' and permission not in principal.permissions:
        raise HTTPException(403, 'Your role does not permit this action.')
    context = _principal.set(principal)
    try:
        yield
    finally:
        _principal.reset(context)
