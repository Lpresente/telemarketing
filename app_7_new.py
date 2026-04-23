#!/usr/bin/env python
# coding: utf-8

# In[5]:


# Imports
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# CONFIG
st.set_page_config(
    page_title='Análise de dados de Telemarketing',
    layout="wide"
)

# Tema
sns.set_theme(style="ticks")

# =========================
# LOAD DATA (corrigido)
# =========================
@st.cache_data(show_spinner=True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except pd.errors.ParserError:
        try:
            return pd.read_excel(file_data)
        except Exception as e:
            st.error(f"Erro ao ler Excel: {e}")
            return None

# =========================
# FILTRO
# =========================
def safe_multiselect(df, col, selected):
    if col not in df.columns:
        return df
    if 'all' in selected:
        return df
    return df[df[col].isin(selected)]

# =========================
# EXCEL
# =========================
@st.cache_data
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output.getvalue()

# =========================
# MAIN
# =========================
def main():
    st.title('Telemarketing analysis')

    # Imagem
    try:
        image = Image.open("Bank-Branding.jpg")
        st.sidebar.image(image)
    except FileNotFoundError:
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

    # Verifica colunas
    required_cols = ['age', 'job', 'marital', 'default', 'housing', 'loan', 'contact', 'month', 'day_of_week', 'y']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Coluna obrigatória ausente: {col}")
            return

    # =========================
    # FILTROS
    # =========================
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

    # =========================
    # APLICAR FILTROS
    # =========================
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

    # =========================
    # PROPORÇÕES
    # =========================
    try:
        raw_perc = df['y'].value_counts(normalize=True) * 100
        filt_perc = df_filtered['y'].value_counts(normalize=True) * 100
    except Exception as e:
        st.error(f"Erro ao calcular proporções: {e}")
        return

    col1, col2 = st.columns(2)

    col1.write("Original")
    col1.write(raw_perc)

    col2.write("Filtrado")
    col2.write(filt_perc)

    # =========================
    # GRÁFICO
    # =========================
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

    # =========================
    # 📦 ANÁLISE POR PRODUTO
    # =========================
    st.markdown("## 📦 Performance por Produto")

    try:
        produto_perf = (
            df_filtered.groupby('contact')['y']
            .value_counts(normalize=True)
            .rename('taxa')
            .reset_index()
        )

        produto_perf = produto_perf[produto_perf['y'] == 'yes']

        fig_prod, ax_prod = plt.subplots()
        sns.barplot(data=produto_perf, x='contact', y='taxa', ax=ax_prod)
        ax_prod.set_title("Taxa de Conversão por Tipo de Contato")

        st.pyplot(fig_prod)

    except KeyError as e:
        st.warning(f"Erro na análise por produto: {e}")

    # =========================
    # 👤 ANÁLISE POR CLIENTE
    # =========================
    st.markdown("## 👤 Performance por Cliente")

    try:
        df_filtered['faixa_etaria'] = pd.cut(
            df_filtered['age'],
            bins=[0, 25, 40, 60, 100],
            labels=['18-25', '26-40', '41-60', '60+']
        )

        col1, col2 = st.columns(2)

        # Idade
        idade_perf = (
            df_filtered.groupby('faixa_etaria')['y']
            .value_counts(normalize=True)
            .rename('taxa')
            .reset_index()
        )

        idade_perf = idade_perf[idade_perf['y'] == 'yes']

        fig_idade, ax_idade = plt.subplots()
        sns.barplot(data=idade_perf, x='faixa_etaria', y='taxa', ax=ax_idade)
        ax_idade.set_title("Conversão por Faixa Etária")

        col1.pyplot(fig_idade)

        # Profissão
        job_perf = (
            df_filtered.groupby('job')['y']
            .value_counts(normalize=True)
            .rename('taxa')
            .reset_index()
        )

        job_perf = job_perf[job_perf['y'] == 'yes']

        fig_job, ax_job = plt.subplots()
        sns.barplot(data=job_perf, x='job', y='taxa', ax=ax_job)
        ax_job.set_title("Conversão por Profissão")
        plt.xticks(rotation=45)

        col2.pyplot(fig_job)

    except KeyError as e:
        st.warning(f"Erro na análise por cliente: {e}")


if __name__ == "__main__":
    main()
    


# In[ ]:




