from flask import Flask, render_template, request, flash, url_for, redirect, jsonify
import httplib, urllib2
import random
import json
from flaskext.mysql import MySQL

app = Flask(__name__)
app.secret_key = "super secret key"
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'user_info'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
cursor = mysql.connect().cursor()
usernameAndPassword = dict()

# Server API URLs
QUERY = "http://localhost:8080/query?id={}"
ORDER = "http://localhost:8080/order?id={}&side=sell&qty={}&price={}"


@app.route("/")
def show_homepage():
    return render_template('homepage.html')


@app.route("/login", methods=['GET', 'POST'])
def login_process():
    error = None
    connection = mysql.get_db()
    try:
        cursor.execute("SELECT username,password FROM user_info.user_info")
    except Exception as e:
        pass
    record = cursor.fetchall()
    # get all the user info and store them in the dictionary
    for row in record:
        usernameAndPassword[row[0]] = row[1]
    connection.commit()
    if request.method == "POST":
        if request.form['username'] not in usernameAndPassword:
            error = 'User name does not exist.'
        elif request.form['password'] != usernameAndPassword.get(request.form['username']):
            error = 'Invalid credentials. Please try again.'
        else:
            return render_template('login.html')
        flash(error)
    return render_template("homepage.html",error=error)


@app.route("/logout")
def logout_process():
    flash("You have successfully logged out")
    return render_template("homepage.html")


@app.route("/sell_action", methods=['POST', 'GET'])
def sell_stock():
    price = int(request.form['price'])
    quantity = int(request.form['quantity'])
    print price
    print quantity
    order_parameters = (quantity, price)
    print "Executing 'sell' of {:,} @ {:,}".format(*order_parameters)
    url = ORDER.format(random.random(), *order_parameters)
    order = json.loads(urllib2.urlopen(url).read())

    connection = mysql.get_db()
    cursor = connection.cursor()

    username = "wangxucan"
    timestamp = order['timestamp']
    sold_price = order['avg_price']

    if  sold_price > 0:  # indicates a successful transaction
        notional = float(sold_price * sold_price)
        status = "success"
        result = "Sold {:,} for ${:,}/share, ${:,} notional".format(quantity, sold_price, notional)
        query = """INSERT INTO trade_history (timestamp,username,qty,avg_price,notional,status) VALUES(%s,%s,%s,%s,%s,%s)"""
        cursor.execute(query, (timestamp,username,quantity,sold_price,notional,status))
        connection.commit()
    else:
        share_num = 10
        notional = 0
        status = "fail"
        query = """INSERT INTO trade_history (timestamp,username,qty,avg_price,notional,status) VALUES(%s,%s,%s,%s,%s,%s)"""
        cursor.execute(query, (timestamp,username,quantity,sold_price,notional,status))
        connection.commit()
        result = "Unfilled Order"



    flash(result)
    return render_template('homepage.html')


@app.route('/fetch_bid_price')
def background_process():
    quote = json.loads(urllib2.urlopen(QUERY.format(random.random())).read())
    price = float(quote['top_bid']['price'])
    return jsonify(result=price)


@app.route('/fetch_trade_history')
def fetch_trade_history():
    connection = mysql.get_db()
    cursor = connection.cursor()
    query = """SELECT timestamp,qty,avg_price,notional,status FROM trade_history WHERE username='wangxucan' """
    cursor.execute(query)
    result = cursor.fetchall()
    trade_history = [list(elem) for elem in result]
    return jsonify(trade_history)

if __name__ == "__main__":
    app.debug = True
    app.run()
