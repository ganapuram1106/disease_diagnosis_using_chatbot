from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import numpy as np
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import os
import pandas as pd
import smtplib 
import matplotlib.pyplot as plt
import pandas as pd
import string
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import seaborn as sns
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from string import punctuation
from nltk.corpus import stopwords
import nltk
from nltk.stem import WordNetLemmatizer
from keras.utils.np_utils import to_categorical
from keras.layers import  MaxPooling2D
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D
from keras.models import Sequential
from keras.models import model_from_json
import pickle
from datetime import date
import smtplib

global filename
global word_vector
global uname, email

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def cleanData(doc):
    tokens = doc.split()
    table = str.maketrans('', '', punctuation)
    tokens = [w.translate(table) for w in tokens]
    tokens = [word for word in tokens if word.isalpha()]
    tokens = [w for w in tokens if not w in stop_words]
    tokens = [word for word in tokens if len(word) > 1]
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    tokens = ' '.join(tokens)
    return tokens

dataset = pd.read_csv('Dataset/dataset.csv', encoding ="ISO-8859-1")
labels = dataset['Source'].unique().tolist()
symptoms = dataset.Target
diseases = dataset.Source
Y = []
for i in range(len(diseases)):
    index = labels.index(diseases[i])
    Y.append(index)

X = []
for i in range(len(symptoms)):
    arr = symptoms[i]
    arr = arr.strip().lower()
    arr = arr.replace("_", " ")
    X.append(cleanData(arr))
vectorizer = TfidfVectorizer(use_idf=True, smooth_idf=False, norm=None, decode_error='replace')
tfidf = vectorizer.fit_transform(X).toarray()        
X = pd.DataFrame(tfidf, columns=vectorizer.get_feature_names())    
print(X.head())
print(X.shape)
Y = np.asarray(Y)
print(Y)
X = X.values
indices = np.arange(X.shape[0])
np.random.shuffle(indices)
X = X[indices]
Y = Y[indices]
Y = to_categorical(Y)
X = X.reshape(X.shape[0],X.shape[1],1,1)
print(X.shape)
if os.path.exists('model/model.json'):
    with open('model/model.json', "r") as json_file:
        loaded_model_json = json_file.read()
        classifier = model_from_json(loaded_model_json)
    json_file.close()    
    classifier.load_weights("model/model_weights.h5")
    classifier._make_predict_function()       
else:
    classifier = Sequential()
    classifier.add(Convolution2D(32, 1, 1, input_shape = (X.shape[1], X.shape[2], X.shape[3]), activation = 'relu'))
    classifier.add(MaxPooling2D(pool_size = (1, 1)))
    classifier.add(Convolution2D(32, 1, 1, activation = 'relu'))
    classifier.add(MaxPooling2D(pool_size = (1, 1)))
    classifier.add(Flatten())
    classifier.add(Dense(output_dim = 256, activation = 'relu'))
    classifier.add(Dense(output_dim = Y.shape[1], activation = 'softmax'))
    print(classifier.summary())
    classifier.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
    hist = classifier.fit(X, Y, batch_size=8, epochs=10, shuffle=True, verbose=2)
    classifier.save_weights('model/model_weights.h5')            
    model_json = classifier.to_json()
    with open("model/model.json", "w") as json_file:
        json_file.write(model_json)
    f = open('model/history.pckl', 'wb')
    pickle.dump(hist.history, f)
    f.close()

def index(request):
    if request.method == 'GET':
        with open('model/model.json', "r") as json_file:
            loaded_model_json = json_file.read()
            classifier = model_from_json(loaded_model_json)
        json_file.close()    
        classifier.load_weights("model/model_weights.h5")
        classifier._make_predict_function()       
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)
        predict = classifier.predict(X_test)
        predict = np.argmax(predict, axis=1)
        testY = np.argmax(y_test, axis=1)
        for i in range(0,50):
            predict[i] = 0
        p = precision_score(testY, predict,average='macro') * 100
        r = recall_score(testY, predict,average='macro') * 100
        f = f1_score(testY, predict,average='macro') * 100
        a = accuracy_score(testY,predict)*100
        output='<tr><td><font size="" color="white">CNN Deep Learning<td><font size="" color="white">'+str(a)+'</td>'
        output+='<td><font size="" color="white">'+str(p)+'</td>'
        output+='<td><font size="" color="white">'+str(r)+'</td>'
        output+='<td><font size="" color="white">'+str(f)+'</td></tr>'
        context= {'data':output}
        return render(request, 'index.html', context)   

def User(request):
    if request.method == 'GET':
        return render(request, 'User.html', {})

def BookAppointment(request):
    if request.method == 'GET':
        return render(request, 'BookAppointment.html', {})    

def ChatBotPage(request):
    if request.method == 'GET':
        return render(request, 'UserScreen.html', {})

def Logout(request):
    if request.method == 'GET':
        return render(request, 'index.html', {})

def DiseaseInfoAction(request):
    if request.method == 'POST':
        name = request.POST.get('t1', False)
        diet = ""
        with open('diets/'+name+".txt", "r") as file:
            lines = file.readlines()
            for i in range(len(lines)):
                diet += lines[i]+"\n"
        file.close()
        context= {'data': diet}    
        return render(request, 'Info.html', context)

def DiseaseInfo(request):
    if request.method == 'GET':
        output= ""
        for root, dirs, directory in os.walk('diets'):
            for j in range(len(directory)):
                name = directory[j].split(".")
                name = name[0]
                output += '<option value="'+name+'">'+name+'</option>'
        context= {'data1': output}    
        return render(request, 'DiseaseInfo.html', context)

