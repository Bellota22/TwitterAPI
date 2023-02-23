#
import json
from uuid import UUID
from datetime import date
from datetime import datetime
from typing import Optional, List


# Pydantic
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field

# FastAPI
from fastapi import FastAPI, HTTPException
from fastapi import status
from fastapi import Body, Path, Form
from fastapi.responses import JSONResponse

from tokens.jwt_manager import create_token

app = FastAPI()

# Models

class UserBase(BaseModel):
        # Universal unique identifier
    user_id: UUID = Field(...   )
    email: EmailStr = Field(...)

class UserLogin(UserBase):
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=69,
        example = 'passwor123123'
    )    

class User(UserBase):

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example= 'Pedro'
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example= "Garcia"
    )

    birth_date: Optional[datetime] = Field(default=None)

class UserRegister(User, UserLogin):
    pass
class Tweet(BaseModel):
    
    tweet_id: UUID = Field(...)
    content: str = Field(
        ...,
        min_length=1,
        max_length= 256
    )
    created_at: datetime = Field(default=datetime.now())
    updated_at: Optional[datetime] = Field(default= None)
    by: User = Field(...)

class LoginOut(BaseModel): 
    email: EmailStr = Field(...)
    message: str = Field(default="Login Successfully!")
# Path operation



## Users

### Register a User
@app.post(
    path='/signup',
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a User ",
    tags=["Users"]
    )
def signup(user: UserRegister = Body(...)):
    """
        This path operation register a User in the app
        
        Params:

            - Request body parameter
                - user :  UserRegister
        
        Returns a json with basic user information:

            - user_id : UUID
            - email : EmailStr
            - first_name : str
            - Lat_name : str
            - birth_date : date
    """
    # To open the json file with r/w 
    with open("users.json", "r+", encoding="utf-8") as f:
        # loads recieve a string and return a json's sinil (dict)
        results = json.load(f)
        # transf explicitly json to dict
        user_dict = user.dict()
        
        # The kind of types of these can't soport transf
        # to dict automat, we must do it
        user_dict["user_id"] = str(user_dict["user_id"])
        user_dict["birth_date"] = str(user_dict["birth_date"])
        results.append(user_dict)

        # find the first byte of the file, that prevents us to 
        # agregg a lot of list
        f.seek(0)
        # write a json from results
        f.write(json.dumps(results))

        # Returns the user and say OK
        return user 

### Login a user
@app.post(
    path='/login',
    response_model=LoginOut,
    status_code=status.HTTP_200_OK,
    summary="Login a User ",
    tags=["auth"]
    )
def login(
    email: EmailStr = Form(...),
    password: str = Form(...)
):
    with open("users.json", "r+", encoding="utf-8") as f: 
            datos = json.loads(f.read())
            for user in datos:
                if email == user['email'] and password == user['password']:
                    return LoginOut(email=email)
                else:
                    return LoginOut(email=email, message="Login Unsuccessfully!")


### Show all user
@app.get(
    path='/users',
    response_model=List[User],
    status_code=status.HTTP_200_OK,
    summary="Show all user ",
    tags=["Users"]
    )
def show_all_users():
    """
    This path operation show all users

    Params:

    Return a json list with all user in the app with the following
    keys:
    - user_id : UUID
    - email : EmailStr
    - first_name : str
    - Lat_name : str
    - birth_date : date
    """
    with open('users.json','r', encoding="utf-8") as f:
        results = json.load(f)
        return results


### Show specific user
@app.get(
    path='/users/{user_id}',
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Show a specific user information",
    tags=["Users"]
    )
def show_user(
    user_id: UUID = Path(
        ...,
        description="The user's id",
        example= "3fa85f64-5717-4562-b3fc-2c963f66afa2"),

):
    """
    This path operation show an especific users

    Params:

    Return a json list with the user in the app with the following
    keys:
    - user_id : UUID
    - email : EmailStr
    - first_name : str
    - Lat_name : str
    - birth_date : date
    """
    with open("users.json", "r+", encoding="utf-8") as f: 
        results = json.loads(f.read())
        id = str(user_id)
        for data in results:
            if data["user_id"] == id:
                return data
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"¡This user_id doesn't exist!"
            )
    

    

### Delete specific user
@app.delete(
    path='/users/{user_id}/delete',
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Delete a specific user information",
    tags=["Users"]
    )
def delete_user(
    user_id: UUID = Path(
        ...,
        title="User ID",
        description="This is the user ID",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa2"
    )):
    """
    Delete a user

    This path operation delete a user in the app

    Parameters:

        - user_id: UUID

    Returns a json with deleted user data:

        - user_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
        - by: User
    """
    with open("users.json", "r+", encoding="utf-8") as f: 
        results = json.loads(f.read())
        id = str(user_id)
    for data in results:
        if data["user_id"] == id:
            results.remove(data)
            with open("users.json", "w", encoding="utf-8") as f:
                f.seek(0)
                f.write(json.dumps(results))
            return data
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="¡This user_id doesn't exist!"
        )

### Update specific user
@app.put(
    path='/users/{user_id}/update',
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Update a specific user information",
    tags=["Users"]
    )
