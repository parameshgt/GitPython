"""Tests for dynamic and static errors and warnings in GitPython's git.compat module.

These tests verify that the is_<platform> aliases are available, and are even listed in
the output of dir(), but issue warnings, and that bogus (misspelled or unrecognized)
attribute access is still an error both at runtime and with mypy. This is similar to
some of the tests in test_toplevel, but the situation being tested here is simpler
because it does not involve unintuitive module aliasing or import behavior. So this only
tests attribute access, not "from" imports (whose behavior can be intuitively inferred).
"""

import os
import sys

import pytest

import git.compat


_MESSAGE_LEADER = "{} and other is_<platform> aliases are deprecated."


def test_cannot_access_undefined() -> None:
    """Accessing a bogus attribute in git.compat remains a dynamic and static error."""
    with pytest.raises(AttributeError):
        git.compat.foo  # type: ignore[attr-defined]


def test_is_platform() -> None:
    """The is_<platform> aliases work, warn, and mypy accepts code accessing them."""
    fully_qualified_names = [
        "git.compat.is_win",
        "git.compat.is_posix",
        "git.compat.is_darwin",
    ]

    with pytest.deprecated_call() as ctx:
        is_win = git.compat.is_win
        is_posix = git.compat.is_posix
        is_darwin = git.compat.is_darwin

    messages = [str(entry.message) for entry in ctx]
    assert len(messages) == 3

    for fullname, message in zip(fully_qualified_names, messages):
        assert message.startswith(_MESSAGE_LEADER.format(fullname))

    # These exactly reproduce the expressions in the code under test, so they are not
    # good for testing that the values are correct. Instead, the purpose of this test is
    # to ensure that any dynamic machinery put in place in git.compat to cause warnings
    # to be issued does not get in the way of the intended values being accessed.
    assert is_win == (os.name == "nt")
    assert is_posix == (os.name == "posix")
    assert is_darwin == (sys.platform == "darwin")
