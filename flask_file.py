from flask import Flask, render_template,request, redirect, jsonify
#import pymongo
import urllib.parse
username = urllib.parse.quote_plus('brain_tumor_detection')
password = urllib.parse.quote_plus('Qwert@123')
app = Flask(__name__)
import certifi
import joblib
import os
import numpy as np
from keras_preprocessing.image import load_img
from keras_preprocessing.image import img_to_array
from tensorflow.keras.models import load_model

# Database connection
import pymongo
from pymongo.server_api import ServerApi
uri = "mongodb+srv://%s:%s@cluster0.mi4tymu.mongodb.net/?retryWrites=true&w=majority"%(username,password)
# Create a new client and connect to the server
client = pymongo.MongoClient(uri, server_api=ServerApi('1'),tlsCAFile=certifi.where())
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
db = client["Brain-Tumor-Detection"]

#model 
filepath = "/Users/palgunir/Documents/Brain_Tumor_Detection/model1.h5"
model = load_model(filepath)
print("Model Loaded Successfully")
def predict_tumor_class(file_path):
    test_image = load_img(file_path, target_size = (128, 128)) 
    test_image = img_to_array(test_image)/255 
    test_image = np.expand_dims(test_image, axis = 0) 
    result = model.predict(test_image) 
    pred = np.argmax(result, axis=1)
    print(pred)
    if pred==0:
        return "glioma"
    elif pred==1:
        return "meningioma"
    elif pred==2:
        return "notumor"
    elif pred==3:
        return "pitutary"
    
@app.route('/')
def welcome_page():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('register.html',ele = '')

@app.route('/register2',methods=['POST','GET'])
def register_post():
    if request.form['Password'] == request.form['CfmPass'] and len(request.form['Password']) >= 8 and len(list(db.Users.find({'Email' : request.form['Email']}))) == 0:
        db.Users.insert_one({
            "Full Name" : request.form['Name'],
            "Doctor ID" : request.form['doctor_id'],
            "Designation" : request.form['designation'],
            "Email" : request.form['Email'],
            "Password" : request.form['Password']
            })
        return redirect('/upload')
    elif request.form['Password'] != request.form['CfmPass']:
        return render_template('register.html',ele='Passwords must match..!')
    elif len(request.form['Password']) < 8:
        return render_template('register.html',ele='Required Password of min 8 characters..!')
    elif len(list(db.Users.find({'Email' : request.form['Email']}))) != 0:
        return render_template('register.html',ele='Required a unique email..!')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login2',methods=['POST','GET'])
def login_post():
    if len(list(db.Users.find({'Email' : request.form['Email'], 'Password' : request.form['Password']}))) == 1:
        return redirect('/upload')
    else:
        return render_template('login.html',ele = 'Wrong credentials..!')
    
@app.route('/upload')
def upload_page():
    return render_template('upload.html',ele = '')

@app.route('/upload2',methods=['POST','GET'])
def upload_post():
    filename = request.form['image']
    file_path = os.path.join("/Users/palgunir/Documents/Brain_Tumor_Detection", filename)
    res = predict_tumor_class(file_path)
    res2 = ""
    if res == 'glioma':
        res2 = 'glioma.html'
        res = 'Glioma Tumor'
    elif res == 'meningioma':
        res2 = 'meningioma.html'
        res = 'Meningioma Tumor'
    elif res == 'notumor':
        res2 = 'notumor.html'
        res = 'Not a Tumor'
    else:
        res2 = 'pitutary.html'
        res = 'Pitutary Tumor'
    return render_template(res2,ele = 'It\'s '+res)

@app.route('/aboutus')
def aboutus_page():
    return render_template('aboutus.html')

if __name__ == '__main__':
    app.run(debug = True)






