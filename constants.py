import environ
env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env()
SPORTS_API_KEY=env('SPORTS_API_KEY')
