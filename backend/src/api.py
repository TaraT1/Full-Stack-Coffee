import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks = Drink.query.all()
    drinks = [drink.short() for drink in all_drinks] #formats (not object, but list)

    try:
        if len(drinks) == 0:
            abort(404) #resource not found

        return jsonify({
            "success": True,
                "drinks": drinks
            }), 200

    except Exception as e:
        print("Exception is >>", e)
        #print(sys.exc_info())
        abort(404)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    all_drinks = Drink.query.all()
    drinks = [drink.long() for drink in all_drinks] #formats (not object, but list)
    
    try:
        if len(drinks) == 0:
            abort(404) #resource not found

        return jsonfy({
            "success": True,
            "drinks": drinks
        }), 200

    except Exception as e:
        print("Exception is >>", e)
        print(sys.exc_info())
        abort(404)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    data = request.get_json()
    new_title = data.get('title')
    new_recipe = data.get('recipe')

    if data is None:
        abort(404)

    try:
        new_drink = Drink(
            title = new_title,
            recipe = json.dumps(new_recipe))
        new_drink.insert()

        '''
        all_drinks = Drink.query.all()
        drinks = [drink.long() for drink in all_drinks]
        '''

        return jsonify({
            "success": True,
            "drinks": [new_drink.long()] #for drink in drinks?
        }), 200

    except Exception as e:
        print("Exception is >>", e)
        print(sys.exc_info())
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    data = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)#resource not found
    
    try:
        drink.title = data.get('title')
        drink.recipe = data.get('recipe')
        drink.update()

        '''
        all_drinks = Drink.query.all()
        drinks = [drink.long() for drink in all_drinks]
        '''

        return jsonify({
            "success": True,
            "drinks": [drink.long()],
            "update": id
        }), 200

    except Exception as e:
        print("Exception is >>", e)
        print(sys.exc_info())
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none
        
        if drink is None:
            abort(404) #resource not found

        drink.delete()

        return jsonify({
            "success": True,
            "delete": id
        }), 200

    except Exception as e:
        print("Exception is >>", e)
        print(sys.exc_info())
        abort(422)




## Error Handling
'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
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
@TODO implement error handler for 404
    error handler should conform to general task above 
'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO implement error handler for AuthError (401)
    error handler should conform to general task above 
'''
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "Unauthorized"
                    }), 401
