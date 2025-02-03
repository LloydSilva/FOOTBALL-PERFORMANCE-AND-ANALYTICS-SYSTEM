import mysql.connector
import pandas as pd
import numpy as np
from DFStruct import *


# Function to map pandas dtypes to MySQL dtypes
def map_dtype_to_mysql(dtype):
    if np.issubdtype(dtype, np.integer):
        return "INT"
    elif np.issubdtype(dtype, np.floating):
        return "FLOAT"
    elif np.issubdtype(dtype, np.datetime64):
        return "DATETIME"
    elif np.issubdtype(dtype, np.object_):
        return "VARCHAR(255)"  # Default string length, can be adjusted based on data
    else:
        return "VARCHAR(255)"  # Fallback for unknown types


def generate_create_table_statement(df, table_name):
    columns = df.columns
    column_defs = []

    # Iterate through each column and generate its definition
    for col in columns:
        dtype = df[col].dtype
        mysql_type = map_dtype_to_mysql(dtype)
        
        # Escape column names that might be reserved keywords or contain special characters
        escaped_col = f"`{col}`"  # Using backticks around column names
        
        column_defs.append(f"{escaped_col} {mysql_type}")
    
    # Add an auto-incremented primary key 'ID_Index' column at the beginning
    column_defs.insert(0, "ID_Index INT AUTO_INCREMENT PRIMARY KEY")

    # Create the SQL statement
    create_table_statement = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join(column_defs)}
    );
    """
    
    return create_table_statement

def MySql_table_statements():    
    df_list=[pd.read_csv(df) for df in csv_files]
    table_names=[csv_file.split("/")[-1].split(".")[0] for csv_file in csv_files]
    result=[]

    for df,table_name in zip(df_list,table_names):
        result.append(generate_create_table_statement(df, table_name))

    return result


# Function to escape column names that might be reserved keywords or contain special characters
def escape_column_name(col_name):
    # MySQL reserved keywords should be wrapped in backticks
    return f"`{col_name}`"

# Connect to MySQL
# Connect MongoDB create/recreate DB,tables
def MySql_connect():
    database_name = "DB_Football"

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ulisboa123&&345",
    )

    cursor = connection.cursor()

    # Create database if not exists
    cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    cursor.execute(f"USE {database_name}")

    # List of CSV files to process
    
    shots_drop_columns,matches_drop_columns,players_drop_columns,teams_drop_columns, new_table_drop_columns=get_drop_columns()
    df_shots,df_matches,df_players,df_teams,df_new_table=read_all_csvs(shots_drop_columns,matches_drop_columns,players_drop_columns,teams_drop_columns,new_table_drop_columns)

    df_list=[df_shots,df_matches,df_players,df_teams,df_new_table]

    # Loop through each CSV file
    for df, csv_file in zip(df_list, csv_files):
        # Handle missing data (NaNs), replace with None (NULL for MySQL)
        df = df.where(pd.notnull(df), None)

        # Rename columns like "Unnamed: 0" or any unnamed columns
        df.columns = [col if not col.startswith("Unnamed") else f"Unnamed_{i}" for i, col in enumerate(df.columns)]

        # Ensure that 'id' column does not conflict with any CSV column
        # if 'id' in df.columns:
        #     df = df.drop(columns=['id'])  # Drop the 'id' column from CSV if it exists

        # Convert DataFrame to a list of dictionaries (records)
        try:
            data_dict = df.to_dict(orient="records")
        except Exception as e:
            print(f"Error converting DataFrame to dict for {csv_file}: {e}")
            continue

        # Define table name based on the CSV file name
        table_name = csv_file.split("/")[-1].split(".")[0]  # Extract table name from the file name

        # Drop the table if it exists
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

        # Dynamically create table based on the DataFrame columns
        columns = df.columns
        column_defs = []
        for col in columns:
            escaped_col = escape_column_name(col)
            dtype = df[col].dtype

            # Mapping the dtypes to MySQL types
            if np.issubdtype(dtype, np.number):
                if np.issubdtype(dtype, np.integer):
                    column_defs.append(f"{escaped_col} INT")
                else:
                    column_defs.append(f"{escaped_col} FLOAT")
            elif np.issubdtype(dtype, np.datetime64):
                column_defs.append(f"{escaped_col} DATETIME")
            else:
                column_defs.append(f"{escaped_col} VARCHAR(255)")

        # Add 'id' column as primary key
        column_defs.insert(0, "ID_Index INT AUTO_INCREMENT PRIMARY KEY")

        # Create table SQL query
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join(column_defs)}
        );
        """
        cursor.execute(create_table_query)

        # Insert data into the table
        insert_query = f"INSERT INTO {table_name} ({', '.join([escape_column_name(col) for col in columns])}) VALUES ({', '.join(['%s'] * len(columns))});"

        # Prepare data to insert, ensuring that NaN values are converted to None (NULL for MySQL)
        data_to_insert = []
        for item in data_dict:
            data_to_insert.append(tuple([None if pd.isna(val) else val for val in item.values()]))

        try:
            cursor.executemany(insert_query, data_to_insert)
            connection.commit()
            print(f"Inserted {cursor.rowcount} rows into {table_name}.")
        except mysql.connector.Error as err:
            print(f"Error inserting data into {table_name}: {err}")
            connection.rollback()

        # Query and show indexes for the created table
        sql_show_indexes = f"SHOW INDEX FROM {table_name};"
        cursor.execute(sql_show_indexes)
        index_list = cursor.fetchall()
        # print(f"List of indexes for {table_name}: {index_list}")
    
    print("\nData inserted successfully for all files!")

    # Close cursor and connection
    # cursor.close()
    # connection.close()
    
    return cursor,connection,df_shots,df_matches,df_players,df_teams,df_new_table



