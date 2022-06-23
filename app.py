from flask import Flask, jsonify, request, render_template, Response
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_swagger import swagger
from auth import mariaDBConnection
from pymongo import MongoClient
import datetime
import bcrypt
#from flask_cors import CORS, cross_origin
#from waitress import serve

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1000
#CORS(app)

jwt = JWTManager(app) # initialize JWTManager
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
app.config['JWT_SECRET_KEY'] = 'f8de2f7257f913eecfa9aae8a3c7750e'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=23) # define the life span of the token

@app.route('/')
def home():
	return render_template('swaggerui.html')

@app.route('/api/v1/login', methods=['POST'])
def login():
	client = MongoClient("mongodb+srv://api-capel-access:EpNtgYI8X66oR2O4@cademsmart0.hj6jy.mongodb.net/?retryWrites=true&w=majority")
	db = client["api-capel"]
	users_collection = db["users"]
	login_details = request.args # store the json body request
	user_from_db = users_collection.find_one({'username': login_details['username']})  # search for user in database

	if user_from_db:
		decrpted_password = bcrypt.checkpw(login_details['password'].encode(), user_from_db['password'].encode())

		if decrpted_password:
			access_token = create_access_token(identity=user_from_db['username']) # create jwt token
			app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=user_from_db['duration_token_in_hours']) # define the life span of the token
			return jsonify(access_token=access_token), 200

	return jsonify({'msg': 'ACCESS_FAILURE'}), 401

@app.route('/api/v1/data', methods=['GET'])
@jwt_required()
def data():
	client = MongoClient("mongodb+srv://api-capel-access:EpNtgYI8X66oR2O4@cademsmart0.hj6jy.mongodb.net/?retryWrites=true&w=majority")
	db = client["api-capel"]
	conf_collection = db['configuraciones']
	errorDocument = conf_collection.find({})
	for error in errorDocument:
		allowedSize = error['ERR_RESPONSE_TOO_LARGE']

	if request.args.get('initialdate') == None and request.args.get('finaldate') == None:
		return jsonify({'error': 'ERR_DATES_NOT_DEFINED', 'message': 'En la petición no se está enviando la fecha.'}), 400
	elif request.args.get('initialdate') == None:	
		return jsonify({'error': 'ERR_FILTERS_EMPTY', 'message': 'Uno o más de los filtros enviados en la petición están vacíos.'}), 400
	elif request.args.get('finaldate') == None:
		return jsonify({'error': 'ERR_FILTERS_EMPTY', 'message': 'Uno o más de los filtros enviados en la petición están vacíos.'}), 400
	elif str(request.args.get('initialdate')).isdigit() == False or str(request.args.get('finaldate')).isdigit() == False:
		return jsonify({'error': 'ERR_DATES_FORMAT', 'message': 'Las fechas enviadas tiene un formato incorrecto. El formato correcto es: YYYYMMDD'}), 400	
	elif datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date() > datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date():
		return jsonify({'error': 'ERR_DIFF_DATE', 'message': 'La fecha inicio es mayor a la fecha fin.'}), 400
	else:
		initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
		finaldate = datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date()
		conn = mariaDBConnection()
		cursor = conn.cursor()
		cursor.execute(
				"""
				SELECT *
				FROM `b2b-api`.movimiento_api_rest
				WHERE fecha BETWEEN ? AND ?
				ORDER BY fecha ASC
				""",
				(initialdate, finaldate)
		)

		row_headers=[x[0] for x in cursor.description]
		cursor = cursor.fetchall()

		json_data = []
		json_dict = {}
		metadata = []
		total_venta_unidades = 0.0
		total_venta_valor = 0.0

		for result in cursor:
			json_data.append(dict(zip(row_headers,result)))

		if len(json_data) < int(allowedSize):

			for i in json_data:
				i['fecha'] = i['fecha'].strftime("%d-%m-%Y")
				if i['venta_unidades'] != None:
					total_venta_unidades += int(i['venta_unidades'])
				if i['venta_valor'] != None:
					total_venta_valor += int(i['venta_valor'])
				
			cursorb = conn.cursor()
			cursorb.execute("Select * from `b2b-api`.flags")
			flag = cursorb.fetchall()[0][0]

			metadata.append({
				'reproceso': flag,
				'cantidad de registros': len(json_data),
				'total_venta_unidades': total_venta_unidades,
				'total_venta_valor': total_venta_valor
			})

			json_dict['message']=200	
			json_dict['data']=json_data
			json_dict['metadata']=metadata
		
			return json_dict, 200

		return jsonify({'error': 'ERR_RESPONSE_TOO_LARGE', 'message': 'El tamaño de la información solicitada es demasiado grande y se requiere utilizar filtros.'}), 400

