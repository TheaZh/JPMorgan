from flask import Flask, render_template, request, flash, url_for, redirect
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
    error = ''
    try:
        cursor.execute("SELECT username,password FROM user_info")
    except Exception as e:
        pass
    record = cursor.fetchall()
    #get all the user info and store them in the dictionary
    for row in record:
        usernameAndPassword[row[0]] = row[1]
    print usernameAndPassword
    cursor.close()

    if request.method == "POST":
        attempted_username = request.form['username']
        attempted_password = request.form['password']
        if attempted_username not in usernameAndPassword:
            error = 'User name does not exist'
        elif attempted_password != usernameAndPassword.get(attempted_username):
            error = 'Invalid credentials. Please try again.'
        else:
            return render_template('login.html')
        flash(error)
    return render_template("homepage.html")

@app.route("/logout")
def logout_process():
    flash("You have successfully logged out")
    return render_template("homepage.html")



@app.route("/sell_action", methods=['POST','GET'])
def sell_stock():
    price = int(request.form['price'])
    quantity = int(request.form['quantity'])
    print price
    print quantity
    order_parameters = (price, quantity)
    print "Executing 'sell' of {:,} @ {:,}".format(*order_parameters)
    url = ORDER.format(random.random(), *order_parameters)
    order = json.loads(urllib2.urlopen(url).read())
    if order['avg_price'] > 0:  # indicates a sucessful transaction
        sold_price = order['avg_price']
        notional = float(price * quantity)
        result = "Sold {:,} for ${:,}/share, ${:,} notional".format(quantity, sold_price, notional)
        print "Sold {:,} for ${:,}/share, ${:,} notional".format(quantity, sold_price, notional)
    else:
        print "Unfilled order"

    flash(result)
    return render_template('homepage.html')


if __name__ == "__main__":
    app.debug = True
    app.run()
