'''
Michael Zayne Lumpkin, mzl190000
Siddhi Mahesh Potdar, smp220001
Desong Li, dxl180019
Tanya Sharma, txs220004
Priya Singh, pxs220067
'''
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
import mysql.connector as con
from connector import cursor, db
import random
import string
from datetime import date
import datetime
import requests
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
                                        email, street, zip_code, login_name, 'SILVER', 0.0, 0.0))
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
    ## also called available nfts page
    if "user_id" in session:
        user_id = session["user_id"]
        #print(user_id)
        get_curr_ethereum_address = f"select ethereum_address from temp.Trader T where T.client_id = %s"
        avail_nft_sql = f"select N.* from temp.NFT N where N.ethereum_address != %s"
        try:
            # fetch user info
            cursor.execute(get_curr_ethereum_address, (user_id,))
            trader_ethereum_address = cursor.fetchall()
            #print(trader_ethereum_address)
            cursor.execute(avail_nft_sql, (trader_ethereum_address[0]))
            avail_nft_sql_result = cursor.fetchall()
            #print(avail_nft_sql_result)

        except con.Error as err:
        # query error
            print(err.msg)
        return render_template('home.html', content=user_id, avail_nft_sql=avail_nft_sql_result)
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
    
    
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == "POST":

        payment_id = random.randrange(100000, 999999)
        user_id = session["user_id"]
        payment_type = request.form['payment_type'].upper()
        payment_address = request.form['payment_address'].upper()
        amount = request.form['amount']
        date = datetime.datetime.now()

        if payment_type == "ETH":
            payment_type = "E"
        elif payment_type == "FIAT":
            payment_type = "F"
        else:
            flash("No such payment", "error")
            return render_template('payment.html')

        insert_new_address = f"INSERT INTO Payment(payment_id, client_id, payment_type, payment_address, " \
                             f"amount_paid, cancelled, date) VALUES (%s,%s,%s,%s,%s,%s,%s) "

        search_user_sql1 = f"SELECT fiat_balance, ethereum_balance FROM Trader Where client_id = %s "

        update_user_sql1 = f"UPDATE Trader SET fiat_balance = %s WHERE client_id = %s"
        update_user_sql2 = f"UPDATE Trader SET ethereum_balance = %s WHERE client_id = %s"

        try:

            cursor.execute(insert_new_address,
                           (payment_id, user_id, payment_type, payment_address, amount, False, date))
            db.commit()

            cursor.execute(search_user_sql1, (user_id,))
            result = cursor.fetchall()

            if payment_type == "F":
                balance = result[0][0]
                total = balance + float(amount)
                cursor.execute(update_user_sql1, (total, user_id))
                db.commit()
            else:
                balance = result[0][1]
                total = balance + float(amount)
                cursor.execute(update_user_sql2, (total, user_id))
                db.commit()

            return redirect(url_for("profile"))

        except con.Error as err:
            print(err)
            return render_template('payment.html')

    return render_template('payment.html')


@app.route('/payment_history')
def payment_history():
    user_id = session["user_id"]
    # query
    payment_sql = f"SELECT * FROM Payment WHERE client_id = %s ORDER BY date DESC"
    try:
        # fetch user info
        cursor.execute(payment_sql, (user_id,))
        payment_result = cursor.fetchall()

        return render_template('payment_history.html', payment_detail=payment_result)

    except con.Error as err:
        # query error
        print(err.msg)

    return render_template('payment_history.html')


@app.route('/cancel_payment')
def cancel_payment():
    payment_id = request.args.to_dict()["payment_id"]
    print(payment_id)
    user_id = session["user_id"]

    update_payment = f"UPDATE Payment SET cancelled = %s WHERE payment_id = %s"
    search_payment = f"SELECT payment_type, amount_paid FROM Payment WHERE payment_id = %s "
    search_payment_date = f"SELECT date FROM Payment WHERE payment_id = %s"

    search_user = f"SELECT fiat_balance, ethereum_balance FROM Trader Where client_id = %s "

    update_user_sql1 = f"UPDATE Trader SET fiat_balance = %s WHERE client_id = %s"
    update_user_sql2 = f"UPDATE Trader SET ethereum_balance = %s WHERE client_id = %s"

    try:
        # check if the payment exceeded 15 minutes
        cursor.execute(search_payment_date, (payment_id,))
        payment_date = cursor.fetchall()

        current_date = datetime.datetime.now()
        diff = current_date - payment_date[0][0]
        minutes = divmod(diff.seconds, 60)

        if minutes[0] >= 15:
            flash(f"You may only cancel the payment that is placed within 15 minutes", "info")
            return redirect(url_for("payment_history"))

        # update payment status
        cursor.execute(update_payment, (True, payment_id))
        db.commit()

        # fetch payment type
        cursor.execute(search_payment, (payment_id,))
        payment_result = cursor.fetchall()

        # fetch user balance
        cursor.execute(search_user, (user_id,))
        trader_result = cursor.fetchall()

        payment_type = payment_result[0][0]

        if payment_type == "F":

            total = trader_result[0][0] - payment_result[0][1]
            cursor.execute(update_user_sql1, (total, user_id))
            db.commit()

        else:
            total = trader_result[0][1] - payment_result[0][1]
            cursor.execute(update_user_sql2, (total, user_id))
            db.commit()


        return redirect(url_for("profile"))

    except con.Error as err:
        print(err)
        return redirect(url_for("profile"))