def update_user(
    user_id: UUID = Path(
        ...,
        title="User ID",
        description="This is the user ID",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa2"
    ),
    user: User = Body(...)
):
    """
    This path operation show update an user

    Params:

    Return a json list with the updated user in the app with the following
    keys:
    - user_id : UUID
    - email : EmailStr
    - first_name : str
    - Lat_name : str
    - birth_date : date
    """
    user_id = str(user_id)
    user_dict = user.dict()
    user_dict["user_id"] = str(user_dict["user_id"])
    user_dict["birth_date"] = str(user_dict["birth_date"])
    with open("users.json", "r+", encoding="utf-8") as f: 
        results = json.loads(f.read())
        for user in results:
            if user["user_id"] == user_id:  
                results[results.index(user)] = user_dict
                with open("users.json", "w", encoding="utf-8") as f:
                    f.seek(0)
                    f.write(json.dumps(results))
                return user_dict
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="¡This user_id doesn't exist!"
            )



## Tweets

### Show all tweets
@app.get(
    path='/',
    response_model=List[Tweet],
    status_code=status.HTTP_200_OK,
    summary="Show all tweets ",
    tags=["Tweets"]
)
def home():
    """
    This path operation show all tweets

    Params:

    Return a json list with all tweet in the app with the following
    keys:
    - tweet_id : UUID
    - email : EmailStr
    - first_name : str
    - Lat_name : str
    - birth_date : date
    """
    with open('tweets.json','r', encoding="utf-8") as f:
        results = json.load(f)
        return results


### Post a tweet
@app.post(
    path='/post',
    response_model=Tweet,
    status_code=status.HTTP_201_CREATED,
    summary="Post a tweet ",
    tags=["Tweets"]
    )
def post(tweet: Tweet = Body(...)):

    """
    This path operation post a tweet in the app
    
    Params:

        - Request body parameter
            - tweet : Tweet
    
    Returns a json with basic tweet information:

    tweet_id: UUID 
    content: str 
    created_at: datetime 
    update_at: Optional[datetime] 
    by: User
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        tweet_dict = tweet.dict()
        

        tweet_dict["tweet_id"] = str(tweet_dict["tweet_id"])
        tweet_dict["created_at"] = str(tweet_dict["created_at"])
        tweet_dict["updated_at"] = str(tweet_dict["updated_at"])
        tweet_dict["by"]["user_id"] = str(tweet_dict["by"]["user_id"])
        tweet_dict["by"]["birth_date"] = str(tweet_dict["by"]["birth_date"])


        results.append(tweet_dict)
        f.seek(0)
        f.write(json.dumps(results))

        return tweet 


### show a tweet
@app.get(
    path='/tweets/{tweet_id}',
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Show a tweet ",
    tags=["Tweets"]
    )
def show_a_tweet(
    tweet_id: UUID = Path(
        ...,
        example="3fa85f64-5717-4562-b3fc-2c963f66afa2",
        description="The tweet's id",

    )

):
    with open("tweets.json", "r+", encoding="utf-8") as f:
        results = json.load(f)
        id = str(tweet_id)
        for data in results:
            if data["tweet_id"] == id:
                return data
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"¡This tweet_id doesn't exist!"
            )

### Delete a tweet
@app.delete(
    path='/tweets/{tweet_id}/delete',
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Delete a tweet ",
    tags=["Tweets"]
    )
def delete_a_tweet(
    tweet_id: UUID = Path(
        ...,
        title="Tweet ID",
        description="This is the tweet ID",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa2"
    )):
    """
    Delete a Tweet

    This path operation delete a tweet in the app

    Parameters:
        - tweet_id: UUID

    Returns a json with deleted tweet data:
        - tweet_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
        - by: User
    """
    with open("tweets.json", "r+", encoding="utf-8") as f: 
        results = json.loads(f.read())
        id = str(tweet_id)
    for data in results:
        if data["tweet_id"] == id:
            results.remove(data)
            with open("tweets.json", "w", encoding="utf-8") as f:
                f.seek(0)
                f.write(json.dumps(results))
            return data
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="¡This tweet_id doesn't exist!"
        )

### Update a tweet
@app.put(
    path='/tweets/{tweet_id}/update',
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Update a tweet ",
    tags=["Tweets"]
    )
def update_tweet(
    tweet_id: UUID = Path(
        ...,
        title="Tweet ID",
        description="This is the Tweet ID",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa2"
    ),
    content: str = Form(
        ..., 
        min_length=1,
        max_length=256,
        title="Tweet content",
        description="This is the content of the tweet",
        )
  
):
    """
    This path operation show update an tweet

    Params:

    Return a json list with the updated tweet in the app with the following
    keys:
    - tweet_id : UUID
    - email : EmailStr
    - created_at: datetime 
    - updated_at: datetime
    - by: user: User
    """
    tweet_id = str(tweet_id)
    # tweet_dict = tweet.dict()
    # tweet_dict["tweet_id"] = str(tweet_dict["tweet_id"])
    # tweet_dict["birth_date"] = str(tweet_dict["birth_date"])
    with open("tweets.json", "r+", encoding="utf-8") as f: 
        results = json.loads(f.read())
        for tweet in results:
            if tweet["tweet_id"] == tweet_id:  
                tweet["content"] = content
                tweet["updated_at"] = str(datetime.now())
                print(tweet)
                with open("tweets.json", "w", encoding="utf-8") as f:
                    f.seek(0)
                    f.write(json.dumps(results))
                return tweet
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="¡This twee_id doesn't exist!"
            )

