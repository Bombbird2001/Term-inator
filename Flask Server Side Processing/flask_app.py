from flask import Flask, redirect, render_template, request, url_for, abort
from flask_sslify import SSLify
import re
import json
import math
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

###################TF-IDF###################
def getWords(line):
	"""
	Extract each word from the line
	"""
	chars = list(line)
	chars.append(" ")
	tmpWord = []
	tmpList = []
	for char in chars:
		if char.isalnum():
			tmpWord.append(char)
		elif len(tmpWord) > 0:
			tmpList.append(''.join(tmpWord))
			tmpWord = []
	return tmpList

def UniqueWords(wordDict):
	"""
	Finds all the unique words in the list of words
	"""
	unique_words = []
	for line in wordDict:
		for word in line:
			if word not in unique_words:
				unique_words.append(word)
	return unique_words

def TfCalculate (wordDict, wordList):
	"""
	Calculates number of times a word appears in a document over total number of words in it
	for each unique word
	"""
	totalLength = len(wordList)
	tfDict = {}
	for word in wordDict:
		count = 0
		for x in wordList:
			if word == x:
				count = count + 1
		tfDict[word] = count / float(totalLength)
	return tfDict

def IdfCalculate(listOfLines, wordsInDoc):
	"""
	Calculates log2(number of documents/number of documents word appears in) for each unique
	word
	"""
	IdfDict = {}
	N = len(listOfLines) #Number  of documents
	for word in wordsInDoc: #For every unique word
		count2 = 0
		for line in listOfLines: #Check every line,
			for x in line: #Check each word in the line
				if word == x:
					count2 += 1
					break
		IdfDict[word] = math.log2(N / float(count2))
	return IdfDict


def computeTFIDF(Tf, Idf, wordDict):
	"""
	Calculates tf * idf for each unique word
	"""
	TFIDF = {}
	for lemeow in wordDict:
		TFIDF[lemeow] = Tf[lemeow] * Idf[lemeow]
	return TFIDF

def findImpWords(tfidf):
	for index, line in enumerate(tfidf):
		print("Important words in line", index, "are:")
		for word in line:
			if line[word] > 0:
				print(word, line[word])

def tfidf(lines):
	for index, line in enumerate(lines):
		lines[index] = line.lower()
	wordList = [] #List of lines, each containing list of words in the line
	for line in lines:
		wordList.append(getWords(line))
	uniqueWords = UniqueWords(wordList)
	tfLines = [] #List of dictionaries of tf values of each word in each line
	for index, line in enumerate(lines): #For each line, calculate tf values to be stored in dictionaries
		tfLines.append(TfCalculate(uniqueWords, wordList[index]))
	idfList = IdfCalculate(wordList, uniqueWords) #Calculate idf values for each unique word
	tfidfList = [] #List of dictionaries of tf-idf values of each unique word in a line
	for tfLine in tfLines: #Calculate tf-idf values for each line
		tfidfList.append(computeTFIDF(tfLine, idfList, uniqueWords))
	return findImpWords(tfidfList)
############################################

#############Summarise function#############
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
    text = ' '.join(filtered)
    textLength = len(text)
    rat = 6500 / textLength
    finalText = summarize(text, ratio=rat)
    print(finalText)
    print("Initial length:", textLength)
    print("Final length:", len(finalText))
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

#Already initiaized but leaving it here anyways
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