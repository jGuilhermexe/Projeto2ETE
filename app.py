from flask import Flask
from models import db
from views import app_blueprint

app = Flask(__name__)
app.secret_key = '1'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tratamento_db.sqlite' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(app_blueprint)

if __name__ == '__main__':
    with app.app_context():
        from views import gerar_e_salvar_numeros_aleatorios
        gerar_e_salvar_numeros_aleatorios()
    app.run(debug=True)
