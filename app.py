
from flask import Flask, jsonify, request, render_template, Response
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_swagger import swagger
from auth import mariaDBConnection, mariaDBConnectionII
from pymongo import MongoClient
import datetime
import bcrypt
import sys
#from flask_cors import CORS, cross_origin
#from waitress import serve

app = Flask(__name__)
#CORS(app)

#For production purposes
client = MongoClient("mongodb+srv://api-capel-access:EpNtgYI8X66oR2O4@cademsmart0.hj6jy.mongodb.net/?retryWrites=true&w=majority")
db = client["api-capel"]
users_collection = db["users"]

jwt = JWTManager(app) # initialize JWTManager
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
app.config['JWT_SECRET_KEY'] = 'f8de2f7257f913eecfa9aae8a3c7750e'
TRAP_BAD_REQUEST_ERRORS = True
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=23) # define the life span of the token

@app.route('/')
def home():
	return render_template('swaggerui.html')


@app.route('/api/v1/login', methods=['POST'])
def login():

	login_details = request.args # store the json body request
	user_from_db = users_collection.find_one({'username': login_details['username']})  # search for user in database

	if user_from_db:
		decrpted_password = bcrypt.checkpw(login_details['password'].encode(), user_from_db['password'].encode())

		if decrpted_password:
			access_token = create_access_token(identity=user_from_db['username']) # create jwt token
			#app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=user_from_db['duration_token_in_hours']) # define the life span of the token
			return jsonify(access_token=access_token), 200

	return jsonify({'msg': 'ACCESS_FAILURE'}), 401

