import pandas as pd
from datetime import datetime

data = pd.read_csv('Data/DSNY_Monthly_Tonnage_Data.csv')

# Create accurate borocd numbers
district = []
for i in data['COMMUNITYDISTRICT']:
    if len(str(i)) == 1:
        i = "0" + str(i)
        district.append(i)
    else:
        district.append(i)

data['COMMUNITYDISTRICT'] = district

# join to create borocd
data['BoroCD'] = data['BOROUGH_ID'].astype(str) + data['COMMUNITYDISTRICT'].astype(str)

# Format Time in order to subset latter
data['Collection_Date'] = [datetime.strptime(x, '%Y / %m') for x in data['MONTH']]

# set time as index to subset later
data.set_index('Collection_Date', inplace=True)

# Read population
pop = pd.read_excel('Data/t_pl_p1_cd.xlsx', skiprows=5)

# Subset
pop.dropna(inplace=True)
pop.columns = ['BoroCD','Community_District', '1970', '1980','1990','2000','2010','Number','Percent']
pop = pop[['BoroCD', '2010']]

# Clean Data
district = []
for i in pop['BoroCD']:
    i = str(i).strip()
    if len(str(i)) == 1:
        i = "0" + str(i)
        district.append(i)
    else:
        district.append(str(i))
pop['BoroCD'] = district

# Create proper BoroCD column
pop['BoroCD'][0:12] = ["2" + str(x) for x in pop['BoroCD'][0:12]]
pop['BoroCD'][12:30] = ["3" + str(x) for x in pop['BoroCD'][12:30]]
pop['BoroCD'][30:42] = ["1" + str(x) for x in pop['BoroCD'][30:42]]
pop['BoroCD'][42:56] = ["4" + str(x) for x in pop['BoroCD'][42:56]]
pop['BoroCD'][56:59] = ["5" + str(x) for x in pop['BoroCD'][56:59]]

# Subset 2014 data
tons_2014 = data['2014'].groupby(['BoroCD'])['REFUSETONSCOLLECTED', 'PAPERTONSCOLLECTED','MGPTONSCOLLECTED'].sum()

# Merge population data with tonnage data
tons = tons_2014.reset_index().merge(pop)

# Add Paper recycling and MGP recycling for total recycling
tons['Total_Recycling'] = tons['PAPERTONSCOLLECTED'] + tons['MGPTONSCOLLECTED']

# Calculate Diversion Rate
tons['Diversion_Rate'] = tons['Total_Recycling'] / (tons['REFUSETONSCOLLECTED'] + tons['Total_Recycling'])

# Calculate Per Capita Diversion Rate - multiple by 100000 to have reasonable numbers
tons['Per_Capita_Diversion_Rate'] = (tons['Diversion_Rate'] / tons['2010']) * 100000

tons.to_csv('Data/diversion_rate.csv', index=False)