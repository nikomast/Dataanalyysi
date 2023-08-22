import requests
import json
import http.client
import mysql.connector
from datetime import datetime
import time

#API tiedot ja käskyt
token = "8c09986ea89b04f86e45b5e0f326054c"
conn = http.client.HTTPSConnection("v3.football.api-sports.io")
headers = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': token
    }


#Haetaan joukkueen kausi kohtainen statistiikka ja luodaan kausistatistiikasta sql lauseita, jotka suoritetaan
def joukkueen_data_sql():

    joukkueet = [42, 66, 35, 55, 51, 44, 49, 52, 45, 36, 40, 1359, 50, 33, 34, 65, 62, 47, 48, 15433] 
    vuosi = 2021#2022 löytyy tietokannasta
    for x in joukkueet:
        haku = "/teams/statistics?season="+str(vuosi)+"&team="+str(x)+"&league=39"
        conn.request("GET",haku,headers=headers)
        res = conn.getresponse()
        data = res.read()
        my_json = data.decode('utf8').replace('"', '"')
        my_dict = json.loads(data)
        my_dict = my_dict["response"]
        my_dict.pop("league")
        data = my_dict


    sql_statements = []
    #Käydään APIlta saatu kirjasto läpi ja tehdään sql lauseet
    for key, value in data.items():
        if key == 'team':
            #Joukkueen data
            team_id = value['id']
            team_name = value['name']
            team_logo = value['logo']
            table_name = 'team'
            columns = 'id, name, logo'
            values = f"{team_id}, '{team_name}', '{team_logo}'"

            insert_statement = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
            sql_statements.append(insert_statement)

        elif key == 'form':
            form = value
            table_name = 'form'
            columns = 'team_id, form'
            values = f"{team_id}, '{form}'"

            insert_statement = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
            sql_statements.append(insert_statement)

        elif key == 'fixtures':
            played = value['played']
            wins = value['wins']
            draws = value['draws']
            loses = value['loses']
            played = value['played']
            wins = value['wins']
            draws = value['draws']
            loses = value['loses']

            table_name_played = 'fixtures_played'
            columns_played = 'team_id, home, away, total'
            values_played = f"{team_id}, {played['home']}, {played['away']}, {played['total']}"
            insert_statement_played = f"INSERT INTO {table_name_played} ({columns_played}) VALUES ({values_played});"
            sql_statements.append(insert_statement_played)

            table_name_wins = 'fixtures_wins'
            columns_wins = 'team_id, home, away, total'
            values_wins = f"{team_id}, {wins['home']}, {wins['away']}, {wins['total']}"
            insert_statement_wins = f"INSERT INTO {table_name_wins} ({columns_wins}) VALUES ({values_wins});"
            sql_statements.append(insert_statement_wins)
            
            table_name_draws = 'fixtures_draws'
            columns_draws = 'team_id, home, away, total'
            values_draws = f"{team_id}, {draws['home']}, {draws['away']}, {draws['total']}"
            insert_statement_draws = f"INSERT INTO {table_name_draws} ({columns_draws}) VALUES ({values_draws});"
            #print(insert_statement_draws)
            sql_statements.append()

            table_name_loses = 'fixtures_losses'
            columns_loses = 'team_id, home, away, total'
            values_loses = f"{team_id}, {loses['home']}, {loses['away']}, {loses['total']}"
            insert_statement_loses = f"INSERT INTO {table_name_loses} ({columns_loses}) VALUES ({values_loses});"
            sql_statements.append(insert_statement_loses)



        elif key == 'goals':
            # Extract goals data and insert into the 'goals_for_total', 'goals_for_average', and 'goals_for_minute' tables
            # Build and execute SQL insert statements for 'goals_for_total', 'goals_for_average', and 'goals_for_minute' tables
            goals_for_total = value['for']['total']
            goals_for_average = value['for']['average']
            goals_for_minute = value['for']['minute']

            # Build insert statement for goals_for_total table
            table_name_total = 'goals_for_total'
            columns_total = 'team_id, home, away, total'
            values_total = f"{team_id}, {goals_for_total['home']}, {goals_for_total['away']}, {goals_for_total['total']}"
            insert_statement_total = f"INSERT INTO {table_name_total} ({columns_total}) VALUES ({values_total});"
            sql_statements.append(insert_statement_total)

            # Build insert statement for goals_for_average table
            table_name_average = 'goals_for_average'
            columns_average = 'team_id, home, away, total'
            values_average = f"{team_id}, {goals_for_average['home']}, {goals_for_average['away']}, {goals_for_average['total']}"
            insert_statement_average = f"INSERT INTO {table_name_average} ({columns_average}) VALUES ({values_average});"
            sql_statements.append(insert_statement_average)

            # Build insert statements for goals_for_minute table
            table_name_minute = 'goals_for_minute'
            columns_minute = 'team_id, minute, total, percentage'
            for minute, data in goals_for_minute.items():
                values_minute = f"{team_id}, '{minute}', {data['total']}, '{data['percentage']}'"
                insert_statement_minute = f"INSERT INTO {table_name_minute} ({columns_minute}) VALUES ({values_minute});"
                insert_statement_minute = insert_statement_minute.replace("%","")
                insert_statement_minute = insert_statement_minute.replace("minute,","minute_range,")
                insert_statement_minute = insert_statement_minute.replace("None","0")
                sql_statements.append(insert_statement_minute)



            # Extract goals data and insert into the 'goals_against_total', 'goals_against_average', and 'goals_against_minute' tables
            # Build and execute SQL insert statements for goals_against_total', 'goals_against_average', and 'goals_against_minute' tables
            goals_against_total = value['against']['total']
            goals_against_average = value['against']['average']
            goals_against_minute = value['against']['minute']

            # Build insert statement for goals_against_total table
            table_name_total = 'goals_against_total'
            columns_total = 'team_id, home, away, total'
            values_total = f"{team_id}, {goals_against_total['home']}, {goals_against_total['away']}, {goals_against_total['total']}"
            insert_statement_total = f"INSERT INTO {table_name_total} ({columns_total}) VALUES ({values_total});"
            sql_statements.append(insert_statement_total)

            # Build insert statement for goals_against_average table
            table_name_average = 'goals_against_average'
            columns_average = 'team_id, home, away, total'
            values_average = f"{team_id}, {goals_against_average['home']}, {goals_against_average['away']}, {goals_against_average['total']}"
            insert_statement_average = f"INSERT INTO {table_name_average} ({columns_average}) VALUES ({values_average});"
            sql_statements.append(insert_statement_average)

            # Build insert statements for goals_against_minute table
            table_name_minute = 'goals_against_minute'
            columns_minute = 'team_id, minute, total, percentage'
            for minute, data in goals_against_minute.items():
                values_minute = f"{team_id}, '{minute}', {data['total']}, '{data['percentage']}'"
                insert_statement_minute = f"INSERT INTO {table_name_minute} ({columns_minute}) VALUES ({values_minute});"
                insert_statement_minute = insert_statement_minute.replace("%","")
                insert_statement_minute = insert_statement_minute.replace("minute,","minute_range,")
                insert_statement_minute = insert_statement_minute.replace("None","0")
                sql_statements.append(insert_statement_minute)
                

        elif key == 'biggest':
            # Extract biggest data and insert into the 'biggest_streak', 'biggest_wins', 'biggest_goals_for', and 'biggest_goals_against' tables
            biggest_streak = value['streak']
            biggest_wins = value['wins']
            biggest_goals_for = value['goals']['for']
            biggest_goals_against = value['goals']['against']
            biggest_streak = value['streak']
            biggest_wins = value['wins']
            biggest_goals_for = value['goals']['for']
            biggest_goals_against = value['goals']['against']

            # Build insert statement for biggest_streak table
            table_name_streak = 'biggest_streak'
            columns_streak = 'team_id, wins, draws, losses'
            values_streak = f"{team_id}, {biggest_streak['wins']}, {biggest_streak['draws']}, {biggest_streak['loses']}"
            insert_statement_streak = f"INSERT INTO {table_name_streak} ({columns_streak}) VALUES ({values_streak});"
            sql_statements.append(insert_statement_streak)

            # Build insert statement for biggest_wins table
            table_name_wins = 'biggest_wins'
            columns_wins = 'team_id, home, away'
            values_wins = f"{team_id}, '{biggest_wins['home']}', '{biggest_wins['away']}'"
            insert_statement_wins = f"INSERT INTO {table_name_wins} ({columns_wins}) VALUES ({values_wins});"
            sql_statements.append(insert_statement_wins)

            # Build insert statement for biggest_goals_for table
            table_name_goals_for = 'biggest_goals_for'
            columns_goals_for = 'team_id, home, away'
            values_goals_for = f"{team_id}, {biggest_goals_for['home']}, {biggest_goals_for['away']}"
            insert_statement_goals_for = f"INSERT INTO {table_name_goals_for} ({columns_goals_for}) VALUES ({values_goals_for});"
            sql_statements.append(insert_statement_goals_for)

            # Build insert statement for biggest_goals_against table
            table_name_goals_against = 'biggest_goals_against'
            columns_goals_against = 'team_id, home, away'
            values_goals_against = f"{team_id}, {biggest_goals_against['home']}, {biggest_goals_against['away']}"
            insert_statement_goals_against = f"INSERT INTO {table_name_goals_against} ({columns_goals_against}) VALUES ({values_goals_against});"
            sql_statements.append(insert_statement_goals_against)


        elif key == 'clean_sheet':
            table_name_clean_sheet = 'clean_sheet'
            columns_clean_sheet = 'team_id, home, away, total'
            values_clean_sheet = f"{team_id}, {value['home']}, {value['away']}, {value['total']}"
            insert_statement_clean_sheet = f"INSERT INTO {table_name_clean_sheet} ({columns_clean_sheet}) VALUES ({values_clean_sheet});"
            sql_statements.append(insert_statement_clean_sheet)



        elif key == 'failed_to_score':
            # Build insert statement for failed_to_score table
            table_name_failed_to_score = 'failed_to_score'
            columns_failed_to_score = 'team_id, home, away, total'
            values_failed_to_score = f"{team_id}, {value['home']}, {value['away']}, {value['total']}"
            insert_statement_failed_to_score = f"INSERT INTO {table_name_failed_to_score} ({columns_failed_to_score}) VALUES ({values_failed_to_score});"
            sql_statements.append(insert_statement_failed_to_score)



        elif key == 'penalty':
            # Extract penalty data and insert into the 'penalties' table
            table_name_penalties = 'penalties'
            columns_penalties = 'team_id, scored_total, missed_total, total'
            values_penalties = f"{team_id}, {value['scored']['total']}, {value['missed']['total']}, {value['total']}"
            insert_statement_penalties = f"INSERT INTO {table_name_penalties} ({columns_penalties}) VALUES ({values_penalties});"
            sql_statements.append(insert_statement_penalties)



        elif key == 'lineups':
            # Extract lineup data and insert into the 'lineups' table
            lineups = value

            # Build insert statements for lineups table
            table_name = 'lineups'
            columns = 'team_id, formation, played'
            values_list = []

            for lineup in lineups:
                formation = lineup['formation']
                played = lineup['played']
                values = f"{team_id}, '{formation}', {played}"
                #values_list.append(values)

            insert_statements = []
            for values in values_list:
                insert_statement = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
                insert_statements.append(insert_statement)

            for statement in insert_statements:
                sql_statements.append(statement)


        elif key == 'cards':
            # Extract card data and insert into the 'cards_yellow' and 'cards_red' tables
            cards_red = value['yellow']

            # Build insert statements for cards_red table
            table_name = 'cards_yellow'
            columns = 'team_id, minute, total, percentage'
            values_list = []

            for minute, data in cards_red.items():
                total = data['total']
                percentage = data['percentage']
                values = f"{team_id}, '{minute}', {total}, '{percentage}'"
                values_list.append(values)

            insert_statements = []
            for values in values_list:
                insert_statement = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
                insert_statement = insert_statement.replace("%", "")
                insert_statement = insert_statement.replace("minute,","minute_range,")
                insert_statement = insert_statement.replace("None","0")
                insert_statements.append(insert_statement)

        
            for statement in insert_statements:
                sql_statements.append(statement)
            
            
            
            cards_red = value['red']

            # Build insert statements for cards_red table
            table_name = 'cards_red'
            columns = 'team_id, minute, total, percentage'
            values_list = []

            for minute, data in cards_red.items():
                total = data['total']
                percentage = data['percentage']
                values = f"{team_id}, '{minute}', {total}, '{percentage}'"
                values_list.append(values)

            insert_statements = []
            for values in values_list:
                insert_statement = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
                insert_statement = insert_statement.replace("%", "")
                insert_statement = insert_statement.replace("minute,","minute_range,")
                insert_statement = insert_statement.replace("None","0")
                insert_statements.append(insert_statement)

            # Print insert statements
            for statement in insert_statements:
                sql_statements.append(statement)

    execute_sql_statements(sql_statements)


    # Commit the database changes

