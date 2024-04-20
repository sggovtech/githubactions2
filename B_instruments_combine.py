import pandas as pd
import glob

# Get a list of all CSV files in the directory
csv_files = glob.glob('B_instruments*.csv')

# Create an empty list to store the dataframes
dfs = []

# Read each CSV file and append its contents to the list
for file in csv_files:
    df = pd.read_csv(file)
    dfs.append(df)

# Concatenate the dataframes into one
combined_df = pd.concat(dfs)

# Save the combined dataframe to a new CSV file
combined_df.to_csv('combined_instruments.csv', index=False)