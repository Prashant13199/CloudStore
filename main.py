# imports
import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, session, Blueprint, jsonify, make_response, flash, Response
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from models import Image1
import shutil
import math
import json
import shutil
import ifcfg
from zipfile import ZipFile
import datetime
from datetime import date
import multiprocessing
import mysql.connector
from flask_session import Session
import requests
from qbittorrent import Client
import random
import webvtt
import psutil
import math

print("Starting CloudStore App")

print("Connecting to database")
global mydb
global mycursor
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="prashant13",
    database="cloudstore"
)
mycursor = mydb.cursor()

# init flask app
print("Configuring app")
app = Flask(__name__, static_folder="static")
app.config['SECRET_KEY'] = 'SECRETKEY'
app.config['MAX_CONTENT_LENGTH'] = 300000 * 1024 * 1024
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config['cinehub'] = 'data/cinehub/'
Session(app)

gallery = Blueprint('gallery', __name__,
                    template_folder='templates', static_folder='static')
ALLOWED_EXTENSIONS_IMAGE = ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.icon']
ALLOWED_EXTENSIONS_VIDEO = ['.mp4', '.mov', '.mkv', '.avi', '.mpeg', '.webm']
ALLOWED_EXTENSIONS_AUDIO = ['.mp3', '.m4a']
ALLOWED_EXTENSIONS_DOCUMENT = ['.pdf', '.html', '.xml', '.py', '.pages',
                               '.numbers', '.keynote', '.xlsx', '.csv', '.docx', '.pptx', '.css', '.js', '.txt', '.srt', '.vtt']
app.register_blueprint(gallery, url_prefix='/gallery')

bootstrap = Bootstrap(app)

print("Connecting to qbittorrent")
global qb
qb = Client("http://127.0.0.1:8080/")
qb.login("admin", "123456")


######################### Routes ##########################

# home
@app.route('/')
def home():
    global mydb
    global mycursor
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="prashant13",
        database="cloudstore"
    )
    mycursor = mydb.cursor()
    if session.get("name"):
        return redirect('/file')
    else:
        sql = "SELECT * from users WHERE user = ('{}')".format("admin")
        mycursor.execute(sql)
        user = mycursor.fetchone()
        if user:
            return redirect('/signin')
        else:
            return redirect('/register-admin')

# switch to local network


@app.route('/switch')
def switch():
    try:
        hosts = []
        for name, interface in ifcfg.interfaces().items():
            if (interface['inet4']):
                hosts.append(interface['inet4'])
        host = ', '.join(hosts[0])
        return redirect('http://{}:80'.format(host))
    except:
        return render_template("signin.html", error="a", message="Unable to connect")

# sign in


@app.route('/signin', methods=["GET", "POST"])
def login():
    global mydb
    global mycursor
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="prashant13",
        database="cloudstore"
    )
    mycursor = mydb.cursor()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        sql = "SELECT * from users WHERE email = ('{}')".format(email)
        mycursor.execute(sql)
        user = mycursor.fetchone()
        if user:
            if password in user[1]:
                session['name'] = user[2]
                session['email'] = user[0]
                session['userid'] = email
                session['user'] = user[3]
                session['FILE_ROOT_DIR'] = 'data/{}/Files/'.format(
                    session['userid'])
                session['BIN_ROOT_DIR'] = 'data/{}/bin/'.format(
                    session['userid'])
                session['DOWNLOAD_ROOT_DIR'] = 'data/{}/Files/Downloads/'.format(
                    session['userid'])
                try:
                    session['pic'] = 'data/{}/profile.png'.format(
                        session['userid'])
                except:
                    session['pic'] = 'static/sample.png'
                return redirect(url_for('show_file'))
            else:
                return render_template("signin.html", error="a", message="Wrong Password")
        else:
            return render_template("signup.html", error="a", message="User not found")
    else:
        return render_template("signin.html")

# register admin


