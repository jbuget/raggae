import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from raggae.application.use_cases.organization.accept_organization_invitation import (
    AcceptOrganizationInvitation,
)
from raggae.application.use_cases.organization.create_organization import CreateOrganization
from raggae.application.use_cases.organization.delete_organization import DeleteOrganization
from raggae.application.use_cases.organization.get_organization import GetOrganization
from raggae.application.use_cases.organization.invite_organization_member import (
    InviteOrganizationMember,
)
from raggae.application.use_cases.organization.leave_organization import LeaveOrganization
from raggae.application.use_cases.organization.list_organization_invitations import (
    ListOrganizationInvitations,
)
from raggae.application.use_cases.organization.list_organization_members import (
    ListOrganizationMembers,
)
from raggae.application.use_cases.organization.list_organizations import ListOrganizations
from raggae.application.use_cases.organization.remove_organization_member import (
    RemoveOrganizationMember,
)
from raggae.application.use_cases.organization.resend_organization_invitation import (
    ResendOrganizationInvitation,
)
from raggae.application.use_cases.organization.revoke_organization_invitation import (
    RevokeOrganizationInvitation,
)
from raggae.application.use_cases.organization.update_organization import UpdateOrganization
from raggae.application.use_cases.organization.update_organization_member_role import (
    UpdateOrganizationMemberRole,
)
from raggae.domain.exceptions.organization_exceptions import (
    LastOrganizationOwnerError,
    OrganizationAccessDeniedError,
    OrganizationInvitationInvalidError,
    OrganizationNotFoundError,
)
from raggae.presentation.api.dependencies import (
    get_accept_organization_invitation_use_case,
    get_create_organization_use_case,
    get_current_user_id,
    get_delete_organization_use_case,
    get_get_organization_use_case,
    get_invite_organization_member_use_case,
    get_leave_organization_use_case,
    get_list_organization_invitations_use_case,
    get_list_organization_members_use_case,
    get_list_organizations_use_case,
    get_remove_organization_member_use_case,
    get_resend_organization_invitation_use_case,
    get_revoke_organization_invitation_use_case,
    get_update_organization_member_role_use_case,
    get_update_organization_use_case,
)
from raggae.presentation.api.v1.schemas.organization_schemas import (
    AcceptOrganizationInvitationRequest,
    CreateOrganizationRequest,
    InviteOrganizationMemberRequest,
    OrganizationInvitationResponse,
    OrganizationMemberResponse,
    OrganizationResponse,
    UpdateOrganizationMemberRoleRequest,
    UpdateOrganizationRequest,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user_id)])
async def create_organization(
    data: CreateOrganizationRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[CreateOrganization, Depends(get_create_organization_use_case)],
) -> OrganizationResponse:
    organization = await use_case.execute(
        user_id=user_id,
        name=data.name,
        description=data.description,
        logo_url=data.logo_url,
    )
    logger.info(
        "organization_created",
        extra={"organization_id": str(organization.id), "user_id": str(user_id)},
    )
    return OrganizationResponse(**organization.__dict__)


@router.get("", dependencies=[Depends(get_current_user_id)])
async def list_organizations(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListOrganizations, Depends(get_list_organizations_use_case)],
) -> list[OrganizationResponse]:
    organizations = await use_case.execute(user_id=user_id)
    return [OrganizationResponse(**organization.__dict__) for organization in organizations]


@router.get("/{organization_id}", dependencies=[Depends(get_current_user_id)])
async def get_organization(
    organization_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[GetOrganization, Depends(get_get_organization_use_case)],
) -> OrganizationResponse:
    try:
        organization = await use_case.execute(organization_id=organization_id, user_id=user_id)
    except OrganizationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found") from None
    except OrganizationAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden") from None
    return OrganizationResponse(**organization.__dict__)


@router.patch("/{organization_id}", dependencies=[Depends(get_current_user_id)])
async def update_organization(
    organization_id: UUID,
    data: UpdateOrganizationRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[UpdateOrganization, Depends(get_update_organization_use_case)],
) -> OrganizationResponse:
    try:
        organization = await use_case.execute(
            organization_id=organization_id,
            user_id=user_id,
            name=data.name,
            description=data.description,
            logo_url=data.logo_url,
        )
    except OrganizationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found") from None
    except OrganizationAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden") from None
    logger.info(
        "organization_updated",
        extra={"organization_id": str(organization_id), "user_id": str(user_id)},
    )
    return OrganizationResponse(**organization.__dict__)


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user_id)])
async def delete_organization(
    organization_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[DeleteOrganization, Depends(get_delete_organization_use_case)],
) -> None:
    try:
        await use_case.execute(organization_id=organization_id, user_id=user_id)
    except OrganizationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found") from None
    except OrganizationAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden") from None
    logger.info(
        "organization_deleted",
        extra={"organization_id": str(organization_id), "user_id": str(user_id)},
    )


@router.get("/{organization_id}/members", dependencies=[Depends(get_current_user_id)])
async def list_organization_members(
    organization_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListOrganizationMembers, Depends(get_list_organization_members_use_case)],
) -> list[OrganizationMemberResponse]:
    try:
        members = await use_case.execute(organization_id=organization_id, user_id=user_id)
    except OrganizationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found") from None
    except OrganizationAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden") from None
    return [OrganizationMemberResponse(**member.__dict__) for member in members]


