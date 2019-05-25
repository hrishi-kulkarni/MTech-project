import pandas_profiling
import pandas as pd
df=pd.read_csv('operator.csv',names=['id','name','login_time','opr_time','boom','bucket'],header=None)
print(df.head())
profile = pandas_profiling.ProfileReport(df)
profile.to_file(outputfile="output.html")