@app.route('/api/v1/dailydata', methods=['GET'])
@jwt_required()
def dailydata():
	client = MongoClient("mongodb+srv://api-capel-access:EpNtgYI8X66oR2O4@cademsmart0.hj6jy.mongodb.net/?retryWrites=true&w=majority")
	db = client["api-capel"]
	conf_collection = db['configuraciones']
	errorDocument = conf_collection.find({})
	for error in errorDocument:
		allowedSize = error['ERR_RESPONSE_TOO_LARGE']

	if request.args.get('initialdate') == None:
		return jsonify({'error': 'ERR_DATES_NOT_DEFINED', 'message': 'En la petición no se está enviando la fecha.'}), 400
	elif str(request.args.get('initialdate')).isdigit() == False:
		return jsonify({'error': 'ERR_DATES_FORMAT', 'message': 'Las fechas enviadas tiene un formato incorrecto. El formato correcto es: YYYYMMDD'}), 400	
	else:
		initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
		finaldate = initialdate - datetime.timedelta(2)
		conn = mariaDBConnection()
		cursor = conn.cursor()
		cursor.execute(
				"""
				SELECT *
				FROM `b2b-api`.movimiento_api_rest
				WHERE fecha BETWEEN ? AND ?
				""",
				(str(finaldate), str(initialdate))
		)

		row_headers=[x[0] for x in cursor.description]
		cursor = cursor.fetchall()

		json_data = []
		json_dict = {}
		metadata = []
		total_venta_unidades = 0
		total_venta_valor = 0

		for result in cursor:
			json_data.append(dict(zip(row_headers,result)))

		if len(json_data) < int(allowedSize):
			for i in json_data:
				i['fecha'] = i['fecha'].strftime("%d-%m-%Y")
				if i['venta_unidades'] != None:
					total_venta_unidades += int(i['venta_unidades'])
				if i['venta_valor'] != None:
					total_venta_valor += int(i['venta_valor'])

			cursorb = conn.cursor()
			cursorb.execute("Select * from `b2b-api`.flags")
			flag = cursorb.fetchall()[0][0]

			metadata.append({
				'reproceso': flag,
				'cantidad de registros': len(json_data),
				'total_venta_unidades': total_venta_unidades,
				'total_venta_valor': total_venta_valor
			})

			json_dict['message']=200	
			json_dict['data']=json_data
			json_dict['metadata']=metadata

			try:
				return json_dict, 200
			except Exception as error:
				print(error)

		return jsonify({'error': 'ERR_RESPONSE_TOO_LARGE', 'message': 'El tamaño de la información solicitada es demasiado grande y se requiere utilizar filtros.'}), 400

