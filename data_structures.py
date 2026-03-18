from typing import NamedTuple

class Game(NamedTuple):
    home: str
    away: str
    home_score: int
    away_score: int
    game_thread: str
    post_thread: str
    when_played: str

class Comment(NamedTuple):
    id: str
    author: str
    post_id: str
    parent_id: str
    body: str
    upvotes: int
    created_at: str

class User(NamedTuple):
    id: str
    username: str
    flair_1: str
    flair_2: str
    created_at: str

class Post(NamedTuple):
    id: str
    title: str
    body: str
    user_id: str
    category: str
    upvotes: int
    created_at: str

class Comment(NamedTuple):
    id: str
    author: str
    post_id: str
    parent_id: str
    body: str
    upvotes: int
    created_at: str

class Team(NamedTuple):
    team_name: str
    conference: str
    wins: int
    losses: int

class Player(NamedTuple):
    player_name: str
    team_name: str