import mysql.connector

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "spcatrs"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def save_students(records):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO student (FirstName, LastName, Absences, Quizzes, Exam, Activities, Subject, Section, UID)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(sql, records)
    conn.commit()
    cursor.close()
    conn.close()

def get_all_students(uid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT FirstName, LastName, Absences, Quizzes, Exam, Activities, Subject, Section FROM student WHERE UID=%s",
        (uid,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def update_student(uid, original_first, original_last, new_data):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        UPDATE student
        SET FirstName=%s, LastName=%s, Subject=%s, Section=%s,
            Absences=%s, Quizzes=%s, Exam=%s, Activities=%s
        WHERE UID=%s AND FirstName=%s AND LastName=%s
        LIMIT 1
    """
    cursor.execute(sql, (
        new_data["first_name"], new_data["last_name"],
        new_data.get("subject", ""), new_data.get("section", ""),
        new_data["absences"], new_data["quizzes"],
        new_data["exam"], new_data["activities"],
        uid, original_first, original_last
    ))
    conn.commit()
    cursor.close()
    conn.close()

def delete_student(uid, row_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student WHERE UID=%s AND id=%s", (uid, row_id))
    conn.commit()
    cursor.close()
    conn.close()