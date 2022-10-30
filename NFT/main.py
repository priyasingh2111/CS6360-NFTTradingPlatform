from flask import Flask, request, render_template, redirect, url_for, session, flash
import mysql.connector as con
from connector import cursor, db
import random
import string

app = Flask(__name__)
app.secret_key = "key"


# login page
@app.route('/', methods=['GET', 'POST'])
def index():
    # if user enters the username & password
    if request.method == "POST":
        # get the username and password
        login_name = request.form['login_name']
        password = request.form['password']

        sql = f"SELECT * FROM Trader Where login = %s AND password = %s"
        try:
            # execute query
            cursor.execute(sql, (login_name, password))
            result = cursor.fetchall()
            # if there exist a user in DB
            if len(result) > 0:
                # set user session = user_id
                # redirect to home page
                session["user_id"] = result[0][0]
                session["user_name"] = result[0][8]
                return redirect(url_for("home"))
            else:
                # no such user in DB
                flash("Wrong Username or Password", "info")
                return render_template('login.html')
        except con.Error as err:
            # query error
            print(err.msg)

    else:
        # if user already login
        if "user_id" in session:
            redirect(url_for("home"))
        # stay in login page
        return render_template('login.html')


# signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        # get the user info
        first_name = request.form['first_name'].upper()
        last_name = request.form['last_name'].upper()
        phone_number = request.form['phone_number']
        cell_phone_number = request.form['cell_phone_number']
        email = request.form['email']
        login_name = request.form['login_name']
        password = request.form['password']
        street = request.form['street'].upper()
        city = request.form['city'].upper()
        state = request.form['state'].upper()
        zip_code = request.form['zip_code']

        # generate random eth_address & client_id
        lst = [random.choice(string.ascii_letters + string.digits) for _ in range(42)]
        eth_address = "".join(lst)
        client_id = random.randrange(10000, 99999)

        trader_sql = f"INSERT INTO Trader (client_id, ethereum_address, street, first_name, last_name, phone_no, " \
                     f"cell_no, email, login, password, level,fiat_balance, ethereum_balance) VALUES " \
                     f"(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "

        address_insert_sql = "INSERT INTO Address(street, city, state, zip_code) VALUES (%s,%s,%s,%s)"
        address_search_sql = f"SELECT * FROM Address Where Street = %s"

        try:
            # address table primary key constraint
            cursor.execute(address_search_sql, (street,))
            result = cursor.fetchall()
            # if there does not exist such street in DB
            if len(result) == 0:
                cursor.execute(address_insert_sql, (street, city, state, zip_code))
                db.commit()

            # insert new trader
            cursor.execute(trader_sql, (client_id, eth_address, street, first_name, last_name, phone_number,
                                        cell_phone_number, email, login_name, password, 'D', 0.0, 0.0))
            db.commit()
            return render_template('login.html')

        except con.Error as err:
            print(err.msg)
            # Duplicate username
            flash("Username already taken", "error")
            return render_template('signup.html')

    else:
        return render_template('signup.html')


# home page
@app.route('/home', methods=['GET', 'POST'])
def home():
    if "user_id" in session:
        user_id = session["user_id"]
        return render_template('home.html', content=user_id)
    else:
        return redirect(url_for("index"))


# user profile
@app.route('/profile')
def profile():
    user_id = session["user_id"]

    # querys
    trader_sql = f"SELECT * FROM Trader Where client_id = %s"
    address_sql = f"SELECT * FROM Address Where street = %s"

    try:
        # fetch user info
        cursor.execute(trader_sql, (user_id,))
        trader_result = cursor.fetchall()

        # fetch address info
        user_street = trader_result[0][2]
        cursor.execute(address_sql, (user_street,))
        address_result = cursor.fetchall()

        # if there exist a user who lives in certain address
        if len(trader_result) > 0 and len(address_result) > 0:
            return render_template('profile.html', trader_detail=trader_result, address_detail=address_result)

    except con.Error as err:
        # query error
        print(err.msg)
    return render_template('profile.html')


# logout
@app.route("/logout")
def logout():
    if "user_name" in session:
        user_name = session["user_name"]
        flash(f"You have been logged out, {user_name}", "info")
    session.pop("user_id", None)
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True)
