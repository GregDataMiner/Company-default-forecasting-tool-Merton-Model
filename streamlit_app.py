import streamlit as st
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
import requests

# Établir la connexion à l'API Financial Modeling Prep
api_url = st.secrets["financial_api"]["url"]
api_key = st.secrets["financial_api"]["apikey"]

# Fonctions de récupération des données avec mise en cache
@st.cache_data(ttl=600)
def get_total_debt(ticker):
    response = requests.get(f"{api_url}/balance-sheet-statement/{ticker}?apikey={api_key}")
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0].get("totalDebt", 0)
    return None

@st.cache_data(ttl=600)
def get_market_cap(ticker):
    response = requests.get(f"{api_url}/profile/{ticker}?apikey={api_key}")
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0].get("mktCap", 0)
    return None

@st.cache_data(ttl=600)
def get_volatility_equity(ticker):
    response = requests.get(f"{api_url}/historical-price-full/{ticker}?apikey={api_key}")
    if response.status_code == 200:
        data = response.json()
        if "historical" in data:
            prices = [day["close"] for day in data["historical"][:252]]
            returns = np.diff(np.log(prices))
            return np.std(returns) * np.sqrt(252)
    return None

# Modèle de Merton

def d1(A, D, T, r, sigma_A):
    return (np.log(A / D) + (r + 0.5 * sigma_A**2) * T) / (sigma_A * np.sqrt(T))

def d2(d1, sigma_A, T):
    return d1 - sigma_A * np.sqrt(T)

def equity_value(A, D, T, r, sigma_A):
    d1_val = d1(A, D, T, r, sigma_A)
    d2_val = d2(d1_val, sigma_A, T)
    return A * norm.cdf(d1_val) - D * np.exp(-r * T) * norm.cdf(d2_val)

def asset_volatility(A, E, sigma_E, T, r):
    return sigma_E * (E / (A * norm.cdf(d1(A, D, T, r, sigma_E))))

def objective(x, D, E, T, r, sigma_E):
    A, sigma_A = x
    E_estimated = equity_value(A, D, T, r, sigma_A)
    sigma_A_estimated = asset_volatility(A, E, sigma_E, T, r)
    return (E_estimated - E)**2 + (sigma_A_estimated - sigma_A)**2

def probability_of_default(A0, D, T, r, sigma_A):
    d2_val = (np.log(D / A0) - (r - 0.5 * sigma_A**2) * T) / (sigma_A * np.sqrt(T))
    return norm.cdf(d2_val)

# Interface Streamlit
st.title("Évaluation du Risque de Crédit - Modèle de Merton")

companies = {
    "Apple": "AAPL", "Tesla": "TSLA", "Amazon": "AMZN", "Microsoft": "MSFT", "Meta": "META",
    "Nvidia": "NVDA", "Alphabet (Google)": "GOOGL", "Netflix": "NFLX", "Adobe": "ADBE", "Intel": "INTC",
    "Cisco": "CSCO", "Paypal": "PYPL", "Qualcomm": "QCOM", "AMD": "AMD", "Uber": "UBER",
    "Lyft": "LYFT", "Zoom": "ZM", "Snowflake": "SNOW", "Palantir": "PLTR", "Roku": "ROKU"
}

selected_company = st.selectbox("Sélectionnez une entreprise :", list(companies.keys()))
ticker = companies[selected_company]

# Sélection du multiplicateur de la dette
multiplier = st.slider("Sélectionnez le multiplicateur de la dette (de 1x à 50x)", 1, 50, 10)
T = 1  # Échéance de la dette en années
r = 0.05  # Taux d'intérêt sans risque (5%)

if st.button("Évaluer le risque"):
    with st.spinner("Chargement des données..."):
        D = get_total_debt(ticker)
        E = get_market_cap(ticker)
        sigma_E = get_volatility_equity(ticker)
    
    if D is None or E is None or sigma_E is None:
        st.error("Impossible de récupérer toutes les données requises.")
    else:
        D *= multiplier
        st.write(f"Nouvelle dette après augmentation ({multiplier}x) : {D:,.2f} USD")

        # Optimisation
        initial_guess = [E + D, sigma_E]
        result = minimize(objective, initial_guess, args=(D, E, T, r, sigma_E), method='Nelder-Mead')
        A_estimated, sigma_A_estimated = result.x
        PD = probability_of_default(A_estimated, D, T, r, sigma_A_estimated)

        # Affichage des résultats
        st.success("Calcul terminé")
        st.write(f"**Valeur estimée des actifs :** {A_estimated:,.2f} USD")
        st.write(f"**Volatilité estimée des actifs :** {sigma_A_estimated:.2%}")
        st.write(f"**Probabilité de défaut :** {PD:.2%}")
