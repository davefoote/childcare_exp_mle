# childcare_exp_mle
##The Economic Structure of Household Childcare Decisions

2014 SIPP Wave 1 Dataset can be found on the NBER website here:
http://data.nber.org/sipp/2014/pu2014w1.csv.zip

If you use bash try:  
....> wget http://data.nber.org/sipp/2014/pu2014w1.csv.zip  
....> unzip pu2014w1.csv.zip  
....> rm pu2014w1.csv.zip  

Once this CSV is in your directory, run the command below to generate 
a cleaned and useable SIPP dataset  
....> python sipp_reader.py  
....> rm pu2014w1.csv  

Now you have only the 113 most import MB from the original 6GB dataset. 

