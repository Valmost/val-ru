import requests

r = requests.post('http://valmost.site/api/token',
                  json={'username': 'Valmost3377@mail.ru', 'password': '123'})
token = r.json()['token']

with open('input.pdf', 'rb') as f:
    r = requests.post('http://valmost.site/api/process',
                      headers={'Authorization': f'Bearer {token}'},
                      files={'file': f},
                      data={'width': 500, 'height': 500, 'algorithm': 'shelf'})

    with open('output.pdf', 'wb') as out:
        out.write(r.content)
