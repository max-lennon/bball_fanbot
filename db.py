from sqlalchemy import create_engine, MetaData, Table

from typing import List
from data_structures import *

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/bball_db"

engine = create_engine(DATABASE_URL, echo=True)
metadata = MetaData()

def get_table(name: str) -> Table:
    return Table(name, metadata, autoload_with=engine)

class_table_map = {
    Comment: "comments",
    Game: "games",
    User: "users",
    Team: "teams",
    Player: "players",
    Post: "posts",
}

# Add a sequence of entries to the database
# Records can be any mix of Comment, Game, User, etc
# Table placement is determined by object type
def insert_pipeline(new_records: List[NamedTuple]):
    with engine.begin() as conn:
        for record in new_records:
            target_table = get_table(class_table_map[type(record)])
            conn.execute(target_table.insert(), record._asdict())

# Add many records of the same type (e.g. Comment) at once
# Table placement is determined by object type
# NOTE: new_records MUST all belong to the same class!
def insert_batch(new_records: List[NamedTuple]):
    target_table = get_table(class_table_map[type(new_records[0])])
    record_dicts = [record._asdict() for record in new_records]
    with engine.begin() as conn:
        conn.execute(target_table.insert(), record_dicts)