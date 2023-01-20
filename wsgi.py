import click
from models import db
from flask.cli import with_appcontext, AppGroup
from main import app

'''
Generic Commands
'''

@app.cli.command("init")
def initialize():
    db.create_all()
    print('database intialized')

@app.cli.command("run")
def initialize():
    app.run(host='0.0.0.0', port=8080, debug=True)
