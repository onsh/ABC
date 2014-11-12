""" An example of how to get a Python handle to a MongoDB database """
# mongod --dbpath /usr/local/var/mongodb

import sys

from datetime import datetime
from pymongo import Connection
from pymongo.errors import ConnectionFailure

def main():
    """ Connect to MongoDB """
    try:
        c = Connection(host="localhost", port=27017)
    except ConnectionFailure as e:
        sys.stderr.write("Could not connect to MongoDB: {0}".format(e))
        sys.exit(1)

    # Get a Database handle to a database named "mydb"
    dbh = c["mydb"]
    
    # Demonstrate the db.connection property to retrieve a reference to the
    # Connection object should it go out of scope. In most cases, keeping a
    # reference to the Database object for the lifetime of your program should
    # be sufficient.

    assert dbh.connection == c
    user_doc = {
        "username" : "janedoe",
        "firstname" : "Jane",
        "surname" : "Doe",
        "dateofbirth" : datetime(1974, 4, 12),
        "email" : "janedoe74@example.com",
        "score" : 0
    }
    dbh.users.insert(user_doc, safe=True)
    print("Successfully inserted document: {0}".format(user_doc))
        
if __name__ == "__main__":
    main()
