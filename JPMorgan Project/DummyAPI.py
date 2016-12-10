from flask import Flask, render_template, request, flash,jsonify,session
import httplib, urllib2
import random
import json
from flaskext.mysql import MySQL
import time
from flask_socketio import SocketIO, send,emit
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super secret key"




socketio = SocketIO(app)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'stock'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
cursor = mysql.connect().cursor()
usernameAndPassword = dict()

# Server API URLs
QUERY = "http://localhost:8080/query?id={}"
ORDER = "http://localhost:8080/order?id={}&side=sell&qty={}&price={}"

id = 0

@app.route("/")
def show_homepage():
    return render_template('homepage.html')


@app.route("/login", methods=['GET', 'POST'])
def login_process():
    error = None
    connection = mysql.get_db()
    try:
        cursor.execute("SELECT username,password FROM stock.user_info")
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
    return render_template("homepage.html",error=error)


@app.route("/logout")
def logout_process():
    flash("You have successfully logged out")
    return render_template("homepage.html")


@socketio.on('form')
def sell_stock(form):
    print form
    if form['price']=='':
        price = 0
    else:
        price = int(form['price'])
    quantity = int(form['quantity'])

    username = session['username']
    curtime = datetime.now().time()

    # process the time
    struct_time = curtime.strftime('%H:%M')
    t0 = struct_time.split(":")  # current time
    endTime = "23:59"
    t1 = endTime.split(":")
    process = (int(t1[0]) - int(t0[0])) * 60 + int(t1[1]) - int(t0[1])

    if process < 0:
        result = "The stock market ends at 23:59, please sell stocks tomorrow."
        emit('message',result)
        return '{}'

    # execute a transaction as soon as possible
    k = 1
    f = 0
    global id
    total_avg=0
    total_non=0

    cur = datetime.now().time()
    curr = cur.strftime('%H:%M')
    quan = quantity

    while quantity > 0 and k > 0 and curr < endTime:
        id += 1
        description = ""
        qty = quantity / k
        order_parameters = (qty, price)
        print "Executing 'sell' of {:,} @ {:,}".format(*order_parameters)
        url = ORDER.format(random.random(), *order_parameters)
        order = json.loads(urllib2.urlopen(url).read())

        connection = mysql.get_db()
        cursor = connection.cursor()

        #timestamp = order['timestamp']
        sold_price = order['avg_price']

        if sold_price > 0:  # indicates a successful transaction
            notional = float(sold_price * sold_price)
            status = "success"
            result = "Sold {:,} for ${:,}/share".format(qty, sold_price)
            emit('message',result)

            quantity -= qty
            total_avg += sold_price * qty
            total_non += notional * qty
            f = 0
            k -= 1
            query = """INSERT INTO history (id,timestamp,username,qty,avg_price,notional,status,description) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(query, (id,datetime.utcnow(),username,qty,sold_price,notional,status,description))
            connection.commit()

        elif k < quantity:
            notional = 0
            status = "fail"
            f += 1
            if f >= 3:
                k += 1
                f = 0
            query = """INSERT INTO history (id,timestamp,username,qty,avg_price,notional,status,description) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(query, (id,datetime.utcnow(),username,qty,sold_price,notional,status,description))
            connection.commit()
            result = "Unfilled Order"
            #k-=1
            #socketio.sleep(2)

        cur = datetime.now().time()
        curr = cur.strftime('%H:%M')

    id += 1
    status = "left"
    description = "summary"
    total_avg /= quan
    total_non /= quan
    query = """INSERT INTO history (id,timestamp,username,qty,avg_price,notional,status,description) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"""
    cursor.execute(query, (id,datetime.utcnow(),username,quantity,total_avg,total_non,status,description))
    connection.commit()

    return '{}'


@socketio.on('form2')
def sell_stock(form2):
    print form2
    if form2['price']=='':
        price = 0
    else:
        price = int(form2['price'])
    quantity = int(form2['quantity'])

    username = session['username']
    curtime = datetime.now().time()

    # process the time
    struct_time = curtime.strftime('%H:%M')
    t0 = struct_time.split(":")  # current time
    endTime = "22:53"
    t1 = endTime.split(":")
    process = (int(t1[0]) - int(t0[0])) * 60 + int(t1[1]) - int(t0[1])

    print t0
    print t1
    print process

    if process < 0:
        result = "The stock market ends at 23:59, please sell stocks tomorrow."
        emit('message',result)
        return '{}'

    # execute a transaction using TWAP algorithm
    global id
    total_avg=0
    total_non=0

    cur = datetime.now().time()
    curr = cur.strftime('%H:%M')
    quan = quantity

    if quantity < 12:
        count = quantity
        k = count
    elif quantity < 120:
        count = 12
        k = count
    else:
        count = 12 * quantity / 120
        k = count
        if process * 60 < count:
            count = process * 60
            k = count

    while quantity > 0 and curr < endTime:
        if k == 0:
            result = "this transaction can not be finished in this time"
            print "this transaction can not be finished in this time"
            emit('message',result)
        else:
            id += 1
            description = ""
            qty = quantity / k
            order_parameters = (qty, price)
            print "Executing 'sell' of {:,} @ {:,}".format(*order_parameters)
            url = ORDER.format(random.random(), *order_parameters)
            order = json.loads(urllib2.urlopen(url).read())

            connection = mysql.get_db()
            cursor = connection.cursor()

            #timestamp = order['timestamp']
            sold_price = order['avg_price']

            if sold_price > 0:  # indicates a successful transaction
                notional = float(sold_price * sold_price)
                status = "success"
                result = "Sold {:,} for ${:,}/share".format(qty, sold_price)
                emit('message',result)

                quantity -= qty
                total_avg += sold_price * qty
                total_non += notional * qty
                query = """INSERT INTO history (id,timestamp,username,qty,avg_price,notional,status,description) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"""
                cursor.execute(query, (id,datetime.utcnow(),username,qty,sold_price,notional,status,description))
                connection.commit()

            else:
                notional = 0
                status = "fail"
                query = """INSERT INTO history (id,timestamp,username,qty,avg_price,notional,status,description) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"""
                cursor.execute(query, (id,datetime.utcnow(),username,qty,sold_price,notional,status,description))
                connection.commit()
                result = "Unfilled Order"
            k-=1
            socketio.sleep(process*60/count)

        cur = datetime.now().time()
        curr = cur.strftime('%H:%M')

    id += 1
    status = "left"
    description = "summary"
    total_avg /= quan
    total_non /= quan
    connection = mysql.get_db()
    cursor = connection.cursor()
    query = """INSERT INTO history (id,timestamp,username,qty,avg_price,notional,status,description) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"""
    cursor.execute(query, (id,datetime.utcnow(),username,quantity,total_avg,total_non,status,description))
    connection.commit()

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
    query = """SELECT id,timestamp,qty,avg_price,notional,status,description FROM history WHERE username = '%s'""" %username
    cursor.execute(query)
    result = cursor.fetchall()
    trade_history = [list(elem) for elem in result]
    return jsonify(trade_history)

if __name__ == "__main__":
    app.debug = True
    socketio.run(app)


