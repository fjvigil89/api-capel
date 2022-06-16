from crypt import methods
from flask import Flask, jsonify, make_response, request
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from pymongo import MongoClient
import datetime
import bcrypt
from utils import getAllItems, filterItems, filterComuna, filterMarca
from auth import mariaDBConnection

app = Flask(__name__)

#For production purposes
client = MongoClient("mongodb+srv://api-capel-access:EpNtgYI8X66oR2O4@cademsmart0.hj6jy.mongodb.net/?retryWrites=true&w=majority")
db = client["api-capel"]
users_collection = db["users"]

#For development purposes
#client = MongoClient("mongodb+srv://apicapel:N7gySu1HwmzqvTsD@apicapel.scttl.mongodb.net/?retryWrites=true&w=majority")
#db = client["ApiCapel"]
#users_collection = db["systemUsers"]

jwt = JWTManager(app) # initialize JWTManager
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
app.config['JWT_SECRET_KEY'] = 'f8de2f7257f913eecfa9aae8a3c7750e'
#app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=23) # define the life span of the token

@app.route('/api/v1/login', methods=['POST'])
def login():

	login_details = request.args # store the json body request
	user_from_db = users_collection.find_one({'username': login_details['username']})  # search for user in database
	print(user_from_db)

	if user_from_db:
		decrpted_password = bcrypt.checkpw(login_details['password'].encode(), user_from_db['password'].encode())

		if decrpted_password:
			access_token = create_access_token(identity=user_from_db['username']) # create jwt token
			app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=user_from_db['duration_token_in_hours']) # define the life span of the token
			return jsonify(access_token=access_token), 200

	return jsonify({'msg': 'The username or password is incorrect'}), 401

@app.route('/api/v1/data', methods=['GET'])
@jwt_required()
def data():
	initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
	finaldate = datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date()
	#retail = request.args['retail']
	conn = mariaDBConnection()
	cursor = conn.cursor()
	cursor.execute(
			"""
			SELECT *
			FROM movimiento_api_rest
			WHERE fecha BETWEEN ? AND ?
			LIMIT 500
			""",
			(initialdate, finaldate)
	)

	row_headers=[x[0] for x in cursor.description]
	cursor = cursor.fetchall()

	json_data = []
	json_dict = {}
	metadata_section = []
	total_venta_unidades = 0
	total_venta_valor = 0

	for result in cursor:
		json_data.append(dict(zip(row_headers,result)))

	for i in json_data:
		total_venta_unidades += int(i['venta_unidades'])
		total_venta_valor += int(i['venta_valor'])

	metadata_section.append({
		'preproceso': 'false',
		'cantidad de registros': len(json_data),
		'total_venta_unidades': total_venta_unidades,
		'total_venta_valor': total_venta_valor
	})

	json_dict['message']=200	
	json_dict['data']=json_data
	json_dict['metadata_section']=metadata_section	

	return json_dict, 200

@app.route('/api/v1/dailydata', methods=['GET'])
@jwt_required()
def dailydata():
	initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
	finaldate = initialdate - datetime.timedelta(3)
	#retail = request.args['retail']
	conn = mariaDBConnection()
	cursor = conn.cursor()
	cursor.execute(
			"""
			SELECT *
			FROM movimiento_api_rest
			WHERE fecha BETWEEN ? AND ?
			LIMIT 500
			""",
			(finaldate, initialdate)
	)

	row_headers=[x[0] for x in cursor.description]
	cursor = cursor.fetchall()

	json_data = []
	json_dict = {}
	metadata_section = []
	total_venta_unidades = 0
	total_venta_valor = 0

	for result in cursor:
		json_data.append(dict(zip(row_headers,result)))

	for i in json_data:
		total_venta_unidades += int(i['venta_unidades'])
		total_venta_valor += int(i['venta_valor'])

	metadata_section.append({
		'preproceso': 'false',
		'cantidad de registros': len(json_data),
		'total_venta_unidades': total_venta_unidades,
		'total_venta_valor': total_venta_valor
	})

	json_dict['message']=200	
	json_dict['data']=json_data
	json_dict['metadata_section']=metadata_section	

	return json_dict, 200

@app.route('/api/v1/monthlydata', methods=['GET'])
@jwt_required()
def monthlydata():
	initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
	finaldate = initialdate - datetime.timedelta(30)
	#retail = request.args['retail']
	conn = mariaDBConnection()
	cursor = conn.cursor()
	cursor.execute(
			"""
			SELECT *
			FROM movimiento_api_rest
			WHERE fecha BETWEEN ? AND ?
			LIMIT 500
			""",
			(finaldate, initialdate)
	)

	row_headers=[x[0] for x in cursor.description]
	cursor = cursor.fetchall()

	json_data = []
	json_dict = {}
	metadata_section = []
	total_venta_unidades = 0
	total_venta_valor = 0

	for result in cursor:
		json_data.append(dict(zip(row_headers,result)))

	for i in json_data:
		total_venta_unidades += int(i['venta_unidades'])
		total_venta_valor += int(i['venta_valor'])

	metadata_section.append({
		'preproceso': 'false',
		'cantidad de registros': len(json_data),
		'total_venta_unidades': total_venta_unidades,
		'total_venta_valor': total_venta_valor
	})

	json_dict['message']=200	
	json_dict['data']=json_data
	json_dict['metadata_section']=metadata_section	

	return json_dict, 200

