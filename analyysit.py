import mysql.connector
import pandas as pd
import random
from collections import Counter
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.cluster import DBSCAN
from scipy.stats import chi2
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

right = []
wrong = []
draw = []
wrong_not_draw = []
all = []
home_win = []
away_win = []


# Yhdistetään tietokantaan
def get_connection():
    # Connect to the database
    conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="jalkapallo"
        )

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    return conn, cursor

#Haetaan tietokannasta tiedot
def get_data():

    conn, cursor = get_connection()

    try:
        query = "SELECT played_games.match_id, played_games.date, played_games.home_team_id, played_games.away_team_id, played_games.home_score, played_games.away_score FROM predictions INNER JOIN played_games ON predictions.match_id = played_games.match_id;"
        cursor.execute(query)

        ottelu_id = cursor.fetchall()

    except mysql.connector.Error as error:
        print("Error retrieving match_id IDs:", error)

    finally:
        ennuste_id = []
        try:
            for x in ottelu_id:
                # Haetaan matsi_id:n perusteella ennusteet
                query = "SELECT * FROM predictions WHERE match_id = "+str(x[0])+";"
                cursor.execute(query)

                
                results = cursor.fetchall()
                if len(results) == 1:
                    for y in results:
                        ennuste_id.append(y)
                        #print(y)
                elif len(results) == 2:
                        ennuste_id.append(results[0])
                else:
                    pass
                        
        except mysql.connector.Error as error:
                    print("Error retrieving match_id IDs:", error)

        finally:
            vertailu_id = []
            try:
                    for x in ennuste_id:
                        # Haetaan ennuste_id:n perusteella vertailut
                        query = "SELECT * FROM comparison WHERE prediction_id = "+str(x[0])+";"
                        cursor.execute(query)

                        results = cursor.fetchall()
                        for y in results:
                            vertailu_id.append(y)

            except mysql.connector.Error as error:
                        print("Error retrieving match_id IDs:", error)

            finally:
                        cursor.close()
                        conn.close()
            
            #Käsitellään ja lajitellaan tulokset
            n = 0
            temp = []
            while n < len(ottelu_id):
                temp.append(oikeat_arvaukset(kirjasto(column_names("played_games"), ottelu_id[n]), kirjasto(column_names("predictions"), ennuste_id[n]), kirjasto(column_names("comparison"),vertailu_id[n]), n))
                n += 1
            
            print("Oikeiden ennusteiden todennäköisyys:",round(temp.count(1)/len(temp), 2))
            print("Oikein 'arvattuja' kohteita oli:",len(right))
            print("Väärin 'arvattuja' kohteita oli:",len(wrong))

            #tasapelit
            for x in wrong:
                if x[0]["home_score"] == x[0]["away_score"]:
                    draw.append(x)

            #tappiot jotka ei ole tasapelejä
            for x in wrong:
                testi = 0  
                for y in draw:
                    if x == y:
                        testi = 1
                        break  

                if testi == 0:
                    wrong_not_draw.append(x)
                
            for x in all:
                if x[0]["home_score"] > x[0]["away_score"]:
                    home_win.append(x)
                elif x[0]["home_score"] < x[0]["away_score"]:
                    away_win.append(x)

            print("Kotivoittojen määrä:", len(home_win))
            print("Vierasvoittojen määrä:", len(away_win))
            print("Tasureiden määrä:", len(draw))
            print("Tasureiden osuus vääristä:", round(len(draw)/len(wrong), 2))

#Muutetaan tietotyyppiä
def percent_to_float(group_data):
    for data_point in group_data:
        for key in data_point:
            if '%' in str(data_point[key]):
                data_point[key] = float(data_point[key].replace('%', '')) / 100.0
    return group_data

def column_names(taulu):
    conn, cursor = get_connection()
    table_name = taulu
    query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}';"

    cursor.execute(query)

    column_names = [column[0] for column in cursor.fetchall()]
    return column_names

def kirjasto(keys, values):
      result_dict = dict(zip(keys, values))
      return result_dict

