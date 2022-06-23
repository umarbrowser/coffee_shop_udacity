import json
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_available_drinks():
    try:
        available_drinks = Drink.query.order_by(Drink.id).all()
        return jsonify({
            'success': True,
            'drinks': [available_drink.short() for available_drink in available_drinks]
        }), 200
    except Exception:
        abort(404)

'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_available_drinks_detail(payload):
    try:
        available_drinks = Drink.query.order_by(Drink.id).all()
        return jsonify({
            'success': True,
            'drinks': [available_drink.long() for available_drink in available_drinks]
        }), 200
    except Exception:
        abort(503)


'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink(payload):
    try:
        body = request.get_json()
        body_recipe = body['recipe']
        if isinstance(body_recipe, dict):
            body_recipe = [body_recipe]
        new_drink = Drink()
        new_drink.recipe = json.dumps(body_recipe)
        new_drink.title = body['title']
        new_drink.insert()
        
        return jsonify({"success": True, "drinks": [new_drink.long()]})
    except Exception:
        abort(400)
    


'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_individual_drink(payload, drink_id):
    try:
        body = request.get_json()
        drink_to_be_updated = Drink.query.filter(Drink.id==drink_id).one_or_none()
        if not drink_to_be_updated:
            abort(404)
        else:
            if body['title']:
                drink_to_be_updated.title = body['title']
            elif body['recipe']:
                drink_to_be_updated.recipe = json.dumps(body['recipe'])
            drink_to_be_updated.update()
            return jsonify({'success': True, 'drinks': [drink_to_be_updated.long()]}), 200
    except Exception:
        abort(400)


'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_individual_drink(drink_id):
    try:
        drink_to_be_deleted = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if not drink_to_be_deleted:
            abort(404)
        else:
            drink_to_be_deleted.delete()
            return json({"success": True, "deleted": drink_id})
    except Exception:
        abort(400)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": 'resource not found'
    }), 404

'''
@DONE implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401
    
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405
    
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401
    
    
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500
'''
@DONE implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
