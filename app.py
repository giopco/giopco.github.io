import secrets
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_session import Session
import requests

app = Flask(__name__)
app.secret_key = '115723'  # Substitua por uma chave secreta adequada
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
app.static_folder = 'templates/static'

api_keys = {}
cidades = ['São Paulo', 'Nova York', 'Cidade do México', 'Paris', 'Tóquio', 'Londres', 'Roma', 'Sydney']

def gerar_api_key():
    return secrets.token_urlsafe(32)

########################################

@app.route('/')
def inicioprevisao():
    return render_template('index.html', cidades=cidades)

########################################

@app.route('/documentacao')
def documentacao():
    return render_template('Documentação Swagger.html')

########################################

@app.route('/resultado')
def resultado():
    username = session.get('username')
    email = session.get('email')
    return render_template('previsaotempo.html', username=username, email=email)

########################################

@app.route('/home', methods=['GET', 'POST'])
def cadastrar():
    username = session.get('username')
    email = session.get('email')

    if not username or not email:
        username = request.form.get('username')
        email = request.form.get('email')

        if username and email:
            session['username'] = username
            session['email'] = email
        else:
            return render_template('obter_nome_email.html')

    return render_template('previsaotempo.html', username=username, email=email)

########################################

@app.route('/cidade', methods=['GET', 'POST'])
def cadastrar2():
    username = session.get('username')
    email = session.get('email')

    if username is None:
        return jsonify({'erro': 'O nome de usuário não está definido na sessão.'}), 400
    if email is None:
        return jsonify({'erro': 'O email não está definido na sessão.'}), 400

    # Gerar uma API Key segura
    api_key = gerar_api_key()

    # Armazenar a API Key (em um ambiente de produção, armazenar de forma segura)
    api_keys[api_key] = {'username': username, 'email': email}

    cidade = request.form.get('cidade')
    httpsite = f"{request.url_root}{url_for('previsao_tempo', api_key=api_key, cidade=cidade)}"
    print(httpsite)
    return redirect(httpsite)

########################################

@app.route('/api_key/<api_key>', methods=['DELETE'])
def delete_api_key(api_key):
    if api_key in api_keys:
        del api_keys[api_key]
        return jsonify({'message': 'API Key excluída com sucesso.'})
    else:
        return jsonify({'erro': 'API Key não encontrada.'}), 404

########################################

@app.route('/previsao', methods=['GET'])
def previsao_tempo():
    api_key = request.args.get('api_key')

    if api_key not in api_keys:
        return jsonify({'erro': 'API Key inválida.'}), 401

    cidade = request.args.get('cidade')
    username = api_keys[api_key]['username']
    email = api_keys[api_key]['email']

    ## ------
    url = f'http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid=00b553b1378a9e2260f2310347689ce3&units=metric'
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'erro': 'Não foi possível obter a previsão do tempo.'}), 500

    previsao = response.json()

    # Imprima as 10 informações da previsão no terminal
    temperatura = previsao["main"]["temp"]
    descricao_clima = previsao["weather"][0]["description"]
    umidade = previsao["main"]["humidity"]
    pressao_atmosferica = previsao["main"]["pressure"]
    velocidade_vento = previsao["wind"]["speed"]
    direcao_vento = previsao["wind"]["deg"]
    nascer_sol = previsao["sys"]["sunrise"]
    por_sol = previsao["sys"]["sunset"]
    temperatura_maxima = previsao["main"]["temp_max"]
    temperatura_minima = previsao["main"]["temp_min"]

    print("Informações da Previsão:")
    print(f"Temperatura: {temperatura}°C")
    print(f"Temperatura máxima: {temperatura_maxima}°C")
    print(f"Temperatura mínima: {temperatura_minima}°C")
    print(f"Descrição do Clima: {descricao_clima}")
    print(f"Umidade: {umidade}%")
    print(f"Pressão Atmosférica: {pressao_atmosferica} hPa")
    print(f"Velocidade do Vento: {velocidade_vento} m/s")
    print(f"Direção do Vento: {direcao_vento}°")
    print(f"Nascer do Sol: {nascer_sol}")
    print(f"Pôr do Sol: {por_sol}")
    
    # Retorna as informações da previsão em formato JSON
    previsao_tempo = {
        'username': username,
        'email' : email,
        'cidade': cidade,
        'temperatura': temperatura,
        'temperatura_maxima': temperatura_maxima,
        'temperatura_minima': temperatura_minima,
        'descricao_clima': descricao_clima,
        'umidade': umidade,
        'pressao_atmosferica': pressao_atmosferica,
        'velocidade_vento': velocidade_vento,
        'direcao_vento': direcao_vento,
        'nascer_sol': nascer_sol,
        'por_sol': por_sol
    }

    rendered_template = render_template('resultado.html', **previsao_tempo)

    # Salve o resultado em um arquivo HTML
    with open('resultado.html', 'w') as file:
        file.write(rendered_template)

    return rendered_template

if __name__ == '__main__':
    app.run(debug=True)