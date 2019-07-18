import sqlite3
import pandas as pd

dat = sqlite3.connect('site.db')
query = dat.execute("SELECT * From Details")
cols = [column[0] for column in query.description]
results= pd.DataFrame.from_records(data = query.fetchall(), columns = cols)

print(results)