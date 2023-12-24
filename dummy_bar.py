"""
Stubbed version of alive_progress.alive_bar for when it's disabled or not imported.
"""

from contextlib import AbstractContextManager


class DummyBar(AbstractContextManager):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(*args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
