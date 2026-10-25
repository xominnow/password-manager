"""Tests for advisory password-strength feedback."""

import pytest

from app.services.password_strength import (
    PasswordStrengthError,
    evaluate_password,
)


def test_strength_feedback_confirms_policy_compliant_password():
    result = evaluate_password("Longer-Synthetic!Password9")

    assert result.meets_policy is True
    assert result.score >= 3
    assert result.label in {"Strong", "Very strong"}
    assert not hasattr(result, "password")


def test_strength_feedback_identifies_missing_policy_categories():
    result = evaluate_password("lowercaseonly")

    assert result.meets_policy is False
    assert result.score <= 1
    assert any("uppercase" in item.lower() for item in result.feedback)
    assert any("number" in item.lower() for item in result.feedback)
    assert any("special" in item.lower() for item in result.feedback)


def test_strength_feedback_flags_common_and_predictable_passwords():
    common = evaluate_password("password1")
    repeated = evaluate_password("AAAAAaaa111!!!")

    assert common.score == 0
    assert any("common" in item.lower() for item in common.feedback)
    assert any("repeating" in item.lower() for item in repeated.feedback)


@pytest.mark.parametrize("password", ["", "short", "abc123"])
def test_strength_feedback_reports_short_passwords(password):
    result = evaluate_password(password)

    assert result.meets_policy is False
    assert any("at least 8" in item.lower() for item in result.feedback)


def test_strength_evaluator_rejects_non_text_values():
    with pytest.raises(PasswordStrengthError):
        evaluate_password(None)
