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
from matplotlib.pyplot import plot
from extractors import combine_piecemeal_dfs

plt_classifiers  =  {
#                 'rfc': RandomForestClassifier(),
# #                  'kn': KNeighborsClassifier(), 
#                  'abclf': AdaBoostClassifier(),
                 'gbclf': GradientBoostingClassifier(),     
#                  'dtc': DecisionTreeClassifier(max_depth=5),
#                  'lgr': LogisticRegression(), 
#                  'lgr_cv': LogisticRegressionCV()
                 }  


classifiers =   {
                'rfc': RandomForestClassifier(),
#                  'kn': KNeighborsClassifier(), 
                 'abclf': AdaBoostClassifier(),
                 'gbclf': GradientBoostingClassifier(),     
                 'dtc': DecisionTreeClassifier(max_depth=5),
                 'lgr': LogisticRegression(), 
                 'lgr_cv': LogisticRegressionCV()
                 }             

GBC_attempts = {
                'standard': GradientBoostingClassifier(),
                'depth_5': GradientBoostingClassifier(max_depth=5), 
                'depth_2': GradientBoostingClassifier(max_depth=2), 
                'depth_4': GradientBoostingClassifier(max_depth=1), 
                'max_features_auto': GradientBoostingClassifier(max_features="auto"),
                'n_est_200': GradientBoostingClassifier(n_estimators=200), 
                'n_est_40': GradientBoostingClassifier(n_estimators=40),
                'n_est_40_l_rate_05': GradientBoostingClassifier(n_estimators=40, learning_rate=.05) }
       

'''
Setting up the test / train split
''' 
# read in file from pickle
df = combine_piecemeal_dfs()
# all_features = df.columns[1:-1]
sk_features = df.columns[1:-1] # everything 
# sk_features = all_features.drop(['Self Pay', 'Medicaid', 'Medicare', 'Private', 'Government']) # without insurance stuff
# sk_features = df.columns[1:-19] # removes ccs stuff
# sk_features = df.columns[1:-37] # removes ccs and charleston
# sk_features = df.columns[1:4] # tiny set 
# sk_features = df.columns[1:20] # just demo
X = df[sk_features]
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

def run_auc_bootstrapping(data, clf):
    aucs = [] 
    n = 100
    for x in range(n):
        boot = bootstrap(data)
        mean_auc = get_mean_auc(boot, clf)
        aucs.append(mean_auc)
        print(x, mean_auc)
    
    return aucs

def get_percentiles(data): # by defaut these
    ninety_seventh = np.percentile(data, 97.5) 
    two_half = np.percentile(data, 2.5)
    fifth = np.percentile(data, 5.0)  
    ninety_fifth = np.percentile(data, 95.0)  
    
    return{'97.5th': ninety_seventh, '2.5th': two_half, '95th': ninety_fifth, 'fifth': fifth}
        

def plot_aucs():
    for name, clf in plt_classifiers.iteritems():
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
        
        fig = plt.figure()
        fig.suptitle('GradientBoostingClassifier | Mean AUC: {0}'.format(mean_auc), fontsize=14)
        for plot in plots: 
            plt.plot(plot[0], plot[1], lw=1, color='b')
        
        plt.plot(mean_fpr, mean_tpr, lw=3, color ='r')
        plt.xlabel('FPR', fontsize=14)
        plt.ylabel('TPR', fontsize=14)
        plt.show()
        
def run_all_classifiers(data, classifiers=classifiers):
    for name, clf in classifiers.iteritems(): 
        mean_auc = get_mean_auc(data, clf)
        print(name, mean_auc)

def run_bootstrap_confidence(data, clf):
    print('running bootstrap + confidence for {}').format(clf)
#     aucs = run_auc_bootstrapping(data=data, clf=clf)
    aucs = run_auc_bootstrapping(data=data, clf=clf)
    percentiles = get_percentiles(aucs)
    print(percentiles)
    return percentiles
    

run_all_classifiers(X, classifiers=GBC_attempts)
# result = run_bootstrap_confidence(X,classifiers['gbclf'])

# plot_aucs()
    






if __name__ == '__main__':
    pass
