import math
import re

def getWords(line):
	"""
	Extract each word from the line
	"""
	return re.findall(r"[\w']+", line)
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
	"""

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
	impWords = []
	for index, line in enumerate(tfidf):
		impWords.append({})
		print("Important words in line", index, "are:")
		for word in line:
			if line[word] > 0:
				impWords[index][word] = line[word]
				print(word, line[word])
	return impWords
	
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

#25 words
line1 = """You may need a Google Account in order to use some of our Services. You may create your own Google Account, or your Google Account may be assigned to you by an administrator, such as your employer or educational institution. If you are using a Google Account assigned to you by an administrator, different or additional terms may apply, and your administrator may be able to access or disable your account.

To protect your Google Account, keep your password confidential. You are responsible for the activity that happens on or through your Google Account. Try not to reuse your Google Account password on third-party applications. If you learn of any unauthorised use of your password or Google Account, follow these instructions."""
#10 words
line2 = """You must follow any policies made available to you within the Services.

Do not misuse our Services, for example, do not interfere with our Services or try to access them using a method other than the interface and the instructions that we provide. You may use our Services only as permitted by law, including applicable export and control laws and regulations. We may suspend or stop providing our Services to you if you do not comply with our terms or policies or if we are investigating suspected misconduct.

Using our Services does not give you ownership of any intellectual property rights in our Services or the content that you access. You may not use content from our Services unless you obtain permission from its owner or are otherwise permitted by law. These terms do not grant you the right to use any branding or logos used in our Services. Do not remove, obscure or alter any legal notices displayed in or along with our Services.

Our Services display some content that is not Google’s. This content is the sole responsibility of the entity that makes it available. We may review content to determine whether it is illegal or violates our policies, and we may remove or refuse to display content that we reasonably believe violates our policies or the law. But that does not necessarily mean that we review content, so please do not assume that we do.

In connection with your use of the Services, we may send you service announcements, administrative messages and other information. You may opt out of some of those communications.

Some of our Services are available on mobile devices. Do not use such Services in a way that distracts you and prevents you from obeying traffic or safety laws."""

line3 = "Google gives you a personal, worldwide, royalty-free, non-assignable and non-exclusive licence to use the software provided to you by Google as part of the Services."
line4 = "This licence is for the sole purpose of enabling you to use and enjoy the benefit of the Services as provided by Google in the manner permitted by these terms. "
lines = [line1, line2]
returnList = tfidf(lines)
for dictt in returnList:
	print(sorted(dictt.items(), key = lambda x: x[1], reverse = True))