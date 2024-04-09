from src.main import engine
from models.base import Model
from src.models.data import *

def create_db():
    Model.metadata.create_all(engine)