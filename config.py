    # config.py
import os
from dotenv import load_dotenv

_ = load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    MODEL_NAME = 'llama3-8b-8192'  
    EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

config = Config()
