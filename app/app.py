#!/usr/bin/env python3
import sys
from flask import Flask, jsonify, abort, request, make_response, session
from flask_restful import reqparse, Resource, Api
from flask_session import Session
import json
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import *
import pymysql
import pymysql.cursors
import ssl #include ssl libraries

import settings # Our server and db settings, stored in settings.py

app = Flask(__name__)
#CORS(app)
# Set Server-side session config: Save sessions in the local app directory.
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'chocolateCrinkle'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST

Session(app)

# Error handlers
@app.errorhandler(400) # decorators to add to 400 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Bad request' } ), 400)

@app.errorhandler(404) # decorators to add to 404 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Resource not found' } ), 404)

@app.errorhandler(500) # decorators to add to 500 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Internal server error' } ), 500)


class Root(Resource):
   # get method. What might others be aptly named? (hint: post)
	def get(self):
		return app.send_static_file('index.html')

class Developer(Resource):
   # get method. What might others be aptly named? (hint: post)
	def get(self):
		return app.send_static_file('developer.html')

class SignIn(Resource):
	#
	# Set Session and return Cookie
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X POST -d '{"username": "Rick", "password": "crapcrap"}'
	#  	-c cookie-jar -k https://192.168.10.4:61340/signin
	#
	def post(self):

		if not request.json:
			abort(400) # bad request

		# Parse the json
		parser = reqparse.RequestParser()
		try:
 			# Check for required attributes in json document, create a dictionary
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400) # bad request
		if request_params['username'] in session:
			response = {'status': 'success'}
			responseCode = 200
		else:
			try:
				ldapServer = Server(host=settings.LDAP_HOST)
				ldapConnection = Connection(ldapServer,
					raise_exceptions=True,
					user='uid='+request_params['username']+', ou=People,ou=fcs,o=unb',
					password = request_params['password'])
				ldapConnection.open()
				ldapConnection.start_tls()
				ldapConnection.bind()
				# At this point we have sucessfully authenticated.
				session['username'] = request_params['username']
				# Stuff in here to find the esiting userId or create a use and get the created userId
				response = {'status': 'success', 'user_id':'1' }
				responseCode = 201
			except LDAPException:
				response = {'status': 'Access denied'}
				print(response)
				responseCode = 403
			finally:
				ldapConnection.unbind()

		return make_response(jsonify(response), responseCode)

	# GET: Check Cookie data with Session data
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X GET
	#	-b cookie-jar -k https://192.168.10.4:61340/signin
	def get(self):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success', 'username': username}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)

class User(Resource):

	# GET: Return an identified User (by ID).
	def get(self, userId):

		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail', 'message': 'Access Denied'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUserById'
			cursor = dbConnection.cursor()
			sqlArgs = (userId,)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchone() # get the single result
			if row is None:
				response = {'status': 'fail', 'message': 'Not Found'}
				responseCode = 404
			else:
				response = {'user': row }
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify(response), responseCode) # successful

	def delete(self, userId):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail', 'message': 'Access Denied'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

		# Get Executing User
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUserByName'
			cursor = dbConnection.cursor()
			sqlArgs = (username,)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			user = cursor.fetchone()
			if user is None:
				abort(404)
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()

		# Only allow deletion by an admin
		if not user["isAdmin"]:
			response = {'status': 'fail', 'message': 'Access Denied'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

		# Delete User
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'removeUser'
			cursor = dbConnection.cursor()
			sqlArgs = (userId, user["userID"],)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			dbConnection.commit()
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"status": "success"}), 200) # successful

