import re
import collections

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

# ethnicity_values = {'race_other': 0, 
#                     'white': 1, 
#                     'black': 2, 
#                     'latino': 3, 
#                     'asian': 4, 
#                     'multi_racial': 5, 
#                     'middle_eastern': 6,
#                     'pacific_islander': 7, 
#                     'american_indian': 8 }

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
    


# marital_status_dict = {
#                         'SEPARATED': 3, 
#                         'MARRIED': 1, 
#                         'DIVORCED': 3, 
#                         'UNKNOWN (DEFAULT)': 0, 
#                         'SINGLE': 2, 
#                         'WIDOWED': 3, 
#                         'LIFE PARTNER': 1
#                         }
                        

'''
Charleston comorbidity dicts
Based off of http://czresearch.com/dropbox/Quan_MedCare_2005v43p1130.pdf
'''

charleston_icd10_coding = {
                            'myocardial infarction':                    ['I21.x', 'I22.x', 'I25.2'],
                            'congestive heart failure':                 ['I09.9', 'I11.0', 'I13.0', 'I13.2', 'I25.5', 'I42.0', 'I42.5-I42.9', 'I43.x', 'I50.x', 'P29.0'],
                            'cardiac arrhythmias':                      ['I44.1-I44.3', 'I45.6', 'I45.9', 'I47.x-I49.x', 'R00.0',
                                                                         'R00.1', 'R00.8', 'T82.1', 'Z45.0', 'Z95.0'],
                            'valvular disease':                         ['A52.0', 'I05.x-I08.x', 'I09.1', 'I09.8', 'I34.x-I39.x',
                                                                        'Q23.0-Q23.3', 'Z95.2-Z95.4'],
                            'pulmonary circulation disorders':          ['I26.x', 'I27.x', 'I28.0', 'I28.8', 'I28.9'],
                            'peripheral vascular disorders':            ['I70.x', 'I71.x', 'I73.1', 'I73.8', 'I73.9', 
                                                                        'I77.1', 'I79.0', 'I79.2', 'K55.1', 'K55.8',
                                                                        'K55.9', 'Z95.8', 'Z95.9'],
                            'hypertension, uncomplicated ':             ['I10.x'],
                            'hypertension, complicated':                ['I11.x-I13.x', 'I15.x'],
                            'paralysis':                                ['G04.1', 'G11.4', 'G80.1', 'G80.2', 'G81.x', 
                                                                        'G82.x', 'G83.0-G83.4', 'G83.9'],
                            'other neurological disorders':             ['G10.x-G13.x', 'G20.x-G22.x', 'G25.4', 'G25.5', 'G31.2', 
                                                                        'G31.8', 'G31.9', 'G32.x', 'G35.x-G37.x', 'G40.x', 
                                                                        'G41.x', 'G93.1', 'G93.4', 'R47.0', 'R56.x'],
                            'chronic pulmonary disease':                ['I27.8', 'I27.9', 'J40.x-J47.x', 'J60.x-J67.x', 'J68.4',
                                                                         'J70.1', 'J70.3'],
#                              'diabetes, uncomplicated'
#                              'diabetes, complicated'
#                              'hypothyroidism'
#                              'renal failure'
#                              'liver disease'
#                              'peptic ulcer disease excluding bleeding'
#                              'aids/hiv'
#                              'lymphoma'
#                              'metastatic cancer'
#                              'solid tumor without metastasis'
#                              'rheumatoid arthritis/collagen vascular diseases'
#                              'coagulopathy'
#                              'obesity'
#                             ' weight loss'
#                              'fluid and electrolyte disorders'
#                              'blood loss anemia'
#                              'deficiency anemia'
#                              'alcohol abuse'
#                              'drug abuse'
#                              'psychoses'
#                              'depression'
    } 

# charleston_icd9_coding = {
#                             'congestive heart failure'
#                             'cardiac arrhythmias'
#                             'valvular disease'
#                             'pulmonary circulation disorders'
#                             'peripheral vascular disorders'
#                             'hypertension, uncomplicated '
#                             'hypertension, complicated'
#                             'paralysis'
#                             'other neurological disorders'
#                             'chronic pulmonary disease'
#                             'diabetes, uncomplicated'
#                             'diabetes, complicated'
#                             'hypothyroidism'
#                             'renal failure'
#                             'liver disease'
#                             'peptic ulcer disease excluding bleeding'
#                             'aids/hiv'
#                             'lymphoma'
#                             'metastatic cancer'
#                             'solid tumor without metastasis'
#                             'rheumatoid arthritis/collagen vascular diseases'
#                             'coagulopathy'
#                             'obesity'
#                            ' weight loss'
#                             'fluid and electrolyte disorders'
#                             'blood loss anemia'
#                             'deficiency anemia'
#                             'alcohol abuse'
#                             'drug abuse'
#                             'psychoses'
#                             'depression'
#     } 

# charleston_values = {
#                             'myocardial infarction': 1, 
#                             'congestive heart failure': 1, 
#                             'cardiac arrhythmias': 1,
#                             'valvular disease': 1, 
#                             'pulmonary circulation disorders': 1, 
#                             'peripheral vascular disorders': 2, 
#                             'hypertension, uncomplicated '
#                             'hypertension, complicated'
#                             'paralysis'
#                             'other neurological disorders'
#                             'chronic pulmonary disease'
#                             'diabetes, uncomplicated'
#                             'diabetes, complicated'
#                             'hypothyroidism'
#                             'renal failure'
#                             'liver disease'
#                             'peptic ulcer disease excluding bleeding'
#                             'aids/hiv'
#                             'lymphoma'
#                             'metastatic cancer': 6, 
#                             'solid tumor without metastasis'
#                             'rheumatoid arthritis/collagen vascular diseases'
#                             'coagulopathy'
#                             'obesity'
#                            ' weight loss'
#                             'fluid and electrolyte disorders'
#                             'blood loss anemia'
#                             'deficiency anemia'
#                             'alcohol abuse'
#                             'drug abuse'
#                             'psychoses'
#                             'depression'
#     } 


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

def check_whatever(codes_dict, user_codes=None): # won't be none
    counter = 0
    for key, value in codes_dict: 
        # create set for that 
        # if any in user codes in that
        # take value from charleston dict of values 
        # add that value to some counter? 
        pass
        


if __name__ == '__main__':
    pass