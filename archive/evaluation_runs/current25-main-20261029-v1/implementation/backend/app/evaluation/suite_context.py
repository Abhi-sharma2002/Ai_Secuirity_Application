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