@app.route('/api/v1/monthlydata', methods=['GET'])
@jwt_required()
def monthlydata():
	client = MongoClient("mongodb+srv://api-capel-access:EpNtgYI8X66oR2O4@cademsmart0.hj6jy.mongodb.net/?retryWrites=true&w=majority")
	db = client["api-capel"]
	conf_collection = db['configuraciones']
	errorDocument = conf_collection.find({})
	for error in errorDocument:
		allowedSize = error['ERR_RESPONSE_TOO_LARGE']

	if request.args.get('initialdate') == None:
		return jsonify({'error': 'ERR_DATES_NOT_DEFINED', 'message': 'En la petición no se está enviando la fecha.'}), 400
	elif str(request.args.get('initialdate')).isdigit() == False:
		return jsonify({'error': 'ERR_DATES_FORMAT', 'message': 'Las fechas enviadas tiene un formato incorrecto. El formato correcto es: YYYYMMDD'}), 400	
	else:
		initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
		finaldate = initialdate - datetime.timedelta(30)
		#retail = request.args['retail']
		conn = mariaDBConnection()
		cursor = conn.cursor()
		cursor.execute(
				"""
				SELECT *
				FROM `b2b-api`.movimiento_api_rest
				WHERE fecha BETWEEN ? AND ?
				""",
				(str(finaldate), initialdate)
		)

		row_headers=[x[0] for x in cursor.description]
		cursor = cursor.fetchall()

		json_data = []
		json_dict = {}
		metadata = []
		total_venta_unidades = 0
		total_venta_valor = 0

		for result in cursor:
			json_data.append(dict(zip(row_headers,result)))

		if len(json_data) < int(allowedSize):
			for i in json_data:
				i['fecha'] = i['fecha'].strftime("%d-%m-%Y")
				if i['venta_unidades'] != None:
					total_venta_unidades += int(i['venta_unidades'])
				if i['venta_valor'] != None:
					total_venta_valor += int(i['venta_valor'])
			
			metadata.append({
				'reproceso': 'false',
				'cantidad de registros': len(json_data),
				'total_venta_unidades': total_venta_unidades,
				'total_venta_valor': total_venta_valor
			})

			json_dict['message']=200	
			json_dict['data']=json_data
			json_dict['metadata']=metadata	

			try:
				return json_dict, 200
			except Exception as error:
				print(error)

		return jsonify({'error': 'ERR_RESPONSE_TOO_LARGE', 'message': 'El tamaño de la información solicitada es demasiado grande y se requiere utilizar filtros.'}), 400
		

@app.route('/api/v1/filter',  methods=['GET'])
@jwt_required()
def filter():
	client = MongoClient("mongodb+srv://api-capel-access:EpNtgYI8X66oR2O4@cademsmart0.hj6jy.mongodb.net/?retryWrites=true&w=majority")
	db = client["api-capel"]
	conf_collection = db['configuraciones']
	errorDocument = conf_collection.find({})
	for error in errorDocument:
		allowedSize = error['ERR_RESPONSE_TOO_LARGE']
	
	if request.args.get('initialdate') == None and request.args.get('finaldate') == None:
		return jsonify({'error': 'ERR_DATES_NOT_DEFINED', 'message': 'En la petición no se está enviando la fecha.'}), 400
	elif request.args.get('initialdate') == None or request.args.get('finaldate') == None or request.args.get('retail') == None or request.args.get('comuna') == None or request.args.get('retail') == None:
		return jsonify({'error': 'ERR_FILTERS_EMPTY', 'message': 'Uno o más de los filtros enviados en la petición están vacíos.'}), 400
	elif str(request.args.get('initialdate')).isdigit() == False or str(request.args.get('finaldate')).isdigit() == False:
		return jsonify({'error': 'ERR_DATES_FORMAT', 'message': 'Las fechas enviadas tiene un formato incorrecto. El formato correcto es: YYYYMMDD'}), 400	
	elif datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date() > datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date():
		return jsonify({'error': 'ERR_DIFF_DATE', 'message': 'La fecha inicio es mayor a la fecha fin.'}), 400
	else:
	
		initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
		finaldate = datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date()
		retail = request.args['retail']
		comuna = request.args['comuna']
		marca = request.args['marca']
		#ciudad = request.args['ciudad']
		conn = mariaDBConnection()
		cursor = conn.cursor()
		cursor.execute(
				"""
				SELECT *
				FROM `b2b-api`.movimiento_api_rest
				WHERE fecha BETWEEN ? AND ?
				AND s_cadena = ? AND s_comuna = ? AND i_marca = ?
				""",
				(initialdate, finaldate, retail, comuna, marca)
		)

		row_headers=[x[0] for x in cursor.description]
		cursor = cursor.fetchall()

		json_data = []
		json_dict = {}
		metadata = []
		total_venta_unidades = 0
		total_venta_valor = 0

		for result in cursor:
			json_data.append(dict(zip(row_headers,result)))

		if len(json_data) < int(allowedSize):
			for i in json_data:
				i['fecha'] = i['fecha'].strftime("%d-%m-%Y")
				if i['venta_unidades'] != None:
					total_venta_unidades += int(i['venta_unidades'])
				if i['venta_valor'] != None:
					total_venta_valor += int(i['venta_valor'])
			
			cursorb = conn.cursor()
			cursorb.execute("Select * from `b2b-api`.flags")
			flag = cursorb.fetchall()[0][0]

			metadata.append({
				'reproceso': flag,
				'cantidad de registros': len(json_data),
				'total_venta_unidades': total_venta_unidades,
				'total_venta_valor': total_venta_valor
			})

			json_dict['message']=200	
			json_dict['data']=json_data
			json_dict['metadata']=metadata	

			try:
				return json_dict, 200
			except Exception as error:
				print(error)

		return jsonify({'error': 'ERR_RESPONSE_TOO_LARGE', 'message': 'El tamaño de la información solicitada es demasiado grande y se requiere utilizar filtros.'}), 400

