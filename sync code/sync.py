import os
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
from models import Image1
import urllib.request as request
from bs4 import BeautifulSoup
import json
import wget
import time
import requests

authconfig = {
    "databaseURL" : "",
    "apiKey": "AIzaSyDbpGOYeQiO-zSNzFIhV1ARBg-IWYmSKLE",
    "authDomain": "mystorage-c0037.firebaseapp.com",
    "projectId": "mystorage-c0037",
    "storageBucket": "mystorage-c0037.appspot.com",
    "messagingSenderId": "609857072687",
    "appId": "1:609857072687:web:2ad53d5f42399a34e3a0da",
    "measurementId": "G-HZE332F31E"
}

config = {
  "type": "service_account",
  "project_id": "mystorage-c0037",
  "private_key_id": "6ad4ea0986d6ac833e1a737313630b146c82f06b",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC1jQdK0cfDL+wA\nxeOlhgBTjMwAx8J6WAQiLXQHLW6HD7BxX2/AKerwZt7lz8tZa0EpVBI6O9Pv/L9e\nUpH4/6B9D3ZGWMiBhidRqh+pf5LFw/EGjqJQTIBkpCQMH5dAYzz/mchr7AJ2xDqh\ne6TG/h3e89bOVUuQpFCqTlbNidkLSzsxYyDFrUuqRlIhYMTqwVcP/L/dDdi93kjB\nitnbeeL1N/lymcKxZR+nMPltxXQLfLXEcwMvAVIcqEbXEtZGvCnI0Tq7Tnb4Ncqm\nUHylNk81t3qyLfVa2Kn+G1CbLKVH0jOkloBlyfxHvNuf0e5MSFRyxuSZYvSb+7hW\nAw+qkkbLAgMBAAECggEAGxkfu4UwYevnN/5RikVECzR6xqsKViSJCWjrZp7bXoFy\n/pkWHwKitJtGLdskKQafRUHtLo/7hFifX77HVvkgxUnnh3x9AQg7Gi9gZnZKPAaR\nFT947q9cgqkVUFHuy4eEdUpI5gLmI0AK2EuSPrlzT/HpYAbPLpm4CJOE1Uz7/nlN\nURs5kGs9KTEYeuJnPMWUrpg44nft0qn3oIsVrjNuX5IIi9IZW/HWTTwvIFKAx9IR\ndRoD06JJv95mxZsCGRdo9l1x5HO9UqMDn6c2tIkiuJegM6CIIGnCjbq0tQQYx5Ty\n7hecduE2hOhKGnsqg+PNfOr/bo9DUIpyK0S+yA/8YQKBgQD0a09fJ4DDHzRmhTWx\nSEol1ZZyaVylOFf/jwpKV61BfLUazrOu64bwqK6COPpr7yzXn/HvFzJYJLAXdLMT\ncH8djj3mgytcKK+8dnTUyns4xvxS/WZf739nbNzcGzBCQRNuK9181eeHlrPq2fiv\nBdVLcvJqlUmuqhauXLpJy3tqCQKBgQC+JyfWdXvktFxA0l7WuzOU/EyrSAS63CeK\ngWnxhBWUQS0UZfZgc452M8e0EMrLH/Qh/5C0RAieu+4r0yy8gEFJNkXbhge8e3SD\nrNOV9dj+akXj8a91/W96y4TXpCHrsnu1iFvHq8pycA78Ue6uULMrUPIlE/4Bv+pO\njElLh4CvMwKBgC5KVJH07VIHCumPuQeGZWSc+w1YHw+7iA8CjDRgPpP0hmg5VZZ/\nTOMvTz2ihOsENT3xMOTTQ9mluSP4GiJIYAq88cRCe2fM3NuYo6/ZWVT7erZM/6KT\nvVFdMMcO7yjdIkzvSddmu57WT+Teu1aKiEbt0jOVaosF8526Oh3Xx9vhAoGBALzF\nmGnyJfWtC+yaK+aW36VnNyHPFEsBJgv9X9SRIO8WKQ+YDZhA/8veqcHb7cbrSOy7\njsc2xyv2O4KsWTwlQyrQQ1ekXmfCU7Ao0cCM2Ufw7sNU+rBy0cog4xdE7RvVC7Ty\n0tKNfCRRlL7vA7lvif9Vk541k7Pe91fVMypVMe47AoGASVIcZ7Ud6UjlSGfJxyWw\nMfgA5BtpKiPgWvc53Djd99wRcpcy810+eBaGzzngS+6tspqX03tFMqgV2UhI23s1\n8Vf2rx/3rHtsnt8DNrvWoQO9SgJ7XseZdX47wBTCYlYAFnjG81q+hw026+zg6CFP\nyTywh54uWC32Ccbyvd1r1TI=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-pvjg7@mystorage-c0037.iam.gserviceaccount.com",
  "client_id": "112206516783906336102",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-pvjg7%40mystorage-c0037.iam.gserviceaccount.com"
}

#firebase init
firebase = pyrebase.initialize_app(authconfig)
auth1 = firebase.auth()
cred = credentials.Certificate(config)
firebase_admin.initialize_app(cred)
db = firestore.client()
storage = firebase.storage()

files_cloud = []
files_local = []

source_folder = "sync"

print("To change id and password , delete sync.txt file")

try:
    f = open("sync.txt", "r")
    a = f.read().split()
    email = a[0]
    password = a[1]
    link = a[2]
    userid = email
except:
    email = input("Email: ")
    password = input("Password: ")
    collection = db.collection('users')
    doc = collection.document(email).get()
    data = doc.to_dict()
    try:
        usr = data['email']
        if usr == email:
            try:
                auth1.sign_in_with_email_and_password(email, password)
                userid = email
            except:
                print("Passsword is incorrect")
    except:
        print("User not found")
    link = input("Link: ")
    f = open("sync.txt", "a")
    f.write(email)
    f.write("\t")
    f.write(password)
    f.write("\t")
    f.write(link)
    f.write("\t")
    f.write(userid)
    f.close()

print("Starting server to sync")
while True:
    files_cloud = []
    files_local = []
    
    local = Image1.all(source_folder)
    for q in local:
        files_local.append(str(q.path))
    url = "{}/sync/{}".format(link,userid)
    try:
        response = request.urlopen(url)
        soup = BeautifulSoup(response, 'html.parser')
        files = json.loads(str(soup))
        for i in files.values():
            files_cloud.append(i)
    except:
        print("Unable to establish connection")

    for p in files_cloud:
        if p not in files_local:
            try:
                wget.download("{}/getToLocal/{}/{}".format(link,userid,p), 'sync/{}'.format(p))
                print("File downloaded from cloud")
            except:
                print("Not able to download")

    for w in files_local:
        if w not in files_cloud:
            try:
                if w == ".DS_Store":
                    continue
                path = os.path.join(source_folder, w)
                test_file = open(path, "rb")
                files = {'file': (w, open('sync/{}'.format(w), 'rb'),'text/csv')}
                print("Uploading")
                test_response = requests.post("{}/getToCloud/{}".format(link,userid), files = files)
                print(test_response.text)
                print("File uploaded to Cloud")
            except:
                print("Not able to upload")
    time.sleep(2)