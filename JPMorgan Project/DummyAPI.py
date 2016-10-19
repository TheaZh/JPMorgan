from flask import Flask, render_template, request, flash, url_for, redirect
import httplib, urllib2
import random
import json

app = Flask(__name__)
app.secret_key = "super secret key"
# Server API URLs
QUERY = "http://localhost:8080/query?id={}"
ORDER = "http://localhost:8080/order?id={}&side=sell&qty={}&price={}"


@app.route("/")
def show_homepage():
    flash('flashTest!!!!!')
    return render_template('homepage.html')


@app.route("/login", methods=['GET', 'POST'])
def login_process():
    error = ''
    try:
        if request.method == "POST":
            attempted_username = request.form['username']
            attempted_password = request.form['password']

        if attempted_username == "wangxucan" and attempted_password == "password":
            flash("You have successfully logged in")
            return redirect(url_for('show_homepage'))
        else:
            flash("Invalid Credentials, Try Again!")
            return render_template('homepage.html')


    except Exception as e:
        flash(e)
        return render_template('homepage.html')


@app.route("/sell_action", methods=['POST'])
def sell_stock():
    price = int(request.form['price'])
    quantity = int(request.form['quantity'])
    order_parameters = (price, quantity)
    print "Executing 'sell' of {:,} @ {:,}".format(*order_parameters)
    url = ORDER.format(random.random(), *order_parameters)
    order = json.loads(urllib2.urlopen(url).read())
    if order['avg_price'] > 0:  # indicates a sucessful transaction
        sold_price = order['avg_price']
        notional = float(price * quantity)
        print "Sold {:,} for ${:,}/share, ${:,} notional".format(quantity, sold_price, notional)
    else:
        print "Unfilled order"
    return render_template('success.html', **order)


if __name__ == "__main__":
    app.debug = True
    app.run()
