import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="DUO & Hypotheek Dashboard", layout="wide")
st.title("💡 DUO & Hypotheek")

# --- Gegevens ---
min_aflossing_duo = 50  # verplicht per maand
max_duo_jaartijd = 35  # DUO wordt kwijtgescholden na 35 jaar

schulden = np.array([48000, 45000, 40000, 35000, 30000, 25000, 20000, 15000, 10000, 5000, 0])
hypotheken_maandbedrag = np.array([651, 664, 686, 708, 729, 751, 773, 794, 816, 838, 859])
max_hypotheek = np.array([144.782, 147.669, 152.490, 157.310, 162.109, 166.929, 171.750, 176.570, 181.368, 186.189, 191.009]) * 1000  # euro

# --- Invoer ---
st.sidebar.header("Invoer")
duo_schuld_start = st.sidebar.number_input("Totale DUO schuld (€)", value=48000, step=1000)
spaarsaldo = st.sidebar.number_input("Beschikbaar spaarsaldo (€)", value=38000, step=1000)
extra_aflossing_duo = st.sidebar.slider(
    "Bedrag gelijk aflossen aan DUO (€) - dit is voor scenario 'gelijk aflossen'), voor een goede vergelijking laat je deze op zijn hoogst",
    0, min(spaarsaldo, duo_schuld_start),
    value=min(spaarsaldo, duo_schuld_start), step=100
)
over_hoeveel_jaar_hypotheek = st.sidebar.number_input("Over hoeveel jaar krijg je een hypotheek", value=5, step=1)
beschikbaar_spaargeld_na_aflossen = spaarsaldo - extra_aflossing_duo
duo_rente_percentage = st.sidebar.number_input("Rente DUO ([zie hier](https://www.duo.nl/particulier/rente/rente-voor-studenten.jsp))", value=2.57, step=0.1)
rente_duo = duo_rente_percentage/100
hypotheek_rente_percentage = st.sidebar.number_input("Rente Hypotheek", value=3.52, step=0.1)
rente_hypotheek = hypotheek_rente_percentage/100

st.sidebar.header("Info")
st.sidebar.markdown("Verkrijgbare hypotheek is berekend vanuit de [Rabobank rekentool](https://www.rabobank.nl/particulieren/hypotheek/hypotheek-berekenen?utm_source=Google&utm_medium=CPC&utm_id=google_ads_262289088&utm_cid=262289088&utm_agid=16946959848&utm_kw=rabobank%20hypotheek%20berekenen&utm_mt=e&utm_campaign=MPD2522135029_semibrand--berekenen&gad_source=1&gad_campaignid=262289088&gbraid=0AAAAADsaNlfRx6MXNu9CmYUQRDD5Rua-f&gclid=Cj0KCQjwgpzIBhCOARIsABZm7vHJl7WPQQFlz2vfjrMf4PJ0d1ZlCd7katt6bRMtxn0dFkDYtfnnRnMaAhoHEALw_wcB)")
st.sidebar.markdown("Minimaal maandbedrag DUO dat betaald moet worden kan met [Rekenhulp Terugbetalen](https://duo.nl/particulier/rekenhulp-studiefinanciering.jsp#/nl/terugbetalen) van DUO berekend worden. Voor een inkomen van jou en je partner van beide 40.000eu is dit 'slechts' 147eu per maand")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Scenario 1: Gelijk DUO aflossen")
    maandlast_duo_s1 = st.number_input(
        "Maandelijkse DUO aflossing (€)",
        min_value=min_aflossing_duo, value=100, step=50
    )
    extra_aflossing_hypotheek_s1 = st.number_input(
        "Extra hypotheek aflossen  (€) (bovenop verplicht maandelijks bedrag)", value=0, step=50
    )
with col2:
    st.subheader("Scenario 2: Wachten met aflossen DUO")
    maandlast_duo_s2 = st.number_input(
        "Maandelijkse DUO aflossing  (€)",
        min_value=min_aflossing_duo, value=100, step=50
    )
    extra_aflossing_hypotheek_s2 = st.number_input(
        "Extra hypotheek aflossen  (€) (bovenop verplicht maandelijks bedrag)", value=165, step=50
    )


# --- Direct aflossen ---
duo_na_aflossing = duo_schuld_start - extra_aflossing_duo

# --- Lineaire interpolatie voor maandlast hypotheek en maximale hypotheek ---
def interpolate_linear(x, xp, fp):
    return np.interp(x, xp[::-1], fp[::-1])  # reverse arrays zodat np.interp van hoog naar laag werkt