#haetaan pelaajat joukkueen perusteella 
def api_hae_pelaajat():
        sql_statements = []
        joukkueet = []# alku 42, 66, 35, 55, 51, 44, 49, 52, 45, 36, 40, 1359, 50 33, 34, 65, 62, 47, 48, 15433
        for x in joukkueet:
            haku = "/players/squads?team="+str(x)
            conn.request("GET",haku,headers=headers)
            res = conn.getresponse()
            data = res.read()
            my_json = data.decode('utf8').replace('"', '"')
            my_dict = json.loads(data)
            my_dict = my_dict["response"]
            id = str(x)
            time.sleep(5)
            for team_info in my_dict:
                team_name = team_info['team']['name']
                players = team_info['players']
                for player in players:
                    player_id = player['id']
                    player_name = player['name']
                    player_age = player['age']
                    player_number = player['number']
                    if player_number is None:
                        player_number = 00
                    player_position = player['position']
                    player_photo = player['photo']
                    insert_statement = "INSERT INTO players (player_id, team_id, name, age, number, position, photo) VALUES ({}, {}, '{}', {}, {}, '{}', '{}');".format(player_id, id, player_name, player_age, player_number, player_position, player_photo)
                    sql_statements.append(insert_statement)
        execute_sql_statements(sql_statements)
    
