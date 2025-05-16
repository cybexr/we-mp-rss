from  .base import Base,Column,String,Integer,DateTime
class Article(Base):
    __tablename__ = 'articles'
    id = Column(String(255), primary_key=True)
    mp_id = Column(String(255))
    title = Column(String(500))
    pic_url = Column(String(500))
    publish_time = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)  # Changed from Integer to DateTime for consistency
    is_export = Column(Integer)