# --- Berekeningen ---
# Scenario 1: DUO direct aflossen vs Scenario 2: DUO open laten
maandlast_hypotheek_s1 = interpolate_linear(duo_na_aflossing, schulden, hypotheken_maandbedrag)
max_hypotheek_s1 = interpolate_linear(duo_na_aflossing, schulden, max_hypotheek)

maandlast_hypotheek_s2 = interpolate_linear(duo_schuld_start, schulden, hypotheken_maandbedrag)
max_hypotheek_s2 = interpolate_linear(duo_schuld_start, schulden, max_hypotheek)

# --- DataFrame maken ---
data = {
    "Direct aflossen DUO": [
        f"€{duo_na_aflossing:,}",
        f"€{int(max_hypotheek_s1):,}",
        f"€{int(beschikbaar_spaargeld_na_aflossen):,}",
        f"€{int(max_hypotheek_s1+beschikbaar_spaargeld_na_aflossen):,}",
        f"€{int(maandlast_hypotheek_s1)}",
        f"€{int(extra_aflossing_hypotheek_s1)}",
        f"€{int(maandlast_hypotheek_s1+extra_aflossing_hypotheek_s1)}",
        f"€{int(maandlast_duo_s1)}",
        f"€{int(maandlast_duo_s1+maandlast_hypotheek_s1+extra_aflossing_hypotheek_s1)}"
    ],
    "DUO open laten staan": [
        f"€{duo_schuld_start:,}",
        f"€{int(max_hypotheek_s2):,}",
        f"€{int(spaarsaldo):,}",
        f"€{int(max_hypotheek_s2+spaarsaldo):,}",
        f"€{int(maandlast_hypotheek_s2)}",
        f"€{int(extra_aflossing_hypotheek_s2)}",
        f"€{int(maandlast_hypotheek_s2+extra_aflossing_hypotheek_s2)}",
        f"€{int(maandlast_duo_s2)}",
        f"€{int(maandlast_duo_s2+maandlast_hypotheek_s2+extra_aflossing_hypotheek_s2)}"
    ]
}

index = [
    "Overgebleven DUO schuld",
    "Max. verkrijgbare hypotheek",
    "Spaargeld",
    "Hypotheek + spaargeld",
    "Hypotheek maandlast (verplicht)",
    "Hypotheek extra aflossing",
    "Hypotheek totaal (verplicht + extra)",
    "DUO maandlast",
    "Totale maandlast"
]

df = pd.DataFrame(data, index=index)

# === Split in twee delen ===
df_totaal = df.loc[["Overgebleven DUO schuld", "Max. verkrijgbare hypotheek", "Spaargeld", "Hypotheek + spaargeld"]]
df_maandelijks = df.loc[["Hypotheek maandlast (verplicht)", "Hypotheek extra aflossing", "Hypotheek totaal (verplicht + extra)", "DUO maandlast", "Totale maandlast"]]

# === Streamlit layout ===
st.header("Vergelijking van scenario's")

# --- Kopje 1: Totale bedragen ---
st.subheader("💰 Totale bedragen")
st.dataframe(df_totaal)

# --- Kopje 2: Maandelijkse lasten ---
st.subheader("📆 Maandelijkse lasten")

# Stijl toepassen
st.dataframe(df_maandelijks)


# --- Simulatie over tijd ---
years = 40
months = years * 12
months_array = np.arange(months)

