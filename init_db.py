import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

# No need for a separate cursor in this case

connection.commit()

connection.close()
