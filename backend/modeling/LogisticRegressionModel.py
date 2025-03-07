# -*- coding: utf-8 -*-
import pandas as pd 
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.preprocessing import StandardScaler


# read dataset

df = pd.read_csv('MVP_dataset.csv')

# MVPs vs nonMVPs EDA
stat_metrics = ['per', 'usagePercent', 'offensiveWs', 'defensiveWs', 'winShares', 'offensiveBox', 'defensiveWs', 'winShares', 'offensiveBox', 'defensiveBox', 'vorp', 'PPG_Score', 'APG_Score', 'RPG_Score', 'SPG_Score', 'BPG_Score', 'ranking', 'eFG%_Score']

df_mvp = df[df['MVP'] == 1]
df_non_mvp = df[df['MVP'] == 0]

for metric in stat_metrics:
    plt.figure(figsize=(8, 4))
    
    sns.histplot(df_non_mvp[metric], color='red', label='Non-MVPs', kde=True, alpha=0.5)
    sns.histplot(df_mvp[metric], color='blue', label='MVPs', kde=True, alpha=0.5)
    
    plt.title(f'Distribution of {metric} for MVPs vs. Non-MVPs')
    plt.xlabel(metric)
    plt.ylabel('Density')
    plt.legend()
    plt.show()

''' Findings about MVP for each of these statistics:
    PER > 16
    usagePercent > 17
    offensiveWs > 2.5
    defensiveWs was too widespread, no point
    winShares > 5
    offensiveBox > 2
    defensiveBox same thing too widespread
    winShares > 5
    offensiveBox > 2
    defensiveBox again doesnt matter
    vorp > 2.25
    per > 17.5
    PPG_Score > 0.5
    APG_Score > 0.3
    RPG_Score > 0.2
    SPG_Score doesnt matter
    BPG_Score doesnt matter
    ranking > 17
'''
# filter data by these values
df_filtered = df[
    (df['per'] > 17.5) &
    (df['usagePercent'] > 17) &
    (df['offensiveWs'] > 2.5) &
    (df['winShares'] > 5) &
    (df['offensiveBox'] > 2) &
    (df['vorp'] > 2.25) &
    (df['PPG_Score'] > 0.5) &
    (df['APG_Score'] > 0.3) &
    (df['RPG_Score'] > 0.2) &
    (df['ranking'] < 17)
].copy()

# ensure that we have 25 MVPs
mvp_count = df_filtered[df_filtered['MVP'] == 1]


# logistic regression to predict MVPs
# before filtering we want to keep names of players
df['original_index'] = df.index  # Store original index
# drop all irrelevant data
df_filtered = df_filtered.drop(columns = ['playerName', 'position_x', 'team', 'points', 'assists', 'totalRb', 'steals', 'blocks', 'season', 'position_y', 'games_y', 'PPG', 'APG', 'RPG', 'SPG', 'BPG', 'full_team_name', 'wins', 'effectFgPercent'])

# define the independent and dependent variable

Y = df_filtered['MVP'].values

X = df_filtered.drop(labels = ['MVP'], axis = 1)



# split data 
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size= 0.2, random_state= 20)

# scale the data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)
# Increase the impact of PPG_Score and PER by scaling them up
X_train_scaled['PPG_Score'] *= 2  # Double its influence
X_train_scaled['per'] *= 1.5  # Increase by 50%

X_test_scaled['PPG_Score'] *= 2
X_test_scaled['per'] *= 1.5

# define the model
custom_weights = {0: 1, 1: 5}  # Increase weight for MVPs
model = LogisticRegression(class_weight=custom_weights, max_iter=5000, random_state=42)


model.fit(X_train, Y_train)

# test the model
prediction_test = model.predict(X_test)

# verify the model accuracy
print("Accuracy = ", metrics.accuracy_score(Y_test, prediction_test))

# weights 

weights = pd.Series(model.coef_[0], index = X.columns.values)
print(weights)


# what did the model guess
# Reset index before splitting
df_filtered = df_filtered.reset_index(drop=True)

# Split train/test data
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=20, stratify=Y)

# Retrieve player names using df's original index
player_names = df.loc[X_test.index, 'playerName']

# Create a DataFrame with player names and predictions
'''
test_results_with_names = pd.DataFrame({
    'Player': player_names.values,  # Use .values to avoid index mismatch
    'Actual MVP': Y_test,
    'Predicted MVP': prediction_test
})


train_results_with_names = pd.DataFrame({
    'Player': player_names.values,  # Use .values to avoid index mismatch
    'Actual MVP': Y_train,
    'Predicted MVP': prediction_test
})
'''

    
    
