# app/db/base.py

# 1. Import the foundation (The Concrete Slab)
from app.db.base_class import Base  # noqa

# 2. Import every model (The Blueprints) to register them with the Metadata

from app.models.user import User  
from app.models.question import Subject, Question, question_subjects 
from app.models.interview import InterviewSession, InterviewQuestion, Answer

# After these imports, Base.metadata now contains the 
# definitions for all 7 of your tables.