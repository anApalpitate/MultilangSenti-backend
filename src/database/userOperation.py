from sqlalchemy.orm import Session

from model.user import User


def getByName(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def getById(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, username: str, hashed_password: str, role="user"):
    user = User(username=username, hashed_password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, username: str, hashed_password: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None
    user.username = username
    user.hashed_password = hashed_password
    db.commit()
    return user


def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None
    db.delete(user)
    db.commit()
    return user