@app.route('/api/v1/filtercadena',  methods=['GET'])
@jwt_required()
def filtercadena():
	client = MongoClient("mongodb+srv://api-capel-access:EpNtgYI8X66oR2O4@cademsmart0.hj6jy.mongodb.net/?retryWrites=true&w=majority")
	db = client["api-capel"]
	conf_collection = db['configuraciones']
	errorDocument = conf_collection.find({})
	for error in errorDocument:
		allowedSize = error['ERR_RESPONSE_TOO_LARGE']

	if request.args.get('initialdate') == None and request.args.get('retail') == None:
		return jsonify({'error': 'ERR_DATES_NOT_DEFINED', 'message': 'En la petición no se está enviando la fecha.'}), 400
	elif request.args.get('initialdate') == None or request.args.get('finaldate') == None or request.args.get('retail') == None:	
		return jsonify({'error': 'ERR_FILTERS_EMPTY', 'message': 'Uno o más de los filtros enviados en la petición están vacíos.'}), 400
	elif str(request.args.get('initialdate')).isdigit() == False:
		return jsonify({'error': 'ERR_DATES_FORMAT', 'message': 'Las fechas enviadas tiene un formato incorrecto. El formato correcto es: YYYYMMDD'}), 400
	elif datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date() > datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date():
		return jsonify({'error': 'ERR_DIFF_DATE', 'message': 'La fecha inicio es mayor a la fecha fin.'}), 400
	else:
		initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
		finaldate = datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date()
		retail = request.args['retail']
		conn = mariaDBConnection()
		cursor = conn.cursor()
		cursor.execute(
				"""
				SELECT *
				FROM `b2b-api`.movimiento_api_rest
				WHERE fecha BETWEEN ? AND ?
				AND s_cadena = ?
				""",
				(str(initialdate), str(finaldate), retail)
		)

		row_headers=[x[0] for x in cursor.description]
		cursor = cursor.fetchall()

		json_data = []
		json_dict = {}
		metadata = []
		total_venta_unidades = 0
		total_venta_valor = 0

		for result in cursor:
			json_data.append(dict(zip(row_headers,result)))

		if len(json_data) < int(allowedSize):

			for i in json_data:
				i['fecha'] = i['fecha'].strftime("%d-%m-%Y")
				if i['venta_unidades'] != None:
					total_venta_unidades += int(i['venta_unidades'])
				if i['venta_valor'] != None:
					total_venta_valor += int(i['venta_valor'])

			cursorb = conn.cursor()
			cursorb.execute("Select * from `b2b-api`.flags")
			flag = cursorb.fetchall()[0][0]

			metadata.append({
				'reproceso': flag,
				'cantidad de registros': len(json_data),
				'total_venta_unidades': total_venta_unidades,
				'total_venta_valor': total_venta_valor
			})

			json_dict['message']=200	
			json_dict['data']=json_data
			json_dict['metadata']=metadata	

			try:
				return json_dict, 200
			except Exception as error:
				print(error)

		return jsonify({'error': 'ERR_RESPONSE_TOO_LARGE', 'message': 'El tamaño de la información solicitada es demasiado grande y se requiere utilizar filtros.'}), 400
		
