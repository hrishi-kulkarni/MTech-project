import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import pandas_profiling
import seaborn as sns

QUERY='SELECT * FROM operator;'
db=pymysql.connect(host='localhost',user='root',passwd='',db='operatorpersonalization')
results = pd.read_sql_query(QUERY, db)
results.to_csv("operator.csv", index=False)

df=pd.read_csv('operator.csv')
print(df.head())

#TODO: Require change in SQL Query for new data insertion - o/w divide by zero error
df['Efficiency']=(df['OperationTime']*100)/df['LoginTime']

sns.set(style="whitegrid")
ax = sns.barplot(df['Name'], df['Efficiency'])
fig=ax.get_figure()
fig.savefig('efficiency.jpg')

fig=df.plot.bar(x='Name',y=['LoginTime','OperationTime'], rot=0).get_figure()
fig.savefig('time_compare.jpg')