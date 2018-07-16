from pip._internal import main as pipmain

def install(package):
    pipmain(['install', package])

if __name__ == '__main__':
	install('bs4')
	install('gensim')
	
import re
import requests
from bs4 import BeautifulSoup
from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords

link = input("Enter link of website:")
html = requests.get(link).text
soup = BeautifulSoup(html, "lxml")
data = soup.findAll(text=True)

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True
 
filtered = list(filter(visible, data))
text = ' '.join(filtered)
textLength = len(text)
rat = 6500 / textLength
finalText = summarize(text, ratio=rat)
print(finalText)
print("Initial length:", textLength)
print("Final length:", len(finalText))