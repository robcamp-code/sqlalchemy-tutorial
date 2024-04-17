from main import engine
from models.base import Model
from models.schema import *

def create_db():
    Model.metadata.create_all(engine)