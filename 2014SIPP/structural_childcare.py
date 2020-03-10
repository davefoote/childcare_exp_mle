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

def categorical_split(df):
    cond1 = (df['monthly_childcare_expenditure'] == 0)
    cond2 = (df['monthly_childcare_expenditure'] > 0)
    cond3 = (df['monthly_wage'] > 0)
    cond4 = (df['monthly_wage'] == 0)

    return df[cond1 & cond3], df[cond2 & cond3], df[cond4]

def extract_x_matrix(df, xcols):
    '''
    inputs: df with data and column names of your x variables
    output: n x k matrix of x data where n is #observations and k is
    #of columns
    '''
    
    return df[xcols].to_numpy()

def mle_beta_vec(df, xcols, init_guess, f):
    '''
    df = dataframe
    xcolumn names in list form
    init_guess in list form
    criterion function f
    doin the damn thing (write better comment later)
    '''
    d1, d2, d3 = categorical_split(df)
    d1 = extract_x_matrix(d1, xcols)
    d2 = extract_x_matrix(d2, xcols)
    d3 = extract_x_matrix(d3, xcols)
    data = (d1, d2, d3)
    
    results_uncstr = opt.minimize(f, np.array(init_guess), args=data)
    
    return results_uncstr.x

def prob_1(x_matrix, beta_vec):
    '''
    calculate probability a set of observations is a member of d1, using logit
    classification
    '''
    linear_kernel = x_matrix.dot(beta_vec)
    rv = np.exp(linear_kernel) / (1 + np.exp(linear_kernel))
    rv[rv == 1] = .999999

    return rv

def sum_three_criterion(beta_guess, *args):
    '''
    beta_guess comes in as array
    '''
    d1, d2, d3 = args
    
    return (logit_neglog_likelihood(beta_guess, d1, prob_1) +
            logit_neglog_likelihood(beta_guess, d2, prob_1) +
            logit_neglog_likelihood(beta_guess, d3, prob_1))

def logit_neglog_likelihood(beta_vec, *args):
    '''
    calculate the log likelihood that the probability is correct
    '''
    xm, probability_now = args
    p = probability_now(xm, beta_vec)
    rv = []
    for x in p:
        to_add = (x * math.log(x)) + ((1 - x) * math.log(1 - x))
        if to_add is not np.nan:
            rv.append(to_add)
            
    rv = pd.Series(rv)
        
    print(rv.sum())

    return -(rv.sum())
    
'''
Data Summary/Visualization Functions
'''
