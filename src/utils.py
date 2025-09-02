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


def compute_cumulative_points(df, classe, year, top_n=6, race_order=None):
    """
    Ritorna un Dataframe con i punti cumulati per evento
    per i top_n piloti della classe e anno specificati.
    """
    data = df.copy()
    data.columns = data.columns.str.lower()
    if race_order is None:
        race_order = get_race_order()
    
    #filtro gare
    data = data[(data['class'] == classe) & (data['year'] == year) & (data['session'] == 'Race')]
    #pivot: event x rider con punti (somma)
    pts = data.pivot_table(index='event', columns='rider', values='pts', aggfunc='sum').fillna(0)
    #Ordina le righe secondo race_order (se presente)
    present_order = [e for e in race_order if e in pts.index]
    remaining = [e for e in pts.index if e not in present_order]
    ordered_index = present_order + remaining
    pts = pts.reindex(ordered_index).fillna(0)
    # cumulativo e selezione top_n sulla base del totale finale
    cum = pts.cumsum()
    if cum.shape[0] == 0:
        return cum
    final_totals = cum.iloc[-1].sort_values(ascending=False)
    top = final_totals.head(top_n).index.tolist()
    return cum[top]

def plot_championship_battle(cum_df, figsize=(10,6), palette='tab10'):
    """
    Disenga il grafico dei punti cumulati 
    Restituisce l'asse matplotlib per ulteriori personalizzazioni
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set(style='whitegrid')
    plt.figure(figsize=figsize)
    for col in cum_df.columns:
        plt.plot(cum_df.index, cum_df[col], marker='o', label=col)
    plt.xticks(rotation=45)
    plt.xlabel('Evento')
    plt.ylabel('Punti cumulati')
    plt.title('Championship battle - punti cumulati')
    plt.legend(title='Rider', bbox_to_anchor=(1.02,1), loc='upper left')
    plt.tight_layout()
    return plt.gca()
    
def get_dnfs_count_by_event(df, year=None, classe=None, session='Race'):
    """
    Restituisce un Dataframe con il conteggio dei DNF per evento
    Filtra opzionalmente per year, classe e session
    """
    data = df.copy()
    # Normalizza nomi colonne (gestissci input non normalizzato)
    data.columns = data.columns.str.lower()
    if year is not None:
        data = data[data['year'] == year]
    if classe is not None:
        data = data[data['class'] == classe]
    if session is not None:
        data = data[data['session'] == session]
    
    # Conta DNF per evento
    dnfs = data[data['pos.'] == 'DNF'].groupby('event').size().rename('dnf_count')
    if dnfs.empty:
        return dnfs.to_frame()
    # Ritorna ordinato deccrescente 
    return dnfs.sort_values(ascending=False).to_frame()

def plot_dnfs_bar(dnfs_df, figsize=(8,6), color='#c44e52'):
    """
    Disegna un barh con il conteggio DNF per evento
    Restitsuice l'asse matplotlib
    """
    import matplotlib.pyplot as plt
    if dnfs_df is None or dnfs_df.empty:
        print("Nessun DNF da plottare")
        return None
    df_plot = dnfs_df.copy()
    # ordina per plotting
    df_plot = df_plot.sort_values('dnf_count')
    plt.figure(figsize=figsize)
    ax = plt.gca()
    ax.barh(df_plot.index.astype(str), df_plot['dnf_count'], color=color)
    # annotazioni: etichette numeriche a fine barra
    for i, (idx, row) in enumerate(df_plot.iterrows()):
        ax.text(row['dnf_count'] + 0.05, i, int(row['dnf_count']), va='center')
    ax.set_xlabel('Numero di DNF')
    ax.set_ylabel('Evento (codice)')
    ax.set_title('DNF per evento')
    plt.tight_layout()
    return ax

def get_podium_matrix(df, year=None, classe=None, session = 'Race' , top_n = None, normalize = False):
    """
    Restituisce una matrice rider x event con il conteggio dei podi
    - year . se lista -> conta su tutti gli anni
    - classe: filtro su 'class'
    - session: default 'Race'
    - top_n: se formito limita ai top_n piloti ordinati per numero totale di podi
    - normalize: se True divide i conteggi per il numero di anni considerati
    """
    import pandas as pd
    data = df.copy()
    data.columns = data.columns.str.lower()

    # filtri
    if year is not None:
        if isinstance(year, (list, tuple, set)):
            data = data[data['year'].isin(list(year))]
            n_years = len(set(year))
        else:
            data = data[data['year'] == year]
            n_years = 1
    else:
        n_years = 1
    if classe is not None:
        data = data[data['class'] == classe]
    if session is not None:
        data = data[data['session'] == session]
    if data.empty:
        return pd.DataFrame()

    # flag podio
    data['podium_flag'] = data['pos.'].isin(['1', '2', '3']).astype(int)
    # pivot rider x event sommando i podi
    pivot = data.groupby(['rider', 'event'])['podium_flag'].sum().unstack(fill_value=0)
    # opzionale normalizzazione per numero di anni
    if normalize and n_years > 1:
        pivot = pivot / n_years
    # seleziona top_n piloti se richiesto
    if top_n is not None and pivot.shape[0] > top_n:
        totals = pivot.sum(axis=1)
        top_riders = totals.sort_values(ascending=False).head(top_n).index.tolist()
        pivot = pivot.loc[top_riders]
    try:
        race_order = get_race_order()
        present_order = [e for e in race_order if e in pivot.columns]
        remaining = [e for e in pivot.columns if e not in present_order]
        pivot = pivot.reindex(columns=present_order + remaining).fillna(0)
    except Exception:
        pivot = pivot.fillna(0)
    return pivot

def plot_podiums_heatmap(matrix_df, figsize=(12,8), cmap='YlGnBu', annot=True, fmt='d'):
    """
    Disegna una heatmap dei podi (matrix_df: rider x event).
    - annot: se True annota le celle con i valori.
    - fmt: formato annotazioni ('d' per integer, '.2f' per float)
    Restituisce l'asse matplotlib.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    if matrix_df is None or matrix_df.empty:
        print("Nessuna informazione per la heatmap.")
        return None
    plt.figure(figsize=figsize)
    ax = plt.gca()
    sns.heatmap(matrix_df, cmap=cmap, annot=annot, fmt=fmt, cbar_kws={'label': 'Numero di podi'})
    ax.set_xlabel('Evento (codice)')
    ax.set_ylabel('Rider')
    ax.set_title('Podi per pilota × evento')
    plt.tight_layout()
    return ax