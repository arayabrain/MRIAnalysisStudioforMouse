# import logging
# from pathlib import Path
# from sqlmodel import SQLModel
# from sqlalchemy_seed import load_fixture_files, load_fixtures

# from alembic.config import main as alembic_run

# from .database import testing_engine, async_session

# BASE_DIR = str(Path(__file__).parent.absolute())


# FILE_DATA_SEEDINGS: list[str] = []
# FILE_DATA_SEEDINGS_STATIC: list[str] = []
# FILE_SHOPIFY_SEEDINGS: list[str] = []


# def create_tables():
#     """
#     Create table by definitions. Use this only when you created new table and migrations are to be made
#     """
#     SQLModel.metadata.create_all(testing_engine)


# async def reset_database():
#     """Reset an exist database. Use this only when remove all tables and re-migration."""
#     logging.info('DROPPING TABLES')
#     testing_engine.execute('SET FOREIGN_KEY_CHECKS = 0')
#     testing_engine.execute('DROP TABLE IF EXISTS alembic_version')
#     for tbl in SQLModel.metadata.tables:
#         testing_engine.execute('DROP TABLE IF EXISTS ' + tbl)
#     testing_engine.execute('SET FOREIGN_KEY_CHECKS = 1')

#     async with async_session() as session:
#         await session.flush()
#     # alembic_run(argv=['downgrade', 'base'])
#     alembic_run(argv=['upgrade', 'head'])


# def load_seedings(static_only=False):
#     """Load datas to database from yml files.

#     Args:
#         static_only (bool, optional): If set is True,
#         files from FILE_DATA_SEEDINGS_STATIC will be saved. Defaults to False.
#     """
#     logging.info('SEEDING TABLE')

#     fixture_dir = BASE_DIR + '/seeders'

#     with async_session() as session:
#         testing_engine.execute('SET FOREIGN_KEY_CHECKS = 0')
#         if static_only:
#             data_fixtures = load_fixture_files(fixture_dir, FILE_DATA_SEEDINGS_STATIC)
#             load_fixtures(session, data_fixtures)
#         else:
#             data_fixtures = load_fixture_files(fixture_dir, FILE_DATA_SEEDINGS)
#             load_fixtures(session, data_fixtures)

#             shopify_fixtures = load_fixture_files(fixture_dir, FILE_SHOPIFY_SEEDINGS)
#             load_fixtures(session, shopify_fixtures)
#         testing_engine.execute('SET FOREIGN_KEY_CHECKS = 1')
