import logging

from fastapi import FastAPI

import queries

app = FastAPI()

logger = logging.getLogger()
logger.setLevel("INFO")

stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


@app.get("/")
def root():
    return {"message": "API is working"}


@app.get("/genres", tags=["Genres"])
def genres(search: str = "", limit: int = 10):
    return queries.get_genres(search, limit)


@app.get("/genres/{genre_key}", tags=["Genres"])
def genre(genre_key: str):
    return queries.get_genre(genre_key)


@app.get("/movies", tags=["Movie"])
def movies(search: str = "", limit: int = 10):
    return queries.get_movies(search, limit)


@app.get("/movies/{movie_key}", tags=["Movie"])
def movie(movie_key: str):
    return queries.get_movie(movie_key)


@app.get("/dicrectors", tags=["Directors"])
def dicrectors(search: str = "", limit: int = 10):
    return queries.get_directors(search, limit)


@app.get("/dicrectors/{dicrector_key}", tags=["Directors"])
def dicrector(dicrector_key: str):
    return queries.get_director(dicrector_key)


@app.get("/actors", tags=["Actors"])
def actors(search: str = "", limit: int = 10):
    return queries.get_actors(search, limit)


@app.get("/actors/{actor_key}", tags=["Actors"])
def actor(actor_key: str):
    return queries.get_actor(actor_key)
