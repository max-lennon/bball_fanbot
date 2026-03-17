from typing import NamedTuple

class Game(NamedTuple):
    home: str
    away: str
    home_score: int
    away_score: int
    game_thread: str
    post_thread: str
    when_played: str