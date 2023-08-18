from flask import Flask, jsonify, request
import json
import datetime
import random
import string
import mysql.connector
from mysql.connector import Error



app = Flask(__name__)

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





@app.route('/orientation_test', methods=['POST'])
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
