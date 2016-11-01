# JPMorgan
This is a stock-trade-for-you project.

To run the program:

1. Make sure you have install the Python 2.7, run python server.py

2. Till now, we can only run the program locally, since we have built a mysql database locally.
   The user information is stored in the local database, which includes the username, password, email-address,number of shares the user owns for now. 
   You can also try to build the databse based on the schema we provide on your own computer.
   
3. Go to 127.0.0.1(your local ip address, the server will give the info of this address).

4. When the app is running, it will show up the main page of the app. When the user successfully logs in, in the trade sub tab:  the user can get the real-time bid_price of the market. Also, the user can execute a sell order for now. The buy function is not supported right now.