#haetaan kilpailussa pelatut tai tulevat ottelut ja tehdään sql lauseet
def kilpailussa_pelatut_ottelut():
    sql_statements = []
    # Specify the competition ID for the Premier League
    competition_id = 39  # Update with the correct competition ID
    
    # Make the API request to fetch the past matches
    endpoint = f"/fixtures?league={competition_id}&season=2020"
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()
    data = res.read()
    
    # Parse the JSON response
    matches_data = json.loads(data.decode('utf-8'))
    
    # Extract the relevant information from the response
    if "response" in matches_data:
        match_data = matches_data["response"]
        for match in match_data:    
            match_id = match["fixture"]["id"]
            date = match["fixture"]["date"]
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            home_team_id = match["teams"]["home"]["id"]
            away_team_id = match["teams"]["away"]["id"]
            home_score = match["goals"]["home"]
            away_score = match["goals"]["away"]
            #Data sisältää joukkueita viime kaudelta jotka eivät ole enää valioliigassa siitä tulee virhe
            insert_statement = "INSERT IGNORE INTO `played_games` (match_id, date, home_team_id, away_team_id, home_score, away_score) VALUES ({}, '{}', {}, {}, {}, {});".format(match_id, date, home_team_id, away_team_id, home_score, away_score)
            #insert_player_statement = insert_player_statement.replace("None","NULL")
            sql_statements.append(insert_statement)
    else:
        return None
    execute_sql_statements(sql_statements)