@app.route('/register-admin', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        sql = "SELECT * from users WHERE user = ('{}')".format("admin")
        mycursor.execute(sql)
        user = mycursor.fetchone()
        if user:
            return render_template("signin.html", error="a", message="Admin already registered")
        else:
            return render_template("signup.html")
    else:
        name = request.form['name']
        email = request.form['email']
        email = email.lower()
        password = request.form['password']
        sql = "SELECT * from users WHERE email = ('{}')".format(email)
        mycursor.execute(sql)
        user1 = mycursor.fetchall()
        if user1:
            return render_template("signup.html", error="a", message='User exists')
        user = 'admin'
        sql = "INSERT INTO users (email, password, name, user) VALUES ('{}', '{}', '{}', '{}')".format(
            email, password, name, user)
        mycursor.execute(sql)
        mydb.commit()
        userid = email
        print("User Registered")
        print('Making Directories')
        os.mkdir("data/{}".format(userid))
        os.mkdir("data/{}/Files".format(userid))
        os.mkdir("data/{}/Files/Sync".format(userid))
        os.mkdir("data/{}/Files/Downloads".format(userid))
        os.mkdir("data/{}/bin".format(userid))
        return render_template('signin.html', success="a", message="User Registered")

# register user


@app.route('/register_user', methods=["GET", "POST"])
def register_user():
    if request.method == 'GET':
        sql = "SELECT * from users"
        mycursor.execute(sql)
        users = mycursor.fetchall()
        arr = []
        size = 0
        for user in users:
            dic = {}
            size = 0
            path1 = os.path.join(os.getcwd(), 'data')
            path2 = os.path.join(path1, user[0])
            pathimg = os.path.join('data', user[0])
            for path, dirs, files in os.walk(path2):
                for f in files:
                    fp = os.path.join(path, f)
                    size += os.path.getsize(fp)
            size = round(size/1024/1024, 2)
            dic['image'] = os.path.join(pathimg, 'profile.png')
            dic['email'] = user[0]
            dic['name'] = user[2]
            dic['size'] = size
            dic['user'] = user[3]
            arr.append(dic)
        return render_template("register_user.html", users=arr)
    else:
        name = request.form['name']
        email = request.form['email']
        email = email.lower()
        password = request.form['password']
        user = request.form['user']
        print(name, email, password, user)
        sql = "SELECT * from users WHERE email = ('{}')".format(email)
        mycursor.execute(sql)
        user1 = mycursor.fetchall()
        if user1:
            sql = "SELECT * from users"
            mycursor.execute(sql)
            users = mycursor.fetchall()
            return render_template("register_user.html", error="a", message='User exists', users=users)
        sql = "INSERT INTO users (email, password, name, user) VALUES ('{}', '{}', '{}', '{}')".format(
            email, password, name, user)
        mycursor.execute(sql)
        mydb.commit()
        userid = email
        print("User Registered")
        print('Making Directories')
        os.mkdir("data/{}".format(userid))
        os.mkdir("data/{}/Files".format(userid))
        os.mkdir("data/{}/Files/Sync".format(userid))
        os.mkdir("data/{}/Files/Downloads".format(userid))
        os.mkdir("data/{}/bin".format(userid))
        sql = "SELECT * from users"
        mycursor.execute(sql)
        users = mycursor.fetchall()
        arr = []
        size = 0
        for user in users:
            dic = {}
            size = 0
            path1 = os.path.join(os.getcwd(), 'data')
            path2 = os.path.join(path1, user[0])
            pathimg = os.path.join('data', user[0])
            for path, dirs, files in os.walk(path2):
                for f in files:
                    fp = os.path.join(path, f)
                    size += os.path.getsize(fp)
            size = round(size/1024/1024, 2)
            dic['image'] = os.path.join(pathimg, 'profile.png')
            dic['email'] = user[0]
            dic['name'] = user[2]
            dic['size'] = size
            dic['user'] = user[3]
            arr.append(dic)
        return render_template('/register_user.html', success="a", message="User Registered", users=arr)

# del user


@app.route('/delete_user/<string:email>', methods=["GET", "POST"])
def delete_user(email):
    sql = "select * from users where user = '{}'".format("admin")
    mycursor.execute(sql)
    user = mycursor.fetchall()
    if len(user) == 1:
        return jsonify({'message': 'Atleast one admin required'})
    else:
        sql = "delete from users where email = '{}'".format(email)
        mycursor.execute(sql)
        shutil.rmtree("data/{}".format(email))
        mydb.commit()
        return jsonify({'message': 'User Deleted'})

# show profile


@app.route('/edituser/<string:email>', methods=["GET", "POST"])
def edituser(email):
    pathimg = os.path.join('data', email)
    userimg = os.path.join(pathimg, 'profile.png')
    sql = "SELECT * from users WHERE email = ('{}')".format(email)
    mycursor.execute(sql)
    user = mycursor.fetchone()
    return render_template("edit_user.html", user=user, userimg=userimg)

# show profile


@app.route('/edit_user', methods=["GET", "POST"])
def edit_user():
    name = request.form['name']
    password = request.form['password']
    user = request.form['user']
    email = request.form['email']
    sql = "select * from users where user = '{}'".format("admin")
    mycursor.execute(sql)
    user1 = mycursor.fetchall()
    if user1 == "Admin":
        if len(user1) == 1:
            flash("Altleast one admin required")
            return redirect("edituser/{}".format(email))
        else:
            sql = "UPDATE users set name = ('{}'), password = ('{}'), user = ('{}') WHERE email = ('{}')".format(
                name, password, user, email)
            mycursor.execute(sql)
            flash("Details Updated")
            return redirect("edituser/{}".format(email))
    else:
        sql = "UPDATE users set name = ('{}'), password = ('{}'), user = ('{}') WHERE email = ('{}')".format(
            name, password, user, email)
        mycursor.execute(sql)
        flash("Details Updated")
        return redirect("edituser/{}".format(email))

# error handler


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# error page


@app.route('/error')
def error():
    return render_template('404.html')

# logout


@app.route('/logout', methods=["GET", "POST"])
def logout():
    try:
        os.remove(os.path.join(os.path.join(
            session['FILE_ROOT_DIR'], "Takeout.zip")))
    except:
        pass
    session.clear()
    return redirect("/")

# custom path for files


@app.route('/custom_static/<path:filename>')
def custom_static(filename):
    path = filename.split('/')
    filename = path[-1]
    path = '/'.join(path[:-1])
    return send_from_directory(path, filename)

# download photos


@app.route('/downloadimage/<path:subpath>', methods=['GET', 'POST'])
def downloadimage(subpath):
    path = subpath.split('/')
    filename = path[-1]
    path = '/'.join(path[:-1])
    return send_from_directory(path, filename, as_attachment=True)

# delete photos


@app.route('/deletephoto/<path:subpath>', methods=['GET', 'POST'])
def deletephoto(subpath):
    try:
        path = subpath.split('/')
        filename = path[-1]
        path = '/'.join(path[:-1])
        source = os.path.join(path, filename)
        os.utime(source)
        destination = os.path.join(session['BIN_ROOT_DIR'], filename)
        shutil.move(source, destination)
        return jsonify({"message": "Moved to Bin"})
    except:
        return jsonify({"message": "Unable to delete"})

# show only photos


@app.route('/image', methods=['GET', 'POST'])
def show_gallery():
    try:
        if session.get("name"):
            year = []
            arr = []
            images = []
            path = [x[0] for x in os.walk(session['FILE_ROOT_DIR'])]
            for q in path:
                images.append(Image1.all(q))
            for k in images:
                for j in k:
                    name, ext = os.path.splitext(j.path)
                    ext = ext.lower()
                    if ext in ALLOWED_EXTENSIONS_IMAGE:
                        arr.append(j)
            for i in arr:
                if i.date not in year:
                    year.append(i.date)
            year.sort(reverse=True)
            l = len(arr)
            return render_template('image.html', images=arr, year=year, le=l)
        else:
            return redirect(url_for('error'))
    except:
        return redirect(url_for('error'))

# show only videos


@app.route('/video', methods=['GET', 'POST'])
def show_video():
    try:
        if session.get("name"):
            arr = []
            images = []
            path = [x[0] for x in os.walk(session['FILE_ROOT_DIR'])]
            for q in path:
                images.append(Image1.all(q))
            for k in images:
                for j in k:
                    name, ext = os.path.splitext(j.path)
                    ext = ext.lower()
                    if ext in ALLOWED_EXTENSIONS_VIDEO:
                        arr.append(j)
            sql = "SELECT * from video where id = ('{}')".format(
                session.get("email"))
            mycursor.execute(sql)
            resume = mycursor.fetchall()
            res = []
            for a in arr:
                for r in resume:
                    if r[0] == str(a.path) and r[1] != '0':
                        res.append(a)
            return render_template('video.html', files=arr, res=res)
        else:
            return redirect(url_for('error'))
    except:
        return redirect(url_for('error'))

# upload file


@app.route('/uploadfile/<path:subpath>', methods=['POST'])
def uploadfile(subpath):
    try:
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        filename = gen_file_name(uploaded_file.filename, subpath)
        filename = filename.replace(" ", "_")
        uploaded_file.save(os.path.join(subpath, filename))
        return make_response(("Upload successful", 200))
    except:
        return make_response(("Upload not successful", 400))

# generate filename


def gen_file_name(filename, path):
    i = 1
    while os.path.exists(os.path.join(path, filename)):
        name, extension = os.path.splitext(filename)
        filename = '%s_%s%s' % (name, str(i), extension)
        i += 1
    return filename

# create new folder


@app.route('/newfiledir', methods=['GET', 'POST'])
def newfiledir():
    try:
        information = request.data
        data = json.loads(information)
        path = data[1]
        name = data[0]
        i = 1
        while os.path.exists(os.path.join(path, name)):
            name = '%s_%s' % (name, str(i))
            i += 1
        name = name.replace(" ", "_")
        os.mkdir(os.path.join(path, name))
        return jsonify({'message': 'Folder Created'})
    except:
        return jsonify({'message': 'Unable to create'})

# show file


@app.route('/file', methods=['GET', 'POST'])
def show_file():
    try:
        path = "/"
        stat = shutil.disk_usage(path)
        free = math.floor(stat.free/1024/1024/1024)
        total = math.floor(stat.total/1024/1024/1024)
        session['free'] = free
        session['total'] = total
        session['percentage'] = ((total-free)/total)*100
        if session.get("name"):
            sql = "SELECT email from users"
            mycursor.execute(sql)
            users = mycursor.fetchall()
            year = []
            arr = []
            images = []
            path = [x[0] for x in os.walk(session['FILE_ROOT_DIR'])]
            for q in path:
                images.append(Image1.all(q))
            for k in images:
                for j in k:
                    name, ext = os.path.splitext(j.path)
                    ext = ext.lower()
                    if ext in ALLOWED_EXTENSIONS_IMAGE:
                        arr.append(j)
            for i in arr:
                if i.date not in year:
                    year.append(i.date)
            year.sort(reverse=True)
            files = Image1.all(session['FILE_ROOT_DIR'])
            path1 = session['FILE_ROOT_DIR'].split('/')
            path1 = path1[2:-1]
            dirpath = [x[0] for x in os.walk(session['FILE_ROOT_DIR'])]
            dirname = []
            for i in dirpath:
                a = i.split('/')
                a = a[2:]
                a = '/'.join(a)
                dirname.append(a)
            lst = []
            for i in range(len(dirname)):
                dic = {}
                dic["key"] = dirname[i]
                dic["value"] = dirpath[i]
                lst.append(dic)
            return render_template('file.html', files=files, path=session['FILE_ROOT_DIR'], path1=path1, lst=lst, images=arr, year=year, users=users)
        else:
            return redirect(url_for('error'))
    except:
        return redirect(url_for('error'))

# rename file


@app.route('/renamefile', methods=['GET', 'POST'])
def renamefile():
    try:
        information = request.data
        data = json.loads(information)
        newname = data[1]
        path = data[0].split('/')
        filename = path[-1]
        if filename == "Sync" or filename == "Downloads":
            return jsonify({'message': "Not able to rename"})
        path = '/'.join(path[:-1])
        i = 1
        while os.path.exists(os.path.join(session['FILE_ROOT_DIR'], newname)):
            name, ext = os.path.splitext(newname)
            newname = '%s_%s%s' % (name, str(i), ext)
        old1 = os.path.join(path, filename)
        new1 = os.path.join(path, newname)
        new1 = new1.replace(" ", "_")
        os.rename(old1, new1)
        return jsonify({'message': "Renamed"})
    except:
        return jsonify({'message': "Unable to rename"})

# delete multiple files


@app.route('/deletefiles', methods=['GET', 'POST'])
def deletefiles():
    try:
        information = request.data
        data = json.loads(information)
        for i in data:
            path = i.split('/')
            filename = path[-1]
            path = '/'.join(path[:-1])
            source = os.path.join(path, filename)
            os.utime(source)
            destination = os.path.join(session['BIN_ROOT_DIR'], filename)
            if filename == 'Sync' or filename == "Downloads":
                continue
            shutil.move(source, destination)
            try:
                id = filename+session['email']
                sql = "DELETE FROM shared WHERE id = '{}'".format(id)
                mycursor.execute(sql)
                mydb.commit()
            except:
                pass
        return jsonify({'message': 'Moved to Bin'})
    except:
        return jsonify({'message': 'Unable to delete'})


@app.route('/deletefile', methods=['GET', 'POST'])
def deletefile():
    try:
        information = request.data
        data = json.loads(information)
        i = data[0]
        path = i.split('/')
        filename = path[-1]
        path = '/'.join(path[:-1])
        source = os.path.join(path, filename)
        os.utime(source)
        destination = os.path.join(session['BIN_ROOT_DIR'], filename)
        if filename == 'Sync':
            return jsonify({'message': 'Unable to delete Sync'})
        if filename == "Downloads":
            return jsonify({'message': 'Unable to delete Downloads'})
        shutil.move(source, destination)
        return jsonify({'message': 'Moved to Bin'})
    except:
        return jsonify({'message': 'Unable to delete'})

# share files with others


@app.route('/sharefiles/<path:emailto>', methods=['GET', 'POST'])
def sharefiles(emailto):
    try:
        information = request.data
        data = json.loads(information)
        for i in data:
            path = i.split('/')
            filename = path[-1]
            date1 = date.today().strftime("%d-%m-%Y")
            path = '/'.join(path[:-1])
            id = filename+session['email']+emailto
            sql = "INSERT INTO shared (filename, path, email, emailto,date, id) VALUES ('{}', '{}' , '{}', '{}', '{}', '{}')".format(
                filename, path, session['email'], emailto, date1, id)
            mycursor.execute(sql)
            mydb.commit()
        return jsonify({'message': 'Shared'})
    except:
        return jsonify({'message': 'Not able to share'})

# move files to another directories


@app.route('/movefiles/<path:newpath>', methods=['GET', 'POST'])
def movefiles(newpath):
    try:
        information = request.data
        data = json.loads(information)
        destination = newpath
        for i in data:
            path = i.split('/')
            filename = path[-1]
            source = i
            if filename == 'Sync' or filename == "Downloads":
                continue
            shutil.move(source, destination)
            msg = 'Moved to {}'.format(destination)
            try:
                id = filename+session['email']
                sql = "DELETE FROM shared WHERE id = '{}'".format(id)
                mycursor.execute(sql)
                mydb.commit()
            except:
                pass
        return jsonify({'message': msg})
    except:
        return jsonify({'message': 'Unable to move'})

# show file


@app.route('/showfile/<path:subpath>', methods=["GET", "POST"])
def showfile(subpath):
    try:
        if session.get("email") in subpath:
            sql = "SELECT email from users"
            mycursor.execute(sql)
            users = mycursor.fetchall()
            path = subpath.split('/')
            filename = path[-1]
            path = '/'.join(path[:-1])
            dirpath = [x[0] for x in os.walk(session['FILE_ROOT_DIR'])]
            dirname = []
            for i in dirpath:
                a = i.split('/')
                a = a[2:]
                a = '/'.join(a)
                dirname.append(a)
            lst = []
            for i in range(len(dirname)):
                dic = {}
                dic["key"] = dirname[i]
                dic["value"] = dirpath[i]
                lst.append(dic)
            name, ext = os.path.splitext(filename)
            ext = ext.lower()
            if ext == '.zip':
                print("zip")
                files = Image1.all(path)
                path1 = subpath.split('/')
                path1 = path1[2:]
                multiprocessing.Process(
                    target=unzip, args=(path, subpath)).start()
                red = '/showfile/{}'.format(path)
                flash("{} Unzipping".format(filename))
                return redirect(red)
            if ext not in ALLOWED_EXTENSIONS_AUDIO and ext not in ALLOWED_EXTENSIONS_VIDEO and ext not in ALLOWED_EXTENSIONS_DOCUMENT and ext not in ALLOWED_EXTENSIONS_IMAGE:
                files = Image1.all(subpath)
                path1 = subpath.split('/')
                path1 = path1[2:]
                return render_template('file.html', files=files, path=subpath, path1=path1, lst=lst, users=users)
            name1, ext1 = os.path.splitext(filename)
            ext1 = ext1.lower()
            if ext1 in ALLOWED_EXTENSIONS_AUDIO:
                return redirect('/playaudio/{}'.format(subpath))
            if ext1 in ALLOWED_EXTENSIONS_VIDEO:
                return redirect('/playvideo/{}'.format(subpath))
            return send_from_directory(path, filename)
        else:
            return redirect(url_for('error'))
    except:
        return redirect(url_for('error'))

# play video page


@app.route("/playvideo/<path:subpath>")
def playvideo(subpath):
    path = subpath.split('/')
    filename = path[-1]
    path = '/'.join(path[:-1])
    na, ex = os.path.splitext(subpath)
    poster = na+'.jpg'
    nam = na+".srt"
    nam2 = na+".vtt"
    nam3 = na+".en.srt"
    try:
        if os.path.exists(nam):
            webvtt.from_srt(nam).save()
            nam = na+".vtt"
        if os.path.exists(nam2):
            nam = na+".vtt"
        if os.path.exists(nam3):
            webvtt.from_srt(nam3).save()
            nam = na+".en.vtt"
    except:
        pass
    arr = []
    videos = []
    path = [x[0] for x in os.walk(path)]
    for q in path:
        videos.append(Image1.all(q))
    for k in videos:
        for j in k:
            name, ext = os.path.splitext(j.path)
            ext = ext.lower()
            if ext in ALLOWED_EXTENSIONS_VIDEO:
                arr.append(j)
    arr.sort(key=lambda x: x.path)
    for i in range(len(arr)):
        if str(arr[i].path) == str(filename):
            try:
                video = arr[i+1]
                break
            except:
                video = ""
        else:
            video = ""
    sql = "SELECT time from video WHERE filename = ('{}') and id = ('{}')".format(
        filename, session.get("email"))
    mycursor.execute(sql)
    time = mycursor.fetchone()
    if time:
        time1 = time[0]
    else:
        time1 = 0
    return render_template('playvideo.html', path=subpath, name=filename, video=video, n=nam, time=time1, poster=poster)


# play audio page


@app.route("/playaudio/<path:subpath>")
def playaudio(subpath):
    path = subpath.split('/')
    filename = path[-1]
    path = '/'.join(path[:-1])
    arr = []
    audios = []
    path = [x[0] for x in os.walk(session['FILE_ROOT_DIR'])]
    for q in path:
        audios.append(Image1.all(q))
    for k in audios:
        for j in k:
            name, ext = os.path.splitext(j.path)
            ext = ext.lower()
            if ext in ALLOWED_EXTENSIONS_AUDIO:
                arr.append(j)
    audio = random.choice(arr)
    return render_template('playaudio.html', path=subpath, name=filename, audio=audio)


def unzip(path, subpath):
    with ZipFile(subpath, 'r') as zip_ref:
        zip_ref.extractall(path)

# convert video


@app.route('/converttomp4/<path:subpath>')
def converttomp4(subpath):
    file = subpath.split('/')
    filename = file[-1]
    path = '/'.join(file[:-1])
    old = os.path.join(path, filename)
    name, ext = os.path.splitext(filename)
    new = os.path.join(path, name+"_converted.mp4")
    multiprocessing.Process(target=convert_mp4, args=(old, new)).start()
    red = '/showfile/{}'.format(path)
    flash("Converting")
    return redirect(red)


def convert_mp4(old, new):
    comd = "ffmpeg -i {} -codec copy {}".format(old, new)
    os.system(comd)

# show files from directories


@app.route('/showfile1/<path:name>/<path:path>')
def showfile1(path, name):
    try:
        if session.get("email") in path:
            sql = "SELECT email from users"
            mycursor.execute(sql)
            users = mycursor.fetchall()
            dirpath = [x[0] for x in os.walk(session['FILE_ROOT_DIR'])]
            path = path.split('/')
            dirname = []
            for i in dirpath:
                a = i.split('/')
                a = a[2:]
                a = '/'.join(a)
                dirname.append(a)
            lst = []
            for i in range(len(dirname)):
                dic = {}
                dic["key"] = dirname[i]
                dic["value"] = dirpath[i]
                lst.append(dic)
            subpath = []
            for i in path:
                if (i == name):
                    subpath.append(i)
                    break
                subpath.append(i)
            path1 = '/'.join(subpath)
            files = Image1.all(path1)
            path2 = path1.split('/')
            path2 = path2[2:]
            return render_template('file.html', files=files, path=path1, path1=path2, lst=lst, users=users)
    except:
        return redirect(url_for('error'))


def zipfile(names, path):
    with ZipFile('{}.zip'.format(session.get('email')), 'w') as zip:
        for file0 in names:
            n, e = os.path.splitext(file0)
            if not e:
                file1 = get_all_file_paths(os.path.join(path, file0))
                for file in file1:
                    zip.write(file)
            else:
                file1 = os.path.join(path, file0)
                zip.write(file1)
    source = os.path.join(os.getcwd(), '{}.zip'.format(session.get('email')))
    destination = os.path.join(session['FILE_ROOT_DIR'], 'Takeout.zip')
    shutil.move(source, destination)
    return

# download multiple files


@app.route('/downloadfiles', methods=["GET", "POST"])
def downloadfiles():
    try:
        names = []
        information = request.data
        data = json.loads(information)
        for i in data:
            path = i.split('/')
            filename = path[-1]
            path = '/'.join(path[:-1])
            names.append(filename)
        zipfile(names, path)
        return
    except:
        return jsonify({'message': 'Unable to create zip'})

# download file


@app.route('/downloadfile/<path:name1>/<path:subpath>', methods=["GET", "POST"])
def downloadfile(name1, subpath):
    path = subpath.split('/')
    filename = path[-1]
    name, extension = os.path.splitext(filename)
    path = '/'.join(path[:-1])
    if not extension:
        file_paths = get_all_file_paths(subpath)
        with ZipFile('{}.zip'.format(session.get('email')), 'w') as zip:
            for file in file_paths:
                zip.write(file)
        source = os.path.join(
            os.getcwd(), '{}.zip'.format(session.get('email')))
        destination = os.path.join(session['FILE_ROOT_DIR'], 'Takeout.zip')
        shutil.move(source, destination)
        return send_from_directory(session['FILE_ROOT_DIR'], "Takeout.zip", as_attachment=True)
    return send_from_directory(path, filename, as_attachment=True)

# get all files in directory


def get_all_file_paths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths

# show shared


@app.route('/shared', methods=['GET', 'POST'])
def show_shared():
    try:
        if session.get("name"):
            sql = "SELECT * from shared"
            mycursor.execute(sql)
            files = mycursor.fetchall()
            dirpath = [x[0] for x in os.walk(session['FILE_ROOT_DIR'])]
            dirname = []
            for i in dirpath:
                a = i.split('/')
                a = a[2:]
                a = '/'.join(a)
                dirname.append(a)
            lst2 = []
            for i in range(len(dirname)):
                dic = {}
                dic["key"] = dirname[i]
                dic["value"] = dirpath[i]
                lst2.append(dic)
            return render_template('shared.html', files=files, lst2=lst2)
    except:
        return redirect(url_for('error'))

# show shared file


@app.route('/showshared/<filename>/<path:subpath>', methods=['GET', 'POST'])
def showshared(filename, subpath):
    try:
        if session.get("name"):
            path = os.path.join(subpath, filename)
            name, ext = os.path.splitext(filename)
            if not ext:
                file_paths = get_all_file_paths(path)
                with ZipFile('{}.zip'.format(session.get('email')), 'w') as zip:
                    for file in file_paths:
                        zip.write(file)
                source = os.path.join(
                    os.getcwd(), '{}.zip'.format(session.get('email')))
                destination = os.path.join(
                    session['FILE_ROOT_DIR'], 'Takeout.zip')
                shutil.move(source, destination)
                return send_from_directory(session['FILE_ROOT_DIR'], "Takeout.zip", as_attachment=True)
            return send_from_directory(subpath, filename)
    except:
        return redirect(url_for('error'))

# download shared file


@app.route('/downloadshared/<filename>/<path:path>', methods=["GET", "POST"])
def downloadshared(filename, path):
    name, ext = os.path.splitext(filename)
    subpath = os.path.join(path, filename)
    if not ext:
        file_paths = get_all_file_paths(subpath)
        with ZipFile('{}.zip'.format(session.get('email')), 'w') as zip:
            for file in file_paths:
                zip.write(file)
        source = os.path.join(
            os.getcwd(), '{}.zip'.format(session.get('email')))
        destination = os.path.join(session['FILE_ROOT_DIR'], 'Takeout.zip')
        shutil.move(source, destination)
        return send_from_directory(session['FILE_ROOT_DIR'], "Takeout.zip", as_attachment=True)
    return send_from_directory(path, filename, as_attachment=True)

# delete shared file


@app.route('/deleteshared', methods=['GET', 'POST'])
def deleteshared():
    try:
        information = request.data
        data = json.loads(information)
        id = data[0]
        sql = "DELETE FROM shared WHERE id = '{}'".format(id)
        mycursor.execute(sql)
        mydb.commit()
        return jsonify({'message': 'Removed from sharing'})
    except:
        return jsonify({'message': 'Not able to remove'})

# movw shared files to personal directory


@app.route('/moveshared', methods=['GET', 'POST'])
def moveshared():
    try:
        information = request.data
        data = json.loads(information)
        destination = data[0]
        source = os.path.join(data[2], data[1])
        shutil.copy(source, destination)
        return jsonify({'message': 'Copied'})
    except:
        return jsonify({'message': 'Unable to copy'})

# Bin


@app.route('/bin', methods=['GET', 'POST'])
def show_bin():
    try:
        if session.get("name"):
            file1 = Image1.all(session['BIN_ROOT_DIR'])
            for i in file1:
                old_time = datetime.datetime.strptime(i.date, "%d-%m-%Y")
                current_time = datetime.datetime.now().strftime("%d-%m-%Y")
                current_time1 = datetime.datetime.strptime(
                    current_time, "%d-%m-%Y")
                diff = current_time1 - old_time
                if diff.days > 30:
                    os.remove(os.path.join(session['BIN_ROOT_DIR'], i.path))
            images = Image1.all(session['BIN_ROOT_DIR'])
            return render_template('bin.html', images=images)
        else:
            return redirect(url_for('error'))
    except:
        return redirect(url_for('error'))

# deleting multiple files from trash


@app.route('/deletebins', methods=['GET', 'POST'])
def deletebins():
    try:
        information = request.data
        data = json.loads(information)
        for i in data:
            name1, extension = os.path.splitext(i)
            if extension not in ALLOWED_EXTENSIONS_AUDIO and extension not in ALLOWED_EXTENSIONS_VIDEO and extension not in ALLOWED_EXTENSIONS_DOCUMENT and extension not in ALLOWED_EXTENSIONS_IMAGE:
                try:
                    shutil.rmtree(os.path.join(session['BIN_ROOT_DIR'], i))
                except:
                    os.remove(os.path.join(session['BIN_ROOT_DIR'], i))
            else:
                os.remove(os.path.join(session['BIN_ROOT_DIR'], i))
        return jsonify({'message': 'Deleted', 'urll': url_for('show_bin')})
    except:
        return jsonify({'message': 'Unable to Delete'})

# restoring multiple files from trash


@app.route('/restoremultiple', methods=['GET', 'POST'])
def restoremultiple():
    try:
        if session.get("name"):
            try:
                information = request.data
                data = json.loads(information)
                for i in data:
                    source = os.path.join(session['BIN_ROOT_DIR'], i)
                    j = 1
                    while os.path.exists(os.path.join(session['FILE_ROOT_DIR'], i)):
                        name, extension = os.path.splitext(i)
                        i = '%s_%s%s' % (name, str(i), extension)
                        j += 1
                    destination = os.path.join(session['FILE_ROOT_DIR'], i)
                    shutil.move(source, destination)
                return jsonify({'message': 'Restored to home directory'})
            except:
                return jsonify({'message': 'Not able restore'})
    except:
        return redirect(url_for('error'))

# empty trash


@app.route('/emptytrash', methods=["POST"])
def emptytrash():
    try:
        folder = session['BIN_ROOT_DIR']
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        return jsonify({"message": "Trash emptied"})
    except:
        return jsonify({"message": "Not able to Delete"})

# sending file to public link


@app.route('/public/<path:subpath>')
def public(subpath):
    arr = subpath.split('/')
    filename = arr[-1]
    path = '/'.join(arr[:-1])
    name, extension = os.path.splitext(filename)
    if not extension:
        file_paths = get_all_file_paths(subpath)
        with ZipFile('{}.zip'.format(session.get('email')), 'w') as zip:
            for file in file_paths:
                zip.write(file)
        source = os.path.join(
            os.getcwd(), '{}.zip'.format(session.get('email')))
        destination = os.path.join(session['FILE_ROOT_DIR'], 'Takeout.zip')
        shutil.move(source, destination)
        return send_from_directory(session['FILE_ROOT_DIR'], "Takeout.zip", as_attachment=True)
    return send_from_directory(path, filename, as_attachment=True)

# syncing folders


@app.route('/sync/<user>')
def sync(user):
    dic = {}
    path = 'data/{}/files/sync'.format(user)
    folder = Image1.all(path)
    for i in range(len(folder)):
        dic[i] = str(folder[i].path)
    return dic

# sending files to local sync


@app.route('/getToLocal/<user>/<filename>')
def getToLocal(user, filename):
    path = 'data/{}/files/sync'.format(user)
    return send_from_directory(path, filename, as_attachment=True)

# sending files to cloud sync


@app.route('/getToCloud/<user>', methods=['POST'])
def getToCloud(user):
    if request.method == 'POST':
        path = 'data/{}/files/sync'.format(user)
        file = request.files
        file_final = file['file']
        file_final.save(os.path.join(path, file_final.filename))
        return "200"

# show downloads


@app.route('/download', methods=["GET", "POST"])
def download():
    torrents = qb.torrents()
    downloads = Image1.all(session["DOWNLOAD_ROOT_DIR"])
    return render_template("download.html", downloads=downloads, torrents=torrents)

# downloading video


@app.route('/download_yt', methods=["GET", "POST"])
def download_yt():
    link = request.form['link']
    quality = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]'
    output = str("{}%(title)s.%(ext)s".format(session['DOWNLOAD_ROOT_DIR']))
    url = str("youtube-dl -f '{}' -o '{}' '{}'".format(quality, output, link))
    multiprocessing.Process(target=downloadyt, args=(url,)).start()
    flash("Downloading YT Video")
    return redirect(url_for('download'))


