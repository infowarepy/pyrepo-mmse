from flask import Flask, jsonify, request
import json
import datetime
import random
import string
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS, cross_origin
import numpy as np
import pyttsx3
import pygame
import speech_recognition as sr
from utils import *



app = Flask(__name__)
# Allow requests from a specific URL

# CORS(app, origins=["http://localhost:3000"], expose_headers='Authorization', supports_credentials=True)
# cors=CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'
cors_config = {
    # "origins": ["http://localhost:3000/"]  # Replace with your desired URL
    "origins": "*"
}
CORS(app)
cors = CORS(app, resource={
    r"/*":cors_config 
    })


def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
    


def generate_unique_pin():
    while True:
        pin = ''.join(random.choice(string.digits) for _ in range(4))
        connection = create_connection()
        if connection is not None:
            try:
                with connection.cursor() as cursor:
                    query = "SELECT pin FROM demo_mmse WHERE pin = %s"
                    cursor.execute(query, (pin,))
                    result = cursor.fetchone()
                    if not result:
                        # PIN will be unique now 
                        break
            except Error as e:
                print(f"Error while checking PIN uniqueness: {e}")
            finally:
                connection.close()
        else:
            print("Failed to connect to the database.")
            return None
    return pin

@app.route('/start_mmse', methods=['POST'])
@cross_origin()
def generate_pin():
    data = request.get_json()
    user_id = data.get('user_id')
    org_id = data.get('org_id')
    test_id = data.get('test_id')

    if user_id is None:
        return jsonify({'error': 'User ID is missing in the request.'}), 400

    pin = generate_unique_pin()

    if not pin:
        return jsonify({'error': 'Failed to generate a unique PIN.'}), 500

    connection = create_connection()
    if connection is not None:
        try:
            with connection.cursor() as cursor:
                query = "INSERT INTO demo_mmse (pin, org_id, user_id, test_id) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (pin, org_id, user_id, test_id))
            connection.commit()
            print("Data added to demo_mmse table successfully.")
        except Error as e:
            print(f"Error while inserting data into demo_mmse table: {e}")
        finally:
            connection.close()
    else:
        print("Failed to connect to the database. Data not added to demo_mmse table.")
        return jsonify({'error': 'Failed to connect to the database. Data not added to demo_mmse table.'}), 500

    return jsonify({'pin': pin})




def updateTable(columnName,pin,user_id,test_id,demo_mmse_json,score):
        connection = create_connection()
        if connection is not None:
            try:
                with connection.cursor() as cursor:
                    query = "SELECT pin FROM demo_mmse WHERE pin = %s AND user_id = %s AND test_id = %s"
                    cursor.execute(query, (pin, user_id, test_id))
                    result = cursor.fetchone()

                    if result:
                        query = f"UPDATE demo_mmse SET {columnName} = %s WHERE pin = %s"
                        cursor.execute(query, (demo_mmse_json, pin))
                    else:
                        print("Invalid Pin")
                        return jsonify({'score': -1})

                connection.commit()
                print(f"Data of {columnName} test successfuly inserted")
                return jsonify({'score': score})
            except Error as e:
                print(f"Error while inserting data into demo_mmse table: {e}")
            finally:
                connection.close()
        else:
            print("Failed to connect to the database. Data not added to demo_mmse table.")

        return jsonify({'score': -1})



