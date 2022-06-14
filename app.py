from flask import Flask, jsonify, make_response, request
from werkzeug.security import generate_password_hash,check_password_hash
#from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
#from auth import mariaDBConnection
from pymongo import MongoClient
#import uuid
#import jwt
import datetime
#import bcrypt
import hashlib
from utils import getAllItems
from waitress import serve

app = Flask(__name__)

#client = MongoClient("mongodb+srv://capel:EpNtgYI8X66oR2O4@apicapel.scttl.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient("mongodb+srv://apicapel:N7gySu1HwmzqvTsD@apicapel.scttl.mongodb.net/?retryWrites=true&w=majority")
db = client["ApiCapel"]
users_collection = db["systemUsers"]

jwt = JWTManager(app) # initialize JWTManager
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
app.config['JWT_SECRET_KEY'] = 'f8de2f7257f913eecfa9aae8a3c7750e'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1) # define the life span of the token

@app.route('/api/v1/login', methods=['POST'])
def login():
	login_details = request.args # store the json body request
	user_from_db = users_collection.find_one({'username': login_details['username']})  # search for user in database
	if user_from_db:
		#salt = bcrypt.gensalt(rounds=10)
		#encrpted_password = hashlib.sha256(login_details['password']).bcrypt.hashpw(encrpted_password, salt)
		encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
		if encrpted_password == user_from_db['password']:
			access_token = create_access_token(identity=user_from_db['username']) # create jwt token
			return jsonify(access_token=access_token), 200

	return jsonify({'msg': 'The username or password is incorrect'}), 401

@app.route('/api/v1/dailydata/<initialdate>/<finaldate>/<retail>', methods=['GET'])
@jwt_required()
def dailydata(initialdate, finaldate, retail):
	items = getAllItems(initialdate, finaldate, retail)

	return items

@app.route('/api/v1/filterv2/<s_cadena>/<s_comuna>/<s_ciudad>/<i_marca>', methods=['GET'])
@jwt_required()
def filterv2(vargs):
	vargs = vargs.split("/")
	#print(type(vargs))
	for i in range(0, len(vargs)):
		print(vargs[i].split("="))
	return str(vargs)
""" 
if __name__ == '__main__':
	app.run(debug=True)
 """

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=80)