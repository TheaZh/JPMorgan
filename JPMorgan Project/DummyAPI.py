from flask import Flask, render_template, request
import httplib, urllib2
import random
import json

app = Flask(__name__)

# Server API URLs
QUERY = "http://localhost:8080/query?id={}"
ORDER = "http://localhost:8080/order?id={}&side=sell&qty={}&price={}"


@app.route("/")
def showHomePage():
    return render_template('main.html')


@app.route("/login", methods=['GET','POST'])
def LoginProcess():
    attempted_username = request.form['username']
    attempted_password = request.form['password']
    print attempted_password
    print attempted_username
    return render_template('success.html')


@app.route("/sell_action", methods=['POST'])
def sellStock():
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
    app.run()
