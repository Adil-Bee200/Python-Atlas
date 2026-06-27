from fastapi import Depends, HTTPException, status, APIRouter
from app import schema, models, database
from sqlalchemy.orm import Session
from ..database import get_db
from app import oauth2


router = APIRouter(
    prefix="/votes",
    tags=['Vote']
)

@router.post("/", status_code= status.HTTP_201_CREATED)
def vote(vote: schema.Vote, db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):
    find_post_query = db.query(models.Post).filter(models.Post.id == vote.post_id)

    if not find_post_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    vote_query = db.query(models.Votes).filter(models.Votes.post_id == vote.post_id, models.Votes.user_id == current_user.id)
    vote_found = vote_query.first()

    if (vote.dir == 1):
        if vote_found:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user.id} has already voted on this post")
        
        new_vote = models.Votes(user_id= current_user.id, post_id= vote.post_id)
        db.add(new_vote)
        db.commit()
        return "Successfully added vote"
    else:
        if not vote_found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        vote_query.delete(synchronize_session=False)
        db.commit()
        return "Vote successfully deleted"
