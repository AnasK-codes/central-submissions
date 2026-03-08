from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import SignupRequest


class UserRepo:
    def get_user_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def create_user(self, db: Session, user_in: SignupRequest, hashed_password: str):
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
        self, db: Session, email: str, name: str, google_id: str
    ):
        # 1. Check if user already exists by email
        user = self.get_user_by_email(db, email)

        if user:
            # Update google_id if it was not previously set (account linking)
            if not user.google_id:
                user.google_id = google_id
                user.auth_provider = "google"
                db.commit()
                db.refresh(user)
            return user

        # 2. If they don't exist, create a new "Social" user
        new_user = User(
            email=email,
            name=name,
            password_hash=None,
            auth_provider="google",
            google_id=google_id,
            is_active=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


user_repo = UserRepo()