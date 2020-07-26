import requests

print(requests.post('http://localhost:8000/login', json = {'username':'samson', 'password': 'BmPW0W8s1^@l'}).text)