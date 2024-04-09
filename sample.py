import sys
from src.main import create_engine, engine
from src.models.base import Model
from src.queries.querying import run_queries

run_queries()
# print(Model.metadata)
# print(sys.path)
