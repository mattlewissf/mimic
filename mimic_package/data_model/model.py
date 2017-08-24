import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics.ranking import roc_curve, auc
from sklearn.tree.tree import DecisionTreeClassifier
from numpy import interp
from sklearn.ensemble.forest import RandomForestClassifier
from sklearn.ensemble.weight_boosting import AdaBoostClassifier
from sklearn.ensemble.gradient_boosting import GradientBoostingClassifier
from sklearn.linear_model.logistic import LogisticRegression,\
    LogisticRegressionCV
import matplotlib.pyplot as plt
from matplotlib.pyplot import plot
from sklearn.pipeline import Pipeline
# from pyearth.earth import Earth # remove
# sklearn 
from sklearntools.earth import Earth
# from sklearntools.model_selection import ModelSelectorCV 


'''
Py-Earth classifiers
'''

# sklearn style! 

earth_classifier = Earth() >> LogisticRegression()

# earth_classifier = Pipeline([('earth', Earth(max_degree=1, penalty=1.5)), 
#                             ('logistic', LogisticRegression())])
# earth_classifier_gdc  = Pipeline([('earth', Earth(max_degree=3, penalty=1.5)), 
#                             ('gbc', GradientBoostingClassifier())])

classifiers =   {
#                 'RandomForestClassifier': RandomForestClassifier(),
#                  'AdaBoostClassifier': AdaBoostClassifier(),
                'GradientBoostingClassifier': GradientBoostingClassifier(),     
#                  'DecisionTreeClassifier': DecisionTreeClassifier(max_depth=5),
#                  'LogisticRegression': LogisticRegression(), 
#                  'LogisticRegressionCV': LogisticRegressionCV(), 
                'earth': earth_classifier,
#                 'earth_gdc': earth_classifier_gdc
                 }             

# hyperparameter tuning for GBC
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
df =  pd.read_pickle('features.pkl')
    
'''
Pulling out the features
- This is set up so easy comparison can be run between different subsets of the total feature set
'''
all_features = df.columns[1:-1] # everything 

# Without insurance status features
no_insurance_features = all_features.drop(['Self Pay', 'Medicaid', 'Medicare', 'Private', 'Government'])

# Without CCS features
no_ccs_features = df.columns[1:-19]

no_ccs_charlson = df.columns[1:-37]

# Just demographic features
only_demo_features = df.columns[1:20]

# set feature set here within df[ ]
X = df[all_features]
y = df["readmit_30"]

# df_ = df.copy()
# df_out = df_.drop(all_features, axis=1)

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

def get_percentiles(data): 
#     ninety_seventh = np.percentile(data, 97.5) 
#     two_half = np.percentile(data, 2.5)
    fifth = np.percentile(data, 5.0)  
    ninety_fifth = np.percentile(data, 95.0)  
    
    return{'95th': ninety_fifth, 'fifth': fifth}
        

def plot_aucs():
    for name, clf in classifiers.iteritems():
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
#             df_out.loc[test, 'prob_{}'.format(name)] = prob[:,1]
#             df_out.loc[test, 'auc_{}'.format(name)] = roc_auc
#             df_out.loc[test, 'classifier_{}'.format(name)] = name
       
        mean_tpr /= kf.get_n_splits(X,y)
        mean_tpr[-1] = 1.0
        mean_auc = auc(mean_fpr, mean_tpr)
        print(name, mean_auc)
        
        fig = plt.figure()
        fig.suptitle('{0} | Mean AUC: {1}'.format(name, mean_auc), fontsize=14)
        for plot in plots: 
            plt.plot(plot[0], plot[1], lw=1, color='b')
        
        plt.plot(mean_fpr, mean_tpr, lw=3, color ='r')
        plt.xlabel('FPR', fontsize=14)
        plt.ylabel('TPR', fontsize=14)
        plt.show()
        
def run_all_classifiers(data, classifiers=classifiers):
    for name, clf in classifiers.iteritems(): 
        print(clf)
        mean_auc = get_mean_auc(data, clf)
        print(name, mean_auc)

def run_bootstrap_confidence(data, clf):
    print('running bootstrap + confidence for {}').format(clf)
    aucs = run_auc_bootstrapping(data=data, clf=clf)
    percentiles = get_percentiles(aucs)
    print(percentiles)
    return percentiles
    

'''
Psuedo-controller
'''
# run all classifiers
run_all_classifiers(X)

# run different tuned versions of GBC
# run_all_classifiers(X, classifiers=GBC_attempts)



if __name__ == '__main__':
    pass
