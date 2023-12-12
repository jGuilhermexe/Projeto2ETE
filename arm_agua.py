from flask import Flask, render_template
import matplotlib.pyplot as plt
import numpy as np
import base64
import io

app = Flask(__name__)

@app.route('/')
def home():
    labels = ['agua no armazenamento', 'espaço restante']
    min_number = 10
    max_number = 100
    n = len(labels)

    random_values = random_numbers(min_number, max_number, n)

    # Matplotlib stuff
    plt.figure(figsize=(6,6))
    plt.pie(random_values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')

    # Converto a figura do gráfico em uma string de base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('arm-agua.html', plot_url=plot_url)

def random_numbers(min, max, n):
    return np.random.randint()
#teste1