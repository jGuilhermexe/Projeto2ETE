from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, abort
from models import db, Usuario, Tag, UsuarioTag, NumerosAleatorios
from functools import wraps
import random

app_blueprint = Blueprint('app', __name__)

def criar_tabelas():
    from app import app
    with app.app_context():
        db.create_all()

def criar_primeiro_usuario_administrador():
    from app import app
    with app.app_context():
        if not Usuario.query.first():
            primeiro_usuario = Usuario(email='samuelhgsa@gmail.com', nome='The One Above All', senha='12345678admin', cargo='administrador')
            db.session.add(primeiro_usuario)
            db.session.commit()

def gerar_e_salvar_numeros_aleatorios():
    NumerosAleatorios.query.delete()

    for _ in range(15):
        numero = random.randint(1, 30)
        novo_numero = NumerosAleatorios(numero=numero)
        db.session.add(novo_numero)

    db.session.commit()

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
                print('Acesso não autorizado.', 'erro')
                abort(403) 
        else:
            print('Você precisa fazer login primeiro.', 'erro')
            return redirect(url_for('app.login'))
    return decorated_function

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

@app_blueprint.route('/')
def index():
    return render_template('index.html')

@app_blueprint.route('/testar-conexao')
def testar_conexao():
    try:
        Usuario.query.first()
        return 'Conexão com o banco de dados bem-sucedida!'
    except Exception as e:
        return f'Erro ao conectar ao banco de dados: {str(e)}'

@app_blueprint.route('/pagina-de-cadastro', methods=['GET', 'POST'])
def pagina_cadastro():
    if request.method == 'POST':
        try:
            email = request.form['email']
            nome = request.form['nome']
            senha = request.form['senha']

            novo_usuario = Usuario(email=email, nome=nome, senha=senha, cargo='padrao')
            db.session.add(novo_usuario)
            db.session.commit()

            print('Cadastro bem-sucedido! Faça login para continuar.', 'sucesso')
            return redirect(url_for('app.index'))

        except Exception as e:
            print(f"Erro ao cadastrar usuário: {str(e)}", 'erro')

    return render_template('pagina-de-cadastro.html')

@app_blueprint.route('/fazer-login', methods=['GET', 'POST'])
def fazer_login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            senha_digitada = request.form['senha']

            usuario = Usuario.query.filter_by(email=email, senha=senha_digitada).first()

            if usuario:
                session['usuario_id'] = usuario.id
                session['tags_usuario'] = [tag.nome for tag in usuario.tags]
                print('Login bem-sucedido!', 'sucesso')
                print('Redirecionando para o dashboard...')
                return redirect(url_for('app.dashboard'))
            else:
                print('Credenciais inválidas. Tente novamente.', 'erro')
                return redirect(url_for('app.index', _anchor='login-failed'))
                #return 'Login falhou', 400
                #return redirect(url_for('app.index'))

        except Exception as e:
            print(f"Erro ao fazer login: {str(e)}", 'erro')

    return redirect(url_for('app.index'))

@app_blueprint.route('/dashboard')
def dashboard():
    if 'usuario_id' in session:
        return render_template('dashboard.html')
    else:
        print('Você precisa fazer login primeiro.', 'erro')
        return redirect(url_for('app.index'))

@app_blueprint.route('/logout')
def logout():
    session.pop('usuario_id', None)
    print('Logout bem-sucedido!', 'sucesso')
    return redirect(url_for('app.index'))

@app_blueprint.route('/administrar_usuarios')
@admin_required
def administrar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('administrar_usuarios.html', usuarios=usuarios)

@app_blueprint.route('/atualizar_cargo/<int:usuario_id>', methods=['POST'])
def atualizar_cargo(usuario_id):
    if request.method == 'POST':
        try:
            novo_cargo = request.form['novo_cargo']
            usuario = Usuario.query.get(usuario_id)

            if usuario:
                usuario.cargo = novo_cargo
                db.session.commit()
                print('Cargo atualizado com sucesso!', 'success')
            else:
                print('Usuário não encontrado!', 'error')
        except Exception as e:
            print(f"Erro ao atualizar cargo: {str(e)}", 'error')

    return redirect(url_for('app.administrar_usuarios'))

@app_blueprint.route('/adicionar_tag/<int:usuario_id>', methods=['POST'])
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
                print('Tag adicionada com sucesso!', 'success')
            else:
                print('Usuário não encontrado!', 'error')
        except Exception as e:
            print(f"Erro ao adicionar tag: {str(e)}", 'error')

    return redirect(url_for('app.administrar_usuarios'))

@app_blueprint.route('/remover_tag/<int:usuario_id>', methods=['POST'])
def remover_tag(usuario_id):
    if request.method == 'POST':
        try:
            tag_remover = request.form['tag_remover']
            usuario = Usuario.query.get(usuario_id)

            if usuario:
                tag = Tag.query.filter_by(nome=tag_remover).first()
                if tag:
                    usuario.tags.remove(tag)
                    db.session.commit()
                    print('Tag removida com sucesso!', 'success')
                else:
                    print('Tag não encontrada!', 'error')
            else:
                print('Usuário não encontrado!', 'error')
        except Exception as e:
            print(f"Erro ao remover tag: {str(e)}", 'error')

    return redirect(url_for('app.administrar_usuarios'))

@app_blueprint.route('/dados-aleatorios')
def dados_aleatorios():
    try:
        numeros_aleatorios = NumerosAleatorios.query.all()
        
        data1 = [num.numero for num in numeros_aleatorios[:5]]
        data2 = [num.numero for num in numeros_aleatorios[5:10]]
        data3 = [num.numero for num in numeros_aleatorios[10:]]
        
        return jsonify({'data1': data1, 'data2': data2, 'data3': data3})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app_blueprint.route('/filtragem')
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
        print(f"Erro ao obter dados para filtragem: {str(e)}", 'erro')
        return render_template('filtragem.html')

@app_blueprint.route('/sobre-filtragem')
@tag_required(['adm','filtrador'])
def sobre_filtragem():
    return render_template('sobre-filtragem.html')

@app_blueprint.route('/aeradores')
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
        print(f"Erro ao obter dados para aeradores: {str(e)}", 'erro')
        return render_template('aeradores.html')

@app_blueprint.route('/sobre-aeradores')
@tag_required(['adm','aerador'])
def sobre_aeradores():
    return render_template('sobre-aeradores.html')

@app_blueprint.route('/coleta_oleo')
@tag_required(['adm','coletor'])
def coleta_oleo():
    return render_template('coleta_oleo.html')

@app_blueprint.route('/tipos-de-coleta')
@tag_required(['adm','coletor'])
def tipos_de_coleta():
    return render_template('tipos-de-coleta.html')

@app_blueprint.route('/gradeamento-peneiracao')
@tag_required(['adm','gradeador'])
def gradeamento_peneiracao():
    return render_template('gradeamento-peneiracao.html')

@app_blueprint.route('/entenda-gradeamento')
@tag_required(['adm','gradeador'])
def entenda_gradeamento():
    return render_template('entenda-gradeamento.html')

@app_blueprint.route('/arm_agua')
@tag_required(['adm','armazenador'])
def arm_agua():
    return render_template('arm_agua.html')

@app_blueprint.route('/sedimentacao')
@tag_required(['adm','sedimentador'])
def sedimentacao():
    return render_template('sedimentacao.html')

