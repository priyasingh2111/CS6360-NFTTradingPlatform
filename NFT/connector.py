import mysql.connector

# connect to mysql
db = mysql.connector.connect(
    user="Li",
    password="26285194",
    host="cs4347.c3bw7ao2sqoy.us-west-2.rds.amazonaws.com",
    database="temp"
)

cursor = db.cursor()


'''
testing 

sql = f"SELECT * FROM Trader"

cursor.execute(sql)
result = cursor.fetchall()
print(result[0][0])
'''




