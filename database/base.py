# database/base.py

# 1. Import the foundation (The Concrete Slab)
from database.base_class import Base  # noqa

# 2. Import every model (The Blueprints) to register them with the Metadata
from database.models.user_model import User  # noqa
from database.models.question_model import Subject, Question, question_subjects  # noqa
from database.models.interview_model import InterviewSession, InterviewQuestion, Answer  # noqa

# After these imports, Base.metadata now contains the
# definitions for all 7 of your tables.