#Haetaan pelaajan laaja statistiikkaa ja luodaan siitä sql lauseet, jotka suoritetaan
def pelaaja_data(id):
        haku = "/players?id="+str(id)+"&season=2022"
        conn.request("GET",haku,headers=headers)
        res = conn.getresponse()
        data = res.read()
        my_json = data.decode('utf8').replace('"', '"')
        my_dict = json.loads(data)
        my_dict = my_dict["response"]
        
        player_data = my_dict
        sql_statements = []

        for player in player_data:
            player_id = player["player"]["id"]
            player_info = player["player"]
            statistics = player["statistics"]

            # Generate INSERT statement for player information
            insert_player_statement = f"INSERT INTO players (player_id, name, firstname, lastname, age, birthdate, place_of_birth, nationality, height, weight, injured, photo) VALUES ({player_info['id']}, '{player_info['name']}', '{player_info['firstname']}', '{player_info['lastname']}', {player_info['age']}, '{player_info['birth']['date']}', '{player_info['birth']['place']}', '{player_info['nationality']}', '{player_info['height']}', '{player_info['weight']}', {player_info['injured']}, '{player_info['photo']}');"
            insert_player_statement = insert_player_statement.replace("None","NULL")
            #sql_statements.append(insert_player_statement)

            # Generate INSERT statement for player statistics
            for statistic in statistics:
                team_id = statistic["team"]["id"]
                league_id = statistic["league"]["id"]
                season = statistic["league"]["season"]
                appearances = statistic["games"]["appearences"]
                lineups = statistic["games"]["lineups"]
                minutes = statistic["games"]["minutes"]
                number = statistic["games"]["number"]
                position = statistic["games"]["position"]
                rating = statistic["games"]["rating"]
                captain = int(statistic["games"]["captain"])
                total_shots = statistic["shots"]["total"]
                shots_on_target = statistic["shots"]["on"]
                goals = statistic["goals"]["total"]
                assists = statistic["goals"]["assists"]
                passes_total = statistic["passes"]["total"]
                passes_key = statistic["passes"]["key"]
                passes_accuracy = statistic["passes"]["accuracy"]
                tackles_total = statistic["tackles"]["total"]
                tackles_blocks = statistic["tackles"]["blocks"]
                tackles_interceptions = statistic["tackles"]["interceptions"]
                dribbles_attempts = statistic["dribbles"]["attempts"]
                dribbles_success = statistic["dribbles"]["success"]
                fouls_drawn = statistic["fouls"]["drawn"]
                fouls_committed = statistic["fouls"]["committed"]
                yellow_cards = statistic["cards"]["yellow"]
                yellowred_cards = statistic["cards"]["yellowred"]
                red_cards = statistic["cards"]["red"]
                penalties_won = statistic["penalty"]["won"]
                penalties_scored = statistic["penalty"]["scored"]
                penalties_missed = statistic["penalty"]["missed"]

                insert_statistic_statement = f"INSERT INTO player_statistics (player_id, team_id, league_id, season, appearances, lineups, minutes, number, position, rating, captain, total_shots, shots_on_target, goals, assists, passes_total, passes_key, passes_accuracy, tackles_total, tackles_blocks, tackles_interceptions, dribbles_attempts, dribbles_success, fouls_drawn, fouls_committed, yellow_cards, yellowred_cards, red_cards, penalties_won, penalties_scored, penalties_missed) VALUES ({player_id}, {team_id}, {league_id}, {season}, {appearances}, {lineups}, {minutes}, {number}, '{position}', {rating}, {captain}, {total_shots}, {shots_on_target}, {goals}, {assists}, {passes_total}, {passes_key}, {passes_accuracy}, {tackles_total}, {tackles_blocks}, {tackles_interceptions}, {dribbles_attempts}, {dribbles_success}, {fouls_drawn}, {fouls_committed}, {yellow_cards}, {yellowred_cards}, {red_cards}, {penalties_won}, {penalties_scored}, {penalties_missed});"
                insert_statistic_statement = insert_statistic_statement.replace("None","NULL")
                sql_statements.append(insert_statistic_statement)
        execute_sql_statements(sql_statements)

