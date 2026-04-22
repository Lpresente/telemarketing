#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Imports
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# CONFIG (sem travar por ícone)
st.set_page_config(
    page_title='Análise de dados de Telemarketing',
    layout="wide"
)

# Tema do seaborn
sns.set_theme(style="ticks")

# Função para ler os dados
@st.cache_data(show_spinner=True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        try:
            return pd.read_excel(file_data)
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
            return None

# Filtro seguro
def safe_multiselect(df, col, selected):
    if col not in df.columns:
        return df
    if 'all' in selected:
        return df
    return df[df[col].isin(selected)]

# Excel
@st.cache_data
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output.getvalue()

def main():
    st.title('Telemarketing analysis')

    # Imagem
    try:
        image = Image.open("Bank-Branding.jpg")
        st.sidebar.image(image)
    except:
        st.sidebar.info("Imagem não encontrada.")

    # Upload
    st.sidebar.write("## Suba o arquivo")
    file = st.sidebar.file_uploader("CSV ou Excel", type=['csv', 'xlsx'])

    if file is None:
        st.warning("Envie um arquivo para começar")
        return

    df = load_data(file)

    if df is None or df.empty:
        st.error("Erro ao carregar dados")
        return

    st.write("## Dados carregados")
    st.write(df.head())

    # Verifica colunas obrigatórias
    required_cols = ['age', 'job', 'marital', 'default', 'housing', 'loan', 'contact', 'month', 'day_of_week', 'y']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Coluna obrigatória ausente: {col}")
            return

    # Filtros
    with st.sidebar:
        graph_type = st.radio('Tipo de gráfico:', ['Barras', 'Pizza'])

        min_age = int(df['age'].min())
        max_age = int(df['age'].max())

        age_range = st.slider("Idade", min_age, max_age, (min_age, max_age))

        def multiselect(col):
            values = df[col].dropna().unique().tolist()
            values.append('all')
            return st.multiselect(col, values, ['all'])

        job = multiselect('job')
        marital = multiselect('marital')
        default = multiselect('default')
        housing = multiselect('housing')
        loan = multiselect('loan')
        contact = multiselect('contact')
        month = multiselect('month')
        day = multiselect('day_of_week')

    # Aplicar filtros
    df_filtered = df[
        (df['age'] >= age_range[0]) &
        (df['age'] <= age_range[1])
    ]

    df_filtered = safe_multiselect(df_filtered, 'job', job)
    df_filtered = safe_multiselect(df_filtered, 'marital', marital)
    df_filtered = safe_multiselect(df_filtered, 'default', default)
    df_filtered = safe_multiselect(df_filtered, 'housing', housing)
    df_filtered = safe_multiselect(df_filtered, 'loan', loan)
    df_filtered = safe_multiselect(df_filtered, 'contact', contact)
    df_filtered = safe_multiselect(df_filtered, 'month', month)
    df_filtered = safe_multiselect(df_filtered, 'day_of_week', day)

    st.write("## Dados filtrados")
    st.write(df_filtered.head())

    # Download
    st.download_button(
        "📥 Download Excel",
        to_excel(df_filtered),
        "dados_filtrados.xlsx"
    )

    # Proporções
    try:
        raw_perc = df['y'].value_counts(normalize=True) * 100
        filt_perc = df_filtered['y'].value_counts(normalize=True) * 100
    except:
        st.error("Erro ao calcular proporções")
        return

    col1, col2 = st.columns(2)

    col1.write("Original")
    col1.write(raw_perc)

    col2.write("Filtrado")
    col2.write(filt_perc)

    # Gráfico
    fig, ax = plt.subplots(1, 2, figsize=(8, 3))

    if graph_type == 'Barras':
        raw_perc.plot(kind='bar', ax=ax[0])
        ax[0].set_title('Original')

        if not filt_perc.empty:
            filt_perc.plot(kind='bar', ax=ax[1])
            ax[1].set_title('Filtrado')
        else:
            ax[1].text(0.5, 0.5, 'Sem dados', ha='center')

    else:
        raw_perc.plot(kind='pie', ax=ax[0])
        ax[0].set_title('Original')

        if not filt_perc.empty:
            filt_perc.plot(kind='pie', ax=ax[1])
            ax[1].set_title('Filtrado')
        else:
            ax[1].text(0.5, 0.5, 'Sem dados', ha='center')

    st.pyplot(fig)


if __name__ == "__main__":
    main()


# In[ ]:




