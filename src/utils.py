import pandas as pd

def load_data(path="../data/RidersSummary.csv"):
    """
    Load dataset from CSV and return a pandas DataFrame
    """
    df = pd.read_csv(path)
    return df

def stats_riders_by_country(df, top_n = 10):
    """
    return a DataFrame with the number of unique riders by country
    """
    # Raggruppiamo per nazione e contiamo i piloti unici
    riders_by_country = (
        df.groupby("home_country")["rider_name"]
        .nunique()
        .sort_values(ascending=False)
        .head(top_n)
    )

    # Convertiamo in DataFrame con colonne leggibili
    result = riders_by_country.reset_index()
    result.columns = ["Country", "Unique Riders"]
    
    # Aggiungiamo un rank (posizione)
    result.insert(0, "Rank", range(1, len(result) + 1))

    # Calcoliamo la percentuale sul totale
    total_riders = df["rider_name"].nunique() # Numero totale di piloti
    result["Percentage"] = (result["Unique Riders"] / total_riders * 100).round(2) # Percentuale 
    return result
