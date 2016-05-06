import os

HERE = os.path.dirname(__file__)
DATASET_DATABASE_URI = 'sqlite:///' + os.path.join(HERE, 'data', 'interviews.db')

# If set, pull tags only from those scorecard questions that match this pattern.
TAGS_QUESTION_RE = None # r'^What was the question'
# If set, pull tags only from those lines that start with this string.
TAGS_PREFIX = 'tags:'

# If set, adds basic auth at the Flask level.
BASIC_AUTH_USERNAME = None
BASIC_AUTH_PASSWORD = None
