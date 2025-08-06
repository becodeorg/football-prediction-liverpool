import streamlit as st
import pandas as pd
import numpy as np

st.title("🏈 Football Prediction - Test App")
st.write("Application de test pour vérifier le fonctionnement de Streamlit")

# Test simple
st.success("✅ Streamlit fonctionne correctement!")
st.info("📊 Version de test - Application principale en cours de résolution")

# Affichage de données de test
data = pd.DataFrame({
    'Equipe': ['Manchester City', 'Liverpool', 'Arsenal'],
    'Victoires': [25, 22, 20],
    'Defaites': [3, 6, 8]
})

st.dataframe(data)
st.bar_chart(data.set_index('Equipe'))
