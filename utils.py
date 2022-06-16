import datetime
import logging
from auth import mariaDBConnection
from flask import jsonify, request

def getAllItems(initialdate, finaldate, retail):
	initialdate = datetime.datetime.strptime(initialdate, "%Y%m%d").date()
	finaldate = datetime.datetime.strptime(finaldate, "%Y%m%d").date()
	print(f'{initialdate}, {finaldate}, {retail}')
	conn = mariaDBConnection()
	cursor = conn.cursor()
	cursor.execute(
		"""
		SELECT
		fecha
		, s_rut_cadena
		, s_descripcion_cadena
		, s_rut_supermercado
		, s_cadena
		, s_direccion
		, s_canal
		, s_cod_local
		, s_nombre_sala
		, s_bandera
		, s_comuna
		, s_ciudad
		, i_marca
		, i_distribuidor
		, i_item
		, i_ean
		, SUM(venta_unidades) unidades
		, SUM(venta_valor) valor
		, SUM(venta_volumen) volumen
		, SUM(stock) stock
		, SUM(stock_valorizado) valorizado
		, SUM(volumen_stock) 'stock volumen'
		, SUM(costo) costo
		FROM movimiento
		INNER JOIN store_master ON s_cadena = retail AND s_cod_local = cod_local
		INNER JOIN item_master ON i_ean = ean
		WHERE fecha BETWEEN ? AND ?
		AND retail = ?
		GROUP BY
		fecha
		, s_rut_cadena
		, s_descripcion_cadena
		, s_rut_supermercado
		, s_cadena
		, s_canal
		, s_cod_local
		, s_nombre_sala
		, s_comuna
		, s_ciudad
		, i_marca
		, i_item
		, i_ean
		, i_distribuidor
		LIMIT 500
		""",
		(initialdate, finaldate, retail)
	)

	row_headers=[x[0] for x in cursor.description] #this will extract row headers
	cursor = cursor.fetchall()
	
	json_dict = {}
	json_data = []
  
	for result in cursor:
		json_data.append(dict(zip(row_headers,result)))

	total_venta_unidades = 0
	total_venta_valor = 0

	for i in json_data:
		iva = 1	 
		iva *=(float(i['valor'])*0.19)
		i['iva']=iva
		total_venta_unidades += int(i['unidades'])
		total_venta_valor += int(i['valor'])

	data_section = []
	metadata_section = []

	for i in json_data:
		#if i['valor']:
		data_section.append({
			'fecha': i['fecha'],
            's_cadena': i['s_cadena'],
			's_cod_local': i['s_cod_local'],
			'i_item': i['i_item'],
			'i_ean': i['i_ean'],
			'i_distribuidor': i['i_distribuidor'],
			's_cadena': i['s_cadena'],
			's_bandera': i['s_bandera'],
			's_canal': i['s_canal'],
			's_comuna': i['s_comuna'],
			's_rut_cadena': i['s_rut_cadena'],
			's_descripcion_cadena': i['s_descripcion_cadena'],
			's_direccion': i['s_direccion'],
			's_rut_supermercado': i['s_rut_supermercado'],
			's_nombre_sala': i['s_nombre_sala'],
			's_direccion': i['s_direccion'],
			's_ciudad': i['s_ciudad'],
			'i_marca': i['i_marca'],
			'i_item': i['i_item'],
			'unidades': i['unidades'],
			'valor': i['valor'],
			'iva': i['iva'],
		})

	metadata_section.append({
		'preproceso': 'false',
		'cantidad de registros': len(json_data),
		'total_venta_unidades': total_venta_unidades,
		'total_venta_valor': total_venta_valor
	})

	json_dict['message']=200
	json_dict['data']=data_section
	json_dict['metadata']=metadata_section
	
	return json_dict, 200

