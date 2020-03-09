import math
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import scipy.stats
from scipy.special import log_ndtr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error

'''
This file estimates a Tobit model using maximum likelihood estimation
'''

def splitter(df, y_col, upper, lower):
    '''
    seperate censored and noncensored portions of data, assuming both ends of
    data are censored
    '''
    left = pd.DataFrame()
    uncensored = pd.DataFrame()
    right = pd.DataFrame()
    
    left = df[df[y_col] == lower]
    uncensored = df[(df[y_col] != lower) & (df[y_col] != upper)]
    right = df[df[y_col] == upper]
    
    return left, uncensored, right

    
    