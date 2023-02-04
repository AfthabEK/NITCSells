import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute("SELECT * FROM requests")
requests = c.fetchall()
print(requests)