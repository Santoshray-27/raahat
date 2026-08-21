from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.repositories.base import BaseRepository
from app.models.user import User, UserPreference
from app.schemas.users import UserProfile
import logging

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository[User]):
    async def sync_user(self, user_profile: UserProfile) -> User:
        """
        Synchronizes a Firebase UserProfile with the PostgreSQL database.
        Returns the synchronized PostgreSQL User record.
        """
        # Find the PostgreSQL User by firebase_uid
        stmt = select(User).where(User.firebase_uid == user_profile.uid)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            # Create a new user
            user = User(
                firebase_uid=user_profile.uid,
                email=user_profile.email,
                phone_number=user_profile.phone_number,
                display_name=user_profile.display_name,
            )
            self.session.add(user)
            
            # Create the default UserPreference record
            preference = UserPreference(user=user)
            self.session.add(preference)

            try:
                await self.session.flush() # flush to generate user.id if needed
                await self.session.commit()
                return user
            except IntegrityError as e:
                await self.session.rollback()
                logger.warning(f"Integrity error creating user {user_profile.uid}, retrying fetch: {e}")
                # It might have been created concurrently, try fetching again
                result = await self.session.execute(stmt)
                user = result.scalar_one_or_none()
                if user is None:
                    raise e
        
        # User exists, synchronize mutable fields if they are not None in the profile
        changed = False
        if user_profile.email is not None and user.email != user_profile.email:
            user.email = user_profile.email
            changed = True
        if user_profile.phone_number is not None and user.phone_number != user_profile.phone_number:
            user.phone_number = user_profile.phone_number
            changed = True
        if user_profile.display_name is not None and user.display_name != user_profile.display_name:
            user.display_name = user_profile.display_name
            changed = True
            
        if changed:
            try:
                await self.session.commit()
            except IntegrityError:
                await self.session.rollback()
                raise
                
        return user
