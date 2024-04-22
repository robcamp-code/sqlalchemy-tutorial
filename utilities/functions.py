from main import engine
from models import Model
from schema.schema import *

def create_db():
    Model.metadata.create_all(engine)