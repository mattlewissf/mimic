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
from sklearntools.model_selection import ModelSelectorCV 
from sklearntools.pandabless import InputFixingTransformer
from sklearntools.kfold import CrossValidatingEstimator
from sklearntools.calibration import ProbaPredictingEstimator
from sklearntools.validation import plot_roc, bootstrap
from matplotlib import pyplot
from sklearntools.sym import numpy_str





# get the data
df =  pd.read_pickle('features.pkl')
columns = df.columns[1:-1]
X = df.iloc[:, 1:-1]
y = df.loc[:,["readmit_30"]]



earth_classifier = InputFixingTransformer() >> Earth(verbose=True) >> ProbaPredictingEstimator(LogisticRegression())

earth_classifier = CrossValidatingEstimator(earth_classifier)
cv_prediction = earth_classifier.fit_predict(X,y)
reg_predicition = earth_classifier.predict(X)

test_sym = numpy_str('test_model', earth_classifier)
print(test_sym)


# lower_statistic = bootstrap(percentile(2.5), inner_stat, n)

# lower_statistic = bootstrap(percentile(2.5), , n)



plot_roc(y, cv_prediction, name='cross_validated')
pyplot.show()
plot_roc(y, reg_predicition, name='regular')
pyplot.show()

# ModelSelectorCV - something we will use but not yet



# av = np.ravel(cv_prediction) - np.ravel(reg_predicition)
# print(np.max(av))


if __name__ == '__main__':
    pass











