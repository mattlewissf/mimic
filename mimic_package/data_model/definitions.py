import re
import collections
import itertools
from ccs import icd9
from ccs.icd9 import ICD9

'''
Based these buckets off of this paper: http://www.aaai.org/ocs/index.php/WS/AAAIW16/paper/view/12669
'''
ethnicity_dict = {
                'HISPANIC/LATINO - CUBAN': 'latino', 
                'HISPANIC/LATINO - MEXICAN': 'latino',
                'UNKNOWN/NOT SPECIFIED': 'race_other',
                'BLACK/HAITIAN': 'black',
                'BLACK/AFRICAN AMERICAN': 'black',
                'HISPANIC/LATINO - DOMINICAN': 'latino',
                'CARIBBEAN ISLAND':    'black',
                'HISPANIC/LATINO - GUATEMALAN': 'latino',
                'HISPANIC/LATINO - CENTRAL AMERICAN (OTHER)': 'latino',
                'HISPANIC OR LATINO': 'latino',
                'MIDDLE EASTERN': 'middle_eastern',
                'ASIAN - JAPANESE':    'asian',
                'ASIAN': 'asian',
                'PATIENT DECLINED TO ANSWER': 'race_other',
                'AMERICAN INDIAN/ALASKA NATIVE FEDERALLY RECOGNIZED TRIBE': 'american_indian',
                'ASIAN - VIETNAMESE': 'asian',
                'ASIAN - KOREAN': 'asian',
                'BLACK/CAPE VERDEAN': 'black',
                'OTHER': 'race_other',
                'ASIAN - FILIPINO': 'asian',
                'WHITE - EASTERN EUROPEAN':    'white',
                'ASIAN - ASIAN INDIAN': 'asian',
                'WHITE - RUSSIAN': 'white',
                'ASIAN - OTHER': 'asian',
                'WHITE - OTHER EUROPEAN': 'white',
                'HISPANIC/LATINO - COLOMBIAN': 'latino',
                'ASIAN - CHINESE': 'asian',
                'BLACK/AFRICAN': 'black',
                'WHITE': 'white',
                'HISPANIC/LATINO - HONDURAN': 'latino',
                'SOUTH AMERICAN': 'latino',
                'UNABLE TO OBTAIN': 'race_other',
                'ASIAN - CAMBODIAN': 'asian',
                'ASIAN - THAI': 'asian',
                'HISPANIC/LATINO - PUERTO RICAN': 'latino',
                'AMERICAN INDIAN/ALASKA NATIVE': 'american_indian',
                'HISPANIC/LATINO - SALVADORAN': 'latino',
                'PORTUGUESE': 'white',
                'MULTI RACE ETHNICITY':    'multi_racial',
                'WHITE - BRAZILIAN': 'white',
                'NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER': 'pacific_islander'
                }




ethnicity_values_tup = (('race_other', 0), 
                    ('white', 0), 
                    ('black', 0), 
                    ('latino', 0), 
                    ('asian', 0), 
                    ('multi_racial', 0), 
                    ('middle_eastern', 0),
                    ('pacific_islander', 0), 
                    ('american_indian', 0))

ethnicity_values = collections.OrderedDict(ethnicity_values_tup)


'''
- unknown
- single 
- married / cohab
- separated / divorced / widowed
'''


marital_status_dict = {
                        'SEPARATED': 'separated', 
                        'MARRIED': 'cohab', 
                        'DIVORCED': 'separated', 
                        'UNKNOWN (DEFAULT)': 'unknown', 
                        'SINGLE': 'single', 
                        'WIDOWED': 'separated', 
                        'LIFE PARTNER': 'cohab'
                        }

marital_values_tup =    (
                    ('unknown', 0), 
                    ('single', 0),
                    ('cohab', 0), 
                    ('separated', 0))


marital_values = collections.OrderedDict(marital_values_tup)
    


'''
Charleston comorbidity dicts
Based off of http://czresearch.com/dropbox/Quan_MedCare_2005v43p1130.pdf
# note that as of MIMIC III 1.0 there are only ICD9 codes... 
'''


