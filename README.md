Voici le **README** complet, prêt à être copié-collé :  

---

# **Company Default Forecasting Tool - Merton Model**  

## 📌 **Introduction**  
Cette application Streamlit permet d'évaluer le **risque de défaut d'une entreprise** en utilisant le **modèle de Merton**. Elle est disponible en ligne à **[ce lien cliquable](#)**.  

Le **modèle de Merton** repose sur l'idée que la valeur des actifs d'une entreprise suit un processus stochastique et que les actionnaires possèdent une option d'achat implicite sur ces actifs. L’entreprise fait défaut si la valeur de ses actifs tombe en dessous du montant de la dette à l'échéance $T$.  

### 🔢 **Formulation Mathématique**  

1. **Définition de la valeur des actifs :**  



2. **Scénarios possibles à maturité \(T\) :**  
   - Si \(A_T > D_T\), les actionnaires récupèrent :  
     \[
     E_T = \max(A_T - D_T, 0)
     \]  
   - Si \(A_T < D_T\), l'entreprise est en défaut et les créanciers récupèrent :  
     \[
     D_T = \min(A_T, D_T)
     \]  

La probabilité de défaut est donnée par :  
   \[
   PD = P(A_T < D_T) = N(-d_2)
   \]  
   où \(d_2\) est défini comme :  
   \[
   d_2 = \frac{\ln(A_0 / D_T) + (r - 0.5 \sigma_A^2) T}{\sigma_A \sqrt{T}}
   \]  

---  

## 🏗️ **Fonctionnalités de l'Application**  

### 🎯 **Sélection d’une Entreprise**  
L'utilisateur peut sélectionner **une entreprise parmi 20 disponibles** via un menu déroulant (`st.selectbox`).  

### 💰 **Récupération des Données Financières**  
L'application récupère automatiquement :  
- **Total de la dette** (`get_total_debt`)  
- **Capitalisation boursière** (`get_market_cap`)  
- **Volatilité des capitaux propres** (`get_volatility_equity`)  

### 📊 **Calcul du Modèle de Merton**  
L'application applique le **modèle de Merton** pour estimer :  
1. **La valeur des actifs de l'entreprise**  
2. **La volatilité des actifs**  
3. **La probabilité de défaut** (`probability_of_default`)  

### 🔄 **Simulation de Scénarios Catastrophes**  
L'utilisateur peut **choisir un multiplicateur de dette (de 2x à 50x)** et voir **comment la probabilité de défaut évolue**. Ce bouton permet d'**imaginer des scénarios d'endettement extrême** où l'entreprise devient fortement exposée au risque de défaut.  

---

## 📝 **Explication des Fonctions Principales**  

### 📌 **1️⃣ `get_total_debt(ticker)`**  
> 📊 **Récupère le total de la dette** depuis l’API Financial Modeling Prep.  

```python
@st.cache_data(ttl=600)
def get_total_debt(ticker):
    response = requests.get(f"{api_url}/balance-sheet-statement/{ticker}?apikey={api_key}")
    if response.status_code == 200:
        data = response.json()
        return data[0].get("totalDebt", 0)
    return None
```

### 📌 **2️⃣ `d1(A, D, T, r, sigma_A)` et `d2(d1, sigma_A, T)`**  
> 📉 **Calcule les paramètres de Black-Scholes utilisés dans le modèle de Merton.**  

```python
def d1(A, D, T, r, sigma_A):
    return (np.log(A / D) + (r + 0.5 * sigma_A**2) * T) / (sigma_A * np.sqrt(T))

def d2(d1, sigma_A, T):
    return d1 - sigma_A * np.sqrt(T)
```

### 📌 **3️⃣ `equity_value(A, D, T, r, sigma_A)`**  
> 🏦 **Calcule la valeur des capitaux propres via la formule de Black-Scholes.**  

```python
def equity_value(A, D, T, r, sigma_A):
    d1_val = d1(A, D, T, r, sigma_A)
    d2_val = d2(d1_val, sigma_A, T)
    return A * norm.cdf(d1_val) - D * np.exp(-r * T) * norm.cdf(d2_val)
```

### 📌 **4️⃣ `asset_volatility(A, E, sigma_E, T, r)`**  
> 🔁 **Estime la volatilité des actifs à partir de la volatilité des capitaux propres.**  

```python
def asset_volatility(A, E, sigma_E, T, r):
    return sigma_E * (E / (A * norm.cdf(d1(A, D, T, r, sigma_E))))
```

### 📌 **5️⃣ `probability_of_default(A0, D, T, r, sigma_A)`**  
> 🔴 **Calcule la probabilité de défaut de l'entreprise.**  

```python
def probability_of_default(A0, D, T, r, sigma_A):
    d2_val = (np.log(D / A0) - (r - 0.5 * sigma_A**2) * T) / (sigma_A * np.sqrt(T))
    return norm.cdf(d2_val)
```

---

## 🚀 **Déploiement sur Streamlit Cloud**  
L'application est disponible **[à ce lien cliquable](#)**.  

Si besoin, les **secrets API** doivent être ajoutés directement dans Streamlit Cloud :  
```toml
[financial_api]
url = "https://financialmodelingprep.com/api/v3"
apikey = "TA_CLE_API_ICI"
```

---

## 📜 **Licence**  
Ce projet est sous licence **MIT**. Vous pouvez le modifier et l'utiliser librement.  

## 📞 **Contact**  
Si vous avez des questions, n'hésitez pas à me contacter sur **GitHub** ou **LinkedIn** ! 🎯  

---

✅ **Maintenant, tu peux copier-coller ce README !** 🚀😊  
Si tu veux des ajustements, fais-moi signe ! 🎯