# logout
@app.route("/logout")
def logout():
    if "user_name" in session:
        user_name = session["user_name"]
        flash(f"You have been logged out, {user_name}", "info")
    session.pop("user_id", None)
    return redirect(url_for("index"))


@app.route('/owned_nfts')
def owned_nfts():
    user_id = session["user_id"]
    user_name = session["user_name"]

    # query
    owned_nft_sql = f"SELECT token_id, name, market_value FROM  NFT N , Trader T WHERE T.client_id = %s AND N.ethereum_address = T.ethereum_address"
    
    try:
        # fetch user info
        cursor.execute(owned_nft_sql, (user_id,))
        owned_nft_result = cursor.fetchall()
        print(owned_nft_result)
    
    except con.Error as err:
        # query error
        print(err.msg)
        return render_template('Error-404.html')
        # fetch address info
    return render_template('owned_nfts.html', owned_nfts=owned_nft_result)

# transaction_history


@app.route('/transaction_history')
def transaction_history():
    user_id = session["user_id"]
    user_name = session["user_name"]

     # get ethereum address for a client
    trader_sql = f"SELECT T.ethereum_address FROM  Trader T , User U WHERE T.login = U.login AND U.login = %s AND T.client_id = %s"

    # get transactions for ethereum address for buy/sell
    transactions_sql = f"SELECT Tr.ethereum_nft_address, Tr.commission_type, Tr.commission_paid, Tr.date, Tr.ethereum_value, Tr.cancelled, Tr.transaction_id FROM  Trader T , User U, Transaction Tr WHERE T.login = U.login AND U.login = %s AND T.client_id = %s AND T.ethereum_address = Tr.ethereum_seller_address"
    try:
        # fetch ethereum address
        cursor.execute(trader_sql, (user_name, user_id))
        trader_ethereum_address_result = cursor.fetchall()
        trader_ethereum_address = trader_ethereum_address_result[0][0]

        # fetch transactions
        cursor.execute(transactions_sql, (user_name, user_id))
        transactions_result = cursor.fetchall()
        #print(transactions_result)
        return render_template('transaction_history.html', transaction_details=transactions_result)

    except con.Error as err:
        # query error
        print(err.msg)
    return render_template('transaction_history.html')


@app.route('/cancel_transaction/<tr_id>')
def cancel_transaction(tr_id):
    #cancel transaction by id + 15 min check logic
    cancel_transaction_time_sql = f"SELECT date FROM Transaction WHERE transaction_id = %s"
    cancel_transaction_sql = f"UPDATE  Transaction Tr SET Tr.cancelled = 1 WHERE Tr.transaction_id = %s"
    #print(tr_id)
    #todo-update timestamp also + check for 15 min logic (here and in html page)
    try:
        #get date query
        cursor.execute(cancel_transaction_time_sql, (tr_id,))
        transaction_date_result = cursor.fetchall()

        current_date = datetime.datetime.now()
        diff = current_date - transaction_date_result[0][0]
        minutes = divmod(diff.seconds, 60)

        if minutes[0] >= 15:
            flash(f"You may only cancel the transaction that is placed within 15 minutes", "info")

        else: 
            # update query
            cursor.execute(cancel_transaction_sql, (tr_id,))
            #todo - after cancelling transaction - what to do?
            db.commit()
        return redirect(url_for("transaction_history"))

    except con.Error as err:
        # query error
        print(err.msg)

    return redirect(url_for("home"))


@app.route('/manager_dashboard')
def manager_dashboard():

    date_today = str(date.today())
    month_today = date.today().month
    
    # fetch aggregate transaction results
    transactions_sql = f"SELECT SUM(Tr.commission_paid) , COUNT(*) FROM Transaction Tr "
    transactions_sql_daily = f"SELECT SUM(Tr.commission_paid) , COUNT(*) FROM Transaction Tr WHERE Tr.date = %s "
    transactions_sql_weekly = f"SELECT SUM(Tr.commission_paid) , COUNT(*) FROM Transaction Tr WHERE WEEK(Tr.date) = WEEK(NOW())"
    transactions_sql_monthly = f"SELECT SUM(Tr.commission_paid) , COUNT(*) FROM Transaction Tr WHERE MONTH(Tr.date) = %s"
    try:

        #alltime transactions
        cursor.execute(transactions_sql)
        transactions_sql_result = cursor.fetchall()
        #print(transactions_sql_result)

        #daily transactions
        cursor.execute(transactions_sql_daily,(date_today,))
        transactions_sql_daily_result = cursor.fetchall()
        #print(transactions_sql_daily_result)

        #weekly transactions
        cursor.execute(transactions_sql_weekly)
        transactions_sql_weekly_result = cursor.fetchall()
        #print(transactions_sql_weekly_result)

        #monthly transactions
        cursor.execute(transactions_sql_monthly,(month_today,))
        transactions_sql_monthly_result = cursor.fetchall()
        #print(transactions_sql_monthly_result)

        return render_template('manager_dashboard.html', 
        transactions = transactions_sql_result, 
        transactions_daily = transactions_sql_daily_result,
        transactions_weekly = transactions_sql_weekly_result,
        transactions_monthly = transactions_sql_monthly_result)

    except con.Error as err:
        # query error
        print(err.msg)

    return render_template('manager_dashboard.html')

