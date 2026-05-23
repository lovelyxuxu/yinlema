import pytest
from pydantic import ValidationError

from app.schemas.user import UpdateIdentityRequest


def test_identity_role_accepts_new_ids():
    for role in ("pure", "max", "random", "moka", "fan", "cat"):
        req = UpdateIdentityRequest(identity_role=role)
        assert req.identity_role == role


def test_identity_role_rejects_unknown():
    with pytest.raises(ValidationError):
        UpdateIdentityRequest(identity_role="unknown")  # type: ignore[arg-type]