def downloadyt(url):
    os.system(url)

# downloading audio


@app.route('/download_audio', methods=["GET", "POST"])
def download_audio():
    link = request.form['link']
    quality = 'bestaudio[ext=m4a]'
    output = str("{}%(title)s.%(ext)s".format(session['DOWNLOAD_ROOT_DIR']))
    url = str("youtube-dl -f '{}' -o '{}' '{}'".format(quality, output, link))
    multiprocessing.Process(target=downloadaudio, args=(url,)).start()
    flash("Downloading YT Audio")
    return redirect(url_for('download'))


def downloadaudio(url):
    os.system(url)

# downloading file


@app.route('/download_file', methods=["GET", "POST"])
def download_file():
    file_url = request.form['link']
    path = session['DOWNLOAD_ROOT_DIR']
    multiprocessing.Process(target=downloadfile,
                            args=(file_url, path,)).start()
    flash("Downloading File")
    return redirect(url_for('download'))


def downloadfile(file_url, path):
    r = requests.get(file_url, stream=True)
    file_name = file_url.split('/')[-1]
    filename = os.path.join(path, file_name)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

# downloading torrent


@app.route('/download_torrent', methods=["GET", "POST"])
def download_torrent():
    magnet_link = request.form['link']
    path = session['DOWNLOAD_ROOT_DIR']
    multiprocessing.Process(target=downloadtorrent,
                            args=(magnet_link, path,)).start()
    flash("Downloading Torrent")
    return redirect(url_for('download'))