def bereken_verloop_schulden(months, startschuld_duo, max_hypotheek, maand_hypotheek, maandlast_duo, extra_aflossing_hypotheek=0, over_hoeveel_jaar_hypotheek=5):
    # Vaste input
    duo_schuld_aflossen = np.zeros(months)
    hypotheek_aflossen = np.zeros(months)
    totale_betalingen = np.zeros(months)
    maandbedragen_totaal = np.zeros(months)

    # Startschuld DUO en maandbedrag hypotheek
    duo_schuld_aflossen[0] = startschuld_duo
    hypotheek_aflossen[over_hoeveel_jaar_hypotheek*12] = max_hypotheek
    hypotheek_maandbedrag = maand_hypotheek

    for m in range(1, months):

        # DUO berekening
        maand_rente_duo = duo_schuld_aflossen[m-1] * ((rente_duo+1)**(1/12) -1)
        aflossing_duo = min(maandlast_duo, duo_schuld_aflossen[m-1] + maand_rente_duo)
        duo_schuld_aflossen[m] = duo_schuld_aflossen[m-1] + maand_rente_duo - aflossing_duo
        duo_schuld_aflossen[m] = max(duo_schuld_aflossen[m], 0)

        if m >= over_hoeveel_jaar_hypotheek*12+1:
            if m % 12 == 1:
                maand_rente_bedrag_hypotheek = (hypotheek_aflossen[m-1]*rente_hypotheek)/12
            hypotheek_aflossen[m] = max(hypotheek_aflossen[m-1] - hypotheek_maandbedrag - extra_aflossing_hypotheek + maand_rente_bedrag_hypotheek, 0)
            # Als hypotheek afbetaald is: DUO betalen
            if hypotheek_aflossen[m-1] == 0:
                extra_aflossing = min(duo_schuld_aflossen[m], hypotheek_maandbedrag + extra_aflossing_hypotheek)
                duo_schuld_aflossen[m] = duo_schuld_aflossen[m] - extra_aflossing
                aflossing_duo += extra_aflossing
        if hypotheek_aflossen[m-1] > 0 or duo_schuld_aflossen[m-1] > 0:
            maandbedragen_totaal[m] = hypotheek_maandbedrag + extra_aflossing_hypotheek

        # --- Totale betaling deze maand ---
        betaal_duo = aflossing_duo
        betaal_hypotheek = 0
        if m >= over_hoeveel_jaar_hypotheek * 12 + 1 and hypotheek_aflossen[m - 1] > 0:
            betaal_hypotheek = maand_hypotheek + extra_aflossing_hypotheek
        totale_betalingen[m] = betaal_duo + betaal_hypotheek
        if duo_schuld_aflossen[m-1] > 0:
            maandbedragen_totaal[m] = maandbedragen_totaal[m] + maandlast_duo

    totale_schuld = duo_schuld_aflossen + hypotheek_aflossen
    totale_kosten = totale_betalingen.sum()
    totaal_maandbedragen = maandbedragen_totaal.sum()

    nul_index = np.argmax(totale_schuld <= 0)
    jaren_tot_nul = nul_index / 12 if nul_index > 0 else years

    return duo_schuld_aflossen, hypotheek_aflossen, totale_schuld, totale_kosten, jaren_tot_nul


# --- Scenario 1: DUO aflossen direct ---
duo_verloop_s1, hypotheek_verloop_s1, totale_schuld_s1, totale_kosten_s1, jaren_tot_nul_s1 = bereken_verloop_schulden(
    months, duo_na_aflossing, max_hypotheek_s1, maandlast_hypotheek_s1, maandlast_duo_s1, extra_aflossing_hypotheek_s1, over_hoeveel_jaar_hypotheek
)
df_s1 = pd.DataFrame({
    "Jaren": months_array / 12,
    "DUO Schuld": duo_verloop_s1,
    "Hypotheek": hypotheek_verloop_s1,
    "Totale schuld": totale_schuld_s1
})

# --- Scenario 2: DUO niet direct aflossen ---
duo_verloop_s2, hypotheek_verloop_s2, totale_schuld_s2, totale_kosten_s2, jaren_tot_nul_s2 = bereken_verloop_schulden(
    months, duo_schuld_start, max_hypotheek_s2, maandlast_hypotheek_s2, maandlast_duo_s2, extra_aflossing_hypotheek_s2, over_hoeveel_jaar_hypotheek
)
df_s2 = pd.DataFrame({
    "Jaren": months_array / 12,
    "DUO Schuld": duo_verloop_s2,
    "Hypotheek": hypotheek_verloop_s2,
    "Totale schuld": totale_schuld_s2
})

st.subheader("📈 Overzicht totale kosten en duur")
resultaten = pd.DataFrame({
    "Scenario": ["Direct aflossen DUO", "DUO open laten staan"],
    "Totale kosten (€)": [f"€{int(totale_kosten_s1):,}", f"€{int(totale_kosten_s2):,}"],
    "Jaren tot volledig afgelost": [f"{jaren_tot_nul_s1:.1f}", f"{jaren_tot_nul_s2:.1f}"]
})
resultaten_flip = resultaten.set_index("Scenario").T
# 🔹 Style de eerste rij (bijv. dikgedrukt en lichtblauw)
styled = resultaten_flip.style.apply(
    lambda x: ['font-weight: bold; background-color: #e3f2fd' if x.name == resultaten_flip.index[0] else '' for _ in x],
    axis=1
)
st.table(styled)


# Grafieken
st.header("Scenario 1: DUO aflossen direct")
st.line_chart(df_s1.set_index("Jaren"))
st.header("Scenario 2: DUO niet direct aflossen")
st.line_chart(df_s2.set_index("Jaren"))