@router.patch("/{organization_id}/members/{member_id}", dependencies=[Depends(get_current_user_id)])
async def update_organization_member_role(
    organization_id: UUID,
    member_id: UUID,
    data: UpdateOrganizationMemberRoleRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[
        UpdateOrganizationMemberRole, Depends(get_update_organization_member_role_use_case)
    ],
) -> OrganizationMemberResponse:
    try:
        member = await use_case.execute(
            organization_id=organization_id,
            requester_user_id=user_id,
            member_id=member_id,
            role=data.role,
        )
    except OrganizationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found") from None
    except LastOrganizationOwnerError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from None
    except OrganizationAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden") from None
    logger.info(
        "organization_member_role_updated",
        extra={
            "organization_id": str(organization_id),
            "member_id": str(member_id),
            "user_id": str(user_id),
        },
    )
    return OrganizationMemberResponse(**member.__dict__)


@router.delete(
    "/{organization_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user_id)],
)
async def remove_organization_member(
    organization_id: UUID,
    member_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[RemoveOrganizationMember, Depends(get_remove_organization_member_use_case)],
) -> None:
    try:
        await use_case.execute(
            organization_id=organization_id,
            requester_user_id=user_id,
            member_id=member_id,
        )
    except OrganizationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found") from None
    except LastOrganizationOwnerError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from None
    except OrganizationAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden") from None
    logger.info(
        "organization_member_removed",
        extra={
            "organization_id": str(organization_id),
            "member_id": str(member_id),
            "user_id": str(user_id),
        },
    )


@router.post("/{organization_id}/leave", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user_id)])
async def leave_organization(
    organization_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[LeaveOrganization, Depends(get_leave_organization_use_case)],
) -> None:
    try:
        await use_case.execute(organization_id=organization_id, user_id=user_id)
    except OrganizationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found") from None
    except LastOrganizationOwnerError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from None
    except OrganizationAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden") from None
    logger.info(
        "organization_member_left",
        extra={"organization_id": str(organization_id), "user_id": str(user_id)},
    )


@router.post("/{organization_id}/invitations", dependencies=[Depends(get_current_user_id)])
async def invite_organization_member(
    organization_id: UUID,
    data: InviteOrganizationMemberRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[InviteOrganizationMember, Depends(get_invite_organization_member_use_case)],
) -> OrganizationInvitationResponse:
    try:
        invitation = await use_case.execute(
            organization_id=organization_id,
            requester_user_id=user_id,
            email=data.email,
            role=data.role,
        )
    except OrganizationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found") from None
    except OrganizationInvitationInvalidError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from None
    except OrganizationAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden") from None
    logger.info(
        "organization_invitation_created",
        extra={
            "organization_id": str(organization_id),
            "invitation_id": str(invitation.id),
            "user_id": str(user_id),
        },
    )
    return OrganizationInvitationResponse(**invitation.__dict__)


@router.get("/{organization_id}/invitations", dependencies=[Depends(get_current_user_id)])
async def list_organization_invitations(
    organization_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[
        ListOrganizationInvitations, Depends(get_list_organization_invitations_use_case)
    ],
) -> list[OrganizationInvitationResponse]:
    try:
        invitations = await use_case.execute(
            organization_id=organization_id,
            requester_user_id=user_id,
        )
    except OrganizationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found") from None
    except OrganizationAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden") from None
    return [OrganizationInvitationResponse(**invitation.__dict__) for invitation in invitations]


@router.post(
    "/{organization_id}/invitations/{invitation_id}/resend",
    dependencies=[Depends(get_current_user_id)],
)
async def resend_organization_invitation(
    organization_id: UUID,
    invitation_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[
        ResendOrganizationInvitation, Depends(get_resend_organization_invitation_use_case)
    ],
) -> OrganizationInvitationResponse:
    try:
        invitation = await use_case.execute(
            organization_id=organization_id,
            requester_user_id=user_id,
            invitation_id=invitation_id,
        )
    except OrganizationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found") from None
    except OrganizationInvitationInvalidError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from None
    except OrganizationAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden") from None
    logger.info(
        "organization_invitation_resent",
        extra={
            "organization_id": str(organization_id),
            "invitation_id": str(invitation_id),
            "user_id": str(user_id),
        },
    )
    return OrganizationInvitationResponse(**invitation.__dict__)


@router.delete(
    "/{organization_id}/invitations/{invitation_id}",
    dependencies=[Depends(get_current_user_id)],
)
async def revoke_organization_invitation(
    organization_id: UUID,
    invitation_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[
        RevokeOrganizationInvitation, Depends(get_revoke_organization_invitation_use_case)
    ],
) -> OrganizationInvitationResponse:
    try:
        invitation = await use_case.execute(
            organization_id=organization_id,
            requester_user_id=user_id,
            invitation_id=invitation_id,
        )
    except OrganizationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found") from None
    except OrganizationInvitationInvalidError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from None
    except OrganizationAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden") from None
    logger.info(
        "organization_invitation_revoked",
        extra={
            "organization_id": str(organization_id),
            "invitation_id": str(invitation_id),
            "user_id": str(user_id),
        },
    )
    return OrganizationInvitationResponse(**invitation.__dict__)


@router.post("/invitations/accept", dependencies=[Depends(get_current_user_id)])
async def accept_organization_invitation(
    data: AcceptOrganizationInvitationRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[AcceptOrganizationInvitation, Depends(get_accept_organization_invitation_use_case)],
) -> OrganizationMemberResponse:
    try:
        member = await use_case.execute(token_hash=data.token, user_id=user_id)
    except OrganizationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found") from None
    except OrganizationInvitationInvalidError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from None
    return OrganizationMemberResponse(**member.__dict__)
