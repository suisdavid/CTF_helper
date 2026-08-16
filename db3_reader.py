import sqlite3
conn = sqlite3.connect('mystery_message_0.db3')
cursor = conn.cursor()
cursor.execute('SELECT * FROM topics')
rows = cursor.fetchall()
for row in rows:
   print(row)
conn.close()
