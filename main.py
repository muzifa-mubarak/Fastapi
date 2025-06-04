
from fastapi import FastAPI,Body,HTTPException
from pydantic import BaseModel,Field
from typing import List
import random
import json
import requests

api=FastAPI()

data=[
    {"id":248035,"name":"Muzifa","class":"A","age":29},
    {"id":248036,"name":"Reya","class":"B","age":30},
]
class Todo(BaseModel):
    id:int
    name: str
    class_: str=Field(alias="class")
    age: int

#GET,POST,PUT,DELETE

@api.get("/")
def index():
    return {"message":"Hello World"}

@api.get("/todos/{id}")
def todo(id :int):
    for tod in data:
        #return {'result':tod['id']}
        #return id
        if tod['id']==id:
            return {'result':tod}
        
@api.get("/todos")
def todos(n_todo=None):
    if n_todo:
        return data[:n_todo]
    else:
        return data

@api.put("/todos/update-names")
def update_names_from_payload(payload: List[Todo]):
    updated = []
    for item in payload:
        name = item.name
        age=item.age
        if not name.endswith(".A"):
            name += ".A"
        age=age+5
        updated.append({
            "id": item.id,
            "name": name,
            "class": item.class_,
            "age": age
        })
    return updated
    
  
@api.post("/todos")
def create_todo(todos: list[Todo]):
    new_entries = []
    new_id = max(item["id"] for item in data) + 1

    for todo in todos:
        new_data = {
            "id": new_id,
            "name": todo.name,
            "class": todo.class_,
            "age": todo.age
        }
        data.append(new_data)
        new_entries.append(new_data)
        new_id += 1

    return new_entries

@api.get("/movie-recommendation/{genre}")
def movie_rec(genre: str):
    with open("movie.json",'r') as file:
        movies=json.load(file)
    movie_list = [movie for movie in movies if movie["genre"].lower() == genre.lower()]
    
    if not movie_list:
        return [{
            "status": "error",
            "status_code": 400,
            "message": f"No movies found for genre '{genre}'"
        }]

    valid_movies = [m for m in movie_list if m.get("name")]
    invalid_count = len(movie_list) - len(valid_movies)

    selected_movies = random.sample(valid_movies, 1)

    response = {
        "status": "success" if valid_movies else "warning",
        "status_code": 200 if valid_movies else 206,
        "message": f"{len(selected_movies)} movie(s) found for genre '{genre}'" +
                   (f", but {invalid_count} movie(s) had missing names" if invalid_count else ""),
        "data": selected_movies
    }

    return [response]

@api.get("/movie-recommendations/{genre}")
def movie_rec(genre: str):
    url = f"https://moviesminidatabase.p.rapidapi.com/movie/byGen/{genre}/"

    headers = {
        "x-rapidapi-key": "82788a0a25msh329cac9065e5b52p1a5eb3jsn5f03143bd526",
        "x-rapidapi-host": "moviesminidatabase.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    data=response.json()
    movie_list=[dat for dat in data.get("results",[])]
    
    if not movie_list:
        return [{
            "status": "error",
            "status_code": 400,
            "message": f"No movies found for genre '{genre}'"
        }]

    valid_movies = [m for m in movie_list if m.get("title")]
    invalid_count = len(movie_list) - len(valid_movies)

    selected_movies = random.sample(valid_movies, 1)

    response = {
        "status": "success" if valid_movies else "warning",
        "status_code": 200 if valid_movies else 206,
        "message": f"{len(selected_movies)} movie(s) found for genre '{genre}'" +
                   (f", but {invalid_count} movie(s) had missing names" if invalid_count else ""),
        "data": selected_movies
    }

    return response



    
        
    

    



