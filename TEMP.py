import requests

r = requests.post('http://127.0.0.1:5000/api/token',
                  json={'username': 'Valmost3377@mail.ru', 'password': '123'})
token = r.json()['token']

with open('C:/Users/Иван/Documents/low_poly1.pdf', 'rb') as f:
    r = requests.post('http://localhost:5000/api/process',
                      headers={'Authorization': f'Bearer {token}'},
                      files={'file': f},
                      data={'width': 500, 'height': 500, 'algorithm': 'shelf'})

    with open('output.pdf', 'wb') as out:
        out.write(r.content)