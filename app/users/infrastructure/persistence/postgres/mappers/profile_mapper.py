from __future__ import annotations

from app.users.domain.entities.profile import Profile
from app.users.domain.value_objects.display_name import DisplayName
from app.users.infrastructure.persistence.postgres.models.profile import ProfileModel


def to_domain(model: ProfileModel) -> Profile:
    return Profile(
        user_id=model.user_id,
        display_name=DisplayName(model.display_name),
        bio=model.bio,
        avatar_url=model.avatar_url,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def to_model(profile: Profile) -> ProfileModel:
    return ProfileModel(
        user_id=profile.user_id,
        display_name=profile.display_name.value,
        bio=profile.bio,
        avatar_url=profile.avatar_url,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


def apply_domain(model: ProfileModel, profile: Profile) -> None:
    model.display_name = profile.display_name.value
    model.bio = profile.bio
    model.avatar_url = profile.avatar_url
    model.updated_at = profile.updated_at