def filterItems(initialdate, finaldate, retail, comuna, marca):
	initialdate = datetime.datetime.strptime(initialdate, "%Y%m%d").date()
	finaldate = datetime.datetime.strptime(finaldate, "%Y%m%d").date()
	conn = mariaDBConnection()
	cursor = conn.cursor()
	cursor.execute(
		"""
		SELECT
		fecha
		, s_rut_cadena
		, s_descripcion_cadena
		, s_rut_supermercado
		, s_cadena
		, s_direccion
		, s_canal
		, s_cod_local
		, s_nombre_sala
		, s_bandera
		, s_comuna
		, s_ciudad
		, i_marca
		, i_distribuidor
		, i_item
		, i_ean
		, SUM(venta_unidades) unidades
		, SUM(venta_valor) valor
		, SUM(venta_volumen) volumen
		, SUM(stock) stock
		, SUM(stock_valorizado) valorizado
		, SUM(volumen_stock) 'stock volumen'
		, SUM(costo) costo
		FROM movimiento
		INNER JOIN store_master ON s_cadena = retail AND s_cod_local = cod_local
		INNER JOIN item_master ON i_ean = ean
		WHERE fecha BETWEEN ? AND ? AND retail = ? AND s_comuna = ? AND i_marca = ?
		GROUP BY
		fecha
		, s_rut_cadena
		, s_descripcion_cadena
		, s_rut_supermercado
		, s_cadena
		, s_canal
		, s_cod_local
		, s_nombre_sala
		, s_comuna
		, s_ciudad
		, i_marca
		, i_item
		, i_ean
		, i_distribuidor
		Limit 400
		""",
		(initialdate, finaldate, retail, comuna, marca)
	)

	row_headers=[x[0] for x in cursor.description] #this will extract row headers
	cursor = cursor.fetchall()
	
	json_dict = {}
	json_data = []
	
	for result in cursor:
		json_data.append(dict(zip(row_headers,result)))

	total_venta_unidades = 0
	total_venta_valor = 0

	for i in json_data:
		iva = 1
		iva *=float(i['valor'])
		i['iva']=iva
		total_venta_unidades += int(i['unidades'])
		total_venta_valor += int(i['valor'])

	data_section = []
	metadata_section = []

	for j in json_data:
		#if i['valor']:
		data_section.append({
			'fecha': j['fecha'],
            's_cadena': j['s_cadena'],
			's_cod_local': j['s_cod_local'],
			'i_item': j['i_item'],
			'i_ean': j['i_ean'],
			'i_distribuidor': j['i_distribuidor'],
			's_cadena': j['s_cadena'],
			's_bandera': j['s_bandera'],
			's_canal': j['s_canal'],
			's_rut_cadena': j['s_rut_cadena'],
			's_descripcion_cadena': j['s_descripcion_cadena'],
			's_direccion': j['s_direccion'],
			's_rut_supermercado': j['s_rut_supermercado'],
			's_nombre_sala': j['s_nombre_sala'],
			's_direccion': j['s_direccion'],
			's_ciudad': j['s_ciudad'],
			'i_marca': j['i_marca'],
			'i_item': j['i_item'],
			'unidades': j['unidades'],
			'valor': j['valor'],
			'iva': j['iva'],
		})

	metadata_section.append({
		'preproceso': 'false',
		'cantidad de registros': len(json_data),
		'total_venta_unidades': total_venta_unidades,
		'total_venta_valor': total_venta_valor
	})

	json_dict['message']=200
	json_dict['data']=data_section
	json_dict['metadata']=metadata_section
	
	return jsonify(json_dict), 200

def filterComuna(initialdate, finaldate, retail, comuna):
	initialdate = datetime.datetime.strptime(initialdate, "%Y%m%d").date()
	finaldate = datetime.datetime.strptime(finaldate, "%Y%m%d").date()
	conn = mariaDBConnection()
	cursor = conn.cursor()
	cursor.execute(
		"""
		SELECT
		fecha
		, s_rut_cadena
		, s_descripcion_cadena
		, s_rut_supermercado
		, s_cadena
		, s_direccion
		, s_canal
		, s_cod_local
		, s_nombre_sala
		, s_bandera
		, s_comuna
		, s_ciudad
		, i_marca
		, i_distribuidor
		, i_item
		, i_ean
		, SUM(venta_unidades) unidades
		, SUM(venta_valor) valor
		, SUM(venta_volumen) volumen
		, SUM(stock) stock
		, SUM(stock_valorizado) valorizado
		, SUM(volumen_stock) 'stock volumen'
		, SUM(costo) costo
		FROM movimiento
		INNER JOIN store_master ON s_cadena = retail AND s_cod_local = cod_local
		INNER JOIN item_master ON i_ean = ean
		WHERE fecha BETWEEN ? AND ? AND retail = ? AND s_comuna = ?
		GROUP BY
		fecha
		, s_rut_cadena
		, s_descripcion_cadena
		, s_rut_supermercado
		, s_cadena
		, s_canal
		, s_cod_local
		, s_nombre_sala
		, s_comuna
		, s_ciudad
		, i_marca
		, i_item
		, i_ean
		, i_distribuidor
		Limit 400
		""",
		(initialdate, finaldate, retail, comuna)
	)

	row_headers=[x[0] for x in cursor.description] #this will extract row headers
	cursor = cursor.fetchall()
	
	json_dict = {}
	json_data = []
	
	for result in cursor:
		json_data.append(dict(zip(row_headers,result)))

	total_venta_unidades = 0
	total_venta_valor = 0

	for i in json_data:
		iva = 1
		iva *=float(i['valor'])
		i['iva']=iva
		total_venta_unidades += int(i['unidades'])
		total_venta_valor += int(i['valor'])

	data_section = []
	metadata_section = []

	for j in json_data:
		#if i['valor']:
		data_section.append({
			'fecha': j['fecha'],
            's_cadena': j['s_cadena'],
			's_cod_local': j['s_cod_local'],
			'i_item': j['i_item'],
			'i_ean': j['i_ean'],
			'i_distribuidor': j['i_distribuidor'],
			's_cadena': j['s_cadena'],
			's_bandera': j['s_bandera'],
			's_canal': j['s_canal'],
			's_rut_cadena': j['s_rut_cadena'],
			's_descripcion_cadena': j['s_descripcion_cadena'],
			's_direccion': j['s_direccion'],
			's_comuna': j['s_comuna'],
			's_rut_supermercado': j['s_rut_supermercado'],
			's_nombre_sala': j['s_nombre_sala'],
			's_direccion': j['s_direccion'],
			's_ciudad': j['s_ciudad'],
			'i_marca': j['i_marca'],
			'i_item': j['i_item'],
			'unidades': j['unidades'],
			'valor': j['valor'],
			'iva': j['iva'],
		})

	metadata_section.append({
		'preproceso': 'false',
		'cantidad de registros': len(json_data),
		'total_venta_unidades': total_venta_unidades,
		'total_venta_valor': total_venta_valor
	})

	json_dict['message']=200
	json_dict['data']=data_section
	json_dict['metadata']=metadata_section
	
	return json_dict, 200

