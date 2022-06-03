import logging

from arango import ArangoClient


logger = logging.getLogger(__name__)
client = ArangoClient(hosts="http://arangodb:8529")
db = client.db("IMDB", username="root", password="password")


def get_genres(search: str, limit: int):
    query = """
        FOR v IN imdb_vertices
            FILTER v.type == "Genre"
            FILTER @search ? CONTAINS(LOWER(v.label), LOWER(@search), false) : true
            SORT v.label
            LIMIT @limit
            RETURN { _key: v._key, name: v.label }
    """
    return _get_list(query, search, limit)


def get_genre(key: str):
    query = """
        FOR v IN imdb_vertices
            FILTER v._id == @id
            LET movies = (
                FOR v2, edge IN 1..1 ANY v imdb_edges
                    FILTER v2.type == "Movie" AND edge.$label == "has_movie"
                    SORT v2.title
                    RETURN { _key: v2._key, title: v2.title }
            )
            RETURN {
                genre: MERGE(v,
                {
                    movies_num: LENGTH(movies)
                }),
                movies: movies
            }
    """
    return _get_object(query, key)


def get_movies(search: str, limit: int):
    query = """
        FOR v IN imdb_vertices
            FILTER v.type == "Movie"
            FILTER @search ? CONTAINS(LOWER(v.label), LOWER(@search), false) : true
            SORT v.title
            LIMIT @limit
            RETURN { _key: v._key, title: v.title }
    """
    return _get_list(query, search, limit)


def get_movie(key: str):
    query = """
        FOR v IN imdb_vertices
            FILTER v._id == @id
            LET actors = (
                FOR v2, edge IN 1..1 INBOUND v imdb_edges
                    FILTER v2.type == "Person" AND edge.$label == "ACTS_IN"
                    SORT v2.name
                    RETURN { _key: v2._key, name: v2.name }
            )
            LET directors = (
                FOR v2, edge IN 1..1 INBOUND v imdb_edges
                    FILTER v2.type == "Person" AND edge.$label == "DIRECTED"
                    SORT v2.name
                    RETURN { _key: v2._key, name: v2.name }
            )
            LET genres = (
                FOR v2, edge IN 1..1 INBOUND v imdb_edges
                    FILTER v2.type == "Genre" AND edge.$label == "has_movie"
                    SORT v2.label
                    RETURN { _key: v2._key, name: v2.label }
            )
            RETURN {
                movie: MERGE(v,
                {
                    actors_num: LENGTH(actors),
                    directors_num: LENGTH(directors),
                    genres_num: LENGTH(genres),
                }),
                actors: actors,
                directors: directors,
                genres: genres
            }
    """
    return _get_object(query, key)


def get_directors(search: str, limit: int):
    query = """
        FOR v IN imdb_vertices
            FILTER v.type == "Person"
            FILTER @search ? CONTAINS(LOWER(v.label), LOWER(@search), false) : true
            LET edges = (
                FOR e IN imdb_edges
                    FILTER CONTAINS(e.$label, "DIRECTED", false)
                    FILTER e._from == v._id
                    RETURN 1
            )
            FILTER LENGTH(edges) > 1
            SORT v.label
            LIMIT @limit
            RETURN { _key: v._key, name: v.label }
    """
    return _get_list(query, search, limit)


