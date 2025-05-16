from core.db import DB
from core.models import User
from datetime import datetime
from sqlalchemy import text

def upgrade():
    session = DB.get_session()
    try:
        # 检查表是否存在
        table_exists = session.execute(
            text("SHOW TABLES LIKE 'users'")
        ).fetchone()
        
        if not table_exists:
            # 创建新表
            session.execute(text("""
            CREATE TABLE users (
                id VARCHAR(255) PRIMARY KEY,
                username VARCHAR(50) UNIQUE,
                password_hash VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                role VARCHAR(20) DEFAULT 'user',
                permissions JSON,
                mp_name VARCHAR(255),
                mp_cover VARCHAR(255),
                mp_intro VARCHAR(255),
                status INTEGER,
                sync_time DATETIME,
                update_time DATETIME,
                created_at DATETIME,
                updated_at DATETIME,
                faker_id VARCHAR(255)
            )
            """))
        else:
            # 检查并添加缺失的列
            columns = session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'users'
            """)).fetchall()
            existing_columns = {c[0] for c in columns}
            
            if 'username' not in existing_columns:
                session.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN username VARCHAR(50) UNIQUE
                """))
            
            if 'password_hash' not in existing_columns:
                session.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN password_hash VARCHAR(255)
                """))
                
            if 'is_active' not in existing_columns:
                session.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN is_active BOOLEAN DEFAULT TRUE
                """))
                
            if 'role' not in existing_columns:
                session.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN role VARCHAR(20) DEFAULT 'user'
                """))
                
            if 'permissions' not in existing_columns:
                session.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN permissions JSON
                """))
        
        # 创建默认管理员账户
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        from uuid import uuid4
        admin = User(
            id=str(uuid4()),
            username="admin",
            password_hash=pwd_context.hash("admin123"),
            is_active=True,
            role="admin",
            permissions=["*"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(admin)
        session.commit()
    finally:
        session.close()

def downgrade():
    session = DB.get_session()
    try:
        session.execute("""
        ALTER TABLE users 
        DROP COLUMN username,
        DROP COLUMN password_hash,
        DROP COLUMN is_active,
        DROP COLUMN role,
        DROP COLUMN permissions
        """)
        session.commit()
    finally:
        session.close()

if __name__ == "__main__":
    upgrade()