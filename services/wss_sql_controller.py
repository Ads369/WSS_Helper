from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Numeric, Strin
from sqlalchemy import ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import yaml

# Get security data
with open(r"config/config.yaml", encoding="utf8") as f:
    config = yaml.safe_load(f)


def get_engine():
    # Definite consatans
    servername = config["work_db"]["server"]
    dbname = config["work_db"]["db_prime"]

    # Create engine and connect
    engine = create_engine(
        f"mssql+pyodbc://{servername}/{dbname}"
        "?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"
    )
    return engine


def connect_sqla_core(engine):
    connection = engine.connect()
    print(connection)

    # generate MetaData and download Tables from SQL server
    metadata = MetaData()
    con_ais = Table(
        "_list_dms__ContractsAIS_869_bk", metadata, autoload=True, autoload_with=engine
    )
    print(con_ais.columns.keys())


def connect_sql_orm(base, engine):
    # Base.metadata.create_all(engine)
    pass


def main():
    engine = get_engine()
    Base = declarative_base()

    Session = sessionmaker(bind=engine)
    session = Session()

    # connect_sqla_core(engine)

    connect_sql_orm(Base, engine)


if __name__ == "__main__":
    main()
