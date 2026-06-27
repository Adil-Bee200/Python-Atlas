from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from .. import schema, models, utils
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(prefix="/users", tags= ['users'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.UserResponse)
def create_user(user: schema.User, db: Session= Depends(get_db)):

    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # cursor.execute("""INSERT INTO users (email, password) VALUES (%s, %s) RETURNING *""", (user.email, user.password))
    # new_user = cursor.fetchone()
    # conn.commit()

    return new_user

@router.get("/{id}", response_model=schema.UserResponse)
def get_user(id: int, db: Session= Depends(get_db)):
    # cursor.execute("""SELECT * FROM users WHERE id = %s""", (str(id)))
    # user = cursor.fetchone()

    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} not found")
    
    return user