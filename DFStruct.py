import pandas as pd
import time
import pprint
import itertools




csv_files = [
        "data/shots.csv",
        "data/matches.csv",
        "data/all_players.csv",
        "data/teams.csv",
        "data/new_table.csv"
        # Add other CSV filenames here
    ]  # Replace with actual file paths



exec_time={'Mongo':{'1.1':0,'1.2':0,'2.1':0,'2.2':0},
           'MySql':{'1.1':0,'1.2':0,'2.1':0,'2.2':0}}


def get_dict_combinations(dct):
    combinations = []
    # Loop over all possible combination lengths
    for r in range(1, len(dct) + 1):
        # Generate all combinations of key-value pairs of length r
        key_value_combos = itertools.combinations(dct.items(), r)
        combinations.extend(key_value_combos)
    
    # Convert each combination (tuple of key-value pairs) back into a dictionary
    return [dict(comb) for comb in combinations]




def get_drop_columns():
    shots_drop_columns=["Minute","Squad","xG","PSxG","Notes","SCA 1_Player","SCA 1_Event","SCA 2_Player","SCA 2_Event"]
    matches_drop_columns=['Unnamed: 1', 'Referee', 'Notes', 'played','id',
                          'position_home', 'position_away',
       'home_capitan', 'away_capitan', 'home_xg', 'away_xg', 'home_xga',
       'away_xga', 'home_formation', 'away_formation', 'Timestamp']
    players_drop_columns=[
        'Playing Time_MP', 'Playing Time_Starts',
       'Playing Time_Min', 'Playing Time_90s', 'Performance_Gls',
       'Performance_Ast', 'Performance_G+A', 'Performance_G-PK',
       'Performance_PK', 'Performance_PKatt', 'Performance_CrdY',
       'Performance_CrdR', 'Expected_xG', 'Expected_npxG', 'Expected_xAG',
       'Expected_npxG+xAG', 'Progression_PrgC', 'Progression_PrgP',
       'Progression_PrgR', 'Per 90 Minutes_Gls', 'Per 90 Minutes_Ast',
       'Per 90 Minutes_G+A', 'Per 90 Minutes_G-PK', 'Per 90 Minutes_G+A-PK',
       'Per 90 Minutes_xG', 'Per 90 Minutes_xAG', 'Per 90 Minutes_xG+xAG',
       'Per 90 Minutes_npxG', 'Per 90 Minutes_npxG+xAG',
    ]
    teams_drop_columns=['xG', 'xGA', 'xGD', 'xGD/90']
    
    new_table_drop_columns = ['Unamed']

    return shots_drop_columns,matches_drop_columns,players_drop_columns, teams_drop_columns, new_table_drop_columns


# read all csvs
def read_all_csvs(*args):
    shots_drop_columns=args[0]
    matches_drop_columns=args[1]
    players_drop_columns=args[2]
    teams_drop_columns=args[3]
    new_table_drop_columns=args[4]

    df_shots=pd.read_csv('data/shots.csv',index_col=0)
    # df_shots=df_shots[['Player', 'Outcome', 'Distance', 'Body Part', 'match_id']]
    df_shots=df_shots.drop(columns=shots_drop_columns)

    df_matches=pd.read_csv('data/matches.csv',index_col=0)
    # df_matches=df_matches[['Date', 'league','Day', 'Attendance', 'home_id', 'away_id',
    #    'score_away', 'score_home', 'position_home', 'position_away']]

    df_matches=df_matches.drop(columns=matches_drop_columns)

    # don't drop id for players
    df_players=pd.read_csv('data/all_players.csv')
    # df_players=df_players[['id', 'name', 'Pos', 'Matches', 'club_id', 'MP', 'year']]

    df_players=df_players.drop(columns=players_drop_columns)

    # get name and id from id -> en/players/id/name
    df_players['name']=df_players['id'].str.split('/').str[4]
    df_players['id']=df_players['id'].str.split('/').str[3]
    # reorder columns
    # df_players = df_players.loc[:, ['id', 'name','Pos', 'Matches', 'club_id', 'MP', 'year']]
    # df_players = df_players[['id', 'name','Pos', 'Matches', 'club_id', 'MP', 'year']]


    # don't drop id for teams
    df_teams=pd.read_csv('data/teams.csv')
    # df_teams=df_teams[['id', 'name', 'league', 'W', 'D', 'L', 'MP', 'GF', 'GA', 'GD', 'Pts']]

    # df_players['id']=df_players['id']
    df_teams=df_teams.drop(columns=teams_drop_columns)

    df_new_table=pd.read_csv('data/new_table.csv',index_col=0)
    # df_shots=df_shots[['Player', 'Outcome', 'Distance', 'Body Part', 'match_id']]
    df_new_table=df_new_table.drop(columns=new_table_drop_columns)


    return df_shots,df_matches,df_players,df_teams, df_new_table
        
# Decorator to measure execution time
def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Call the original function
        end_time = time.time()  # Record the end time
        execution_time = end_time - start_time  # Calculate the execution time
        print(f"Execution time: {execution_time:.4f} seconds")
        return result , execution_time # Return the result of the original function
    return wrapper


