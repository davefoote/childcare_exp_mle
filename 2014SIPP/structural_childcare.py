import numpy as np
import pandas as pd
import scipy.stats as sts
import math
from matplotlib import pyplot as plt
import requests
import scipy.optimize as opt
from statsmodels.discrete.discrete_model import Probit
import statsmodels.api as sm

'''
Run a structural estimation on Childcare on Women's Workforce Attachment

Dave Foote
Jesus Pacheco
'''

def max_likelihood_estimator(guess, f, data):
    '''
    runs MLE to solve for alpha and beta that best fit a gamma dist to given
    data
    
    FOR 2 PARAMETER PROBLEMS
    
    inputs:
        guess: an initial guess, probably provided by a _firstguess function
        f: the function to be used to generate pdfs for the mle estimation
        data: np array of data
    '''
    p1 = guess[0]
    p2 = guess[1]
    p_init = np.array([p1, p2])
    results_uncstr = opt.minimize(f, p_init, args=(data))
    p1, p2 = results_uncstr.x
    
    return p1, p2

def log_lik(x, params, f):
    '''
    Compute the log likelihood function for data xvalsgiven given distribution
    that uses 2 parameters and those 2 paramters
    '''
    if len(params) == 2:
        p0 = params[0]
        p1 = params[1]

        return np.log(f(x, p0, p1)).sum()
    if len(params) == 3:
        p0 = params[0]
        p1 = params[1]
        p2 = params[2]

        return np.log(f(x, p0, p1, p2)).sum()
    
def probits(df, x_cols1, x_cols2, y1, y2):
    #set up two probit models
    Y1 = df[y1]
    Y2 = df[y2]
    X1 = df[x_cols1]
    X1 = sm.add_constant(X1)
    X2 = df[x_cols2]
    X2 = sm.add_constant(X2)
    #initiate and fit these models
    h_mod = Probit(Y1, X1.astype(float))
    f_mod = Probit(Y2, X2.astype(float))
    h_mod.fit()
    f_mod.fit()
    
    print('H Probit Summary: ', h_mod.summary())
    print('F Probit Summary: ', f_mod.summary())
    
    return h_mod, f_mod

def categorical_split(df):
    cond1 = (df['monthly_childcare_expenditure'] == 0)
    cond2 = (df['monthly_childcare_expenditure'] > 0)
    cond3 = (df['monthly_wage'] > 0)
    cond4 = (df['monthly_wage'] == 0)
    
    return df[cond1 & cond3], df[cond2 & cond3], df[cond4]
    
