"""Request-local suite selection. Historical data remains the default for old tools."""
from contextlib import contextmanager
from contextvars import ContextVar
from app.evaluation.simple_config import ROOT

CURRENT = 'current25'
_SELECTED = ContextVar('evaluation_suite', default='historical-v3')


def is_current():
    return _SELECTED.get() == CURRENT


def dataset(default):
    return ROOT / 'backend/benchmark_current25' if is_current() else default


def store(default):
    return ROOT / '.cache/evaluation_current25' if is_current() else default


def output(default):
    return ROOT / 'results/current25' if is_current() else default


@contextmanager
def current_suite():
    token = _SELECTED.set(CURRENT)
    try:
        yield
    finally:
        _SELECTED.reset(token)

_CONTINUATION = ContextVar('current25_continuation', default=False)

@contextmanager
def continuation_suite():
    with current_suite():
        token = _CONTINUATION.set(True)
        try:
            yield
        finally:
            _CONTINUATION.reset(token)


def execution_scope():
    if _CONTINUATION.get() == 'remaining-challenges':
        from app.evaluation import challenge_remaining_scope
        return challenge_remaining_scope
    if _CONTINUATION.get() == 'challenges':
        from app.evaluation import challenge_scope
        return challenge_scope
    if _CONTINUATION.get() == 'v3':
        from app.evaluation import current25_remaining_scope
        return current25_remaining_scope
    if _CONTINUATION.get():
        from app.evaluation import current25_continuation_scope
        return current25_continuation_scope
    from app.evaluation import current25_scope
    return current25_scope


@contextmanager
def remaining_suite():
    with current_suite():
        token = _CONTINUATION.set('v3')
        try:
            yield
        finally:
            _CONTINUATION.reset(token)


@contextmanager
def challenge_suite():
    with current_suite():
        token = _CONTINUATION.set('challenges')
        try:
            yield
        finally:
            _CONTINUATION.reset(token)


@contextmanager
def remaining_challenge_suite():
    with current_suite():
        token = _CONTINUATION.set('remaining-challenges')
        try:
            yield
        finally:
            _CONTINUATION.reset(token)
