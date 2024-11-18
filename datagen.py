import sqlite3
conn = sqlite3.connect('database2.db')

c = conn.cursor()

c.execute("""CREATE TABLE BookingInfo (
          BookingID integer PRIMARY KEY,
            Username text NOT NULL,
            BookingDate text NOT NULL,
          Subject text NOT NULL
          )""")
conn.commit()

conn.close()
