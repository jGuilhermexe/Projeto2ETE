from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify, app
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
    cargo = db.Column(db.String(50), nullable=False, default='padrao')
    #tags = db.relationship('Tag', backref='usuario', lazy=True)
    tags = db.relationship('Tag', secondary='usuario_tag', backref='usuarios')

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)

class UsuarioTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)


def criar_tabelas():
    with app.app_context():
        db.create_all()
        
def criar_primeiro_usuario_administrador():
    with app.app_context():
        if not Usuario.query.first():
            primeiro_usuario = Usuario(email='samuelhgsa@gmail.com', nome='The One Above All', senha='12345678admin', cargo='administrador')
            db.session.add(primeiro_usuario)
            db.session.commit()



criar_tabelas()
criar_primeiro_usuario_administrador()

def generate_random_data(length):
    return [random.randint(0, 100) for _ in range(length)]

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' in session:
            usuario = Usuario.query.filter_by(id=session['usuario_id']).first()
            if usuario.cargo == 'administrador':
                return f(*args, **kwargs)
            else:
                flash('Acesso não autorizado.', 'erro')
                return redirect(url_for('index'))
        else:
            flash('Você precisa fazer login primeiro.', 'erro')
            return redirect(url_for('login'))
    return decorated_function

# def tag_required(tags):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             if 'tags_usuario' in session:
#                 tags_usuario = session['tags_usuario']
#                 if any(tag in tags_usuario for tag in tags):
#                     return f(*args, **kwargs)
#             flash('Acesso não autorizado.', 'error')
#             return redirect(url_for('index'))
#         return decorated_function
#     return decorator
def tag_required(tags):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'tags_usuario' in session:
                tags_usuario = session['tags_usuario']
                if any(tag in tags_usuario for tag in tags):
                    return f(*args, **kwargs)
            return jsonify({'error': 'Acesso não autorizado.'}), 403  
        return decorated_function
    return decorator

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

            novo_usuario = Usuario(email=email, nome=nome, senha=senha, cargo='padrao')
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
                session['tags_usuario'] = [tag.nome for tag in usuario.tags]
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

@app.route('/administrar_usuarios')
@admin_required
def administrar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('administrar_usuarios.html', usuarios=usuarios)

@app.route('/atualizar_cargo/<int:usuario_id>', methods=['POST'])
def atualizar_cargo(usuario_id):
    if request.method == 'POST':
        try:
            novo_cargo = request.form['novo_cargo']
            usuario = Usuario.query.get(usuario_id)

            if usuario:
                usuario.cargo = novo_cargo
                db.session.commit()
                flash('Cargo atualizado com sucesso!', 'success')
            else:
                flash('Usuário não encontrado!', 'error')
        except Exception as e:
            flash(f"Erro ao atualizar cargo: {str(e)}", 'error')

    return redirect(url_for('administrar_usuarios'))

@app.route('/adicionar_tag/<int:usuario_id>', methods=['POST'])
def adicionar_tag(usuario_id):
    if request.method == 'POST':
        try:
            nova_tag = request.form['nova_tag']
            usuario = Usuario.query.get(usuario_id)

            if usuario:
                tag = Tag.query.filter_by(nome=nova_tag).first()
                if not tag:
                    tag = Tag(nome=nova_tag)
                    db.session.add(tag)


                usuario.tags.append(tag)
                db.session.commit()
                flash('Tag adicionada com sucesso!', 'success')
            else:
                flash('Usuário não encontrado!', 'error')
        except Exception as e:
            flash(f"Erro ao adicionar tag: {str(e)}", 'error')

    return redirect(url_for('administrar_usuarios'))


@app.route('/filtragem')
@tag_required(['filtrador','adm'])
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
@tag_required(['adm','aerador'])
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