import pandas as pd
from sklearn.metrics.ranking import roc_auc_score
from sklearn.linear_model.logistic import LogisticRegression,\
    LogisticRegressionCV
import matplotlib.pyplot as plt
from sklearntools.earth import Earth
from sklearntools.pandables import InputFixingTransformer
from sklearntools.kfold import CrossValidatingEstimator
from sklearntools.calibration import ProbaPredictingEstimator
from sklearntools.validation import plot_roc, bootstrap, percentile,\
    calibration_bin_plot
from matplotlib import pyplot
from sklearntools.sym.printers import model_to_code
from sklearn.ensemble.gradient_boosting import GradientBoostingClassifier
from sklearn.ensemble.forest import RandomForestClassifier
from sklearn.ensemble.weight_boosting import AdaBoostClassifier
from sklearn.tree.tree import DecisionTreeClassifier
from toolz.dicttoolz import valmap
from sklearntools.model_selection import ModelSelector
from toolz.functoolz import compose
from toolz.curried import partial
import traceback

# above are taken directly from sklearn_model example file



if __name__ == '__main__':
    pass