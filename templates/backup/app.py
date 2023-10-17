import secrets
from flask import Flask, request, jsonify, render_template, redirect, url_for
import requests
import json

app = Flask(__name__)

app.static_folder = 'templates/static'

api_keys = {}
cidades = ['São Paulo', 'Nova York', 'Cidade do México', 'Paris', 'Tóquio', 'Londres', 'Roma', 'Sydney']

def gerar_api_key():
    return secrets.token_urlsafe(32)

@app.route('/')
def inicioprevisao():
    return render_template('index.html', cidades=cidades)

@app.route('/documentacao')
def documentacao():
    return render_template('documentacao.html')

@app.route('/previsaotempo')
def previsao1():
    return render_template('previsao-final.html')

@app.route('/home', methods=['POST'])
def cadastrar():
    username = request.form.get('username')
    email = request.form.get('email')

    # Gere uma API Key segura
    api_key = gerar_api_key()

    # Armazene a API Key (em um ambiente de produção, armazene de forma segura)
    api_keys[api_key] = {'username': username, 'email': email}
    cidade = request.form.get('cidade')
    httpsite = f"{request.url_root}{url_for('previsao_tempo', api_key=api_key, cidade=cidade)}"
    print(httpsite)
    return render_template('previsaotempo.html', username=username, cidade=cidade)

    # Redirecione o usuário para a página de previsão do tempo com os parâmetros na URL
    #return render_template('previsaotempo.html')
    #redirect(url_for('previsao_tempo', api_key=api_key, cidade=cidade))


@app.route('/api_key/<api_key>', methods=['DELETE'])
def delete_api_key(api_key):
    if api_key in api_keys:
        del api_keys[api_key]
        return jsonify({'message': 'API Key excluída com sucesso.'})
    else:
        return jsonify({'erro': 'API Key não encontrada.'}), 404

@app.route('/previsao', methods=['GET'])
def previsao_tempo():
    cidade = request.args.get('cidade')  # Obtém a cidade da consulta
    api_key = request.args.get('api_key')  # Obtém a API Key da consulta

    if not cidade:
        return jsonify({'erro': 'Por favor, forneça o parâmetro "cidade" na consulta.'}), 400
    if api_key not in api_keys:
        return jsonify({'erro': 'API Key inválida.'}), 401

    # Solicitação para a API do OpenWeatherMap usando a API Key
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid=00b553b1378a9e2260f2310347689ce3&units=metric'

    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'erro': 'Não foi possível obter a previsão do tempo.'}), 500

    previsao = response.json()
    return json.dumps(previsao)

if __name__ == '__main__':
    app.run(debug=True)