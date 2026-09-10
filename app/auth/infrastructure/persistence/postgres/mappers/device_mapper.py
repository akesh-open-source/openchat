from __future__ import annotations

from app.auth.domain.entities.device import Device
from app.auth.infrastructure.persistence.postgres.models.device import DeviceModel


def to_domain(model: DeviceModel) -> Device:
    return Device(
        id=model.id,
        user_id=model.user_id,
        client_device_id=model.client_device_id,
        name=model.name,
        user_agent=model.user_agent,
        created_at=model.created_at,
        updated_at=model.updated_at,
        last_seen_at=model.last_seen_at,
    )


def to_model(device: Device) -> DeviceModel:
    return DeviceModel(
        id=device.id,
        user_id=device.user_id,
        client_device_id=device.client_device_id,
        name=device.name,
        user_agent=device.user_agent,
        created_at=device.created_at,
        updated_at=device.updated_at,
        last_seen_at=device.last_seen_at,
    )


def apply_domain(model: DeviceModel, device: Device) -> None:
    model.user_id = device.user_id
    model.client_device_id = device.client_device_id
    model.name = device.name
    model.user_agent = device.user_agent
    model.updated_at = device.updated_at
    model.last_seen_at = device.last_seen_at
