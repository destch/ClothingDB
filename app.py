from flask_migrate import Migrate
from app import create_app, db
from flask import Flask

app = create_app()
app = Flask(__name__)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return(dict(db=db))

if __name__ == '__main__':
    app.run()