@app.route('/api/v1/filtermarca',  methods=['GET'])
@jwt_required()
def filtermarca():
	client = MongoClient("mongodb+srv://api-capel-access:EpNtgYI8X66oR2O4@cademsmart0.hj6jy.mongodb.net/?retryWrites=true&w=majority")
	db = client["api-capel"]
	conf_collection = db['configuraciones']
	errorDocument = conf_collection.find({})
	for error in errorDocument:
		allowedSize = error['ERR_RESPONSE_TOO_LARGE']

	if request.args.get('initialdate') == None and request.args.get('retail') == None:
		return jsonify({'error': 'ERR_DATES_NOT_DEFINED', 'message': 'En la petición no se está enviando la fecha.'}), 400
	elif request.args.get('initialdate') == None or request.args.get('finaldate') == None or request.args.get('marca') == None:	
		return jsonify({'error': 'ERR_FILTERS_EMPTY', 'message': 'Uno o más de los filtros enviados en la petición están vacíos.'}), 400
	elif str(request.args.get('initialdate')).isdigit() == False:
		return jsonify({'error': 'ERR_DATES_FORMAT', 'message': 'Las fechas enviadas tiene un formato incorrecto. El formato correcto es: YYYYMMDD'}), 400
	elif datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date() > datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date():
		return jsonify({'error': 'ERR_DIFF_DATE', 'message': 'La fecha inicio es mayor a la fecha fin.'}), 400
	else:
		initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
		finaldate = datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date()
		marca = request.args['marca']
		conn = mariaDBConnection()
		cursor = conn.cursor()
		cursor.execute(
				"""
				SELECT *
				FROM `b2b-api`.movimiento_api_rest
				WHERE fecha BETWEEN ? AND ?
				AND i_marca = ?
				""",
				(initialdate, finaldate, marca)
		)

		row_headers=[x[0] for x in cursor.description]
		cursor = cursor.fetchall()

		json_data = []
		json_dict = {}
		metadata = []
		total_venta_unidades = 0
		total_venta_valor = 0

		for result in cursor:
			json_data.append(dict(zip(row_headers,result)))

		if len(json_data) < int(allowedSize):

			for i in json_data:
				i['fecha'] = i['fecha'].strftime("%d-%m-%Y")
				if i['venta_unidades'] != None:
					total_venta_unidades += int(i['venta_unidades'])
				if i['venta_valor'] != None:
					total_venta_valor += int(i['venta_valor'])

			cursorb = conn.cursor()
			cursorb.execute("Select * from `b2b-api`.flags")
			flag = cursorb.fetchall()[0][0]

			metadata.append({
				'reproceso': flag,
				'cantidad de registros': len(json_data),
				'total_venta_unidades': total_venta_unidades,
				'total_venta_valor': total_venta_valor
			})

			json_dict['message']=200	
			json_dict['data']=json_data
			json_dict['metadata']=metadata	

			try:
				return json_dict, 200
			except Exception as error:
				print(error)

		return jsonify({'error': 'ERR_RESPONSE_TOO_LARGE', 'message': 'El tamaño de la información solicitada es demasiado grande y se requiere utilizar filtros.'}), 400

