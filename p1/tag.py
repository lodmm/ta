from collections import Counter

import textract 

def getRepeatedWord(filePath):
	words = Counter(textract.process(filePath).split())
	return max(words, key=words.get)

