from fastapi import FastAPI, HTTPException,Body,Path
from pydantic import BaseModel
import psycopg2
from typing import List


app = FastAPI()

class Movie(BaseModel):
    movie_id:int
    genre: str
    movie_name: str
    rating: float

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        dbname="postgres",       
        user="postgres",
        password="1234",       
        port="5433"
    )

@app.post("/add-movies")
def add_movies(movies: List[Movie]): 
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for movie in movies:
            cursor.execute(
                "INSERT INTO movies (genre, movie_name, rating) VALUES (%s, %s, %s)",
                (movie.genre, movie.movie_name, movie.rating)
            )
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Movies added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@app.get("/movies/{genre}")
def get_movies(genre:str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE genre = %s", (genre,))
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    if not rows:
        return [{
            "status": "error",
            "status_code": 400,
            "message": f"No movies found for genre '{genre}'"
        }]

    result = [dict(zip(col_names, row)) for row in rows]
    return {"movies": result}

@app.get("/movies")
def get_movies():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("Select * from movies")
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    result = [dict(zip(col_names, row)) for row in rows]
    return {"movies": result}


@app.put("/movies-nameupdate")
def update_movie(movie: Movie = Body(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE movies
        SET genre = %s, movie_name = %s, rating = %s
        WHERE movie_id = %s
        RETURNING movie_id, genre, movie_name, rating
        """,
        (movie.genre, movie.movie_name, movie.rating,movie.movie_id)
    )

    updated_row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if updated_row:
        return {
            "status": "success",
            "status_code": 200,
            "updated_record": {
                "movie_id": updated_row[0],
                "genre": updated_row[1],
                "movie_name": updated_row[2],
                "rating": updated_row[3]
            }
        }
    else:
        return {
            "status": "error",
            "status_code": 404,
            "message": f"No movie found with id {movie.movie_id}"
        }

@app.delete("/delete-movie/{movie_id}")
def delete_movies(movie_id:int):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("Delete from movies where movie_id=%s RETURNING *",(movie_id,))
    deleted=cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    if deleted:
       return {
            "status":"sucess",
            "status code":200,
            "movie id":movie_id,
            "deleted record":"record is deleted sucessfully"
        }
    else:
        return{
            "status":"error",
            "status code":400,
            "deleted record":"record does not exist "
        }
    
@app.get("/movie-reccom/{genre}")
def movie_reccom(genre: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM movies WHERE genre = %s ORDER BY RANDOM() LIMIT 3", 
            (genre,)
        )
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        result = [dict(zip(col_names, row)) for row in rows]
        cursor.close()
        conn.close()

        if result:
            return {
                'status':"sucess",
                "status code":200,
                "movies":result
            }

        if not result:
            return {
                'status':"error",
                "status code":404,
                "movies":"No movies found for the genre"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        