def filterMarca(initialdate, finaldate, retail, marca):
	initialdate = datetime.datetime.strptime(initialdate, "%Y%m%d").date()
	finaldate = datetime.datetime.strptime(finaldate, "%Y%m%d").date()
	conn = mariaDBConnection()
	cursor = conn.cursor()
	cursor.execute(
		"""
		SELECT
		fecha
		, s_rut_cadena
		, s_descripcion_cadena
		, s_rut_supermercado
		, s_cadena
		, s_direccion
		, s_canal
		, s_cod_local
		, s_nombre_sala
		, s_bandera
		, s_comuna
		, s_ciudad
		, i_marca
		, i_distribuidor
		, i_item
		, i_ean
		, SUM(venta_unidades) unidades
		, SUM(venta_valor) valor
		, SUM(venta_volumen) volumen
		, SUM(stock) stock
		, SUM(stock_valorizado) valorizado
		, SUM(volumen_stock) 'stock volumen'
		, SUM(costo) costo
		FROM movimiento
		INNER JOIN store_master ON s_cadena = retail AND s_cod_local = cod_local
		INNER JOIN item_master ON i_ean = ean
		WHERE fecha BETWEEN ? AND ? AND retail = ? AND i_marca = ?
		GROUP BY
		fecha
		, s_rut_cadena
		, s_descripcion_cadena
		, s_rut_supermercado
		, s_cadena
		, s_canal
		, s_cod_local
		, s_nombre_sala
		, s_comuna
		, s_ciudad
		, i_marca
		, i_item
		, i_ean
		, i_distribuidor
		Limit 400
		""",
		(initialdate, finaldate, retail, marca)
	)

	row_headers=[x[0] for x in cursor.description] #this will extract row headers
	cursor = cursor.fetchall()
	
	json_dict = {}
	json_data = []
	
	for result in cursor:
		json_data.append(dict(zip(row_headers,result)))

	total_venta_unidades = 0
	total_venta_valor = 0

	for i in json_data:
		iva = 1
		iva *=float(i['valor'])
		i['iva']=iva
		total_venta_unidades += int(i['unidades'])
		total_venta_valor += int(i['valor'])

	data_section = []
	metadata_section = []

	for j in json_data:
		#if i['valor']:
		data_section.append({
			'fecha': j['fecha'],
            's_cadena': j['s_cadena'],
			's_cod_local': j['s_cod_local'],
			'i_item': j['i_item'],
			'i_ean': j['i_ean'],
			'i_distribuidor': j['i_distribuidor'],
			's_cadena': j['s_cadena'],
			's_bandera': j['s_bandera'],
			's_canal': j['s_canal'],
			's_rut_cadena': j['s_rut_cadena'],
			's_descripcion_cadena': j['s_descripcion_cadena'],
			's_direccion': j['s_direccion'],
			's_rut_supermercado': j['s_rut_supermercado'],
			's_nombre_sala': j['s_nombre_sala'],
			's_direccion': j['s_direccion'],
			's_ciudad': j['s_ciudad'],
			'i_marca': j['i_marca'],
			'i_item': j['i_item'],
			'unidades': j['unidades'],
			'valor': j['valor'],
			'iva': j['iva'],
		})

	metadata_section.append({
		'preproceso': 'false',
		'cantidad de registros': len(json_data),
		'total_venta_unidades': total_venta_unidades,
		'total_venta_valor': total_venta_valor
	})

	json_dict['message']=200
	json_dict['data']=data_section
	json_dict['metadata']=metadata_section
	
	return json_dict, 200