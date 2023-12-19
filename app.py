from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify
import flask
from flask_sqlalchemy import SQLAlchemy
#from flask_mysqldb import MySQL
from functools import wraps
import random
from werkzeug.local import LocalStack as _ctx_stack

print(flask.__version__)

app = Flask(__name__)
app.secret_key = '1'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tratamento_db.sqlite' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    nome = db.Column(db.String(255), nullable=False)
    senha = db.Column(db.String(255), nullable=False)

def criar_tabelas():
    with app.app_context():
        db.create_all()

criar_tabelas()

def generate_random_data(length):
    return [random.randint(0, 100) for _ in range(length)]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/testar-conexao')
def testar_conexao():
    try:
        Usuario.query.first()
        return 'Conexão com o banco de dados bem-sucedida!'
    except Exception as e:
        return f'Erro ao conectar ao banco de dados: {str(e)}'

@app.route('/pagina-de-cadastro', methods=['GET', 'POST'])
def pagina_cadastro():
    if request.method == 'POST':
        try:
            email = request.form['email']
            nome = request.form['nome']
            senha = request.form['senha']

            novo_usuario = Usuario(email=email, nome=nome, senha=senha)
            db.session.add(novo_usuario)
            db.session.commit()

            flash('Cadastro bem-sucedido! Faça login para continuar.', 'sucesso')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f"Erro ao cadastrar usuário: {str(e)}", 'erro')

    return render_template('pagina-de-cadastro.html')

@app.route('/fazer-login', methods=['GET', 'POST'])
def fazer_login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            senha_digitada = request.form['senha']

            usuario = Usuario.query.filter_by(email=email, senha=senha_digitada).first()

            if usuario:
                session['usuario_id'] = usuario.id
                flash('Login bem-sucedido!', 'sucesso')
                print('Redirecionando para o dashboard...')
                return redirect(url_for('dashboard'))
            else:
                flash('Credenciais inválidas. Tente novamente.', 'erro')
                return redirect(url_for('index'))

        except Exception as e:
            flash(f"Erro ao fazer login: {str(e)}", 'erro')

    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' in session:
        return render_template('dashboard.html')
    else:
        flash('Você precisa fazer login primeiro.', 'erro')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash('Logout bem-sucedido!', 'sucesso')
    return redirect(url_for('index'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function   

@app.route('/filtragem')
def filtragem():
    try:
        dados_grafico = {
            'data1': generate_random_data(5),
            'data2': generate_random_data(5),
            'data3': generate_random_data(5),
        }
        return render_template('filtragem.html', dados_grafico=dados_grafico)
    except Exception as e:
        flash(f"Erro ao obter dados para filtragem: {str(e)}", 'erro')
        return render_template('filtragem.html')
    
@app.route('/dados-aleatorios')
def dados_aleatorios():
    try:
        dados_grafico = {
            'data1': generate_random_data(5),
            'data2': generate_random_data(5),
            'data3': generate_random_data(5),
        }
        return jsonify(dados_grafico)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/aeradores')
def aeradores():
    try:
        dados_grafico = {
            'data1': generate_random_data(5),
            'data2': generate_random_data(5),
            'data3': generate_random_data(5),
        }
        return render_template('aeradores.html', dados_grafico=dados_grafico)
    except Exception as e:
        flash(f"Erro ao obter dados para aeradores: {str(e)}", 'erro')
        return render_template('aeradores.html')

if __name__ == '__main__':
    app.run(debug=True)