def oikeat_arvaukset(pelit, ennusteet, vertailu, n):
    koti = pelit["home_team_id"]
    vieras = pelit["away_team_id"]
    koti_tulos = pelit["home_score"]
    vieras_tulos = pelit["away_score"]
    voittaja = ennusteet["winner_id"]
    koti_ennuste = int(ennusteet["home_percent"].replace('%', ''))
    vieras_ennuste = int(ennusteet["away_percent"].replace('%', ''))
    tasa_ennuste = int(ennusteet["draw_percent"].replace('%', ''))
    all.append([pelit, ennusteet, vertailu])
    if koti_tulos > vieras_tulos and voittaja == koti:
        temp = [pelit, ennusteet, vertailu]
        right.append(temp)
        return 1
    elif koti_tulos < vieras_tulos and voittaja == vieras:
        temp = [pelit, ennusteet, vertailu]
        right.append(temp)
        return 1
    else:
        temp = [pelit, ennusteet, vertailu]
        wrong.append(temp)
        return 0 

#Käsitellään data poikkeuksien etsintää varten  
def get_outliers():

    data_list = all

    for sublist in data_list:
        for item in sublist:
            for key, value in item.items():
                if isinstance(value, str):
                    #Tehdään tämä vielä varmuuden vuoksi
                    if '%' in value:
                        percent = value.replace('%', '')
                        try:
                            item[key] = float(percent) / 100
                        except ValueError:
                            print(f"Could not convert {value} to a float.")
                    #Erotellaan kirjaimet ja numerot
                    elif '-' in value and ' ' in value:  #Varmistetaan että tämä ei ole päivämäärä
                        num_parts = [s for s in value.split() if s.lstrip('-').replace('.', '').isdigit()]
                        if num_parts:  #Jos numeroita löytyy
                            try:
                                item[key] = float(num_parts[0])  #Muutetaan
                            except ValueError:
                                print(f"Could not convert {num_parts[0]} to a float.")
                #Korvataan None arvot
                elif value is None:
                    item[key] = 'NaN'

    matches = []
    predictions = []
    comparisons = []

    #Käsitellään dataa
    for game in data_list:
        match, prediction, comparison = game
        
    
        matches.append(match)
        predictions.append(prediction)
        comparisons.append(comparison)

    matches_df = pd.DataFrame(matches)
    predictions_df = pd.DataFrame(predictions)
    comparisons_df = pd.DataFrame(comparisons)
    
    # Merge all DataFrames into one on the 'match_id' field
    df = pd.merge(matches_df, predictions_df, on='match_id')
    df = pd.merge(df, comparisons_df, on='prediction_id')
    for column in df.columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    avaimet = []
    i = 0
    while i < len(data_list[0]):
         
         for x in data_list[0][i].keys():
            avaimet.append(x)

         i += 1
    outliers = []
    temp = list(set(avaimet))
    for x in temp:
        teksti = str(x)
        try:
            outliers.append(detect_outliers(df, teksti))
        except Exception as e:
            print(f"An error occurred with key {x}: {str(e)}")
            continue
    
    for x in outliers:
        if not x[1].empty:
            print(x[0])
            print_selected_columns(x[0], x[1])

#Koneoppimismalli joka etsiin poikkeuksia
def detect_outliers(df, column):


    # Calculate the IQR of the column
    Q1 = df[column].quantile(0.20)
    Q3 = df[column].quantile(0.80)
    IQR = Q3 - Q1

    # Define the upper and lower bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Identify the outliers
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    temp = [column, outliers]
    
    return temp

#Tulostetaan mahdolliset poikkeukset 
def print_selected_columns(poikkeus, df):
    if poikkeus == 0:
        selected_columns = df[['match_id', 'home_score', 'away_score', 'winner_id', 'home_percent', 'draw_percent', 'away_percent', 'home_form', 'away_form', 'home_att', 'away_att', 'home_def', 'away_def', 'home_poisson_distribution', 'away_poisson_distribution', 'home_h2h', 'away_h2h']]
        print(selected_columns)
    else:
         selected_columns = df[['match_id', 'home_team_id', 'away_team_id', 'home_score', 'away_score', 'winner_id', str(poikkeus)]]
         print(selected_columns)

