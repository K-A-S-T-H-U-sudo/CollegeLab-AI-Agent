"""
Tests for Safe Resolution Engine and Whitelist Enforcement.
"""

import pytest
from resolution.safe_fixes import SafeResolutionEngine, SAFE_REPAIR_REGISTRY


def test_whitelist_rejection():
    """Unregistered or arbitrary commands must be rejected immediately."""
    engine = SafeResolutionEngine()
    bad_res = engine.execute_safe_fix("rmdir_c_drive")
    assert bad_res["success"] is False
    assert "whitelist" in bad_res["message"].lower()


def test_registry_safety_guarantees():
    """Every registered fix must have non-destructive safety guarantees and commands."""
    for action_id, meta in SAFE_REPAIR_REGISTRY.items():
        assert "commands" in meta
        assert len(meta["commands"]) > 0
        assert "safety_guarantee" in meta
        assert "manual_instructions" in meta
