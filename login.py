#para o login (ainda não testado)
from flask import Flask, render_template, request
import hashlib

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    # Recebe os inputs do formulário
    username = request.form['usuario']
    password = request.form['senha']

    # Aplica o hash aos inputs
    hashed_username = hash_content(username)
    hashed_password = hash_content(password)

    #aqui realizar uma comparação com o armazenado no banco de dados

    return f'Usuário: {hashed_username}<br>Senha: {hashed_password}'

def hash_content(content):
    # Cria um objeto de hash SHA-256
    sha256_hash = hashlib.sha256()

    # Atualiza o hash com o conteúdo
    sha256_hash.update(content.encode('utf-8'))

    # Retorna a representação hexadecimal do hash
    return sha256_hash.hexdigest()

if __name__ == '__main__':
    app.run(debug=True)
