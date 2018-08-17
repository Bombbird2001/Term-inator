import math

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
	Calculates log10(number of documents/number of documents word appears in) for each unique
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
		IdfDict[word] = math.log10(N / float(count2))
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
line1 = "When a Service requires or includes downloadable software, this software may be updated automatically on your device once a new version or feature is available."
#10 words
line2 = "Some Services may let you adjust your automatic update settings."
lines = [line1, line2]
print(tfidf(lines))
