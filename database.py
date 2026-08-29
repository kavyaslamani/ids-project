import sqlite3

DB_NAME = "ids.db"

def create_database():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS AttackHistory (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        timestamp TEXT,

        source_ip TEXT,

        destination_ip TEXT,

        protocol TEXT,

        attack TEXT,

        anomaly INTEGER,

        reconstruction_error REAL,

        risk TEXT,

        confidence REAL
    )
    """)

    conn.commit()
    conn.close()


def insert_attack(timestamp,
                  src_ip,
                  dst_ip,
                  protocol,
                  attack,
                  anomaly,
                  reconstruction_error,
                  risk,
                  confidence):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO AttackHistory(

        timestamp,

        source_ip,

        destination_ip,

        protocol,

        attack,

        anomaly,

        reconstruction_error,

        risk,

        confidence

    )

    VALUES(?,?,?,?,?,?,?,?,?)

    """,(timestamp,
         src_ip,
         dst_ip,
         protocol,
         attack,
         anomaly,
         reconstruction_error,
         risk,
         confidence))

    conn.commit()

    conn.close()


create_database()