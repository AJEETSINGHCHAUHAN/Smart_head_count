import mysql.connector

def init_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="ajeet"
    )
    cursor = conn.cursor()

    with open('schema.sql', 'r') as f:
        sql = f.read()
        for statement in sql.split(';'):
            if statement.strip():
                cursor.execute(statement)

    conn.commit()
    conn.close()
