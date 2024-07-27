import databases
import ormar
import pytest
import sqlalchemy

DATABASE_URL = "sqlite:///test.db"


def create_config(**args):
    database_ = databases.Database(DATABASE_URL, **args)
    metadata_ = sqlalchemy.MetaData()
    engine_ = sqlalchemy.create_engine(DATABASE_URL)

    return ormar.OrmarConfig(
        metadata=metadata_,
        database=database_,
        engine=engine_,
    )


def init_tests(config, scope="module"):
    @pytest.fixture(autouse=True, scope=scope)
    def create_database():
        config.engine = sqlalchemy.create_engine(config.database.url._url)
        config.metadata.create_all(config.engine)

        yield

        config.metadata.drop_all(config.engine)

    return create_database