class Users(Resource):
    # GET: Return all User resources.
	#
	# Example request: curl -i -H "Content-Type: application/json" -X GET
	# -b cookie-jar -k https://192.168.10.4:61340/users
	def get(self):

		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail', 'message': 'Access Denied'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUsers'
			cursor = dbConnection.cursor()
			cursor.callproc(sql) # stored procedure, no arguments
			rows = cursor.fetchall() # get all the results
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({'user': rows}), 200)

	def post(self):
		#
		# Sample command line usage:
		#
		# curl -i -X POST -H "Content-Type: application/json"
		#	-d '{"Name": "Ricks School of Web", "Province": "NB", "Language":
		#		  "EN", "Level": "simple"}'
		#		 cookie-jar -k https://192.168.10.4:61340/user

		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail', 'message': 'Access Denied'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)
		if not request.json or not 'Name' in request.json:
			response = {'status': 'fail', 'message': 'Bad Request'}
			responseCode = 400
			return make_response(jsonify(response), responseCode)

		name = request.json['Name']
		isAdmin = 0

		# Get executing user
		try:
			dbConnection = pymysql.connect(settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getUserByName'
			cursor = dbConnection.cursor()
			sqlArgs = (username,)
			cursor.callproc(sql,sqlArgs)
			user = cursor.fetchone()
			if user is None:
				abort(404)
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()

		# Only allow users to make a user under their own name
		if username != name and not user["isAdmin"]:
			response = {'status': 'fail', 'message': 'Access Denied'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

		try:
			dbConnection = pymysql.connect(settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'addUser'
			cursor = dbConnection.cursor()
			sqlArgs = (name, isAdmin)
			cursor.callproc(sql,sqlArgs)
			row = cursor.fetchone()
			dbConnection.commit()
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()
		# Return user ID
		ID = row['LAST_INSERT_ID()']
		return make_response(jsonify( { "userID" : ID } ), 201) # successful resource creation


class Present(Resource):
	# GET: Return identified present resource (present by ID)
	#
	# Example request: curl -i -H "Content-Type: application/json" -X GET 
	# -b cookie-jar -k https://192.168.10.4:61340/present/2
	#
	def get(self, presentId):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getPresentById'
			cursor = dbConnection.cursor()
			sqlArgs = (presentId,)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchone() # get the single result
			if row is None:
				abort(404)
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"present": row}), 200) # successful

	# TODO: VALIDATE VALIDATE VALIDATE VALIDATE
	def post(self, presentId):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		if not request.json:
			abort(400)
		presentName = request.json["presentName"]
		presentDesc = request.json["presentDesc"]
		presentPrice = request.json["presentPrice"]
		userId = request.json["userId"]
		
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'updatePresent'
			cursor = dbConnection.cursor()
			sqlArgs = (presentId, presentName, presentDesc, presentPrice, userId,)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			dbConnection.commit()
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"status": "success"}), 200) # successful


	def delete(self, presentId):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'removePresent'
			cursor = dbConnection.cursor()
			# TODO: Supposed to grab executing user from cookies :(
			sqlArgs = (presentId, 1)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			dbConnection.commit()
			
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"status": "success"}), 200) # successful

class Presents(Resource):
    # GET: Return identified present resources belonging to a specified user (presnt by userID)
	#
	# Example request: curl -i -H "Content-Type: application/json" -X GET 
	# -b cookie-jar -k https://192.168.10.4:61340/userPresents/2
	#
	def get(self, userId):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'getPresentsByUser'
			cursor = dbConnection.cursor()
			sqlArgs = (userId)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchall() # get the single result
			if row is None:
				abort(404)
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"present": row}), 200) # successful

	# TODO: VALIDATE VALIDATE VALIDATE VALIDATE
	def post(self, userId):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403
		if not request.json:
			abort(400)
		presentName = request.json["presentName"]
		presentDesc = request.json["presentDesc"]
		presentPrice = request.json["presentPrice"]
		
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql = 'addPresent'
			cursor = dbConnection.cursor()
			sqlArgs = (presentName, presentDesc, presentPrice, userId,)
			cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
			row = cursor.fetchone() # get the single result
			if row is None:
				abort(404)
			dbConnection.commit()
		except:
			abort(500) # Nondescript server error
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"present": row}), 200) # successful

# Identify/create endpoints and endpoint objects
api = Api(app)
api.add_resource(Root,'/')
api.add_resource(Developer,'/dev')
api.add_resource(SignIn, '/signin')
api.add_resource(Present, '/present/<int:presentId>')
api.add_resource(Presents, '/presents/<int:userId>')
api.add_resource(User, '/user/<int:userId>')
api.add_resource(Users, '/users')

if __name__ == "__main__":
	#
	# You need to generate your own certificates. To do this:
	#	1. cd to the directory of this app
	#	2. run the makeCert.sh script and answer the questions.
	#	   It will by default generate the files with the same names specified below.
	#
	context = ('cert.pem', 'key.pem') # Identify the certificates you've generated.
	app.run(
		host=settings.APP_HOST,
		port=settings.APP_PORT,
		ssl_context=context,
		debug=settings.APP_DEBUG)
