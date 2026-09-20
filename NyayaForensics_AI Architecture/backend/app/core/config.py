from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
 app_name:str='NyayaForensics AI'; database_url:str='sqlite:///./nyaya.db'; redis_url:str='redis://localhost:6379/0'; neo4j_uri:str='bolt://localhost:7687'; neo4j_user:str='neo4j'; neo4j_password:str='nyaya_password'; upload_dir:str='./storage/evidence'; jwt_secret:str='change-me'
 model_config=SettingsConfigDict(env_file='.env',extra='ignore')
settings=Settings()
