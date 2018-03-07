# MIMIC-III 30-day Readmission Model

This 30-day readmission model helps to identify  patients with a high risk of readmission based on data drawn from the MIMIC-III open dataset<sup>1</sup>. 

**Project overview:** 
- Data was extracted from the MIMIC-III dataset, and pre-processed to match the OMOP Common Data Model <sup>2</sup> for observational data. 
- Individual patient index records were selected and used to create records of readmission for each patient. 
-  Relevant data features were selected or constructed from demographic, admission, and diagnostic records. Features were built around previous admission types, prior readmission rates, demographic data (such as marital status, ethnicity, age, and gender), and type of insurance at admission. 
-  Features built around the concept of patient comorbidity, as defined by the Charlson Comorbidity Index were included. 
-  Diagnostic data features were included through grouping ICD9CM codes based on an implementation of AHRQ's CCS ICD9 code clustering mapping<sup>3</sup>.


For creating the predictive models, we used a k-fold cross validation scheme. I then applied open-source implementations of ensemble classifiers (from the Python library sk-learn), particularly an implementation of a Gradient Tree Boosting<sup>4</sup> classifier. The AUC (area under the curve) was calculated for each k-fold from the data, and the mean AUC was calculated to build a general ROC curve for the classifier.




**References**

1. Johnson AEW, Pollard TJ, Shen L, Lehman L, Feng M, Ghassemi M, Moody B, Szolovits P, Celi LA, and Mark RG. MIMIC-III, a freely accessible critical care database. Scientific Data (2016). 10.1038/sdata.2016.35.
2. Observational Medical Outcomes Partnership. OMOP Common Data Model. Observational Medical Outcomes Partnership; 2013. Available from: http://omop.org/CDM.
Charlson M, Szatrowski T, Peterson J, et al. Validation of a combined comorbidity index. J Clin Epidemiol. 1994;47:1245e51.
3. Healthcare Cost and Utilization Project (HCUP). Clinical Classifications Software. Available from: https://www.hcup-us.ahrq.gov/toolssoftware/ccs/ccs.jsp.
4. Scikit-learn: Machine Learning in Python, Pedregosa et al., JMLR 12, pp. 2825-2830, 2011.
Tong L, Erdmann C, Daldalian M, et al. Comparison of predictive modeling approaches for 30-day all-cause non-elective readmission risk. BMC Med Res Methodol 2016;16:1–8.
