from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True, cascade="all, delete-orphan")

    def toDict(self):
      return {
        "id": self.id,
        "username": self.username,
        "email": self.email,
        "num_todos": self.get_num_todos(),
        "num_done": self.get_done_todos()
      }
    
    #hashes the password parameter and stores it in the object
    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')
    
    #Returns true if the parameter is equal to the object's password property
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)
    
    #To String method
    def __repr__(self):
      return '<User {}>'.format(self.username)

    def get_num_todos(self):
      return len(self.todos)
      
    def get_done_todos(self):
        numDone = 0
        for todo in self.todos:
          if todo.done:
            numDone += 1
        return numDone  

class Todo(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  text = db.Column(db.String(255), nullable=False)
  userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #set userid as a foreign key to user.id 
  done = db.Column(db.Boolean, nullable=False)

  def toDict(self):
   return {
     'id': self.id,
     'text': self.text,
     'userid': self.userid,
     'done': self.done
   }