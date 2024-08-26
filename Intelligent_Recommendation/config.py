import os

class Config:
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_USER = os.getenv('DATABASE_USER', 'root')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', '')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'Badminton_Raptor_Store')