#Valmistellaan data toista koneoppimismallia varten
def process_and_prepare_data(data_list, selected_features):
    processed_data = []
    #selected_features = ['home_form', 'away_form', 'home_h2h', 'away_h2h']

    for data in data_list:
        comparison_data = data[2]  # The comparison data dictionary is in the third position
        match_data = data[0]  # The match data dictionary is in the first position
        
        # Select the desired features
        feature_data = {feature: comparison_data.get(feature) for feature in selected_features}
        
        # Add team ids from the match_data
        feature_data['home_team_id'] = match_data.get('home_team_id')
        feature_data['away_team_id'] = match_data.get('away_team_id')
        
        # Determine the result of the match
        winner_id = data[1].get('winner_id')
        if winner_id == feature_data['home_team_id']:
            feature_data['result'] = 'home_win'
        elif winner_id == feature_data['away_team_id']:
            feature_data['result'] = 'away_win'
        else:
            feature_data['result'] = 'draw'
        
        processed_data.append(feature_data)

    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(processed_data)

    # Convert the percentage strings into floating point numbers and handle missing values
    for column in selected_features:
        df[column] = df[column].str.rstrip('%').astype('float') / 100.0

    # Fill NaN values with 0
    df.fillna(0, inplace=True)

    return df

#Valmistellaan dataa koneoppimismallia varten joka ottaa muuttujana oppimimateriaalin ja kohteen jota ennuste koskee
def before_predict_one(lst):
    for data_dict in lst:
        for key, value in data_dict.items():
            if value is None or (isinstance(value, float) and np.isnan(value)): #Varmistellaan
                data_dict[key] = 0.0 
            elif isinstance(value, str) and '%' in value:
                data_dict[key] = float(value.strip('%')) / 100
    return lst

#Has description inside
def predict_winners(df, feature_columns, target_column):
    """
    Function to train a model and predict the winners

    Parameters:
    df (pd.DataFrame): DataFrame with the match data
    feature_columns (list): list of columns to be used as features
    target_column (str): column to be predicted

    Returns:
    predictions (list): list with the predicted values
    """
    # Split the dataset into a training set and a test set
    X_train, X_test, y_train, y_test = train_test_split(df[feature_columns], df[target_column], test_size=0.25, random_state=42)

    # Initialize the classifier
    clf = RandomForestClassifier(n_estimators=100)

    # Fit the classifier
    clf.fit(X_train, y_train)

    # Use the trained classifier to make predictions on the test set
    predictions = clf.predict(X_test)

    # Get the accuracy of the model
    accuracy = accuracy_score(y_test, predictions)
    print("Accuracy: ", accuracy)

    return predictions, accuracy

#Käytetään koneoppimismallin opetukseen kun yritetään päätellä yhden kohteen tulosta
def train_model(training_data, features, target):
    #Mitä tutkitaan
    X_train = training_data[features]
    #Mitä yritetään päätellä
    y_train = training_data[target]

    model = RandomForestClassifier(n_estimators=100)

    model.fit(X_train, y_train)

    return model

#Tässä yritetään päätellä yhtä tulosta mallin mukaan
def predict_one(model, data):
    #Treenataan oikeilla arvauksilla ja katsotaan kuinka hyvin tämä korjaa väärät vastaukset?
    training_set = right
    feature = ['home_form', 'away_form', 'home_att', 'away_att', 'home_def', 'away_def', 'home_poisson_distribution', 'away_poisson_distribution', 'home_h2h', 'away_h2h', 'home_goals', 'away_goals', 'home_total', 'away_total']
    target = 'result'

    new_data_point = {
    'home_form': data[2]['home_form'], 
    'away_form': data[2]['away_form'], 
    'home_h2h': data[2]['home_h2h'], 
    'away_h2h': data[2]['away_h2h'],
    
    'home_att': data[2]['home_att'],
    'away_att': data[2]['away_att'],
    'home_def': data[2]['home_def'],
    'away_def': data[2]['away_def'],
    'home_poisson_distribution': data[2]['home_poisson_distribution'],
    'away_poisson_distribution': data[2]['away_poisson_distribution'],
    'home_goals': data[2]['home_goals'],
    'away_goals': data[2]['away_goals'],
    'home_total': data[2]['home_total'],
    'away_total': data[2]['away_total']
                                        }

    new_data_df = pd.DataFrame([new_data_point])
    new_data_df = new_data_df.reindex(columns=feature)

    new_prediction = model.predict(new_data_df)
    return new_prediction[0]

#Muutetaan dataa    
def dict_to_list(d):
    #Palautetaan lista
    return list(d.values())

