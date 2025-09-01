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

def get_riders_positions_by_race(df, rider1, rider2, classe, session, year):
    """
    Restituisce un DataFrame con le posizioni dei due piloti per ogni gara
    in una categoria (class), sessione e anno specifici.
    """
    # Filtra per classe, sessione e anno
    races = df[
        (df['class'] == classe) &
        (df['session'] == session) &
        (df['year'] == year)
    ]
    
    # Filtra per i due piloti
    races = races[races['rider'].isin([rider1, rider2])]
    
    # Pivot per avere le posizioni dei piloti per ogni gara
    pivot = races.pivot_table(
        index=['event'], 
        columns='rider', 
        values='pos.', 
        aggfunc='first'
    )
    return pivot

def get_race_order():
    """
    Restituisce l'ordine ufficiale delle gare (2023-2026).
    Valido per tutte le classi MotoGP, Moto2, Moto3.
    """
    return [
        'THA',  # Thailand
        'ARG',  # Argentina
        'AME',  # Americas / USA
        'QAT',  # Qatar
        'SPA',  # Spain
        'FRA',  # France
        'GBR',  # United Kingdom
        'ARA',  # Aragon
        'ITA',  # Italy
        'NED',  # Netherlands
        'GER',  # Germany
        'CZE',  # Czechia
        'AUT',  # Austria
        'HUN',  # Hungary
        'CAT',  # Catalunya
        'RSM',  # San Marino
        'JPN',  # Japan
        'INA',  # Indonesia
        'AUS',  # Australia
        'MAL',  # Malaysia
        'POR',  # Portugal
        'VAL',  # Valencia
    ]


def get_dnf_riders(df, year, session, classe, event):
    """
    Restituisce una lista di tuple (rider, giro) per i piloti ritirati in una gara specifica
    Se nessun pilota si è ritirato , restituisce una lista vuota
    """

    gara = df[(df['year'] == year) & (df['session'] == session) & (df['class'] == classe) & (df['event'] == event)]

    ritiri = gara[gara['pos.'] == 'DNF']
    risultati = []
    for _, row in ritiri.iterrows():
        giro = None
        if pd.notnull(row['time / gap']):
            if 'laps' in str(row['time / gap']):
                try:
                    giro = int(str(row['time / gap']).split()[0])
                except:
                    giro = row['time / gap']
            else:
                giro = row['time / gap']
        risultati.append((row['rider'], giro))
    return risultati


def get_team_stats(df , classe = None, year = None):
    """
    Restitusice un DataFrame con punti, vittorie e podi per ogni team.
    Puoi filtrare per classe e per anno
    """
    data = df.copy()
    if classe:
        data = data[data['class'] == classe]
    if year:
        data = data[data['year'] == year]
    
    # Vittorie
    data['win'] = (data['pos.'] == '1').astype(int)

    data['podium'] = data['pos.'].isin(['1', '2', '3']).astype(int)
    stats = data.groupby('team').agg({
        'pts': 'sum',
        'win' : 'sum',
        'podium': 'sum'
    }).sort_values('pts' , ascending=False)
    stats = stats.rename(columns={'pts': 'Punti', 'win': 'Vittorie', 'podium': 'Podi'})
    return stats
