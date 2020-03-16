'''
ETL SCRIPT PREPARING 2014 SIPP SURVEY FOR STRUCTURAL ESTIMATION OF LINK
BETWEEN CHILDCARE, WAGES, AND LABOR FORCE ATTACHMENT

Dave Foote
'''
import numpy as np
import pandas as pd
import time
import datetime
from dateutil.relativedelta import relativedelta

'''
MAPS
'''
ed_map = {31: 0, 32: 4, 33: 5, 34:7, 35: 8, 36:9, 37: 10, 38: 11, 39: 12,
          40: 12, 41: 13, 42: 14, 43: 16, 44: 18, 45: 18, 46: 21}
race_map = {1: False, 2: True, 3: True, 4: True}
onetwo_binary_map = {1: True, 2: False}
sex_map = {1: 'Male', 2: 'Female'}
time_map = {1: 'Hours', 2: 'Days', 3: 'Weeks'}
state_map = {1: 'Alabama', 2: 'Alaska', 4: 'Arizona', 5: 'Arkansas',
            6: 'California', 8: 'Colorado', 9: 'Connecticut', 10: 'Delaware',
            11: 'D.C.', 12: 'Florida', 13: 'Georgia', 15: 'Hawaii',
            16: 'Idaho', 17: 'Illinois', 18: 'Indiana', 19: 'Iowa',
            20: 'Kansas', 21: 'Kentucky', 22: 'Louisiana', 23: 'Maine',
            24: 'Maryland', 25: 'Massachusetts', 26: 'Michigan',
            27: 'Minnesota', 28: 'Mississippi', 29: 'Missouri', 30: 'Montana',
            31: 'Nebraska', 32: 'Nevada', 33: 'New Hampshire',
            34: 'New Jersey', 35: 'New Mexico', 36: 'New York',
            37: 'North Carolina', 38: 'North Datoka', 39: 'Ohio',
            40: 'Oklahoma', 41: 'Oregon', 42: 'Pennsylvania',
            44: 'Rhode Island', 45: 'South Carolina', 46: 'South Dakota',
            47: 'Tennessee', 48: 'Texas', 49: 'Utah', 50: 'Vermont',
            51: 'Virginia', 53: 'Washington', 54: 'West Virginia',
            55: 'Wisconsin', 56: 'Wyoming', 60: 'Puerto Rico and Island Areas',
            61: 'Foreign Country'}
southerness_map = {}
for x in state_map.keys():
    if x in [1, 5, 12, 13, 21, 22, 28, 37, 45, 47, 48, 51]:
        southerness_map[x] = True
    else:
        southerness_map[x] = False

'''
Column Groups
'''
childs = ['RPNCHILD' + str(x) for x in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]]
earned_inc_cols = ['TDIS2AMT', 'TDIS3AMT', 'TDIS4AMT', 'TDIS5AMT', 'TDIS6AMT',
                  'TDIS8AMT', 'TDIS9AMT', 'TDIS10AMT', 'TJB1_OINCAMT', 
                  'TJB2_OINCAMT', 'TJB3_OINCAMT', 'TJB4_OINCAMT', 
                   'TJB5_OINCAMT', 'TJB6_OINCAMT', 'TJB7_OINCAMT',
                   'TJB1_CXAMT', 'TJB1_TXAMT', 'TJB1_OXAMT', 'TJB1_BXAMT',
                   'TJB2_CXAMT', 'TJB2_TXAMT', 'TJB2_OXAMT', 'TJB2_BXAMT',
                   'TJB3_CXAMT', 'TJB3_TXAMT', 'TJB3_OXAMT', 'TJB3_BXAMT',
                   'TJB4_CXAMT', 'TJB4_TXAMT', 'TJB4_OXAMT', 'TJB4_BXAMT',
                   'TJB5_CXAMT', 'TJB5_TXAMT', 'TJB5_OXAMT', 'TJB5_BXAMT',
                   'TJB6_CXAMT', 'TJB6_TXAMT', 'TJB6_OXAMT', 'TJB6_BXAMT',
                   'TJB7_CXAMT', 'TJB7_TXAMT', 'TJB7_OXAMT', 'TJB7_BXAMT',
                   'TSSSAMT', 'TSSCAMT']
child_birthyears = ['TCBYR_' + str(x) for x in range(1, 21)]

'''
READ DATA
'''
print("started reading data @: ", time.time())
df = pd.read_csv('pu2014w1.csv')
print('sipp data read, beginning analysis @:', time.time())
start = time.time()
rdf = pd.DataFrame()

'''
LOOKUP FUNCTIONS
'''

def lookup_child_ages(df, rdf, birth_cols):
    '''
    establish a child ages column (with empty lists)
    look through all respondants under 15 (must be run AFTER age is created)
    map these respondants to their parents 
    '''
    for x in birth_cols:
        df[x] = 2014 - df[x]
    byears = df[birth_cols]
    byears = byears.unstack()
    byears = pd.DataFrame(byears)
    byears.columns = ['age']
    byears.index = [x[1] for x in byears.index]
    #filter out people who can watch themselves
    byears = byears[byears['age'] < 15]
    #find the babies
    lowrangemap = byears[byears.age <= 2]
    #find the toddlers
    midrangemap = byears[(byears.age <= 5) & (byears.age > 2)]
    #find the young children
    highrangemap = byears[(byears.age <= 10) & (byears.age > 5)] 
    l = [lowrangemap, midrangemap, highrangemap, byears]
    rl = []
    print([type(x) for x in l])
    #turn these into maps
    for x in l:
        x['idx'] = x.index
    l = [x.groupby('idx').count() for x in l]

        
    return l[0]['age'], l[1]['age'], l[2]['age'], l[3]['age']

