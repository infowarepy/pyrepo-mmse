import requests
import speech_recognition as sr


def get_input(prompt):
    return input(prompt).strip()

def listen_audio():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Speak now...")
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        user_words = recognizer.recognize_google(audio)
        print(f"User words: {user_words}")
        return user_words.split()  
    except sr.UnknownValueError:
        print("Sorry, could not understand your speech.")
        return []
    except sr.RequestError as e:
        print(f"Error occurred while recognizing speech; {e}")
        return []

def listen_phrase():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Speak now...")
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        user_input = recognizer.recognize_google(audio)
        print(f"User input: {user_input}")
        return user_input.strip()
    except sr.UnknownValueError:
        print("Sorry, could not understand your speech.")
        return ""
    except sr.RequestError as e:
        print(f"Error occurred while recognizing speech; {e}")
        return ""
    

# starting test using user_id , test_id, org_id
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



# Orientation test 
user_id = 1
test_id = 1

month = get_input("Enter the month (e.g., July): ")
day = get_input("Enter the day (e.g., 19): ")
year = get_input("Enter the year (e.g., 2023): ")

print("Performing Orientation Test...")
data = {
    'user_id': user_id,
    'test_id': test_id,
    'month': month,
    'pin':pin,
    'day': day,
    'year': year
}
response = requests.post('http://127.0.0.1:80/orientation_test', json=data)
if response.status_code == 200:
    result = response.json()
    score1 = result.get('score')
    print('Score for orientation:', score1)
else:
    print('Error occurred while testing /orientation_test API.')


# Registration
actual_words = ['apple', 'banana', 'orange']
print("\nRepeat this words : Apple , Banana , Orange . and remember them as well")
user_words = listen_audio()
print(user_words)
print("Performing Registration Test...")
data = {
    'user_id': user_id,
    'test_id': test_id,
    'pin':pin,
    'type' : 'registration_test',
    'actual_words': actual_words,
    'user_words': user_words
}
response = requests.post('http://127.0.0.1:80/score-of-two-list', json=data)
if response.status_code == 200:
    result = response.json()
    score2 = result.get('score')
    print('Score for registration test:', score2)
else:
    print('Error occurred while testing /score-of-two-list API.')


# Subtraction test
starting_number = 97
difference = 7
print(f"\nStarting from {starting_number} , subtract {difference} every time and do this at least five times. \n ")
user_answers = [int(x) for x in input("Enter answers separated by spaces (e.g., 17 14 11 8 5): ").split()]

print("Performing Subtraction Test...")
data = {
    'user_id': user_id,
    'test_id': test_id,
    'pin':pin,
    'starting_number': starting_number,
    'difference': difference,
    'user_answers': user_answers
}
response = requests.post('http://127.0.0.1:80/subtraction-test', json=data)
if response.status_code == 200:
    result = response.json()
    score3 = result.get('score')
    print('Score for subtraction test:', score3)
else:
    print('Error occurred while testing /subtraction-test API.')


# Recall test
print("\nSay the words that i told you to remember one by one : \n") 
user_words = listen_audio()
print("Performing Recall Test...")
data = {
    'user_id': user_id,
    'test_id': test_id,
    'pin':pin,
    'type' : 'recall_test',
    'actual_words': actual_words,
    'user_words': user_words
}
response = requests.post('http://127.0.0.1:80/score-of-two-list', json=data)
if response.status_code == 200:
    result = response.json()
    score4 = result.get('score')
    print('Score for recall test:', score4)
else:
    print('Error occurred while testing /score-of-two-list API.')


# No if but test
print("\nSay the phrase : No ifs ands or buts\n") 
phrase = listen_phrase() 

print("Performing Language Test...")
data = {
    'user_id': user_id,
    'test_id': test_id,
    'phrase': phrase,
    'pin':pin,
}

response = requests.post('http://127.0.0.1:80/no-ifs-ands-buts', json=data)
if response.status_code == 200:
    result = response.json()
    score5 = result.get('score')
    print('Score for Language test:', score5)
else:
    print('Error occurred while testing /no-ifs-ands-buts API.')

score = score1 + score2 + score3 + score4 + score5 ;
severity = ""

print("\nMMSE Score:", score, "/ 15\n")
if score >= 12:
    severity='Normal cognition'
elif score >= 9:
    severity='Mild cognitive impairment'
else:
    severity='Severe cognitive impairment'
        
print(severity)


# Finalizing Score 
data = {
    'pin' : pin,
    'final_score' :score,
    'severity' : severity 
}
response = requests.post('http://127.0.0.1:80/finalize-score', json=data)
if response.status_code == 200:
    result = response.json()
    message = result.get('message')
    print(message)
else:
    print('Error occurred saving final score.')