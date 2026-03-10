from sqlalchemy import create_engine, MetaData, Table

DATABASE_URL = "postgresql+psycopg://max:postgres@localhost:5432/bball_db"

engine = create_engine(DATABASE_URL, echo=True)
metadata = MetaData()

def get_table(name: str) -> Table:
    return Table(name, metadata, autoload_with=engine)