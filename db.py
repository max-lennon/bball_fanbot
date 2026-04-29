from sqlalchemy import create_engine, MetaData, Table, select, update, exists
from sqlalchemy.dialects.postgresql import insert

from typing import List
from data_structures import *
import time

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/bball_db"

engine = create_engine(DATABASE_URL, echo=True)
metadata = MetaData()

def get_table(name: str) -> Table:
    return Table(name, metadata, autoload_with=engine)

RECORD_CONFIG = {
    Comment: {"table": "comments", "conflict_cols": ["id"], "update_cols": ["upvotes"]}, # TODO: any reason to update comments?
    Game: {"table": "games", "conflict_cols": ["home", "away", "when_played"], "update_cols": ["home_score", "away_score", "game_thread", "post_thread"]}, 
    User: {"table": "users", "conflict_cols": ["id"], "update_cols": ["flair_1", "flair_2"]},
    Team: {"table": "teams", "conflict_cols": ["team_name"], "update_cols": ["wins", "losses"]},
    Player: {"table": "players", "conflict_cols": ["player_name", "team_name"], "update_cols": []},
    Post: {"table": "posts", "conflict_cols": ["id"], "update_cols": ["upvotes", "body"]},
}

def query_team_related_comments(team_name: str) -> List[Comment]:
    comments = get_table("comments")
    games = get_table("games")

    stmt = (
        select(comments)
        .join(games, ((games.c.game_thread == comments.c.game_thread) | (games.c.post_thread == comments.c.game_thread)))
        .where((games.c.home == team_name) | (games.c.away == team_name))
    )

    with engine.connect() as conn:
        start_time = time.time()
        result = conn.execute(stmt)
        end_time = time.time()
        print(f"Query time: {end_time - start_time}")
        return [Comment(**row._mapping) for row in result]

def record_exists(table_name, pk_values: dict) -> bool:
    """
    Check if a record exists using primary key values.

    Args:
        table_name: SQLAlchemy table name
        pk_values: dict mapping PK column names → values

    Example:
        record_exists(teams, {"team_name": "Duke"})
    """

    table = get_table(table_name)

    where_clause = [
        getattr(table.c, col) == val
        for col, val in pk_values.items()
    ]

    stmt = select(exists().where(*where_clause))

    with engine.connect() as conn:
        return conn.execute(stmt).scalar()

# Add a sequence of entries to the database
# Records can be any mix of Comment, Game, User, etc
# Table placement is determined by object type
def insert_pipeline(new_records: List[NamedTuple]):
    with engine.begin() as conn:
        for record in new_records:
            target_table = get_table(RECORD_CONFIG[type(record)["table"]])
            conn.execute(target_table.insert(), record._asdict())

# Add many records of the same type (e.g. Comment) at once
# Table placement is determined by object type
# NOTE: new_records MUST all belong to the same class!
def insert_batch(new_records: List[NamedTuple]):
    target_table = get_table(RECORD_CONFIG[type(new_records[0])["table"]])
    record_dicts = [record._asdict() for record in new_records]
    with engine.begin() as conn:
        conn.execute(target_table.insert(), record_dicts)

def upsert_batch(records: list[NamedTuple]) -> None:
    if not records:
        return

    record_type = type(records[0])

    if any(type(r) is not record_type for r in records):
        raise ValueError("All records in a batch must have the same type")

    if record_type not in RECORD_CONFIG:
        raise ValueError(f"No upsert config registered for record type {record_type.__name__}")

    config = RECORD_CONFIG[record_type]
    target_table: Table = get_table(config["table"])
    conflict_cols: list[str] = config["conflict_cols"]
    update_cols: list[str] = config["update_cols"]

    values = [r._asdict() for r in records]

    stmt = insert(target_table).values(values)

    stmt = stmt.on_conflict_do_update(
        index_elements=conflict_cols,
        set_={col: getattr(stmt.excluded, col) for col in update_cols},
    )

    with engine.begin() as conn:
        conn.execute(stmt)

def upsert_pipeline(records: list[NamedTuple]) -> None:
    if not records:
        return

    for record in records:
        record_type = type(record)

        if record_type not in RECORD_CONFIG:
            raise ValueError(f"No upsert config registered for record type {record_type.__name__}")
        elif record_type == Team:
            upsert_team(record)

        config = RECORD_CONFIG[record_type]
        target_table: Table = get_table(config["table"])
        conflict_cols: list[str] = config["conflict_cols"]
        update_cols: list[str] = config["update_cols"]

        values = record._asdict()

        stmt = insert(target_table).values(values)

        stmt = stmt.on_conflict_do_update(
            index_elements=conflict_cols,
            set_={col: getattr(stmt.excluded, col) for col in update_cols},
        )

        with engine.begin() as conn:
            conn.execute(stmt)


# Special upsert function for teams since win/loss totals should only be overwritten by newer data
def upsert_team(new_team: Team) -> str:
    teams = get_table("teams")
    with engine.begin() as conn:
        existing = conn.execute(
            select(teams.c.team_name, teams.c.conference, teams.c.wins, teams.c.losses)
            .where(teams.c.team_name == new_team.team_name)
        ).fetchone()

        if existing is None:
            conn.execute(
                insert(teams).values(
                    team_name=new_team.team_name,
                    conference=new_team.conference,
                    wins=new_team.wins,
                    losses=new_team.losses,
                )
            )
            return "inserted"

        needs_update = (
            existing.wins > new_team.wins
            or existing.losses > new_team.losses
        )

        if needs_update:
            conn.execute(
                update(teams)
                .where(teams.c.team_name == new_team.team_name)
                .values(
                    wins=new_team.wins,
                    losses=new_team.losses,
                )
            )
            return "updated"

        return "unchanged"