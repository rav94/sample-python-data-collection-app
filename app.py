from flask import Flask, escape, render_template, request
from datetime import datetime
import pandas as pd
import os

app = Flask(__name__)

# @app.route('/')
# def index():
#     return 'Hello World!'
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        
        # Print the form data to the console 
        for key, value in request.form.items():
            print(f'{key}: {value}')
            
        input_dict = request.form.to_dict()

        input_dict['timestamp'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        print(input_dict)

        df = pd.DataFrame([input_dict])
        
        print(df)

        output_path='test.csv'
        df.to_csv(output_path, mode='a', index=False, header=not os.path.exists(output_path))

    return render_template('questions.html')