@app.route('/finalize-score', methods=['POST'])
@cross_origin(supports_credentials=True)
def finalize_score():
    data = request.get_json()
    pin = data['pin']
    final_score = data['final_score']
    severity = data['severity']

    connection = create_connection()
    if connection is not None:
        try:
            with connection.cursor() as cursor:
                query = "SELECT pin FROM demo_mmse WHERE pin = %s"
                cursor.execute(query, (pin,))
                result = cursor.fetchone()

                if result:
                    # Update the total_score and severity fields in the table
                    update_query = "UPDATE demo_mmse SET total_score = %s, severity = %s WHERE pin = %s"
                    cursor.execute(update_query, (final_score, severity, pin))
                    connection.commit()
                    print("Total score and severity updated successfully.")
                    return jsonify({'message': 'Score updated successfully.'})
                else:
                    print("Invalid Pin")
                    return jsonify({'error': 'Invalid PIN.'}), 400
        except Error as e:
            print(f"Error while updating score: {e}")
        finally:
            connection.close()
    else:
        print("Failed to connect to the database.")
        return jsonify({'error': 'Failed to connect to the database.'}), 500

    return jsonify({'error': 'Failed to update score.'}), 500


@app.route('/random-words', methods=['POST'])
@cross_origin(supports_credentials=True)
def generate_random_words():
    data = request.get_json()
    num_words = data['num_words']

    meaningful_words = ['apple', 'cherry', 'banana', 'cat', 'dog', 'elephant', 'flower', 'guitar', 'house',
                        'island', 'jungle']

    random_words = random.sample(meaningful_words, num_words)

    return jsonify({'random_words': random_words})



@app.route('/orientation_test', methods=['POST'])
@cross_origin()
def process_orientation_test():
    data = request.get_json()
    score = 0

    month = data['month']
    day = data['day']
    year = data['year']
    pin = data['pin']  

    month = month.lower()

    current_time = datetime.datetime.now()
    current_month = current_time.strftime("%B").lower()
    current_day = current_time.strftime("%d")
    current_year = current_time.strftime("%Y")

    if current_month == month:
        score += 1
    if current_day == day:
        score += 1
    if current_year == year:
        score += 1

    user_id = data.get('user_id')
    test_id = data.get('test_id')

    demo_mmse_data = {
        'month': month,
        'day': day,
        'year': year,
        'score':score 
    }
    demo_mmse_json = json.dumps(demo_mmse_data)

    return updateTable('orientation_test',pin,user_id,test_id,demo_mmse_json,score)



@app.route('/score-of-two-list', methods=['POST'])
@cross_origin(supports_credentials=True)
def process_two_lists():
    data = request.get_json()
    actual_words = data['actual_words']
    user_words = data['user_words']
    pin = data['pin'] 
    test_name = str(data['type'])

    actual_answers = list(set([word.lower() for word in actual_words]))
    user_answers = list(set([word.lower() for word in user_words]))

    score = 0
    for i in range(0,len(user_answers)):
        if user_answers[i] in actual_answers:
                score+=1 

    user_id = data.get('user_id')
    test_id = data.get('test_id')

    demo_mmse_data = {
            'actual_words': actual_words,
            'user_words': user_words,
            'score' : score 
        }
    demo_mmse_json = json.dumps(demo_mmse_data)
        
    return updateTable(test_name,pin,user_id,test_id,demo_mmse_json,score) 


@app.route('/subtraction-test', methods=['POST'])
@cross_origin(supports_credentials=True)
def process_subtraction_test():
        data = request.get_json()
        starting_number = data['starting_number']
        difference = data['difference']
        user_answer = data['user_answers']
        pin = data['pin']
        
        score = 0
        previous = starting_number

        for num in user_answer:
            expected = previous - difference
            if num == expected:
                score += 1
            previous = num

        score = min(5, score)

        user_id = data.get('user_id')
        test_id = data.get('test_id')

        demo_mmse_data = {
            'starting_number': starting_number,
            'difference': difference,
            'user_answers': user_answer,
            'score':score 
        }
        demo_mmse_json = json.dumps(demo_mmse_data)  

        return updateTable('calculation_test',pin,user_id,test_id,demo_mmse_json,score) 


