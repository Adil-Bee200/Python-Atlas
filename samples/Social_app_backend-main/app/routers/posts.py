from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from .. import schema, models, utils
from sqlalchemy.orm import Session
from ..database import get_db
from .. import oauth2
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import joinedload


router = APIRouter(prefix="/posts", tags= ['posts'])

@router.get("", response_model=list[schema.PostWithVotes])
def get_posts(db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user), limit : int = 10,
              skip : int = 0, search : Optional[str] = ""):
    
    results = db.query(models.Post, func.count(models.Votes.post_id).label("votes")).join(
        models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
            models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    return [{"post": post, "votes": votes} for post, votes in results]
    


@router.get("/{id}", status_code=status.HTTP_302_FOUND, response_model=schema.PostWithVotes)
def get_post(id: int, db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    # post = cursor.fetchone()

    result = db.query(models.Post, func.count(models.Votes.post_id).label("votes")).join(
        models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.id == id).first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with {id} not found")
    post, votes = result  
    return {"post": post, "votes": votes}  

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schema.PostReturn)
def create_post(post: schema.Post, db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(owner_id = current_user.id,**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id)

    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post with given id not found")
    
    if post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to performed requested action")

    post.delete(synchronize_session=False)
    db.commit()
    
    
    return post


@router.put("/{id}", response_model=schema.PostReturn)
def update_post(id:int, post: schema.Post, db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #                (post.title, post.content, post.published, id))
    # updated_post = cursor.fetchone()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()

    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")
    
    if updated_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to performed requested action")
    
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    db.refresh(updated_post)
    
    # conn.commit()
    
    return updated_post






