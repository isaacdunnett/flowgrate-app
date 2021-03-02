import requests
import json
import os
from flask import Flask, render_template, request, redirect, url_for
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from bs4 import BeautifulSoup
from urllib.parse import urljoin

integromatURL = "https://www.integromat.com/en/integrations"
result = requests.get(integromatURL) # make request
print(result.status_code) # status_code of 200 is OK
src = result.content
soup = BeautifulSoup(src, 'lxml')
images = soup.find_all("a", class_="text-center")
    
# # get the CSS files
# css_files = []
# for css in soup.find_all("link"):
#     if css.attrs.get("href"):
#         # if the link tag has the 'href' attribute
#         css_url = urljoin(integromatURL, css.attrs.get("href"))
#         css_files.append(css_url)

# print("Total CSS files in the page:", len(css_files))
# with open("css_files.txt", "w") as f:
#     for css_file in css_files:
#         print(css_file, file=f)

integromatCSSURL = 'https://www.integromat.com/imt/themes.v2.css'
r = requests.get(integromatCSSURL, allow_redirects=True)
# write file links into files
open("../flow-chart-react-app/src/integromatStyle.css", "wb").write(r.content)

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

apiKey = ""
boardId = ""
apiUrl = 'https://api.monday.com/v2'
headers = {'Authorization' : apiKey}

class Auth(FlaskForm):
    key = StringField('', validators=[DataRequired()])

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/mondayhelp")
def mondayhelp():
    return render_template('mondayhelp.html')

@app.route("/develop")
def develop():
    return render_template('develop.html')

@app.route("/apiauthentication")
def apiauthentication():
    return render_template('apiauthentication.html')


@app.route("/chooseboard", methods=['GET', 'POST'])
def chooseboard():
    global apiKey
    apiKey = request.form.get('apiV2Token')
    apiUrl = 'https://api.monday.com/v2'
    headers = {'Authorization' : apiKey}
    query = 'query{boards(limit:1000){name id}}'
    data = {'query' : query}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    boardJSONData = r.json()
    a = json.dumps(boardJSONData)
    d = json.loads(a)
    boardNamesAndIds = d['data']['boards']
    return render_template('chooseboard.html', apiKey=apiKey, boardJSONData=boardJSONData, boardNamesAndIds=boardNamesAndIds)
# @app.route("/app")
# def about():
#     return render_template('app.html', boardStringData=boardStringData, boardId=boardId);

@app.route("/app", methods=['GET', 'POST'])
def actualApp():
    global apiKey
    apiKey = request.form.get('apiV2Token')
    apiUrl = 'https://api.monday.com/v2'
    headers = {'Authorization' : apiKey}
    query = 'query{boards(limit:1000){name id}}'
    data = {'query' : query}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request
    boardJSONData = r.json()
    a = json.dumps(boardJSONData)
    d = json.loads(a)
    boardNamesAndIds = d['data']['boards']

    global boardId
    manualBoardID = request.form.get('boardID')
    boardIdFromForm = request.form.get('boardNames')
    # boardId = '624406408'

    if(boardIdFromForm is None):
        boardId = d['data']['boards'][0]['id']
    elif(manualBoardID != ""):
        boardId = manualBoardID
    else:
        boardId = boardIdFromForm

    apiUrl = 'https://api.monday.com/v2'
    headers = {'Authorization' : apiKey}

    query = 'query{boards (ids: '+ boardId +'){activity_logs (limit: 3000){data}}}'
    data = {'query' : query}
    r = requests.post(url=apiUrl, json=data, headers=headers) # make request

    queryForBoardName = 'query{boards (ids: '+ boardId +'){name}}'
    data2 = {'query' : queryForBoardName}
    r2 = requests.post(url=apiUrl, json=data2, headers=headers)
    boardNameJSONData = r2.json()
    l = json.dumps(boardNameJSONData)
    m = json.loads(l)
    boardName = m['data']['boards'][0]['name']


    boardJSONData = r.json()
    boardStringData = json.dumps(boardJSONData)

    return render_template(
        'app.html', 
        boardId=boardId, 
        boardNamesAndIds=boardNamesAndIds, 
        boardStringData=boardStringData, 
        boardName=boardName, 
        apiKey=apiKey, 
        images=images
        )

if __name__ == '__main__':
    app.run(debug=True)
