'''
Created on Mar 10, 2017

@author: matt
'''

'''
Based these buckets off of this paper: http://www.aaai.org/ocs/index.php/WS/AAAIW16/paper/view/12669
'''

ethnicity_dict = {
                'HISPANIC/LATINO - CUBAN': 'latino', 
                'HISPANIC/LATINO - MEXICAN': 'latino',
                'UNKNOWN/NOT SPECIFIED': 'other',
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
                'PATIENT DECLINED TO ANSWER': 'other',
                'AMERICAN INDIAN/ALASKA NATIVE FEDERALLY RECOGNIZED TRIBE': 'american_indian',
                'ASIAN - VIETNAMESE': 'asian',
                'ASIAN - KOREAN': 'asian',
                'BLACK/CAPE VERDEAN': 'black',
                'OTHER': 'other',
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
                'UNABLE TO OBTAIN': 'other',
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

ethnicity_values = {'other': 0, 
                    'white': 1, 
                    'black': 2, 
                    'latino': 3, 
                    'asian': 4, 
                    'multi_racial': 5, 
                    'middle_eastern': 6,
                    'pacific_islander': 7, 
                    'american_indian': 8 }

'''
Guide: Unknown 0, Married 1, Single 2, Divorced / Separated  Widowed 3
'''


marital_status_dict = {
                        'SEPARATED': 3, 
                        'MARRIED': 1, 
                        'DIVORCED': 3, 
                        'UNKNOWN (DEFAULT)': 0, 
                        'SINGLE': 2, 
                        'WIDOWED': 3, 
                        'LIFE PARTNER': 1
                        }
                        
                        
                        

if __name__ == '__main__':
    pass