#Haetaan joukkueen perusteella tallennettujen pelaajien id (laajaa statistiikka varten)
def pelaaja_id():
    # Connect to the database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="Valioliiga_Data"
    )

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    try:
        # Execute the SQL query to retrieve player IDs
        query = "SELECT player_id FROM players WHERE player_id >= 20"
        cursor.execute(query)

        # Fetch all the results
        results = cursor.fetchall()

        # Extract player IDs from the results
        player_ids = [result[0] for result in results]

        for x in player_ids:
            pelaaja_data(x)

    except mysql.connector.Error as error:
        print("Error retrieving player IDs:", error)

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

#Toteutetaan "yksinkertaisia sql lauseita"
def execute_sql_statements(sql_statements):
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Valioliiga_Data"
        )

        # Create a cursor
        cursor = connection.cursor()

        # Execute each SQL statement
        for statement in sql_statements:
            cursor.execute(statement)

        # Commit the changes
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        print("SQL statements executed successfully.")

    except mysql.connector.Error as error:
        print(f"Error executing SQL statements: {error}")

#Haetaan pelattujen otteluiden id:t
def ottelu_id():
    # Connect to the database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="Valioliiga_Data"
    )

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    try:
        # Execute the SQL query to retrieve match_id's IDs
        query = "SELECT match_id FROM played_games WHERE match_id NOT IN (SELECT match_id FROM predictions); "
        cursor.execute(query)

        # Fetch all the results
        results = cursor.fetchall()

        # Extract player IDs from the results
        ottelu_ids = [result[0] for result in results]
        ottelu_ids = list(set(ottelu_ids))
        i = 0
        for x in ottelu_ids:
            #tähän voi laittaa kertoimet funktionkin
            ennustus_data(x)
            print(i)
            i += 1
            if i == 24:
                break

    except mysql.connector.Error as error:
        print("Error retrieving match_id IDs:", error)

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