#Etsitään joukkojen samanlaisuutta
def classify_point(new_point, groups):
    #Jokaisen ryhmän keskivertovektorin etsintä
    means = {group_name: np.mean(np.array(group_data), axis=0) 
             for group_name, group_data in groups.items()}
    
    # Katsotaan kuinka kaukana uusi datapiste on keskivertovektoreista
    distances = {group_name: np.linalg.norm(new_point - mean) 
                 for group_name, mean in means.items()}
    
    #Palautetaan joukko joka on lähimpänä uutta datapistettä
    return min(distances, key=distances.get)

#Näyttää keskiverto datapisteen joukossa. Olen käyttänyt tässä oikein tai väärin menneitä ennusteita tai tasapelejä
def average_data_point(group):

    keys = group[0].keys()
    
    avg_point = {}
    for key in keys:
        avg_point[key] = sum(data_point[key] for data_point in group) / len(group)
    
    return avg_point

def get_classified_points():
    #Samanlaisuuden etsintään tarkoitetut joukot
    a = [{k: x[2][k] for k in list(x[2])[2:]} for x in right] #oikein menneet 
    b = [{k: x[2][k] for k in list(x[2])[2:]} for x in wrong_not_draw] #väärin menneet
    c =  [{k: x[2][k] for k in list(x[2])[2:]} for x in draw] #Tasapelit
    random.shuffle(c)

    a = a[37:]
    b = b[23:]

    a = percent_to_float(a)
    b = percent_to_float(b)
    c = percent_to_float(c)

    a_processed = [dict_to_list(point) for point in a]
    b_processed = [dict_to_list(point) for point in b]
    c_processed = [dict_to_list(point) for point in c]

    groups = {
        "Oikein": a_processed,
        "Väärin": b_processed
    }

    tulokset = []
    for x in c_processed:
        new_data_point = x
        #Katsotaan sopiiko tasapeli enemmän oikein vai väärin mennedein ennusteiden ryhmään
        group = classify_point(new_data_point, groups)
        if f"{group}" == "Väärin":
            tulokset.append(0)
        else:
            tulokset.append(1)


    count_ones = tulokset.count(1)
    count_zeros = tulokset.count(0)

    print(f"Oikein: {count_ones}")
    print(f"Väärin: {count_zeros}")

    avg_a = average_data_point(a)
    avg_b = average_data_point(b)
    avg_c = average_data_point(c) 

    print("Keskiverto arvaus joka on oikein näyttää tältä:", avg_a)
    print("Keskiverto arvaus joka on väärin (ei tasuri) näyttää tältä:", avg_b)
    print("Keskiverto arvaus joka tasuri näyttää tältä:", avg_c)

#main funktion "korvaaja"
def suorita():
    
    #Koneoppimismalli tarkkuus n.80% ongelmana on se että käytetty data ei ole "hyvää"
    features = ['home_form', 'away_form', 'home_att', 'away_att', 'home_def', 'away_def', 'home_poisson_distribution', 'away_poisson_distribution', 'home_h2h', 'away_h2h', 'home_goals', 'away_goals', 'home_total', 'away_total']
    target = 'result'
    df = process_and_prepare_data(right, features)
    predict_winners(df, features, target)
    #Tämä täytyy tarkistaa tähän voisi laittaa all joukosta osan ja ennustella loput.
    trained_model = train_model(process_and_prepare_data(right, features), features, target)
    results = []
    extracted_list = wrong
    x = 0
    while x < len(extracted_list):
        match = extracted_list[x][0]
        prediction = extracted_list[x][1]
        #print(f"Orginal prediction winner was: {prediction['winner_id']}")
        temp = (predict_one(trained_model, before_predict_one(extracted_list[x])))
        if temp == "home_win" and match['home_score'] > match['away_score']:
            results.append(1)
        elif temp == "away_win" and match['home_score'] < match['away_score']:
            results.append(1)
        else:
            results.append(0)
        x+= 1

    print("Oikein:",results.count(1))
    print("Väärin:",results.count(0))

    #Tässä voisi olla jotain?

    temp = []
    for x in right:
        x = percent_to_float(x)
        if x[1]['draw_percent'] >= 0.50:
            temp.append(1)
        else:
            temp.append(0)
    print("Tasurien tarkastelu")
    print("Oikein:",temp.count(1))
    print("Väärin:",temp.count(0))

get_data()
suorita()
#get_outliers()
#testi