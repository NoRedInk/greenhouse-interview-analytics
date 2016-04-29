import os

HERE = os.path.dirname(__file__)
DATASET_DATABASE_URI = 'sqlite:///' + os.path.join(HERE, 'data', 'interviews.db')
