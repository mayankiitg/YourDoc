from sklearn.naive_bayes import MultinomialNB
from sklearn.cross_validation import train_test_split
import numpy as np

mnb_classifier = MultinomialNB()
symp = []
dise = []
cooccurMat = []