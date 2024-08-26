from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import crud, models, schemas, auth
from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(SessionLocal)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(SessionLocal)):
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/books/{book_id}/reviews/", response_model=schemas.Review)
def create_review_for_book(
    book_id: int, review: schemas.ReviewCreate, db: Session = Depends(SessionLocal), current_user: schemas.User = Depends(auth.get_current_user)
):
    return crud.create_review(db=db, review=review, user_id=current_user.id)

@app.get("/books/{book_id}/reviews/", response_model=List[schemas.Review])
def read_reviews(book_id: int, db: Session = Depends(SessionLocal)):
    return crud.get_reviews_by_book(db, book_id=book_id)
