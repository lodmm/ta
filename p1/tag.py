from collections import Counter

import textract 
# Install from http://textract.readthedocs.io/en/latest/installation.html



def getRepeatedWord(filePath):
	words = Counter(textract.process(filePath).split())
	return max(words, key=words.get)

w=getRepeatedWord('h.pdf')
print (w)
