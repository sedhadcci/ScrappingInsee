import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz

# Fonction pour trouver la correspondance la plus proche avec token_sort_ratio et token_set_ratio
def find_closest_match(name, df, search_fields):
    if not isinstance(name, str):
        return None, None, None  # Retourner None si le nom n'est pas une chaîne
    max_ratio = 0
    closest_match = None
    matched_field = None
    for field in search_fields:
        for candidate in df[field].dropna().unique():
            if not isinstance(candidate, str):
                continue  # Ignorer les candidats non valides

            # Utiliser token sort ratio et token set ratio
            token_sort = fuzz.token_sort_ratio(name.lower(), candidate.lower())
            token_set = fuzz.token_set_ratio(name.lower(), candidate.lower())

            # Prendre le meilleur score des deux méthodes
            ratio = max(token_sort, token_set)

            if ratio > max_ratio and ratio >= 95:  # Augmenter le seuil à 95
                max_ratio = ratio
                closest_match = candidate
                matched_field = field
    return closest_match, max_ratio, matched_field

# Fonction pour obtenir le SIREN/SIRET et la dénomination sociale à partir du nom
def get_identifier_and_denomination(name, df):
    siret_fields = ['denominationUsuelleEtablissement', 'enseigne1Etablissement', 'enseigne2Etablissement', 'enseigne3Etablissement']
    deno_fields = ['denominationUniteLegale', 'sigleUniteLegale', 'denominationUsuelle1UniteLegale']

    # Chercher d'abord dans les champs de SIRET
    match, _, matched_field = find_closest_match(name, df, siret_fields)
    if match:
        identifier = df[df[matched_field] == match]['siret'].values[0]
        return identifier, 'SIRET', match

    # Si aucune correspondance n'est trouvée dans les champs de SIRET, chercher dans les champs de dénomination
    match, _, matched_field = find_closest_match(name, df, deno_fields)
    if match:
        identifier = df[df[matched_field] == match]['siret'].values[0]
        return identifier, 'SIRET', match
    
    return None, None, None

# Charger le fichier des entreprises avec caching
@st.cache_data
def load_data():
    url = "https://github.com/sedhadcci/ScrappingInsee/raw/main/insee%20entreprise%20informatique.xlsx"
    data = pd.read_excel(url)  # Use 'url' here instead of 'filepath'
    return data

# Interface Streamlit
def main():
    st.title("Trouver le SIREN/SIRET des entreprises et leur dénomination sociale")
    df = load_data()

    uploaded_file = st.file_uploader("Choisissez un fichier Excel", type=["xlsx", "xls"])
    if uploaded_file is not None:
        input_data = pd.read_excel(uploaded_file)
        st.write("Fichier uploadé avec succès. Voici un aperçu :")
        st.write(input_data.head())

        if st.button("Chercher les SIREN/SIRET et les dénominations sociales"):
            st.write("Recherche en cours, veuillez patienter...")
            # Créer de nouvelles colonnes pour le SIREN/SIRET et la dénomination
            results = input_data['Entreprise'].apply(
                lambda x: get_identifier_and_denomination(x, df))
            input_data['Identifiant'] = [res[0] for res in results]
            input_data['Type'] = [res[1] for res in results]
            input_data['Dénomination Sociale'] = [res[2] for res in results]

            st.write("Recherche terminée. Voici les résultats :")
            st.write(input_data)

if __name__ == "__main__":
    main()
