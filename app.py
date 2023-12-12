import random
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from pymysql import MySQLError
from werkzeug.local import LocalStack as _ctx_stack

app = Flask(__name__)
app.secret_key = '1'

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'tratamento_db'

mysql = MySQLError(app)

def get_db():
    conn = mysql.connect()
    return conn

def close_db(e=None):
    conn = mysql.connection
    conn.close()

@app.before_request
def criar_tabela():
    if not hasattr(_ctx_stack.top, 'tabela_criada'):
        try:
            with app.app_context(), app.open_resource('schema.sql') as f:
                db = get_db()
                cursor = db.cursor()
                cursor.execute(f.read().decode('utf8'))
                db.commit()
                _ctx_stack.top.tabela_criada = True
        except Exception as e:
            flash(f"Erro ao criar tabela: {str(e)}", 'erro')

def generate_random_data(length):
    return [random.randint(0, 100) for _ in range(length)]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/testar-conexao')
def testar_conexao():
    try:
        with app.app_context(), mysql.connection.cursor() as cur:
            cur.execute("SELECT 1")
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

            conexao = mysql.connect()
            cur = conexao.cursor()
            cur.execute('''
                INSERT INTO usuarios (email, nome, senha)
                VALUES (%s, %s, %s)
            ''', (email, nome, senha))
            conexao.commit()
            cur.close()
            conexao.close()

            flash('Cadastro bem-sucedido! Faça login para continuar.', 'sucesso')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f"Erro ao cadastrar usuário: {str(e)}", 'erro')

    return render_template('pagina-de-cadastro.html')

@app.route('/fazer-login', methods=['POST'])
def fazer_login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            senha_digitada = request.form['senha']

            with app.app_context(), mysql.connection.cursor() as cur:
                cur.execute('''
                    SELECT * FROM usuarios
                    WHERE email = %s AND senha = %s
                ''', (email, senha_digitada))
                usuario = cur.fetchone()

            if usuario:
                session['usuario_id'] = usuario['id']
                flash('Login bem-sucedido!', 'sucesso')
                print('Redirecionando para o dashboard...')
                return redirect(url_for('dashboard'))  
            else:
                flash('Credenciais inválidas. Tente novamente.', 'erro')

        except Exception as e:
            flash(f"Erro ao fazer login: {str(e)}", 'erro')

    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' in session:
        return render_template('dashboard.html')
    else:
        flash('Você precisa fazer login primeiro.', 'erro')
        return redirect(url_for('index'))

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