@app.route('/api/v1/data', methods=['GET'])
@jwt_required()
def data():
	if request.args.get('initialdate') == None and request.args.get('finaldate') == None:
		message = "ERR_DATES_NOT_DEFINED"
		return jsonify(message), 400
	elif request.args.get('initialdate') == None or request.args.get('finaldate') == None:
		message = "ERR_FILTERS_EMPTY"
		return jsonify(message), 400	
	elif datetime.datetime.strptime(request.args.get('initialdate'), "%Y-%m-%d").date() > datetime.datetime.strptime(request.args.get('finaldate'), "%Y-%m-%d").date():
		message = "ERR_DIFF_DATE"
		return jsonify(message), 400
	elif request.args.get('initialdate') != str(datetime.datetime.strptime(request.args.get('initialdate'), "%Y-%m-%d").date()) or request.args.get('finaldate') != str(datetime.datetime.strptime(request.args.get('finaldate'), "%Y-%m-%d").date()):
		print(request.args.get('initialdate'))
		print(datetime.datetime.strptime(request.args.get('initialdate'), "%Y-%m-%d").date())
		print(request.args.get('finaldate'))
		print(datetime.datetime.strptime(request.args.get('finaldate'), "%Y-%m-%d").date())

		message = ("ERR_DATES_FORMAT")
		return jsonify(message), 400
	else:
		initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y-%m-%d").date()
		finaldate = datetime.datetime.strptime(request.args.get('finaldate'), "%Y-%m-%d").date()
		conn = mariaDBConnection()
		cursor = conn.cursor()
		cursor.execute(
				"""
				SELECT *
				FROM movimiento_api_rest
				WHERE fecha BETWEEN ? AND ?
				""",
				(initialdate, finaldate)
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

		for i in json_data:
			total_venta_unidades += int(i['venta_unidades'])
			total_venta_valor += int(i['venta_valor'])
			i['fecha'] = str(i['fecha'].strftime("%d-%m-%Y"))

		cursorb = conn.cursor()
		cursorb.execute("Select * from flags")
		flag = cursorb.fetchall()[0][0]

		#for result in range(0,1):
		#		print(cursorb.fetchall().index(0))

		metadata.append({
			'reproceso': flag,
			'cantidad de registros': len(json_data),
			'total_venta_unidades': total_venta_unidades,
			'total_venta_valor': total_venta_valor
		})

		json_dict['message']=200	
		json_dict['data']=json_data
		json_dict['metadata']=metadata	

		print(sys.getsizeof(json_dict))

		return json_dict, 200

@app.route('/api/v1/dailydata', methods=['GET'])
@jwt_required()
def dailydata():
	initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
	finaldate = initialdate - datetime.timedelta(3)
	conn = mariaDBConnection()
	cursor = conn.cursor()
	cursor.execute(
			"""
			SELECT *
			FROM movimiento_api_rest
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

	for i in json_data:
		total_venta_unidades += int(i['venta_unidades'])
		total_venta_valor += int(i['venta_valor'])
		i['fecha'] = str(i['fecha'].strftime("%d-%m-%Y"))

	cursorb = conn.cursor()
	cursorb.execute("Select * from flags")
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
			Limit 300
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

	for i in json_data:
		total_venta_unidades += int(i['venta_unidades'])
		total_venta_valor += int(i['venta_valor'])
		i['fecha'] = str(i['fecha'].strftime("%d-%m-%Y"))
	
	metadata.append({
		'reproceso': 'false',
		'cantidad de registros': len(json_data),
		'total_venta_unidades': total_venta_unidades,
		'total_venta_valor': total_venta_valor
	})

	json_dict['message']=200	
	json_dict['data']=json_data
	json_dict['metadata']=metadata	

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
			""",
			(initialdate, finaldate, retail, comuna, marca, ciudad)
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

	for i in json_data:
		total_venta_unidades += int(i['venta_unidades'])
		total_venta_valor += int(i['venta_valor'])
		i['fecha'] = str(i['fecha'].strftime("%d-%m-%Y"))
	
	cursorb = conn.cursor()
	cursorb.execute("Select * from flags")
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

@app.route('/api/v1/filtercadena',  methods=['GET'])
@jwt_required()
def filtercadena():
	initialdate = datetime.datetime.strptime(request.args.get('initialdate'), "%Y%m%d").date()
	print(initialdate)
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

	for i in json_data:
		total_venta_unidades += int(i['venta_unidades'])
		total_venta_valor += int(i['venta_valor'])
		i['fecha'] = str(i['fecha'].strftime("%d-%m-%Y"))

	cursorb = conn.cursor()
	cursorb.execute("Select * from flags")
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

	for i in json_data:
		total_venta_unidades += int(i['venta_unidades'])
		total_venta_valor += int(i['venta_valor'])
		i['fecha'] = str(i['fecha'].strftime("%d-%m-%Y"))

	cursorb = conn.cursor()
	cursorb.execute("Select * from flags")
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

	for i in json_data:
		total_venta_unidades += int(i['venta_unidades'])
		total_venta_valor += int(i['venta_valor'])
		i['fecha'] = str(i['fecha'].strftime("%d-%m-%Y"))

	cursorb = conn.cursor()
	cursorb.execute("Select * from flags")
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

@app.route('/api/v1/filtercomuna',  methods=['GET'])
@jwt_required()
def filtercomuna():
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

	for i in json_data:
		total_venta_unidades += int(i['venta_unidades'])
		total_venta_valor += int(i['venta_valor'])
		i['fecha'] = str(i['fecha'].strftime("%d-%m-%Y"))

	cursorb = conn.cursor()
	cursorb.execute("Select * from flags")
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

@app.route('/api/v1/populate', methods=['GET'])
def populate():
	finaldate = datetime.date.today()
	retailers = ['CENCOSUD', 'SMU', 'WALMART', 'TOTTUS']
	for retailer in retailers:
		connbase = mariaDBConnectionII()
		datecursor = connbase.cursor()
		datecursor.execute("""SELECT MAX(fecha), ? FROM `b2b-andina`.movimiento GROUP BY ?""", (retailer, retailer))
		dateflag = datecursor.fetchall()[0][0]
		print(dateflag)
		initialdate = dateflag - datetime.timedelta(4)
		print(initialdate)
		conn = mariaDBConnection()
		cursor = conn.cursor()
		i_distribuidor = 'CAPEL'

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
			#(str(finaldate), str(initialdate), retailer)
			(str(initialdate), str(dateflag), retailer)
		)
		conn.commit()
		rows = cursor.rowcount

		json_dict = {}
		json_dict['Message'] = 'Succesfull!!'
		json_dict['RowCount'] = rows

		return jsonify(json_dict), 200

if __name__ == '__main__':	
	app.run(host="0.0.0.0", port=5000, debug=True)
