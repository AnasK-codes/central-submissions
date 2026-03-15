from typing import Optional

from sqlalchemy.orm import Session

from database.models.user_model import User


class UserRepository:
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def create_user(self, db: Session, user_in, hashed_password: str) -> User:
        """
        Create a new user from a signup request object.
        Accepts any object with .name and .email attributes (duck-typed).
        """
        db_user = User(
            name=user_in.name,
            email=user_in.email,
            password_hash=hashed_password,
            role="student",
            auth_provider="email",
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_or_create_google_user(
        self,
        db: Session,
        email: str,
        name: str,
        google_id: str,
        picture: Optional[str] = None,
    ) -> User:
        """
        Look up a user by email.

        - If found: link the Google account (if not already linked) and
          refresh name + profile_picture from the latest Google token so
          they stay in sync.
        - If not found: create a new social user with google auth_provider.
        """
        user = self.get_user_by_email(db, email)

        if user:
            changed = False
            # Link Google account if this was previously an email-only user
            if not user.google_id:
                user.google_id = google_id
                user.auth_provider = "google"
                changed = True
            # Always refresh name and picture from Google so they stay current
            if name and user.name != name:
                user.name = name
                changed = True
            if picture and user.profile_picture != picture:
                user.profile_picture = picture
                changed = True
            if changed:
                db.commit()
                db.refresh(user)
            return user

        # New user — create a Google social account
        new_user = User(
            email=email,
            name=name,
            password_hash=None,
            auth_provider="google",
            google_id=google_id,
            profile_picture=picture,
            is_active=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


user_repository = UserRepository()
