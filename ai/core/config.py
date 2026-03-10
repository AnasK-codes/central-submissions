from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")
SECRET_KEY=os.getenv("SECRET_KEY")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
PINECONE_API_KEY=os.getenv("PINECONE_API_KEY")
ALGORITHM="HS256"



