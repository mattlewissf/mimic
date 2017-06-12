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

# Define all the candidates
candidates = {
                'RandomForestClassifier': RandomForestClassifier(),
                'AdaBoostClassifier': AdaBoostClassifier(),
                'GradientBoostingClassifier': GradientBoostingClassifier(),     
                'DecisionTreeClassifier': DecisionTreeClassifier(max_depth=5),
                'LogisticRegression': LogisticRegression(), 
                'LogisticRegressionCV': LogisticRegressionCV(), 
                'earth': Earth(verbose=True) >> LogisticRegression(),
                'earth_gdc': Earth(verbose=True) >> GradientBoostingClassifier(),
                'gbc_standard': GradientBoostingClassifier(),
                'gbc_depth_5': GradientBoostingClassifier(max_depth=5), 
                'gbc_depth_2': GradientBoostingClassifier(max_depth=2), 
                'gbc_depth_4': GradientBoostingClassifier(max_depth=1), 
                'gbc_max_features_auto': GradientBoostingClassifier(max_features="auto"),
                'gbc_n_est_200': GradientBoostingClassifier(n_estimators=200), 
                'gbc_n_est_40': GradientBoostingClassifier(n_estimators=40),
                'gbc_n_est_40_l_rate_05': GradientBoostingClassifier(n_estimators=40, learning_rate=.05)
              }

# Set up the fitting process to choose the best model based on 
# cross validated AUC
n_folds = 3
model = InputFixingTransformer() >> ModelSelector(
                      candidates = valmap(
                                          compose(partial(CrossValidatingEstimator, metric=roc_auc_score, cv=n_folds), 
                                                  ProbaPredictingEstimator), 
                                          candidates
                                          ),
                      verbose=True,
                      )

# Calculate 95% confidence interval for AUC using bootstrap
auc_2_5 = bootstrap(percentile(2.5), roc_auc_score, 1000)
auc_97_5 = bootstrap(percentile(97.5), roc_auc_score, 1000)


if __name__ == '__main__':
    # Load data into memory
    df =  pd.read_pickle('features.pkl')
    columns = df.columns[1:-1]
    X = df.iloc[:, 1:-1]
    y = df.loc[:,["readmit_30"]]
    
    # Fit models and generate predictions from best one
    cv_prediction = model.fit_predict(X,y)
    reg_prediction = model.predict(X)
    
    # Print out the python code for the selected model if possible.
    # Otherwise, just print out the error you get from trying.
    try:
        test_sym = model_to_code(model, 'numpy', 'predict', 'test_model')
        print(test_sym)
    except:
        traceback.print_exc()
        print('Sympy export not implemented yet for this model: %s' % str(model))

    # Print out the 95% confidence interval for the selected model
    print('AUC 95%% CI: %f - %f' % (auc_2_5(y, cv_prediction), auc_97_5(y, cv_prediction)))
    
    # Create a calibration plot (also uses bootstrap inside)
    calibration_bin_plot(cv_prediction, y, cv_prediction)
    plt.show()

    # Create some ROC plots
    plot_roc(y, cv_prediction, name='cross_validated')
    pyplot.show()
    plot_roc(y, reg_prediction, name='regular')
    pyplot.show()


