from sqlalchemy import create_engine, Column, Integer, String, DateTime

from sqlalchemy.orm import sessionmaker
from typing import Optional, List
from .models import Feed,Article

class Db:
    def __init__(self):
        self.session: Optional[sessionmaker] = None
        
    def init(self, con_str: str) -> None:
        """Initialize database connection
        
        Args:
            con_str: Database connection string
            
        Raises:
            Exception: If connection fails
        """
        try:
            engine = create_engine(con_str)
            Session = sessionmaker(bind=engine)
            self.session = Session()
        except Exception as e:
            print(f"Error creating database connection: {e}")
            
    def close(self) -> None:
        """Close the database connection"""
        if self.session:
            self.session.close()
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
            
    def add_article(self, article_data: dict) -> bool:
        try:
            art = Article(**article_data)
            self.session.add(art) 
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Failed to add article: {e}")
            return False
        return True    
    def get_articles(self,id:str=None,limit:int=30,offset:int=0) -> List[Article]:
         try:
            #  data=self.session.query(Feed).filter_by(id=id).limit(10)
             data=self.session.query(Article).limit(limit).offset(offset)
             return data
         except Exception as e:
             print(f"Failed to fetch Feed: {e}")
             return e    
             
    def get_all_mps(self) -> List[Feed]:
         """Get all Feed records"""
         try:
             return self.session.query(Feed).all()
         except Exception as e:
             print(f"Failed to fetch Feed: {e}")
             return e
    def get_mps(self,mp_id:str)->Optional[Feed]:
         try:
             data=self.session.query(Feed).filter_by(id=mp_id).first()
            #  return type(data)
             return  data
         except Exception as e:
             print(f"Failed to fetch Feed: {e}")
             return e

    def get_faker_id(self,mp_id:str):
        data= self.get_mps(mp_id)
        return data.faker_id
        
    def get_session(self):
        """获取数据库会话"""
        if not self.session:
            raise Exception("Database not initialized")
        return self.session

DB=Db()
from .config import config as cfg
DB.init(cfg.get("db"))