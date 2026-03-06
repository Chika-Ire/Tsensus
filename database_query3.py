import sqlite3
import os

DB_PATH = "你自己创一个.db"

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"找不到数据库文件: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

def query_courses(search_params):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 使用 JOIN 关联教师表，以获取教师姓名用于模糊匹配和结果展示
    sql = """
        SELECT e.*, t.name as teacher_name 
        FROM evaluations e 
        JOIN teachers t ON e.teacher_id = t.teacher_id 
        WHERE 1=1
    """
    args = []

    if search_params.get('teacher_name'):
        sql += " AND t.name LIKE ?"
        args.append(f"%{search_params['teacher_name']}%")

    try:
        cursor.execute(sql, args)
        rows = cursor.fetchall() 
        return [dict(row) for row in rows]
    finally:
        conn.close()