from flask import Flask, redirect, render_template, request, url_for
from flask_cors import CORS, cross_origin
from flask_sslify import SSLify
import re
import json
from bs4 import BeautifulSoup
from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords
from googlesearch import search
import urllib
from googleapiclient.discovery import build
from flask_sqlalchemy import SQLAlchemy

##############Cleaning up html##############
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True

def secondFilter(element):
	while True:
		index = element.find("\n")
		if index > 0:
			element = element[:index] + element[index + 1:]
		elif index == 0:
			element = element[index + 1:]
		else:
			break
	element = element.strip()

	while True:
		space = element.find("  ")
		if space > 0:
			element = element[:space] + " " + element[space + 2:]
		else:
			break
	return element
############################################

#############Summarise function#############

def UniqueWords(wordDict):
    unique_words = []
    for b in wordDict:
        if b not in unique_words:
            unique_words.append(b)

    return unique_words

def TfCalculate (wordDict,document):
    split = document.split()
    bow = len(split)


    tfDict = {}

    for word in wordDict:
        count = 0
        for x in split:
            if word == x:
                count = count + 1
        tfDict[word] = count/float(bow)

    return tfDict

def IdfCalculate(allWords,docList,wordDict):
    IdfDict = {}
    N = len(docList)

    for word in wordDict:
        count2 = 0
        for a in allWords:
            if word == a:
                count2 = count2 + 1
        IdfDict[word] = math.log10(N / float(count2))

    return IdfDict


def computeTFIDF(Tf, Idf, line):
    TFIDF = {}
    for lemeow in wordDict:
        TFIDF[lemeow] = Tf[lemeow] * Idf[lemeow]
    return (TFIDF)

def filterTC(html):
    soup = BeautifulSoup(html, "lxml")
    data = soup.findAll(text=True)
    filtered = list(filter(visible, data))
    #print("filtered:", filtered)
    for index, element in enumerate(filtered):
        if len(element) <= 25:
            filtered[index] = ""
        else:
        	element = secondFilter(element)
        	filtered[index] = element

    while True:
    	try:
    		filtered.remove("")
    	except ValueError as e:
    		break

    docList = filtered[:]
    allWords = docList.split()
    wordDict = UniqueWords(allWords)

    N = len(docList)
    for document in range(N):
        docList[document]

"""
    text = ' '.join(filtered)
    textLength = len(text)
    rat = 6500 / textLength
    finalText = summarize(text, ratio=rat)
    print(finalText)
    print("Initial length:", textLength)
    print("Final length:", len(finalText))
    """
    return json.dumps(finalText.split('.'))

"""
def filterText(text):
    textLength = len(text)
    rat = 6500 / textLength
    finalText = summarize(text, ratio=rat)
    return json.dumps(finalText.split('.'))
"""
############################################

#########Google Search for links############
my_api_keys = []
my_cse_id = ""

def apisearch(domain):
    res = {}
    api_no = 0
    link = ""
    while True:
        api_key = my_api_keys[api_no]
        try:
            service = build("customsearch", "v1", developerKey=api_key)
            res = service.cse().list(q=domain + " terms of service", cx=my_cse_id, num=10).execute()
            break
        except:
            if api_no == len(my_api_keys) - 1:
                res = [{'formattedUrl': "Failed to retrieve link"}]
                return link
            api_no += 1

    links = res['items']
    for result in links:
        if "term" in result or "service" in result or "condition" in result or "policy" in result or "policies" in result:
            link = result
            print("link changed to:", link)
            break
    return link

def googleSearch(domain):
    if "google" in domain:
        return "https://policies.google.com/terms"
    try:
        query = str(domain) + " terms of service"
        iterator = search(query, tld="com", num=5, stop=1, pause=2)
        resultList = list(iterator)
        #print(resultList)
        link = ""
        for result in resultList:
            if "term" in result or "service" in result or "condition" in result or "policy" in result or "policies" in result:
                link = result
                print("link changed to:", link)
                break
        return link
    except urllib.error.HTTPError as httperr:
        print(httperr.headers)  # Dump the headers to see if there's more information
        print(httperr.read())   # You can even read this error object just like a normal response file
        link = apisearch(domain)
        return link
    return ""
#########################################
#results = apisearch("facebook")

#googleSearch("stackoverflow")

#filterTC("https://stackoverflow.com/legal/terms-of-service/public")

##########Init app, database############
app = Flask(__name__)
sslify = SSLify(app)
#cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'
app.config["DEBUG"] = True
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="",
    password="",
    hostname="",
    databasename="",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Weburl(db.Model):
    __tablename__ = "termsofservice"
    domain = db.Column(db.String(64), primary_key = True)
    tosurl = db.Column(db.String(4096))
    tc = db.Column(db.Text)
########################################

def insertData(domain, url, filteredHtml):
    for row in db.session.query(Weburl.domain).all():
        if row.domain == domain:
            print("Found", domain)
            return
    db.session.add(Weburl(domain = domain, tosurl = url, tc = filteredHtml))
    db.session.commit()
    print(domain, "added")
    return

@app.route('/')
def index():
    #return render_template("main_page.html")
    return "Nothing to see here!"

@app.route('/getlink', methods=["POST"])
#@cross_origin()
def getlink():
    jsondata = request.get_json()
    domain = jsondata["domain"]
    results = googleSearch(domain)
    if results == "":
        return "Failed to retrieve link"
    return results

@app.route('/gettc', methods=["POST"])
def gettc():
    jsondata = request.get_json()
    url = jsondata["url"]
    domain = jsondata["domain"]
    html = jsondata["html"]
    filtered = filterTC(html)
    insertData(domain, url, filtered)
    return filtered

@app.route('/gettcplaintext', methods = ["POST"])
def gettcplaintext():
    jsondata = request.get_json()
    text = jsondata["text"]
    return filterTC(text)