def downloadtorrent(magnet_link, path):
    qb.download_from_link(magnet_link, savepath=path)

# show profile


@app.route('/profile', methods=["GET", "POST"])
def profile():
    if request.method == "GET":
        sql = "SELECT * from users WHERE email = ('{}')".format(
            session['email'])
        mycursor.execute(sql)
        user = mycursor.fetchone()
        return render_template("profile.html", user=user)
    else:
        name = request.form['name']
        password = request.form['password']
        sql = "UPDATE users set name = ('{}'), password = ('{}') WHERE email = ('{}')".format(
            name, password, session['email'])
        mycursor.execute(sql)
        flash("Details Updated")
        return redirect(url_for("profile"))

# delete profile image


@app.route('/deleteimage', methods=["POST"])
def deleteimage():
    path = os.path.join(
        os.getcwd(), 'data/{}/profile.png'.format(session['email']))
    try:
        os.remove(path)
        session['pic'] = " "
        return jsonify({"message": "Image removed"})
    except:
        return jsonify({"message": "No image found"})

# edit profile image


@app.route('/editimage', methods=["POST"])
def editimage():
    path = os.path.join(
        os.getcwd(), 'data/{}/profile.png'.format(session['email']))
    image = request.files['image']
    image.save(path)
    session['pic'] = 'data/{}/profile.png'.format(session['userid'])
    flash("Image will be updated")
    return redirect(url_for('profile'))


