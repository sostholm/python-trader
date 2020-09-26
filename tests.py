import requests

url = 'http://localhost:8000/login'
myobj = {'username': 'samson', 'password': 'C@frr^Sn87z4NE4n*Qq'}

x = requests.post(url, data = myobj)

print(x.text)