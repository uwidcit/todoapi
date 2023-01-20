from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from models import User, Todo, db
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

app = Flask(__name__)


''' Begin boilerplate code '''
def create_app():
  app = Flask(__name__, static_url_path='', static_folder='static')
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
  app.config['JWT_SECRET_KEY'] = "MYSECRET"
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['JWT_EXPIRATION_DELTA'] = timedelta(days = 7) 
  CORS(app)
  db.init_app(app)
  return app

app = create_app()
jwt = JWTManager(app)
app.app_context().push()
db.create_all()


''' End Boilerplate Code '''

def get_user(username):
    return User.query.filter_by(username=username).first()

@app.route('/', methods=['GET'])
def index():
 return app.send_static_file('index.html')

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = get_user(data['username'])
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=data['username'])
        return jsonify(access_token=access_token)
    return jsonify({"msg": "Bad username or password"}), 401

@app.route('/signup', methods=['POST'])
def signup():
  userdata = request.get_json() # get userdata
  newuser = User(username=userdata['username'], email=userdata['email']) # create user object
  newuser.set_password(userdata['password']) # set password
  try:
    db.session.add(newuser)
    db.session.commit() # save user
  except IntegrityError: # attempted to insert a duplicate user
    db.session.rollback()
    return jsonify({ "error" : "username or email already exists"}) # error message
  return jsonify({ "message" : "user created"}) # success

@app.route('/identify')
@jwt_required()
def protected():
    user = get_user(get_jwt_identity())
    return jsonify(user.toDict())

@app.route('/users', methods=['GET'])
def get_users():
  users = User.query.all()
  users_list = [ user.toDict() for user in users ] 
  # convert user objects to list of dictionaries
  return jsonify({ "num_users": len(users_list), "users": users_list })

@app.route('/todos', methods=['POST'])
@jwt_required()
def create_todo():
  data = request.get_json()
  todo = Todo(text=data['text'], userid=get_user(get_jwt_identity()).id, done=False)
  db.session.add(todo)
  db.session.commit()
  return jsonify({ 'id' : todo.id}), 201 # return data and set the message code

@app.route('/todos', methods=['GET'])
@jwt_required()
def get_todos():
  todos = Todo.query.filter_by(userid=get_user(get_jwt_identity()).id).all()
  todos = [todo.toDict() for todo in todos] # list comprehension which converts todo objects to dictionaries
  return jsonify(todos)

@app.route('/todos/<id>', methods=['GET'])
@jwt_required()
def get_todo(id):
  todo = Todo.query.filter_by(userid=get_user(get_jwt_identity()).id, id=id).first()
  if todo == None:
    return jsonify({'error':'Invalid id or unauthorized'})
  return jsonify(todo.toDict())

@app.route('/todos/<id>', methods=['PUT'])
@jwt_required()
def update_todo(id):
  todo = Todo.query.filter_by(userid=get_user(get_jwt_identity()).id, id=id).first()
  if todo == None:
    return jsonify({'error':'Invalid id or unauthorized'})
  data = request.get_json()
  if 'text' in data: # we can't assume what the user is updating so we check for the field
    todo.text = data['text']
  if 'done' in data:
    todo.done = data['done']
  db.session.add(todo)
  db.session.commit()
  return jsonify({'message':'Updated'}), 201

@app.route('/todos/<id>', methods=['DELETE'])
@jwt_required()
def delete_todo(id):
  todo = Todo.query.filter_by(userid=get_user(get_jwt_identity()).id, id=id).first()
  if todo == None:
    return 'Invalid id or unauthorized'
  db.session.delete(todo) # delete the object
  db.session.commit()
  return jsonify({'message':'Deleted'}), 200

@app.route('/stats/todos', methods=['GET'])
@jwt_required()
def get_todo_stats():
  user = User.query.get(get_user(get_jwt_identity()).id)
  if user:
    return jsonify({
      "num_todos": user.get_num_todos(),
      "num_done": user.get_done_todos()
    })
  else :
    return jsonify({'message': 'User not found'}), 404


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)