@app.route('/system')
def system():
    cpu = psutil.cpu_percent(4)
    ram = psutil.virtual_memory()[2]
    stat = shutil.disk_usage('/')
    total = math.floor(stat.total/1024/1024/1024)
    free = math.floor(stat.free/1024/1024/1024)
    used = total-free
    return render_template("system.html", ram=ram, used=used, cpu=cpu, total=total, free=free)


@app.route('/savetime', methods=["POST"])
def savetime():
    information = request.data
    data = json.loads(information)
    try:
        sql = "INSERT INTO video (filename,time,id) VALUES('{}','{}','{}') ON DUPLICATE KEY UPDATE filename='{}', time='{}', id='{}' ".format(
            data[1], data[0], session.get("email"), data[1], data[0], session.get("email"))
        mycursor.execute(sql)
        mydb.commit()
    except:
        print("Error saving progress")
    return jsonify({"message": "done"})


@app.route('/removevideoprogress', methods=["POST"])
def removevideoprogress():
    try:
        information = request.data
        data = json.loads(information)
        sql = "Delete from video where filename like '{}' and id like '{}' ".format(
            data[0], session.get('email'))
        mycursor.execute(sql)
        mydb.commit()
    except:
        print("Unable to remove continue watching")
    return jsonify({"message": "Removed from continue watching"})

#####END#####
