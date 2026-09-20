from sklearn.ensemble import IsolationForest
import numpy as np
def fit(rows):
 m=IsolationForest(n_estimators=200,random_state=42);m.fit(np.asarray(rows,float));return m
def score(m,rows):return m.decision_function(np.asarray(rows,float)).tolist()
