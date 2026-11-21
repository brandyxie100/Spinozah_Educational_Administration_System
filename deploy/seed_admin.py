"""Create the first tenant and admin. Run inside the api container:

docker compose -f docker-compose.prod.yml --env-file .env.prod exec \
  -e TENANT_NAME="My School" -e TENANT_SLUG=myschool \
  -e ADMIN_EMAIL=you@example.com -e ADMIN_NAME="Admin" -e ADMIN_PASSWORD='...' \
  api python - < deploy/seed_admin.py
"""
import asyncio
import os

from app.infrastructure.persistence.models import TenantModel, UserModel, UserRole
from app.infrastructure.persistence.session import create_engine, create_session_factory
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher


async def main() -> None:
    engine = create_engine()
    session_factory = create_session_factory(engine)
    async with session_factory() as session:
        tenant = TenantModel(name=os.environ["TENANT_NAME"], slug=os.environ["TENANT_SLUG"])
        session.add(tenant)
        await session.flush()
        session.add(
            UserModel(
                tenant_id=tenant.id,
                email=os.environ["ADMIN_EMAIL"],
                full_name=os.environ.get("ADMIN_NAME", "Admin"),
                hashed_password=BcryptPasswordHasher().hash(os.environ["ADMIN_PASSWORD"]),
                role=UserRole.ADMIN,
                is_active=True,
            )
        )
        await session.commit()
        print(f"created tenant_slug={tenant.slug}")
    await engine.dispose()


asyncio.run(main())