def get_director(key: str):
    query = """
        LET director = FIRST(
            FOR v IN imdb_vertices
                FILTER v._id == @id
                RETURN v
        )

        LET direct_movies = (
            FOR v, e IN 1..1 ANY Document(director._id) imdb_edges
                FILTER e._from == director._id AND e.$label == "DIRECTED"
                return { _id: v._id, title: v.title }
        )

        LET direct_genres = (
            FOR movie in direct_movies
                FOR v, e IN 1..1 ANY movie imdb_edges
                    FILTER e.$label == "has_movie"
                    RETURN DISTINCT { _id: v._id, label: v.label }
        )

        LET direct_actors = (
            FOR movie in direct_movies
                FOR v, e IN 1..1 ANY movie imdb_edges
                    FILTER e.$label == "ACTS_IN"
                    RETURN DISTINCT { _id: v._id, label: v.label }
        )

        LET acts_in_movies = (
            FOR v, e IN 1..1 ANY Document(director._id) imdb_edges
                FILTER e._from == director._id AND e.$label == "ACTS_IN"
                return { _id: v._id, title: v.title }
        )

        LET acts_in_genres = (
            FOR movie in acts_in_movies
                FOR v, e IN 1..1 ANY movie imdb_edges
                    FILTER e.$label == "has_movie"
                    RETURN DISTINCT { _id: v._id, label: v.label }
        )

        LET acts_with_actors = (
            FOR movie in acts_in_movies
                FOR v, e IN 1..1 ANY movie imdb_edges
                    FILTER e.$label == "ACTS_IN"
                    RETURN DISTINCT { _id: v._id, label: v.label }
        )

        RETURN {
            director: MERGE(
                director,
                {
                    direct_genres_num: LENGTH(direct_genres),
                    direct_movies_num: LENGTH(direct_movies),
                    direct_actors_num: LENGTH(direct_actors),
                    acts_in_genres_num: LENGTH(acts_in_genres),
                    acts_in_movies_num: LENGTH(acts_in_movies),
                    acts_with_actors_num: LENGTH(acts_with_actors)
                }
            ),
            direct_genres: direct_genres,
            direct_actors: direct_actors,
            direct_movies: direct_movies,
            acts_in_genres: acts_in_genres,
            acts_in_movies: acts_in_movies,
            acts_with_actors: acts_with_actors
        }
    """
    return _get_object(query, key)


def get_actors(search: str, limit: int):
    query = """
        FOR v IN imdb_vertices
            FILTER v.type == "Person"
            FILTER @search ? CONTAINS(LOWER(v.label), LOWER(@search), false) : true
            LET edges = (
                FOR e IN imdb_edges
                    FILTER CONTAINS(e.$label, "ACTS_IN", false)
                    FILTER e._from == v._id
                    RETURN 1
            )
            FILTER LENGTH(edges) > 1
            SORT v.label
            LIMIT @limit
            RETURN { _key: v._key, name: v.label }
    """
    return _get_list(query, search, limit)


def get_actor(key: str):
    query = """
        LET actor = FIRST(
            FOR v IN imdb_vertices
                FILTER v._id == @id
                RETURN v
        )

        LET acts_in_movies = (
            FOR v, e IN 1..1 ANY Document(actor._id) imdb_edges
                FILTER e._from == actor._id AND e.$label == "ACTS_IN"
                return { _id: v._id, title: v.title }
        )

        LET acts_in_genres = (
            FOR movie in acts_in_movies
                FOR v, e IN 1..1 ANY movie imdb_edges
                    FILTER e.$label == "has_movie"
                    RETURN DISTINCT { _id: v._id, label: v.label }
        )

        LET acts_with_actors = (
            FOR movie in acts_in_movies
                FOR v, e IN 1..1 ANY movie imdb_edges
                    FILTER e.$label == "ACTS_IN"
                    RETURN DISTINCT { _id: v._id, label: v.label }
        )

        LET acts_with_directors = (
            FOR movie in acts_in_movies
                FOR v, e IN 1..1 ANY movie imdb_edges
                    FILTER e.$label == "DIRECTED"
                    RETURN DISTINCT { _id: v._id, label: v.label }
        )

        RETURN {
            actor: MERGE(
                actor,
                {
                    acts_in_genres_num: LENGTH(acts_in_genres),
                    acts_in_movies_num: LENGTH(acts_in_movies),
                    acts_with_actors_num: LENGTH(acts_with_actors),
                    acts_with_directors_num: LENGTH(acts_with_directors)
                }
            ),
            acts_in_genres: acts_in_genres,
            acts_in_movies: acts_in_movies,
            acts_with_actors: acts_with_actors,
            acts_with_directors: acts_with_directors
        }
    """
    return _get_object(query, key)


def _log(cursor):
    logger.info(f"Query statistics {cursor.statistics()!r}" )


def _get_list(query: str, search: str, limit: int):
    vars = {'limit': limit, 'search': search}
    cursor = db.aql.execute(query, bind_vars=vars, count=True)
    _log(cursor)
    return { "count": cursor.count(), "data": list(cursor) }


def _get_object(query: str, key: str):
    vars = {'id': f"imdb_vertices/{key}"}
    cursor = db.aql.execute(query, bind_vars=vars)
    _log(cursor)
    return cursor.next()
