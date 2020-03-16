# childcare_exp_mle
##The Economic Structure of Household Childcare Decisions

by Jesus Pacheco and Dave Foote

2014 SIPP Wave 1 Dataset can be found on the NBER website here:
http://data.nber.org/sipp/2014/pu2014w1.csv.zip

If you use bash try:  
>$ wget http://data.nber.org/sipp/2014/pu2014w1.csv.zip  
>$ unzip pu2014w1.csv.zip  
>$ rm pu2014w1.csv.zip  

Once this CSV is in your directory, run the command below to generate 
a cleaned and useable SIPP dataset  
>$ python sipp_reader.py  
>$ rm pu2014w1.csv  

Next, run childcare_project.R in R studio (or your R environment)
and you have our data! To skip these steps simply load rdf_subset.csv.

Our analysis can be recreated in 2014SIPP/structural_childcare.ipynb
 