@app.route('/api/v1/filterciudad',  methods=['GET'])
@jwt_required()
def filterciudad():
	client = MongoClient("mongodb+srv://api-capel-access:EpNtgYI8X66oR2O4@cademsmart0.hj6jy.mongodb.net/?retryWrites=true&w=majority")
	db = client["api-capel"]
	conf_collection = db['configuraciones']
	errorDocument = conf_collection.find({})
	for error in errorDocument:
		allowedSize = error['ERR_RESPONSE_TOO_LARGE']

	if request.args.get('initialdate') == None and request.args.get('retail') == None:
		return jsonify({'error': 'ERR_DATES_NOT_DEFINED', 'message': 'En la petición no se está enviando la fecha.'}), 400
	elif request.args.get('initialdate') == None or request.args.get('finaldate') == None or request.args.get('ciudad') == None:	
		return jsonify({'error': 'ERR_FILTERS_EMPTY', 'message': 'Uno o más de los filtros enviados en la petición están vacíos.'}), 400
	elif str(request.args.get('initialdate')).isdigit() == False:
		return jsonify({'error': 'ERR_DATES_FORMAT', 'message': 'Las fechas enviadas tiene un formato incorrecto. El formato correcto es: YYYYMMDD'}), 400
	elif datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date() > datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date():
		return jsonify({'error': 'ERR_DIFF_DATE', 'message': 'La fecha inicio es mayor a la fecha fin.'}), 400
	else:
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
				""",
				(initialdate, finaldate, ciudad)
		)

		row_headers=[x[0] for x in cursor.description]
		cursor = cursor.fetchall()

		json_data = []
		json_dict = {}
		metadata = []
		total_venta_unidades = 0
		total_venta_valor = 0

		for result in cursor:
			json_data.append(dict(zip(row_headers,result)))

		if len(json_data) < int(allowedSize):

			for i in json_data:
				i['fecha'] = i['fecha'].strftime("%d-%m-%Y")
				if i['venta_unidades'] != None:
					total_venta_unidades += int(i['venta_unidades'])
				if i['venta_valor'] != None:
					total_venta_valor += int(i['venta_valor'])

			cursorb = conn.cursor()
			cursorb.execute("Select * from `b2b-api`.flags")
			flag = cursorb.fetchall()[0][0]

			metadata.append({
				'reproceso': flag,
				'cantidad de registros': len(json_data),
				'total_venta_unidades': total_venta_unidades,
				'total_venta_valor': total_venta_valor
			})

			json_dict['message']=200	
			json_dict['data']=json_data
			json_dict['metadata']=metadata	

			try:
				return json_dict, 200
			except Exception as error:
				print(error)

		return jsonify({'error': 'ERR_RESPONSE_TOO_LARGE', 'message': 'El tamaño de la información solicitada es demasiado grande y se requiere utilizar filtros.'}), 400

@app.route('/api/v1/filtercomuna',  methods=['GET'])
@jwt_required()
def filtercomuna():
	client = MongoClient("mongodb+srv://api-capel-access:EpNtgYI8X66oR2O4@cademsmart0.hj6jy.mongodb.net/?retryWrites=true&w=majority")
	db = client["api-capel"]
	conf_collection = db['configuraciones']
	errorDocument = conf_collection.find({})
	for error in errorDocument:
		allowedSize = error['ERR_RESPONSE_TOO_LARGE']

	if request.args.get('initialdate') == None and request.args.get('retail') == None:
		return jsonify({'error': 'ERR_DATES_NOT_DEFINED', 'message': 'En la petición no se está enviando la fecha.'}), 400
	elif request.args.get('initialdate') == None or request.args.get('finaldate') == None or request.args.get('comuna') == None:	
		return jsonify({'error': 'ERR_FILTERS_EMPTY', 'message': 'Uno o más de los filtros enviados en la petición están vacíos.'}), 400
	elif str(request.args.get('initialdate')).isdigit() == False:
		return jsonify({'error': 'ERR_DATES_FORMAT', 'message': 'Las fechas enviadas tiene un formato incorrecto. El formato correcto es: YYYYMMDD'}), 400
	elif datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date() > datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date():
		return jsonify({'error': 'ERR_DIFF_DATE', 'message': 'La fecha inicio es mayor a la fecha fin.'}), 400
	else:
		initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
		finaldate = datetime.datetime.strptime(request.args.get('finaldate'), "%Y%m%d").date()
		comuna = request.args['comuna']
		conn = mariaDBConnection()
		cursor = conn.cursor()
		cursor.execute(
				"""
				SELECT *
				FROM `b2b-api`.movimiento_api_rest
				WHERE fecha BETWEEN ? AND ?
				AND s_comuna = ?
				""",
				(initialdate, finaldate, comuna)
		)

		row_headers=[x[0] for x in cursor.description]
		cursor = cursor.fetchall()

		json_data = []
		json_dict = {}
		metadata = []
		total_venta_unidades = 0
		total_venta_valor = 0

		for result in cursor:
			json_data.append(dict(zip(row_headers,result)))

		if len(json_data) < int(allowedSize):
			for i in json_data:
				i['fecha'] = i['fecha'].strftime("%d-%m-%Y")
				if i['venta_unidades'] != None:
					total_venta_unidades += int(i['venta_unidades'])
				if i['venta_valor'] != None:
					total_venta_valor += int(i['venta_valor'])

			cursorb = conn.cursor()
			cursorb.execute("Select * from `b2b-api`.flags")
			flag = cursorb.fetchall()[0][0]

			metadata.append({
				'reproceso': flag,
				'cantidad de registros': len(json_data),
				'total_venta_unidades': total_venta_unidades,
				'total_venta_valor': total_venta_valor
			})

			json_dict['message']=200	
			json_dict['data']=json_data
			json_dict['metadata']=metadata	

			try:
				return json_dict, 200
			except Exception as error:
				print(error)
		
		return jsonify({'error': 'ERR_RESPONSE_TOO_LARGE', 'message': 'El tamaño de la información solicitada es demasiado grande y se requiere utilizar filtros.'}), 400
		

@app.route('/api/v1/populate', methods=['GET'])
def populate():
	conn = mariaDBConnection()
	dropcursor= conn.cursor()
	dropcursor.execute("""TRUNCATE `b2b-api`.movimiento_api_rest;""")
	dropcursor.close()

	retailers = ['SMU', 'WALMART', 'TOTTUS', 'CENCOSUD']
	for retailer in retailers:
		datecursor = conn.cursor()
		datecursor.execute(
			"""
			SELECT MAX(fecha), retail
			FROM `b2b-andina`.movimiento 
			GROUP BY retail
			"""
		)

		dateflag = datecursor.fetchall()
		print(f'dateflag: {dateflag}')

		for i in range(0, len(dateflag)):
			if retailer == dateflag[i][1]:
				basedate = datetime.datetime.strptime(str(dateflag[i][0]), "%Y-%m-%d").date()
				
		initialdate = basedate - datetime.timedelta(2)
		cursor = conn.cursor()

		cursor.execute(
			"""
			INSERT INTO `b2b-api`.movimiento_api_rest (
			fecha
			, s_cadena
			, s_cod_local
			, cod_item
			, i_ean
			, i_distribuidor
			, s_comuna
			, s_bandera
			, s_canal
			, s_rut_cadena
			, s_nombre_sala
			, s_descripcion_cadena
			, s_rut_supermercado
			, s_direccion
			, s_ciudad
			, i_marca
			, i_item
			, venta_unidades
			, venta_valor
			, iva
			)
			(
			SELECT
			fecha
			, s_cadena
			, s_cod_local
			, cod_item
			, i_ean
			, i_distribuidor
			, s_comuna
			, s_bandera
			, s_canal
			, s_rut_cadena
			, s_nombre_sala
			, s_descripcion_cadena
			, s_rut_supermercado
			, s_direccion
			, s_ciudad
			, i_marca
			, i_item
			, SUM(venta_unidades) unidades
			, SUM(venta_valor) valor
			, SUM(venta_valor) * 0.19 AS 'iva'
			FROM `b2b-andina`.movimiento
			INNER JOIN `b2b-andina`.store_master ON s_cadena = retail AND s_cod_local = cod_local
			INNER JOIN `b2b-andina`.item_master ON i_ean = ean
			WHERE fecha BETWEEN ? AND ?
			AND s_cadena = ?
			AND i_distribuidor = 'CAPEL'
			GROUP BY
			fecha
			, s_cadena
			, s_cod_local
			, cod_item
			, i_ean
			, i_distribuidor
			, s_comuna
			, s_bandera
			, s_canal
			, s_rut_cadena
			, s_nombre_sala
			, s_descripcion_cadena
			, s_rut_supermercado
			, s_direccion
			, s_ciudad
			, i_marca
			, i_item
			)	
			""",
			(str(initialdate), str(basedate), retailer)
		)

	conn.commit()
	rows = cursor.rowcount

	json_dict = {}
	json_dict['Message'] = 'Succesfull!!'
	json_dict['RowCount'] = rows

	return jsonify(json_dict), 200

@app.errorhandler(500)
def showMessage(error=None):
    message = {
        'status': 500,
        'message': 'El error está del lado del servidor: ' + request.url,
    }
    response = jsonify(message)
    response.status_code = 500
    return response

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=80, debug=True)
