import requests

print(requests.get('localhost:8000/login').response.text())