@app.route('/api/v1/filter',  methods=['GET'])
@jwt_required()
def filter():
	initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
	finaldate = datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date()
	retail = request.args['retail']
	comuna = request.args['comuna']
	marca = request.args['marca']
	ciudad = request.args['ciudad']
	conn = mariaDBConnection()
	cursor = conn.cursor()
	cursor.execute(
			"""
			SELECT *
			FROM movimiento_api_rest
			WHERE fecha BETWEEN ? AND ?
			AND s_cadena = ? AND s_comuna = ? AND i_marca = ? AND s_ciudad = ?
			LIMIT 500
			""",
			(initialdate, finaldate, retail, comuna, marca, ciudad)
	)

	row_headers=[x[0] for x in cursor.description]
	cursor = cursor.fetchall()

	json_data = []
	json_dict = {}
	metadata_section = []
	total_venta_unidades = 0
	total_venta_valor = 0

	for result in cursor:
		json_data.append(dict(zip(row_headers,result)))

	for i in json_data:
		total_venta_unidades += int(i['venta_unidades'])
		total_venta_valor += int(i['venta_valor'])

	metadata_section.append({
		'preproceso': 'false',
		'cantidad de registros': len(json_data),
		'total_venta_unidades': total_venta_unidades,
		'total_venta_valor': total_venta_valor
	})

	json_dict['message']=200	
	json_dict['data']=json_data
	json_dict['metadata_section']=metadata_section	

	return json_dict, 200

@app.route('/api/v1/filtercadena',  methods=['GET'])
@jwt_required()
def filtercadena():
	initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
	finaldate = datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date()
	retail = request.args['retail']
	conn = mariaDBConnection()
	cursor = conn.cursor()
	cursor.execute(
			"""
			SELECT *
			FROM movimiento_api_rest
			WHERE fecha BETWEEN ? AND ?
			AND s_cadena = ?
			LIMIT 500
			""",
			(initialdate, finaldate, retail)
	)

	row_headers=[x[0] for x in cursor.description]
	cursor = cursor.fetchall()

	json_data = []
	json_dict = {}
	metadata_section = []
	total_venta_unidades = 0
	total_venta_valor = 0

	for result in cursor:
		json_data.append(dict(zip(row_headers,result)))

	for i in json_data:
		total_venta_unidades += int(i['venta_unidades'])
		total_venta_valor += int(i['venta_valor'])

	metadata_section.append({
		'preproceso': 'false',
		'cantidad de registros': len(json_data),
		'total_venta_unidades': total_venta_unidades,
		'total_venta_valor': total_venta_valor
	})

	json_dict['message']=200	
	json_dict['data']=json_data
	json_dict['metadata_section']=metadata_section	

	return json_dict, 200

@app.route('/api/v1/filtermarca',  methods=['GET'])
@jwt_required()
def filtermarca():
	initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
	finaldate = datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date()
	marca = request.args['marca']
	conn = mariaDBConnection()
	cursor = conn.cursor()
	cursor.execute(
			"""
			SELECT *
			FROM movimiento_api_rest
			WHERE fecha BETWEEN ? AND ?
			AND s_marca = ?
			LIMIT 500
			""",
			(initialdate, finaldate, marca)
	)

	row_headers=[x[0] for x in cursor.description]
	cursor = cursor.fetchall()

	json_data = []
	json_dict = {}
	metadata_section = []
	total_venta_unidades = 0
	total_venta_valor = 0

	for result in cursor:
		json_data.append(dict(zip(row_headers,result)))

	for i in json_data:
		total_venta_unidades += int(i['venta_unidades'])
		total_venta_valor += int(i['venta_valor'])

	metadata_section.append({
		'preproceso': 'false',
		'cantidad de registros': len(json_data),
		'total_venta_unidades': total_venta_unidades,
		'total_venta_valor': total_venta_valor
	})

	json_dict['message']=200	
	json_dict['data']=json_data
	json_dict['metadata_section']=metadata_section	

	return json_dict, 200

@app.route('/api/v1/filterciudad',  methods=['GET'])
@jwt_required()
def filterciudad():
	initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
	finaldate = datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date()
	ciudad = request.args['ciudad']
	conn = mariaDBConnection()
	cursor = conn.cursor()
	cursor.execute(
			"""
			SELECT *
			FROM movimiento_api_rest
			WHERE fecha BETWEEN ? AND ?
			AND s_ciudad = ?
			LIMIT 500
			""",
			(initialdate, finaldate, ciudad)
	)

	row_headers=[x[0] for x in cursor.description]
	cursor = cursor.fetchall()

	json_data = []
	json_dict = {}
	metadata_section = []
	total_venta_unidades = 0
	total_venta_valor = 0

	for result in cursor:
		json_data.append(dict(zip(row_headers,result)))

	for i in json_data:
		total_venta_unidades += int(i['venta_unidades'])
		total_venta_valor += int(i['venta_valor'])

	metadata_section.append({
		'preproceso': 'false',
		'cantidad de registros': len(json_data),
		'total_venta_unidades': total_venta_unidades,
		'total_venta_valor': total_venta_valor
	})

	json_dict['message']=200	
	json_dict['data']=json_data
	json_dict['metadata_section']=metadata_section	

	return json_dict, 200


if __name__ == '__main__':
	app.run(debug=True)