#Haetaan pelattujen otteluiden perusteella ennusteita
def ennustus_data(id):
        haku = "/predictions?fixture="+str(id)
        conn.request("GET",haku,headers=headers)
        res = conn.getresponse()
        data = res.read()
        my_json = data.decode('utf8').replace('"', '"')
        my_dict = json.loads(data)
        time.sleep(5)
        if "response" in my_dict and len(my_dict["response"]) > 0:
            my_dict = my_dict["response"][0]
            print("Pelin ID:", id)
            #print(my_dict)
            ennustus_sql(my_dict, id)

        else:
            print("The 'response' list is empty.")

#tehdään ennusteista sql lauseita ja toteutetaan ne
def ennustus_sql(data, id):
    statements = []
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="Valioliiga_Data"
    )

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    try:
        insert_statement = "INSERT INTO predictions (match_id, winner_id, win_or_draw, under_over, home_goals, away_goals, advice, home_percent, draw_percent, away_percent) VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {});".format(
            id,
            data['predictions']['winner']['id'], 
            data['predictions']['win_or_draw'], 
            data['predictions']['under_over'], 
            data['predictions']['goals']['home'], 
            data['predictions']['goals']['away'], 
            "'"+data['predictions']['advice']+"'",
            "'"+data['predictions']['percent']['home']+"'",
            "'"+data['predictions']['percent']['draw']+"'",
            "'"+data['predictions']['percent']['away']+"'"
        )
        insert_statement = insert_statement.replace('None', 'NULL')
        insert_statement = insert_statement.replace(':', '')
        statements.append(insert_statement)
        execute_sql_statements(statements)
        statements.clear()

        # Execute the SQL query to retrieve player IDs
        query = "SELECT prediction_id FROM predictions ORDER BY prediction_id DESC LIMIT 1;"
        cursor.execute(query)

        # Fetch all the results
        prediction_id = cursor.fetchall()
        p_id = prediction_id[0][0]
        insert_statement = " INSERT INTO last_five_home (last_five_home_id, prediction_id, form, att, def, goals_for_total, goals_for_average, goals_against_total, goals_against_average) VALUES ({},{},{},{},{},{},{},{},{});".format(
            data['teams']['home']['id'],
            p_id,
            "'"+data['teams']['home']['last_5']['form']+"'",
            "'"+data['teams']['home']['last_5']['att']+"'",
            "'"+data['teams']['home']['last_5']['def']+"'",
            data['teams']['home']['last_5']['goals']['for']['total'], 
            data['teams']['home']['last_5']['goals']['for']['average'], 
            data['teams']['home']['last_5']['goals']['against']['total'], 
            data['teams']['home']['last_5']['goals']['against']['average']
        )
        insert_statement = insert_statement.replace('None', 'NULL')
        statements.append(insert_statement)
        insert_statement = " INSERT INTO last_five_away (last_five_away_id, prediction_id, form, att, def, goals_for_total, goals_for_average, goals_against_total, goals_against_average) VALUES ({},{},{},{},{},{},{},{},{});".format(
            data['teams']['away']['id'],
            p_id,
            "'"+data['teams']['away']['last_5']['form']+"'",
            "'"+data['teams']['away']['last_5']['att']+"'", 
            "'"+data['teams']['away']['last_5']['def']+"'", 
            data['teams']['away']['last_5']['goals']['for']['total'], 
            data['teams']['away']['last_5']['goals']['for']['average'], 
            data['teams']['away']['last_5']['goals']['against']['total'], 
            data['teams']['away']['last_5']['goals']['against']['average']
        )
        insert_statement = insert_statement.replace('None', 'NULL')
        statements.append(insert_statement)
        insert_statement = "INSERT INTO comparison (prediction_id, home_form, away_form, home_att, away_att, home_def, away_def, home_poisson_distribution, away_poisson_distribution, home_h2h, away_h2h, home_goals, away_goals, home_total, away_total) VALUES ({},{},{},{},{},{},{},{},{},{},{},{},{},{},{});".format(
            p_id,
            "'"+data['comparison']['form']['home']+"'", 
            "'"+data['comparison']['form']['away']+"'", 
            "'"+data['comparison']['att']['home']+"'", 
            "'"+data['comparison']['att']['away']+"'", 
            "'"+data['comparison']['def']['home']+"'", 
            "'"+data['comparison']['def']['away']+"'", 
            "'"+data['comparison']['poisson_distribution']['home']+"'", 
            "'"+data['comparison']['poisson_distribution']['away']+"'", 
            "'"+data['comparison']['h2h']['home']+"'", 
            "'"+data['comparison']['h2h']['away']+"'", 
            "'"+data['comparison']['goals']['home']+"'", 
            "'"+data['comparison']['goals']['away']+"'", 
            "'"+data['comparison']['total']['home']+"'", 
            "'"+data['comparison']['total']['away']+"'"
        )

        insert_statement = insert_statement.replace('None', 'NULL')
        statements.append(insert_statement)
        execute_sql_statements(statements)

    except mysql.connector.Error as error:
        print("Error in comparisons:", error)

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