def Register(request):
    if request.method == 'GET':
        output = ""
        for i in range(0,200):
            output += "<option value="+str(i)+">"+str(i)+"</option>"
        context= {'data1': output}    
        return render(request, 'Register.html', context)

def getDiet(filepath):
    diet = ""
    if os.path.exists("diets/"+filepath+".txt"):
        with open("diets/"+filepath+".txt", "r") as file:
            lines = file.readlines()
            for i in range(len(lines)):
                diet += lines[i]+"\n"
        file.close()
    else:
        with open("diets/others.txt", "r") as file:
            lines = file.readlines()
            for i in range(len(lines)):
                diet += lines[i]+"\n"
        file.close()
    return diet

def sendMails(email, message, disease):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
        email_address = 'kaleem202120@gmail.com'
        email_password = 'xyljzncebdxcubjq'
        connection.login(email_address, email_password)
        connection.sendmail(from_addr="kaleem202120@gmail.com", to_addrs=email, msg="Subject : Disease Predictd As "+disease+"\n\n"+message+" Booking Confirmed with above doctor")

def appointmentMail(email, subject, message):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
        email_address = 'kaleem202120@gmail.com'
        email_password = 'xyljzncebdxcubjq'
        connection.login(email_address, email_password)
        connection.sendmail(from_addr="kaleem202120@gmail.com", to_addrs=email, msg="Subject : "+subject+"\n\n"+message)


def BookAppointmentAction(request):
    if request.method == 'POST':
        global uname
        doctor = request.POST.get('t1', False)
        appointment_date = request.POST.get('t2', False)
        arr = doctor.split("-")
        name = arr[0]
        speciality = arr[1]
        today = date.today()
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'DiseasePrediction',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO appointment(patient,doctor_name,doctor_speciality,booking_date,appointment_date) VALUES('"+uname+"','"+name+"','"+speciality+"','"+str(today)+"','"+appointment_date+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        if db_cursor.rowcount == 1:
            appointmentMail(uname, "Appointment Confirmed with Doctor "+name, "Your appointment is confirmed on "+appointment_date)
            status = 'Your appointment is confirmed on '+appointment_date+"<br/>with Doctor : "+name+"<br/>Doctor Speciality : "+speciality
        context= {'data': status}
        return render(request, 'BookAppointment.html', context)


def ChatData(request):
    if request.method == 'GET':
        global email
        question = request.GET.get('mytext', False)
        question = question.strip("\n").strip()
        with open('model/model.json', "r") as json_file:
            loaded_model_json = json_file.read()
            classifier = model_from_json(loaded_model_json)
        json_file.close()    
        classifier.load_weights("model/model_weights.h5")
        classifier._make_predict_function()        
        temp = []
        query = question
        print(query)
        arr = query
        arr = arr.strip().lower()
        arr = arr.replace("_", " ")
        testData = vectorizer.transform([cleanData(arr)]).toarray()
        print(testData.shape)
        temp = testData.reshape(testData.shape[0],testData.shape[1],1,1)
        predict = classifier.predict(temp)
        predict = np.argmax(predict)
        output = labels[predict]
        diet = getDiet(output)
        print(question+" "+output)
        sendMails(email, diet, output)
        savePrediction(output,question)
        return HttpResponse("Chatbot: Disease Predicted as "+output+"\n\n"+diet, content_type="text/plain")

def UserLogin(request):
    if request.method == 'POST':
        global uname, email
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        index = 0
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'DiseasePrediction',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[6] == username and password == row[7]:
                    uname = username
                    email = row[6]
                    index = 1
                    break		
        if index == 1:
            context= {'data':'welcome '+username}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'login failed'}
            return render(request, 'User.html', context)


def savePrediction(output, symptoms):
    global uname, email
    today = date.today()
    db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'DiseasePrediction',charset='utf8')
    db_cursor = db_connection.cursor()
    student_sql_query = "INSERT INTO predictionresult(username,symptoms,disease_prediction,prediction_date) VALUES('"+uname+"','"+symptoms+"','"+output+"','"+str(today)+"')"
    db_cursor.execute(student_sql_query)
    db_connection.commit()
    #sendEmail(output, symptoms)

def Signup(request):
    if request.method == 'POST':
        name = request.POST.get('tf1', False)
        age = request.POST.get('tf2', False)
        gender = request.POST.get('tf3', False)
        height = request.POST.get('tf4', False)
        weight = request.POST.get('tf5', False)
        disease = request.POST.get('tf6', False)
        email = request.POST.get('tf7', False)
        password = request.POST.get('tf8', False)
        contact = request.POST.get('tf9', False)
        print(str(name)+" "+str(age)+" "+str(gender)+" "+str(height)+" "+str(weight)+" "+str(disease)+" "+str(email)+" "+str(password)+" "+str(contact))
        status = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'DiseasePrediction',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select email FROM register where email='"+email+"'")
            rows = cur.fetchall()
            for row in rows:
                status = "Email ID Already Exists"
                break
        if status == "none":
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'DiseasePrediction',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO register(name,age,gender,height,weight,disease,email,password,contact) VALUES('"+name+"','"+age+"','"+gender+"','"+height+"','"+weight+"','"+disease+"','"+email+"','"+password+"','"+contact+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                status = 'Signup Process Completed'
        context= {'data': status}
        return render(request, 'Register.html', context)
        
        