@app.route('/no-ifs-ands-buts', methods=['POST'])
@cross_origin(supports_credentials=True)
def no_ifs_ands_buts():
    data = request.get_json()
    user_id = data.get('user_id')
    test_id = data.get('test_id')
    phrase = data.get('phrase')
    pin = data['pin'] 

    score = 0

    if phrase.lower() == "no ifs ands or buts":
        score += 1

    demo_mmse_data = {
            'phrase': phrase,
            'score' : score ,
        }
    demo_mmse_json = json.dumps(demo_mmse_data)

    return updateTable('language_test',pin,user_id,test_id,demo_mmse_json,score) 

@app.route('/process_clock_image',methods='POST')
@cross_origin(supports_credentials=True)
def process_clock_image():
    time = request.form.get('time')
    uploaded_file = request.files['image']

    total_score = 0.0
    circle_score = 0.0
    digits_score = 0.0
    lines_score = 0.0
    time_match_score = 0.0

    file_array = np.frombuffer(uploaded_file.read(), np.uint8)
    image = cv2.imdecode(file_array, cv2.IMREAD_COLOR)
    processed_image = preprocess_image(image)

    number_lists = []
    circle_info = detect_circle(processed_image)
    if circle_info is not None:
        center, radius, circularity = circle_info
        circle_score = circularity

        lines_in_circle = detect_lines_in_circle(image, center)
        if lines_in_circle is not None:
            lines_score = min(1, len(lines_in_circle) * 0.5)
        else:
            lines_score = 0

        numbers = determine_numbers(lines_in_circle)
        number_lists = list(numbers.keys())

    numbers = extract_handwritten_numbers(processed_image)
    digits_score = (min(12, len(numbers))) / 10

    possible_timings = generate_timings(number_lists)

    match = 0
    if len(possible_timings) > 0:
        for i, timing in enumerate(possible_timings):
            pair_num = i + 1
            temp = str(timing[0]) + ":" + str(timing[1])
            match = max(match, calculate_score(time, temp))

    time_match_score = match
    total_score = circle_score + digits_score + lines_score + time_match_score

    response = {
        'total_score': total_score,
        'circle_score': circle_score,
        'digits_score': digits_score,
        'lines_score': lines_score,
        'time_match_score': time_match_score
    }

    json_response = json.dumps(response)

    return json_response, 200, {'Content-Type': 'application/json'}

@app.route('/random-animals',methods='POST')
@cross_origin(supports_credentials=True)
def get_random_animals():
    animals = [
        {'name': 'elephant', 'image': 'elephant.jpg'},
        {'name': 'lion', 'image': 'lion.jpg'},
        {'name': 'cat', 'image': 'cat.jpg'},
        {'name': 'dog', 'image': 'dog.jpg'},
        {'name': 'tiger', 'image': 'tiger.jpg'},
        {'name': 'horse', 'image': 'horse.jpg'},
    ]

    data = request.get_json()
    num_animals = data['num_animals']

    random_animals = random.sample(animals, num_animals)

    response = []
    for animal in random_animals:
        animal_data = {
            'name': animal['name'],
            'image': f'https://mmse-api.onrender.com/static/img/{animal["image"]}'
        }
        response.append(animal_data)
    return jsonify({'animals': response})

@app.route('/animal-guess',methods=['POST'])
@cross_origin(supports_credentials=True)
def process_animal_guess():
    guesses = request.get_json()  
    correct_guesses = 0

    for guess in guesses:
        actual_animal = guess['actual_animal']
        guessed_animal = guess['guessed_animal']

        if actual_animal.lower() == guessed_animal.lower():
            correct_guesses += 1

    return jsonify({'score': correct_guesses})

## Defining the DB configuration
db_config = {
    'host': 'onlineorder-mysqldb-test.cidxoi55oorv.ap-south-1.rds.amazonaws.com',
    'user': 'pythonuser',
    'password': 'Dev!12345',
    'port': 3306,
    'database': 'pythontest'
}


    
if __name__ == '__main__':
    connection = create_connection()
    if connection is not None:
        app.run(debug=True, port=80)
    else:
        print("Database connection failed.")