#Tulostusfunktioita joita ei luultavasti enää tarvita
def tulostus_functioita():

    def print_player_data(player_data):
        player_info = player_data[0]['player']
        player_stats = player_data[0]['statistics']

        # Print player information
        print("Player Information:")
        print("ID:", player_info['id'])
        print("Name:", player_info['name'])
        print("First Name:", player_info['firstname'])
        print("Last Name:", player_info['lastname'])
        print("Age:", player_info['age'])
        print("Birth Date:", player_info['birth']['date'])
        print("Birth Place:", player_info['birth']['place'])
        print("Country:", player_info['birth']['country'])
        print("Nationality:", player_info['nationality'])
        print("Height:", player_info['height'])
        print("Weight:", player_info['weight'])
        print("Injured:", player_info['injured'])
        print("Photo:", player_info['photo'])

        print("\nPlayer Statistics:")
        for stats in player_stats:
            print("\nTeam:", stats['team']['name'])
            print("League:", stats['league']['name'])
            print("Country:", stats['league']['country'])
            print("Season:", stats['league']['season'])
            print("Position:", stats['games']['position'])
            print("Appearances:", stats['games']['appearences'])
            print("Lineups:", stats['games']['lineups'])
            print("Minutes:", stats['games']['minutes'])
            print("Number:", stats['games']['number'])
            print("Rating:", stats['games']['rating'])
            print("Captain:", stats['games']['captain'])
            print("Shots Total:", stats['shots']['total'])
            print("Shots On:", stats['shots']['on'])
            print("Goals Total:", stats['goals']['total'])
            print("Goals Conceded:", stats['goals']['conceded'])
            print("Assists:", stats['goals']['assists'])
            print("Saves:", stats['goals']['saves'])
            print("Passes Total:", stats['passes']['total'])
            print("Passes Key:", stats['passes']['key'])
            print("Passes Accuracy:", stats['passes']['accuracy'])
            print("Tackles Total:", stats['tackles']['total'])
            print("Tackles Blocks:", stats['tackles']['blocks'])
            print("Interceptions:", stats['tackles']['interceptions'])
            print("Duels Total:", stats['duels']['total'])
            print("Duels Won:", stats['duels']['won'])
            print("Dribbles Attempts:", stats['dribbles']['attempts'])
            print("Dribbles Success:", stats['dribbles']['success'])
            print("Fouls Drawn:", stats['fouls']['drawn'])
            print("Fouls Committed:", stats['fouls']['committed'])
            print("Yellow Cards:", stats['cards']['yellow'])
            print("Yellow-Red Cards:", stats['cards']['yellowred'])
            print("Red Cards:", stats['cards']['red'])
            print("Penalty Won:", stats['penalty']['won'])
            print("Penalty Committed:", stats['penalty']['commited'])
            print("Penalty Scored:", stats['penalty']['scored'])
            print("Penalty Missed:", stats['penalty']['missed'])
            print("Penalty Saved:", stats['penalty']['saved'])

    def print_data(data):
        def print_recursive(data, indent=""):
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"{indent}{key}:")
                    print_recursive(value, indent + "  ")
                else:
                    print(f"{indent}{key}")

    
        print_recursive(data)

    def print_h2h_data(data):
        for item in data:
            print("---------")
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, dict):
                        print(f"{key}:")
                        for nested_key, nested_value in value.items():
                            print(f"\t{nested_key}: {nested_value}")
                    else:
                        print(f"{key}: {value}")

#Tämä on nyt sellainen että se hakee kaikkien matsien ennustukset kun sen ajaa-->
#ottelu_id()

#Tässä tarvitaan ottelun_id
def kertoimet(pelin_id):

    conn.request("GET", "/odds?season=2022&bet=1&bookmaker=1&fixture="+str(pelin_id)+"&league=39", headers=headers)

    res = conn.getresponse()
    data = res.read()

    my_json = data.decode('utf8').replace('"', '"')
    my_dict = json.loads(data)

    if "response" in my_dict and len(my_dict["response"]) > 0:
        my_dict = my_dict["response"][0]
        print("Pelin ID:", id)
        #tähän tarvitaan metodi joka tekee jotain kertoimet sisätävälle "sanakirjalle"
        print(my_dict)
    else:
        print("The 'response' list is empty.")

# tällä voisi hakea tulevia pelejä kertoimia varten kilpailussa_pelatut_ottelut()
ottelu_id()
#ennustus_data(867948)