def lookup_mean_childcare_exp_instate(df):
    '''
    call after creating monthly_childcare_exp column
    '''
    rdf = df[['monthly_childcare_expenditure', 'STATE']]
    map_ = rdf.groupby('STATE').mean()
    rmap = {}
    for i, r in map_.iterrows():
        rmap[i] = r['monthly_childcare_expenditure']

    return df['STATE'].map(rmap)
    
'''
EXTRACT and TRANSFORM INTO RETURN DF (rdf)
'''
def main():
    #KEEPING THESE COLUMNS NAMED THE SAME TO MAKE SPOUSAL LOOKUPS EASIER
    rdf['monthly_wage'] = df.iloc[:,4404:4411].sum(axis=1)
    rdf['monthly_job_hrs'] = df['TMWKHRS']
    rdf['ssuid'] = df.ssuid
    rdf['pid'] = df.PNUM
    rdf['unique_id'] = [str(r['ssuid']) + str(r['pid']) for i, r in rdf.
                        iterrows()]
    rdf['monthcode'] = df.monthcode
    rdf['est_hourly_wage'] = rdf.monthly_wage / rdf.monthly_job_hrs
    rdf['BIRTHMONTH'] = df.EDOB_BMONTH
    rdf['BIRTHYEAR'] = df.TDOB_BYEAR
    rdf['interview_date'] = [datetime.date(2014, int(r['monthcode']), 1) for i, r in
                             rdf.iterrows()]
    rdf['birthday'] = [datetime.date(int(r['BIRTHYEAR']), int(r['BIRTHMONTH']), 1) for i, r
                       in rdf.iterrows()]
    #AGE CALCULATED AT TIME OF INTERVIEW
    rdf['AGE'] = [relativedelta(r['interview_date'], r['birthday']).years for i, r
                  in rdf.iterrows()]
    rdf['EDUCATION'] = df.EEDUC.map(ed_map)
    rdf['MARITAL_STATUS'] = df.EMS
    rdf['gov_childcare_assist'] = df.EWHOPAID1.map(onetwo_binary_map)
    rdf['emp_childcare_assist'] = df.EWHOPAID2.map(onetwo_binary_map)

    #we need more data to turn state into: "state checks criminal records"
    #"south?", "state mandated child:staff ratio", "state regulates family home 
    # daycare"
    rdf['STATE'] = df.tehc_st
    rdf['SOUTHERN'] = rdf.STATE.map(southerness_map)
    rdf['STATE'] = rdf.STATE.map(state_map)
    rdf['METRO'] = df.tehc_metro
    rdf['nonwhite'] = df.ERACE.map(race_map)
    rdf['monthly_childcare_expenditure'] = df.TPAYWK * 4
    rdf['sex'] = df.ESEX.map(sex_map)
    rdf['num_children'] = df[childs].idxmax(axis=1)
    rdf['num_children'].fillna(0, inplace=True)
    rdf['num_children'] = [x[-1] for x in rdf.num_children.astype(str)]
    rdf['hh_childcount'] = df.RHNUMU18
    rdf['hh_headcount'] = df.RHNUMPER
    rdf['hh_adultcount'] = rdf.hh_headcount - rdf.hh_childcount
    rdf.num_children = [int(x) for x in rdf.num_children]
    #num_children under 15 is the actual variable we would need specific records to put this together
    rdf['has_child_in_daycare'] = df.RDAYCARE.map(onetwo_binary_map)
    rdf['missed_work_for_childcare'] = df.ETIMELOST_TP.map({1: 'Hours', 2: 'Days', 3: 'Weeks'})
    rdf['monthly_childcare_expenditure'] = (df.TPAYWK / 7) * 30.42
    rdf['mean_childcare_exp_instate'] = lookup_mean_childcare_exp_instate(rdf)
    #yearly income topcoded at 10,000,000,000
    rdf['TOTAL_ANNUAL_PERSONAL_INCOME'] = df.TPTOTINC
    rdf['total_monthly_income'] = rdf.TOTAL_ANNUAL_PERSONAL_INCOME / 12
    start_years = [df.columns.get_loc(x) for x in ['TJB1_STRTYR', 'TJB2_STRTYR',
                                                   'TJB3_STRTYR', 'TJB4_STRTYR', 
                                                   'TJB5_STRTYR', 'TJB6_STRTYR', 
                                                   'TJB7_STRTYR']] 
    rdf['experience'] = df.iloc[:, start_years].idxmin(axis=1)
    rdf['monthly_earned_income'] = df[earned_inc_cols].sum(axis=1) + rdf['monthly_wage']
    rdf['monthly_unearned_income'] = rdf['total_monthly_income'] - rdf['monthly_earned_income']
    map1, map2, map3, map4 = lookup_child_ages(df, rdf, child_birthyears)
    rdf['k_under2'] = rdf.index.to_series().map(map1)
    rdf['k_3to5'] = rdf.index.to_series().map(map2)
    rdf['k_6to10'] = rdf.index.to_series().map(map3)
    rdf['k_under15'] = rdf.index.to_series().map(map4)
    print("WRITING OUTPUT @: ", time.time())
    rdf.to_csv('output.csv')
    print("OUTPUT SAVED")
    print("TOTAL TRANSFORM/LOAD TIME in Minutes: ", (time.time() - start) / 60)

if __name__ == "__main__":
    main()






