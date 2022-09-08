import os
from models import Image1
import urllib.request as request
from bs4 import BeautifulSoup
import json
import wget
import time
import requests

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
    link = input("Link: ")
    f = open("sync.txt", "a")
    f.write(email)
    f.write("\t")
    f.write(password)
    f.write("\t")
    f.write(link)
    f.close()

print("Starting server to sync")
while True:
    files_cloud = []
    files_local = []

    local = Image1.all(source_folder)
    for q in local:
        files_local.append(str(q.path))
    url = "{}/sync/{}".format(link, userid)
    try:
        response = request.urlopen(url)
        soup = BeautifulSoup(response, 'html.parser')
        files = json.loads(str(soup))
        for i in files.values():
            files_cloud.append(i)
    except:
        print("Unable to establish connection")

    # for p in files_cloud:
    #     if p not in files_local:
    #         try:
    #             wget.download("{}/getToLocal/{}/{}".format(link,
    #                           userid, p), 'sync/{}'.format(p))
    #             print("File downloaded from cloud")
    #         except:
    #             print("Not able to download")

    for w in files_local:
        if w not in files_cloud:
            try:
                if w == ".DS_Store":
                    continue
                path = os.path.join(source_folder, w)
                test_file = open(path, "rb")
                files = {
                    'file': (w, open('sync/{}'.format(w), 'rb'), 'text/csv')}
                print("Uploading")
                test_response = requests.post(
                    "{}/getToCloud/{}".format(link, userid), files=files)
                print(test_response.text)
                print("File uploaded to Cloud")
            except:
                print("Not able to upload")
    time.sleep(2)
