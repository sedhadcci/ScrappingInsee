import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz

# Fonction pour trouver la correspondance la plus proche
def find_closest_match(name, list_of_names):
    max_ratio = 0
    closest_match = None
    for candidate in list_of_names:
        ratio = fuzz.ratio(name.lower(), candidate.lower())
        if ratio > max_ratio and ratio >= 70:
            max_ratio = ratio
            closest_match = candidate
    return closest_match

# Fonction pour obtenir le SIREN à partir du nom
def get_siren(name, df):
    match = find_closest_match(name, df['denominationUniteLegale'].tolist())
    if match is not None:
        return df[df['denominationUniteLegale'] == match]['siren'].values[0]
    return None

# Charger le fichier des entreprises
@st.cache
def load_data():
    # Assurez-vous que l'URL est correcte et que le fichier est accessible publiquement
    url = "https://github.com/sedhadcci/ScrappingInsee/raw/main/Fichier%20Insee.xlsx" 
    data = pd.read_csv(url)
    return data

# Interface Streamlit
def main():
    st.title("Trouver le SIREN des entreprises")
    df = load_data()

    uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")
    if uploaded_file is not None:
        input_data = pd.read_csv(uploaded_file)
        st.write("Fichier uploadé avec succès. Voici un aperçu :")
        st.write(input_data.head())

        if st.button("Chercher les SIREN"):
            st.write("Recherche en cours, veuillez patienter...")
            input_data['SIREN'] = input_data['Entreprise'].apply(lambda x: get_siren(x, df))
            st.write("Recherche terminée. Voici les résultats :")
            st.write(input_data)

if __name__ == "__main__":
    main()
