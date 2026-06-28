from datetime import UTC, datetime
from uuid import uuid4

from raggae.domain.entities.project_mcp_activation import ProjectMcpActivation


def _make_activation(**overrides: object) -> ProjectMcpActivation:
    defaults: dict[str, object] = {
        "project_id": uuid4(),
        "org_mcp_server_id": uuid4(),
        "is_active": True,
        "activated_at": datetime.now(UTC),
        "activated_by_user_id": uuid4(),
    }
    defaults.update(overrides)
    return ProjectMcpActivation(**defaults)  # type: ignore[arg-type]


def test_activate_returns_active_copy() -> None:
    activation = _make_activation(is_active=False)

    activated = activation.activate()

    assert activated.is_active is True
    assert activation.is_active is False


def test_deactivate_returns_inactive_copy() -> None:
    activation = _make_activation(is_active=True)

    deactivated = activation.deactivate()

    assert deactivated.is_active is False
    assert activation.is_active is True