# elixhauser_icd9_coding = {
#                             'congestive heart failure': ['398.91', '402.01', '402.11', '402.91', '404.01', 
#                                                          '404.03', '404.11', '404.13', '404.91', '404.93', 
#                                                          '425.4-425.9', '428.x'],
#                             'cardiac arrhythmias': ['426.0', '426.13', '426.7', '426.9', '426.10', 
#                                                     '426.12', '427.0-427.4', '427.6-427.9', '785.0', '996.01', 
#                                                     '996.04', 'V45.0', 'V53.3'],
#                             'valvular disease': ['093.2', '394.x-397.x', '424.x', '746.3-746.6', 'V42.2', 'V43.3'],
#                             'pulmonary circulation disorders': ['415.0', '415.1', '416.x', '417.0', '417.8', '417.9'],
#                             'peripheral vascular disorders': ['093.0', '437.3', '440.x', '441.x', '443.1-443.9', 
#                                                               '447.1', '557.1', '557.9', 'V43.4'],
#                             'hypertension, uncomplicated ': ['401.x'],
#                             'hypertension, complicated': ['402.x-405.x'],
#                             'paralysis': ['334.1', '342.x', '343.x', '344.0-344.6', '344.9'], 
#                             'other neurological disorders': ['331.9', '332.0', '332.1', '333.4', '333.5', '333.92', 
#                                                              '334.x-335.x', '336.2', '340.x', '341.x', '345.x', 
#                                                              '348.1', '348.3', '780.3', '784.3'],
#                             'chronic pulmonary disease': ['416.8', '416.9', '490.x-505.x', '506.4', '508.1', '508.8'],
#                             'diabetes, uncomplicated': ['250.0-250.3'],
#                             'diabetes, complicated': ['250.4-250.9'],
#                             'hypothyroidism': ['240.9', '243.x', '244.x', '246.1', '246.8'],
#                             'renal failure': ['403.01', '403.11', '403.91', '404.02',
#                                               '404.03', '404.12', '404.13', '404.92', '404.93', 
#                                               '585.x', '586.x', '588.0', 'V42.0', 'V45.1', 'V56.x'],
#                             'liver disease': ['070.22', '070.23', '070.32', '070.33', '070.44', '070.54', '070.6', 
#                                               '070.9', '456.0-456.2', '570.x', '571.x', '572.2-572.8', 
#                                               '573.3', '573.4', '573.8', '573.9',' V42.7'] ,
#                             'peptic ulcer disease excluding bleeding': ['531.7', '531.9', '532.7', '532.9', '533.7', 
#                                                                         '533.9', '534.7', '534.9'],
#                             'aids/hiv': ['042.x-044.x'], 
#                             'lymphoma': ['200.x-202.x', '203.0', '238.6'],
#                             'metastatic cancer': ['196.x-199.x'],
#                             'solid tumor without metastasis': ['140.x-172.x',' 174.x-195.x'],
#                             'rheumatoid arthritis/collagen vascular diseases': ['446.x', '701.0', '710.0-710.4',' 710.8', '710.9',
#                                                                                 '711.2', '714.x', '719.3', '720.x', '725.x', '728.5',
#                                                                                 '728.89', '729.30'],
#                             'coagulopathy': ['286.x', '287.1', '287.3-287.5'], 
#                             'obesity': ['278.0'],
#                             'weight loss': ['260.x-263.x', '783.2', '799.4'], 
#                             'fluid and electrolyte disorders': ['253.6', '276.x'], 
#                             'blood loss anemia': ['280.0'],
#                             'deficiency anemia': ['280.1-280.9', '281.x'], 
#                             'alcohol abuse': ['265.2', '291.1-291.3', '291.5-291.9', '303.0', '303.9', '305.0', 
#                                               '357.5', '425.5', '535.3', '571.0-571.3', '980.x', 'V11.3'],
#                             'drug abuse': ['292.x', '304.x', '305.2-305.9', 'V65.42'],
#                             'psychoses': ['293.8', '295.x', '296.04', '296.14', '296.44', '296.54', '297.x', '298.x'],
#                             'depression': ['296.2', '296.3', '296.5', '300.4', '309.x', '311']
#     } 
# 
# elixhauser_values = {
#                             'congestive heart failure': 0, 
#                             'cardiac arrhythmias': 0, 
#                             'valvular disease': 0, 
#                             'pulmonary circulation disorders': 0, 
#                             'peripheral vascular disorders': 0, 
#                             'hypertension, uncomplicated ': 0, 
#                             'hypertension, complicated': 0, 
#                             'paralysis': 0, 
#                             'other neurological disorders': 0, 
#                             'chronic pulmonary disease': 0, 
#                             'diabetes, uncomplicated': 0, 
#                             'diabetes, complicated': 0, 
#                             'hypothyroidism': 0, 
#                             'renal failure': 0, 
#                             'liver disease': 0,
#                             'peptic ulcer disease excluding bleeding': 0, 
#                             'aids/hiv': 0, 
#                             'lymphoma': 0, 
#                             'metastatic cancer': 0, 
#                             'solid tumor without metastasis': 0, 
#                             'rheumatoid arthritis/collagen vascular diseases': 0, 
#                             'coagulopathy': 0, 
#                             'obesity': 0, 
#                            ' weight loss': 0, 
#                             'fluid and electrolyte disorders': 0, 
#                             'blood loss anemia': 0, 
#                             'deficiency anemia': 0, 
#                             'alcohol abuse': 0, 
#                             'drug abuse': 0, 
#                             'psychoses': 0, 
#                             'depression': 0
#     } 

