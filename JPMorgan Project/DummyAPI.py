import json
import random
import urllib2

from flask import Flask, render_template, request, flash, jsonify, session
from flask_socketio import SocketIO, emit
from flaskext.mysql import MySQL

app = Flask(__name__)
app.secret_key = "super secret key"

socketio = SocketIO(app)

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
            session['username'] = request.form['username']
            return render_template('login.html')
        flash(error)
    return render_template("homepage.html", error=error)


@app.route("/logout")
def logout_process():
    flash("You have successfully logged out")
    return render_template("homepage.html")


@socketio.on('form')
def sell_stock(form):
    print form
    if form['price'] == '':
        price = 0
    else:
        price = int(form['price'])
    quantity = int(form['quantity'])

    username = session['username']
    k = 12

    while quantity > 0:
        if k == 0:
            result = "This Order can not be finished in time " + k
            print result
        else:
            qty = quantity / k
            order_parameters = (qty, price)
            print "Executing 'sell' of {:,} @ {:,}".format(*order_parameters)
            url = ORDER.format(random.random(), *order_parameters)
            order = json.loads(urllib2.urlopen(url).read())

            connection = mysql.get_db()
            cursor = connection.cursor()

            timestamp = order['timestamp']
            sold_price = order['avg_price']

            if sold_price > 0:  # indicates a successful transaction
                notional = float(sold_price * sold_price)
                status = "success"
                result = "Sold {:,} for ${:,}/share".format(qty, sold_price)
                emit('message', result)

                quantity -= qty
                query = """INSERT INTO trade_history (timestamp,username,qty,avg_price,notional,status) VALUES(%s,%s,%s,%s,%s,%s)"""
                cursor.execute(query, (timestamp, username, qty, sold_price, notional, status))
                connection.commit()
            else:
                notional = 0
                status = "fail"
                query = """INSERT INTO trade_history (timestamp,username,qty,avg_price,notional,status) VALUES(%s,%s,%s,%s,%s,%s)"""
                cursor.execute(query, (timestamp, username, qty, sold_price, notional, status))
                connection.commit()
                result = "Unfilled Order"

            k -= 1
            socketio.sleep(2)

    return '{}'


@app.route('/fetch_bid_price')
def background_process():
    quote = json.loads(urllib2.urlopen(QUERY.format(random.random())).read())
    price = float(quote['top_bid']['price'])
    return jsonify(result=price)


@app.route('/fetch_trade_history')
def fetch_trade_history():
    username = session['username']
    connection = mysql.get_db()
    cursor = connection.cursor()
    query = """SELECT timestamp,qty,avg_price,notional,status FROM trade_history WHERE username = '%s'""" % username
    cursor.execute(query)
    result = cursor.fetchall()
    trade_history = [list(elem) for elem in result]
    return jsonify(trade_history)


if __name__ == "__main__":
    app.debug = True
    socketio.run(app)
