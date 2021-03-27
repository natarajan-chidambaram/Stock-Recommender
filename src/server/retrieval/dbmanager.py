import psycopg2


def createDBConn():
    conn = psycopg2.connect("dbname=postgres user=postgres password =postgres")
    return conn
    
def createDBConnWithCursor():
    conn = psycopg2.connect("dbname=postgres user=postgres password =postgres")
    cursor = conn.cursor()
    return conn, cursor
    
def closeDBConn(conn):
    conn.close()

    
def closeDBConnAndCursor(conn, cursor):
    cursor.close()
    conn.close()