import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics.ranking import roc_curve, auc
from sklearn.tree.tree import DecisionTreeClassifier
from numpy import interp
from sklearn.ensemble.forest import RandomForestClassifier
from sklearn.neighbors.classification import KNeighborsClassifier
from sklearn.ensemble.weight_boosting import AdaBoostClassifier
from sklearn.ensemble.gradient_boosting import GradientBoostingClassifier
from sklearn.linear_model.logistic import LogisticRegression,\
    LogisticRegressionCV
import matplotlib.pyplot as plt


classifiers =   {
                'rfc': RandomForestClassifier(),
                 'kn': KNeighborsClassifier(), 
                 'abclf': AdaBoostClassifier(),
                 'gbclf': GradientBoostingClassifier(),     
                 'dtc': DecisionTreeClassifier(max_depth=5),
                 'lgr': LogisticRegression(), 
                 'lgr_cv': LogisticRegressionCV()
                 }                    

'''
Setting up the test / train split
''' 
# read in file from pickle
df = pd.read_pickle('piecemeal.pkl')
sk_features = df.columns[1:-1]
# sk_features = df.columns[1:-19] # removes ccs stuff
# sk_features = df.columns[1:4] # tiny set 
X  = df[sk_features]
y = df["readmit_30"]
df_ = df.copy()
df_out = df_.drop(sk_features, axis=1)


'''
Trying to figure out a bootstrapping function
'''

def get_mean_auc(df, clf):
    kf = KFold(n_splits = 10) # bring back to 10
    kf.get_n_splits(X)

    mean_tpr = 0.0
    mean_fpr = np.linspace(0, 1, 100)

    for train, test in kf.split(X):
        clf.fit(X.loc[train], y.loc[train])
        prob = clf.predict_proba(X.loc[test])
        fpr, tpr, thresholds = roc_curve(y[test], prob[:,1])
        mean_tpr += interp(mean_fpr, fpr, tpr)
        mean_tpr[0] = 0.0
        roc_auc = auc(fpr, tpr)

    mean_tpr /= kf.get_n_splits(X,y)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    return mean_auc
    
def bootstrap(X, n=None):
    df = X.copy()
    df = df[0:0]
    if n == None: 
        n = len(X)

    resample_i = np.floor(np.random.rand(n)*len(X)).astype(int)
    df = X.loc[resample_i]
    return df

def run_auc_bootstrapping(data, n=1000, clf=DecisionTreeClassifier(max_depth=5)):
    aucs = [] 
    for _ in range(n):
        boot = bootstrap(data)
        aucs.append(get_mean_auc(boot, clf))
    
    return aucs

def get_percentile(data): # by defaut these
    ninety_seventh = np.percentile(data, 97.5) 
    two_half = np.percentile(data, 2.5)
        

def plot_aucs():
    for name, clf in classifiers:
        plots = [] # remove later
        kf = KFold(n_splits=10) # bring back to 10
        kf.get_n_splits(X)
           
        mean_tpr = 0.0
        mean_fpr = np.linspace(0, 1, 100)
           
        for train, test in kf.split(X):
            clf.fit(X.loc[train], y.loc[train])
            prob = clf.predict_proba(X.loc[test])
            fpr, tpr, thresholds = roc_curve(y[test], prob[:,1])
            mean_tpr += interp(mean_fpr, fpr, tpr)
            mean_tpr[0] = 0.0
            roc_auc = auc(fpr, tpr)
            plots.append([fpr, tpr])
            df_out.loc[test, 'prob_{}'.format(name)] = prob[:,1]
            df_out.loc[test, 'auc_{}'.format(name)] = roc_auc
            df_out.loc[test, 'classifier_{}'.format(name)] = name
       
        mean_tpr /= kf.get_n_splits(X,y)
        mean_tpr[-1] = 1.0
        mean_auc = auc(mean_fpr, mean_tpr)
        print(name, mean_auc)
        for plot in plots: 
            plt.plot(plot[0], plot[1], color='b')
        plt.plot(mean_fpr, mean_tpr, color ='r')
        plt.xlabel('{0}  -- mean auc = {1}'.format(name, mean_auc))
        plt.show()
        
def run_all_classifiers(data):
    for name, clf in classifiers.iteritems(): 
        mean_auc = get_mean_auc(data, clf)
        print(name, mean_auc)


run_all_classifiers(df)







if __name__ == '__main__':
    pass