@app.route('/checkout/<quoted_amount>')
def checkout(quoted_amount):
    user_id = session["user_id"]
    user_name = session["user_name"]
    quoted_amount = quoted_amount.split('|')
    # query
    trader_sql = f"SELECT fiat_balance, ethereum_balance FROM  Trader T WHERE T.client_id = %s"
    try:
        # fetch user info
        cursor.execute(trader_sql, (user_id, ))
        checkout_result = cursor.fetchall() 
        if quoted_amount[0] == 0:
            print(checkout_result[1]-float(quoted_amount[1]))
        else:
            print(checkout_result[0]-float(quoted_amount[0]))
    
    except con.Error as err:
        # query error
        print(err.msg)
        # fetch address info
    return render_template('checkout.html', checkout_result=checkout_result)

        

@app.route("/daterange_transaction_history",methods=['POST','GET'])
def daterange_transaction_history(): 

    if request.method == "POST":

        #get date range
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        print(start_date)
        print(end_date)

        daterange_sql = f"SELECT SUM(Tr.commission_paid) , COUNT(*) FROM Transaction Tr WHERE Tr.date BETWEEN %s AND %s"

        try:
            cursor.execute(daterange_sql, (start_date, end_date))
            daterange_sql_result = cursor.fetchall()
            print(daterange_sql_result[0][0])
            return jsonify({'htmlresponse': render_template('daterange_transactions.html', transactions = daterange_sql_result)})

        except con.Error as err:
            # query error
            print("TTT- error ")
            print(err.msg)
        
        return jsonify({'htmlresponse': render_template('daterange_transactions.html')})
   

#offers
@app.route('/nft_offer')
def nft_offer():
    user_id = session["user_id"]
    user_name = session["user_name"]

    # query
    nft_offer_sql = f"SELECT N.name, O.token_id, O.fiat_balance, O.ethereum_balance, O.buyerid FROM NFT N , offer O, Trader T1, Trader T2, Transaction TR WHERE N.token_id=O.token_id, O.buyerid = T1.client_id, O.sellerid = T2.client_id,T1.client_id != T2.client_id, TR.seller_ethereum_address = T1.ethereum_address"
    
    try:
        # fetch user info
        cursor.execute(nft_offer_sql, (user_id,))
        nft_offer_result = cursor.fetchall()
        print(nft_offer_result)
    
    except con.Error as err:
        # query error
        print(err.msg)
        return render_template('Error-404.html')
        # fetch address info
    return render_template('offer.html', nft_offer=nft_offer_result)

#add nft to sell
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == "POST":
        user_id=session["user_id"]
        token_id=20
        name=request.form['name'].upper
        market_value = request.form['market_value']
        eth=f"Select ethereum_address FROM Trader T, User U WHERE T.client_id=%s"
        new_nft=f"INSERT INTO NFT(ethereum_address, name, market_value) VALUES(%s,%s,%s)" 
        
        try:
            cursor.execute(eth, (user_id,))
            address=str(cursor.fetchall())
            cursor.execute(new_nft,(address, name, market_value,))

        except con.Error as err:
            print(err)
            return render_template('Error-404.html')

    return render_template('sell.html')




# home page
@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if "user_id" in session:
        user_id = session["user_id"]

        #remove hardcoding
        token_id = 1
        nft_sql = f"SELECT * FROM  NFT N WHERE N.token_id = %s"
        seller_info_sql = f"SELECT T.first_name FROM  Trader T, NFT N WHERE T.ethereum_address = N.ethereum_address AND N.token_id = %s"
    try:
        # fetch nft
        cursor.execute(nft_sql, (token_id,))
        nft_sql_result = cursor.fetchall()
        print(nft_sql_result)

        #fetch seller info
        cursor.execute(seller_info_sql, (token_id,))
        seller_info_sql_result = cursor.fetchall()
        print(seller_info_sql_result)

        return render_template('buy.html', nft_data=nft_sql_result, seller_data = seller_info_sql_result)

    except con.Error as err:
        # query error
        print(err.msg)

    return render_template('checkout.html', quoted_html=10)


if __name__ == '__main__':
    app.run(debug=True)
