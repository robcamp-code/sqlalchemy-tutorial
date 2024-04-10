from src.main import engine
from src.models.base import Model
from src.models.schema import *

def create_db():
    Model.metadata.create_all(engine)