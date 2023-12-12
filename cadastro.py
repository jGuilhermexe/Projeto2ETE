#ainda não testado, vou precisar de ajuda
from flask import Flask, render_template, request
import hashlib

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['POST'])
def cadastro():
    # Recebe os inputs do formulário de cadastro
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    # Aplica o hash à senha
    hashed_senha = hash_content(senha)

    # armazenar no BD

    return f'Nome: {nome}<br>E-mail: {email}<br>Senha: {hashed_senha}'

def hash_content(content):
    # Cria um objeto de hash SHA-256
    sha256_hash = hashlib.sha256()

    # Atualiza o hash com o conteúdo
    sha256_hash.update(content.encode('utf-8'))

    # Retorna a representação hexadecimal do hash
    return sha256_hash.hexdigest()

if __name__ == '__main__':
    app.run(debug=True)
