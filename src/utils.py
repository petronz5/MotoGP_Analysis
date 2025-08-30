import pandas as pd

def load_data(filepath):
    """
    Carica il dataset MotoGP da un file CSV
    Restituisce un DataFrame pandas
    """
    df = pd.read_csv(filepath)
    return df

def get_wins_and_podiums(df, rider_name):
    """
    Restituisce il numero di vittorie e podi di un pilota.
    Una vittoria è pos. == '1', un podio è pos. in ['1', '2', '3'].
    """
    # Filtra solo le gare (session == 'Race')
    races = df[df['session'] == 'Race']
    # Filtra per pilota
    rider_races = races[races['rider'] == rider_name]
    # Conta vittorie
    wins = (rider_races['pos.'] == '1').sum()
    # Conta podi
    podiums = rider_races[rider_races['pos.'].isin(['1', '2', '3'])].shape[0]
    return wins, podiums

def get_riders_positions_by_race(df, rider1, rider2, session, year):
    """
    Restituisce un dataFrame con le posizioni dei due piloti per ogni gara
    in una sessione e anno specifici
    """
    # Filtra per sessione e anno
    races = df[(df['session'] == session) & (df['year'] == year)]
    # Filtra per i due piloti
    races = races[races['rider'].isin([rider1, rider2])]
    # Pivot per avere le posizioni dei piloti per ogni gara
    pivot = races.pivot_table(index=['event'], columns='rider', values='pos.', aggfunc='first')
    return pivot