# from http://czresearch.com/dropbox/Quan_MedCare_2005v43p1130.pdf | 'enhanced ICD-9 CM' 
updated_charlson_icd9_coding = {
                            'Myocardial infarction': ['410.x', '412.x'],
                            'Congestive heart failure': ['398.91', '402.01', '402.11', '402.91',
                                                        '404.01', '404.03', '404.11', '404.13', '404.91', '404.93'],
                            'Peripheral vascular disease': ['093.0', '437.3', '440.x', '441.x',
                                                            '443.1-443.9', '47.1', '557.1',
                                                            '557.9', 'V43.4'],
                            'Cerebrovascular disease': ['362.34', '430.x-438.x'],
                            'Dementia': ['290.x', '294.1', '331.2'],
                            'Chronic pulmonary disease': ['416.8', '416.9', '490.x-505.x',
                                                          '506.4', '508.1', '508.8'],
                            'Rheumatologic disease': ['446.5', '710.0-710.4', '714.0-714.2', '714.8', '725.x'],
                            'Peptic ulcer disease': ['531.x-534.x'],
                            'Mild liver disease': ['070.22', '070.23', '070.32', '070.33',
                                                   '070.44', '070.54', '070.6', '070.9',
                                                   '570.x', '571.x', '573.3', '573.4',
                                                   '573.8', '573.9', 'V42.7'],
                            'Diabetes without chronic complications': ['250.0-250.3', '250.8', '250.9'],
                            'Diabetes with chronic complications': ['250.4-250.7'],
                            'Hemiplegia or paraplegia': ['334.1', '342.x', '343.x', '344.0-344.6', '344.9'],
                            'Renal disease': ['403.01', '403.11', '403.91', '404.02',
                                              '404.03', '404.12', '404.13',
                                              '404.92', '404.93', '582.x',
                                              '583.0-583.7', '585.x', '586.x',
                                              '588.0', 'V42.0', 'V45.1', 'V56.x'],
                            'Any malignancy, including leukemia and lymphoma': ['140.x-172.x', '174.x-195.8',
                                                                                '200.x-208.x', '238.6'],
                            'Moderate or severe liver disease': ['456.0-456.2', '572.2-572.8'],
                            'Metastatic solid tumor': ['196.x-199.x'],
                            'AIDS/HIV': ['042.x-044.x']
                            } 

# from https://academic.oup.com/aje/article/173/6/676/182985/Updating-and-Validating-the-Charlson-Comorbidity

updated_charlson_weights = {
                            'Myocardial infarction': 0,
                            'Congestive heart failure': 2,
                            'Peripheral vascular disease': 0,
                            'Cerebrovascular disease': 0,
                            'Dementia': 2,
                            'Chronic pulmonary disease': 1,
                            'Rheumatologic disease': 1,
                            'Peptic ulcer disease': 0,
                            'Mild liver disease': 2,
                            'Diabetes without chronic complications': 0,
                            'Diabetes with chronic complications': 1,
                            'Hemiplegia or paraplegia': 2,
                            'Renal disease': 1,
                            'Any malignancy, including leukemia and lymphoma': 2,
                            'Moderate or severe liver disease': 4,
                            'Metastatic solid tumor': 6,
                            'AIDS/HIV': 4 
                            }

