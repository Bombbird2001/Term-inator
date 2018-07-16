from flask import Flask, redirect, render_template, request, url_for
from flask_cors import CORS, cross_origin
from flask_sslify import SSLify
import re
import requests
import json
from bs4 import BeautifulSoup
from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords
from googlesearch import search
import MySQLdb
import urllib
from googleapiclient.discovery import build

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

my_api_keys = []
my_cse_id = ""

def apisearch(domain):
    res = {}
    api_no = 0
    while True:
        api_key = my_api_keys[api_no]
        try:
            service = build("customsearch", "v1", developerKey=api_key)
            res = service.cse().list(q=domain + " terms of service", cx=my_cse_id, num=10).execute()
            break
        except:
            if api_no == 1:
                res = [{'formattedUrl': "Failed to retrieve link"}]
            api_no += 1

    links = res['items']
    #print(res['items']['formattedUrl'])
    for result in links:
        if "term" in result or "service" in result or "condition" in result or "policy" in result or "policies" in result:
            link = result
            print("link changed to:", link)
            break

#results = apisearch("facebook")

def googleSearch(domain):
    if "google" in domain:
        return "https://policies.google.com/terms"
    try:
        query = str(domain) + " terms of service"
        iterator = search(query, tld="com", num=5, stop=1, pause=2)
        resultList = list(iterator)
        print(resultList)
        link = ""
        for result in iterator:
            if "term" in result or "service" in result or "condition" in result or "policy" in result or "policies" in result:
                link = result
                print("link changed to:", link)
                break
        return link
    except urllib.error.HTTPError as httperr:
        print(httperr.headers)  # Dump the headers to see if there's more information
        print(httperr.read())   # You can even read this error object just like a normal response file
        return ""
    return ""

#googleSearch("facebook")

#filterTC("https://stackoverflow.com/legal/terms-of-service/public")

app = Flask(__name__)
sslify = SSLify(app)
#cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'
app.config["DEBUG"] = True

@app.route('/')
def index():
    return render_template("main_page.html")

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
    html = jsondata["html"]
    return filterTC(html)
