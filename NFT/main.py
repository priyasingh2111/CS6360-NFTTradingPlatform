from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
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

        sql = f"SELECT T.login, T.client_id FROM Trader T, User U WHERE T.login = U.login AND T.login = %s AND " \
              f"U.password = %s "
        try:
            # execute query
            cursor.execute(sql, (login_name, password))
            result = cursor.fetchall()
            # if there exist such user in DB
            if len(result) > 0:
                # set user session = user_id
                # redirect to home page
                session["user_id"] = result[0][1]
                session["user_name"] = result[0][0]
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


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # if Manager enters the login & password
    if request.method == "POST":
        # get the login and password
        login_name = request.form['login_name']
        password = request.form['password']

        sql = f"SELECT M.login, M.manager_id FROM Manager M, User U WHERE M.login = U.login AND M.login = %s AND " \
              f"U.password = %s "
        try:
            # execute query
            cursor.execute(sql, (login_name, password))
            result = cursor.fetchall()
            # if there exist such Manager in DB
            if len(result) > 0:
                # set Manager session = Manager_id
                # redirect to Dashboard
                session["manager_id"] = result[0][1]
                print(result[0][1])
                session["manager_id_name"] = result[0][0]
                return redirect(url_for("home"))
            else:
                # no such user in DB
                flash("Wrong Login or Password", "info")
                return render_template('admin_login.html')
        except con.Error as err:
            # query error
            print(err.msg)

    else:
        # if Manager already login
        if "manager_id" in session:
            redirect(url_for("home"))

        # stay in login page
        return render_template('admin_login.html')


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
        lst = [random.choice(string.ascii_letters + string.digits)
                             for _ in range(42)]
        eth_address = "".join(lst)
        client_id = random.randrange(10000, 99999)

        User_sql = "INSERT INTO User (login, password) VALUES (%s,%s)"

        trader_sql = f"INSERT INTO Trader (client_id, ethereum_address, first_name, last_name, phone_no, cell_no, " \
                     f"email, street_address, zip_code, login, level,fiat_balance, ethereum_balance) VALUES " \
                     f"(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "

        address_sql = "INSERT INTO Address(street_address, city, state, zip_code) VALUES (%s,%s,%s,%s)"
        address_search_sql = f"SELECT * FROM Address Where street_address = %s AND zip_code = %s"

        try:
            # insert into user table
            cursor.execute(User_sql, (login_name, password))
            db.commit()

            # address table primary key constraint
            # multiple user can live in same address
            cursor.execute(address_search_sql, (street, zip_code))
            print("error")
            result = cursor.fetchall()

            # if there does not exist such street in DB
            if len(result) == 0:
                cursor.execute(address_sql, (street, city, state, zip_code))
                db.commit()

            # insert new trader
            cursor.execute(trader_sql, (client_id, eth_address, first_name, last_name, phone_number, cell_phone_number,
                                        email, street, zip_code, login_name, 'D', 0.0, 0.0))
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
    user_name = session["user_name"]

    # query
    trader_sql = f"SELECT * FROM  Trader T , User U WHERE T.login = U.login AND U.login = %s AND T.client_id = %s"
    address_sql = f"SELECT * FROM Address Where street_address = %s AND zip_code = %s"

    try:
        # fetch user info
        cursor.execute(trader_sql, (user_name, user_id))
        trader_result = cursor.fetchall()

        # fetch address info
        street = trader_result[0][7]
        zip_code = trader_result[0][8]
        cursor.execute(address_sql, (street, zip_code))
        address_result = cursor.fetchall()

        # if there exist a user who lives in certain address
        if len(trader_result) > 0 and len(address_result) > 0:
            return render_template('profile.html', trader_detail=trader_result, address_detail=address_result)

    except con.Error as err:
        # query error
        print(err.msg)
    return render_template('profile.html')


# edit user info
@app.route('/edit_user_info', methods=['GET', 'POST'])
def edit_user_info():
    if request.method == "POST":

        user_id = session["user_id"]

        first_name = request.form['first_name'].upper()
        last_name = request.form['last_name'].upper()
        phone_number = request.form['phone_number']
        cell_phone_number = request.form['cell_phone_number']
        email = request.form['email']

        dic = {0: first_name, 1: last_name,
            2: phone_number, 3: cell_phone_number, 4: email}

        trader_sql = f"SELECT first_name, last_name, phone_no, cell_no, email FROM Trader WHERE client_id = %s"
        update_sql = f"UPDATE Trader SET first_name = %s, last_name = %s, phone_no = %s, cell_no = %s, email = %s " \
                     f"WHERE client_id = %s "
        try:

            cursor.execute(trader_sql, (user_id,))
            trader_result = cursor.fetchall()

            for i in range(5):
                temp = dic[i]
                if temp == "":
                    dic[i] = trader_result[0][i]

            # update trader
            cursor.execute(
                update_sql, (dic[0], dic[1], dic[2], dic[3], dic[4], user_id))
            db.commit()

            return redirect(url_for("profile"))

        except con.Error as err:
            # query error
            print(err.msg)
            return render_template('edit_user_info.html')

    return render_template('edit_user_info.html')