charlson_features = {k: 0 for k in updated_charlson_icd9_coding.keys()}

index_admission_mapper = {"EMERGENCY": 0, "URGENT":0, "ELECTIVE":0}
index_admission_types = collections.OrderedDict(index_admission_mapper)


'''
ICD9 parsing functions
- will move somewhere else
'''

def fill_until(code):
    codes = [] 
    int_code = int(code.split('.')[0])
    code_stop = code.split('.')[1]
    if code_stop == 'x':
        code_stop = 100
    elif len(code_stop) == 2: 
        code_stop = int(code_stop) + 1
    elif len(code_stop) == 1:
        code_stop = (int(code_stop) * 10) + 1 
    for x in range(code_stop):
        x = str(int_code) + '.' + str(x).zfill(2)
        codes.append(x)
    return codes
        

def expand_wildcard_code(code):
    codes = set()
    int_code = int(code.split('.')[0])
    code_start = code.split('.')[1]
    if code_start == 'x':
        code_start = 0
    elif len(code_start) == 2: 
        code_start = int(code_start)
    elif len(code_start) == 1:
        code_start = int(code_start) * 10
    
    for x in xrange(code_start, 100):
        s_code = str(int_code) + '.' + str(x).zfill(2)
        codes.add(s_code)
    return codes

def expand_code_range(code):
    start, stop = code.split('-')
    range_start = int(start.split('.')[0])
    range_end = int(stop.split('.')[0])
    codes = set() 
    for x in xrange(range_start, range_end):
        x_code = str(x) + '.x'
        codes.update(expand_wildcard_code(x_code))
    codes.update(fill_until(stop))
    return codes
    
def parse_icd_code(code):
    prefix = ''
    if code[0].isalpha():
        prefix = code[0]
        code = code.replace(prefix, '')
    if '-' in code:
        codes = expand_code_range(code)
    elif '.x' in code: 
        codes = expand_wildcard_code(code)
    else:
        codes = set()
        codes.add(code)
    for s_code in codes.copy():
        codes.remove(s_code)
        codes.add(prefix+s_code)
    return codes

def return_charlson_score(user_charlson_features):
    categories = {k:v for (k,v) in user_charlson_features.iteritems() if v > 0}
    score = 0
    for key, value in categories.iteritems():
        update_score = updated_charlson_weights[key]
        score += update_score
    return score
        

def check_against_charlson(user_codes, codes_dict=updated_charlson_icd9_coding): # won't be none
    
    charlson_features = {k: 0 for k in updated_charlson_icd9_coding.keys()}
    expanded_codes = {} 
    for key, value in codes_dict.iteritems(): 
        code_set = set()
        for code in value: 
            s = parse_icd_code(code)
            code_set.update(s)
        expanded_codes[key] = code_set
    
    for code in user_codes: 
        for key, value in expanded_codes.iteritems(): 
            if code in value: 
                charlson_features[key] = 1
                
    charlson_score = return_charlson_score(charlson_features)
    return [collections.OrderedDict(charlson_features), charlson_score]



def check_against_ccs(user_codes, codeset, code_type='dx', code_level='single'):
    
    mapper = {'dx': {'single': codeset.dx_single_level_codes, 'category': codeset.dx_category_level_codes, 'multi': codeset.dx_multilevel_codes}, 
              'px': {'single': codeset.px_single_level_codes, 'category': codeset.px_category_level_codes, 'multi': codeset.px_multilevel_codes}}
    
    f = mapper[code_type][code_level]
    

    ccs_features = {} 
    user_set = set(user_codes)
    for k,v in f.iteritems():
        overlap = user_set & v
        if overlap: 
            ccs_features[k] = 1
        else:
            ccs_features[k] = 0
    
    return collections.OrderedDict(ccs_features)


if __name__ == '__main__':
    pass
