from __future__ import annotations

from dataclasses import dataclass

from app.auth.application.commands.register_user import RegisterUserCommand
from app.auth.application.ports.password_hasher import PasswordHasher
from app.auth.application.ports.repositories.user_repository import UserRepository
from app.auth.domain.entities.user import User
from app.auth.domain.exceptions import UserAlreadyExistsError
from app.auth.domain.value_objects.display_name import DisplayName
from app.auth.domain.value_objects.email import Email
from app.auth.domain.value_objects.password import Password


@dataclass(slots=True)
class RegistrationService:
    user_repository: UserRepository
    password_hasher: PasswordHasher

    async def register(self, command: RegisterUserCommand) -> None:

        # 1. Convert primitive values into domain value objects.
        email = Email(command.email)
        display_name = DisplayName(command.display_name)

        # 2. Validate the password.
        Password.validate_plain(command.password)

        # 3. Check whether the email is already registered.
        existing_user = await self.user_repository.get_by_email(email.value)
        if existing_user is not None:
            raise UserAlreadyExistsError(
                f"User with email {email.value} already exists"
            )

        # 4. Hash the password.
        hashed_password = self.password_hasher.hash(command.password)

        # 5. Create the domain entity.
        user = User.create(
            email=email,
            display_name=display_name,
            password=Password(hashed_password),
        )

        # 6. Persist the entity.
        await self.user_repository.save(user)
        
        # 7. Return the domain entity.
        return user