@app.route('/edit_login', methods=['GET', 'POST'])
def edit_login():
    if request.method == "POST":

        user_name = session["user_name"]
        user_id = session["user_id"]

        login = request.form['login']
        temp = login
        password = request.form['password']
        dic = {0: login, 1: password}

        login_sql = f"SELECT * FROM User WHERE login = %s"

        login_insert = f"INSERT INTO User (login, password) VALUES (%s, %s)"
        Trader_update = f"UPDATE Trader SET login = %s WHERE client_id = %s"
        login_delete = f"DELETE FROM User WHERE login = %s"
        login_update = f"UPDATE User SET password = %s WHERE login = %s"

        try:
            # fetch user login info
            cursor.execute(login_sql, (user_name,))
            result = cursor.fetchall()

            # avoid null value
            for i in range(2):
                temp2 = dic[i]
                if temp2 == "":
                    dic[i] = result[0][i]

            # new login
            if temp != "":
                cursor.execute(login_sql, (temp,))
                result2 = cursor.fetchall()

                # user name already taken
                if len(result2) > 0:
                    flash("Username already taken", "error")
                    return render_template('edit_login.html')

                # insert new login
                cursor.execute(login_insert, (dic[0], dic[1]))
                db.commit()

                # update Trader
                cursor.execute(Trader_update, (dic[0], user_id))
                db.commit()

                # delete old login
                cursor.execute(login_delete, (result[0][0],))
                db.commit()

                session["user_name"] = login
            else:
                # if user update password
                cursor.execute(login_update, (dic[1], result[0][0]))
                db.commit()

            return redirect(url_for("profile"))

        except con.Error as err:
            print(err)
            return render_template('edit_login.html')

    return render_template('edit_login.html')


@app.route('/edit_address', methods=['GET', 'POST'])
def edit_address():
    if request.method == "POST":

        user_id = session["user_id"]

        street = request.form['address'].upper()
        city = request.form['city'].upper()
        state = request.form['state'].upper()
        zip_code = request.form['zip']

        address_search_sql = f"SELECT * FROM Address Where street_address = %s AND zip_code = %s"
        update_address_sql = f"UPDATE Address SET city = %s, state = %s WHERE street_address = %s AND zip_code = %s"
        update_user_sql = f"UPDATE Trader SET street_address = %s, zip_code = %s WHERE client_id = %s"
        insert_new_address = f"INSERT INTO Address(street_address, city, state, zip_code) VALUES (%s,%s,%s,%s)"
        try:
            cursor.execute(address_search_sql, (street, zip_code))
            result = cursor.fetchall()

            # if there exist such Address in DB
            if len(result) > 0:

                # update current address's city & state
                if result[0][1] != city or result[0][2] != state:
                    cursor.execute(update_address_sql,
                                   (city, state, street, zip_code))
                    db.commit()

                # update user
                cursor.execute(update_user_sql, (street, zip_code, user_id))
                db.commit()

                return redirect(url_for("profile"))
            # moved to new address
            else:
                # insert new address
                cursor.execute(insert_new_address,
                               (street, city, state, zip_code))
                db.commit()

                # update user
                cursor.execute(update_user_sql, (street, zip_code, user_id))
                db.commit()

                return redirect(url_for("profile"))

        except con.Error as err:
            print(err)
            return render_template('edit_address.html')
    else:
        return render_template('edit_address.html')


# logout
@app.route("/logout")
def logout():
    if "user_name" in session:
        user_name = session["user_name"]
        flash(f"You have been logged out, {user_name}", "info")
    session.pop("user_id", None)
    return redirect(url_for("index"))

# transaction_history


@app.route('/transaction_history')
def transaction_history():
    user_id = session["user_id"]
    user_name = session["user_name"]

     # get ethereum address for a client
    trader_sql = f"SELECT T.ethereum_address FROM  Trader T , User U WHERE T.login = U.login AND U.login = %s AND T.client_id = %s"

    # get transactions for ethereum address for buy/sell
    transactions_sql = f"SELECT Tr.ethereum_nft_address, Tr.commission_type, Tr.commission_paid, Tr.date, Tr.ethereum_value, Tr.cancelled FROM  Trader T , User U, Transaction Tr WHERE T.login = U.login AND U.login = %s AND T.client_id = %s AND T.ethereum_address = Tr.ethereum_seller_address"
    try:
        # fetch ethereum address
        cursor.execute(trader_sql, (user_name, user_id))
        trader_ethereum_address_result = cursor.fetchall()
        trader_ethereum_address = trader_ethereum_address_result[0][0]

        # fetch transactions
        cursor.execute(transactions_sql, (user_name, user_id))
        transactions_result = cursor.fetchall()
        print(transactions_result)
        return render_template('transaction_history.html', transaction_details=transactions_result)

    except con.Error as err:
        # query error
        print(err.msg)
    return render_template('transaction_history.html')


@app.route('/cancel_transaction')
def cancel_transaction():
    # todo

    return redirect(url_for("home"))


@app.route('/manager_dashboard')
def manager_dashboard():
    
    # fetch aggregate transaction results
    transactions_sql = f"SELECT SUM(Tr.commission_paid) , COUNT(*) FROM Transaction Tr"
    try:
        cursor.execute(transactions_sql)
        transactions_sql_result = cursor.fetchall()
        return render_template('manager_dashboard.html', transactions=transactions_sql_result)

    except con.Error as err:
        # query error
        print(err.msg)
        return render_template('manager_dashboard.html')

@app.route("/daterange_transaction_history",methods=['POST','GET'])
def daterange_transaction_history(): 

    if request.method == "POST":

        #get date range
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        print(start_date)
        print(end_date)


        daterange_sql = f"SELECT SUM(Tr.commission_paid) , COUNT(*) FROM Transaction Tr"

        try:
            cursor.execute(daterange_sql)
            daterange_sql_result = cursor.fetchall()
            print(daterange_sql_result[0][0])
            return jsonify({'htmlresponse': render_template('daterange_transactions.html', transactions = daterange_sql_result)})

        except con.Error as err:
            # query error
            print("TTT- error ")
            print(err.msg)
        
        return jsonify({'htmlresponse': render_template('daterange_transactions.html')})

if __name__ == '__main__':
    app.run(debug=True)
