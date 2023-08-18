
import requests
import json


data = {
    'user_id': 1,
    'test_id': 1,
    'org_id':1,
}
pin = ""

response = requests.post('http://127.0.0.1:80/start_mmse', json=data)
if response.status_code == 200:
    result = response.json()
    pin = result.get('pin')
    print('PIN Generated:', pin)
else:
    print('Error occurred while starting test.')
########### SETUP CODE ABOVE ###################


#### Orientation test #######

url = 'http://127.0.0.1:80/orientation_test'

data = {
    'month': 'July',
    'day': '24',
    'year': '2023',
    'pin': pin,  
    'user_id': 1,  
    'test_id': 1  
}

headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, data=json.dumps(data), headers=headers)

print(response.status_code)
print(response.json())




####### Registration Test #############
url = 'http://127.0.0.1:80/score-of-two-list'

data = {
    'actual_words': ['apple', 'banana', 'orange'],
    'user_words': ['banana', 'orange', 'mango'],
    'pin': pin, 
    'user_id': 1,  
    'test_id': 1,  
    'type': 'registration_test'
}

headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, data=json.dumps(data), headers=headers)

print(response.status_code)
print(response.json())




####### Recall Test #############
url = 'http://127.0.0.1:80/score-of-two-list'

data = {
    'actual_words': ['apple', 'banana', 'orange'],
    'user_words': ['banana', 'orange', 'mango'],
    'pin': pin,  
    'user_id': 1,  
    'test_id': 1,  
    'type': 'recall_test'
}

headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, data=json.dumps(data), headers=headers)

print(response.status_code)
print(response.json())


########## Calculation Test #############
url = 'http://127.0.0.1:80/subtraction-test'

data = {
    'starting_number': 100,
    'difference': 7,
    'user_answers': [93, 86, 79, 72, 65],
    'pin': pin,  
    'user_id': 1,  
    'test_id': 1, 
}

headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, data=json.dumps(data), headers=headers)

print(response.status_code)
print(response.json())


######### Language Test #######
url = 'http://127.0.0.1:80/no-ifs-ands-buts'

data = {
    'user_id': 1,
    'test_id': 1,  
    'phrase': 'No ifs ands or buts',
    'pin': pin,  
}

headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, data=json.dumps(data), headers=headers)

print(response.status_code)
print(response.json())