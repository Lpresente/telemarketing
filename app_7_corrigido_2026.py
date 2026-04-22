# Imports
import pandas            as pd
import streamlit         as st
import seaborn           as sns
import matplotlib.pyplot as plt
from PIL                 import Image
from io                  import BytesIO

st.set_page_config(page_title='Análise de dados de Telemarketing',
                   page_icon='telmarketing_icon.png',
                   layout="wide",
                   initial_sidebar_state='expanded')

# Tema do seaborn
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)


# Função para ler os dados
@st.cache_data(show_spinner=True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except Exception:
        try:
            return pd.read_excel(file_data)
        except Exception as e:
            st.error(f"Falha ao ler o arquivo: {e}")
            return None


# Função para filtrar baseado na multiseleção de categorias
@st.cache_data
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)


# Função para converter o df para csv
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


# Função para converter o df para excel
@st.cache_data
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output.getvalue()


# Função principal da aplicação
def main():
    st.write('# Telemarketing analysis')
    st.markdown("---")

    # Imagem na barra lateral
    try:
        image = Image.open("Bank-Branding.jpg")
        st.sidebar.image(image)
    except Exception:
        st.sidebar.info("Imagem não encontrada.")

    # Upload de arquivo
    st.sidebar.write("## Suba o arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=['csv', 'xlsx'])

    if data_file_1 is not None:
        bank_raw = load_data(data_file_1)
        if bank_raw is None:
            return
        bank = bank_raw.copy()

        st.write('## Antes dos filtros')
        st.write(bank_raw.head())

        with st.sidebar.form(key='my_form'):
            # Tipo de gráfico
            graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))

            # Idades
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider(label='Idade',
                               min_value=min_age,
                               max_value=max_age,
                               value=(min_age, max_age),
                               step=1)

            # Profissões
            jobs_list = bank.job.unique().tolist()
            jobs_list.append('all')
            jobs_selected = st.multiselect("Profissão", jobs_list, ['all'])

            # Estado civil
            marital_list = bank.marital.unique().tolist()
            marital_list.append('all')
            marital_selected = st.multiselect("Estado civil", marital_list, ['all'])

            # Default
            default_list = bank.default.unique().tolist()
            default_list.append('all')
            default_selected = st.multiselect("Default", default_list, ['all'])

            # Housing
            housing_list = bank.housing.unique().tolist()
            housing_list.append('all')
            housing_selected = st.multiselect("Tem financiamento imob?", housing_list, ['all'])

            # Loan
            loan_list = bank.loan.unique().tolist()
            loan_list.append('all')
            loan_selected = st.multiselect("Tem empréstimo?", loan_list, ['all'])

            # Contact
            contact_list = bank.contact.unique().tolist()
            contact_list.append('all')
            contact_selected = st.multiselect("Meio de contato", contact_list, ['all'])

            # Month
            month_list = bank.month.unique().tolist()
            month_list.append('all')
            month_selected = st.multiselect("Mês do contato", month_list, ['all'])

            # Day of week
            day_of_week_list = bank.day_of_week.unique().tolist()
            day_of_week_list.append('all')
            day_of_week_selected = st.multiselect("Dia da semana", day_of_week_list, ['all'])

            # Aplicar filtros
            bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                        .pipe(multiselect_filter, 'job', jobs_selected)
                        .pipe(multiselect_filter, 'marital', marital_selected)
                        .pipe(multiselect_filter, 'default', default_selected)
                        .pipe(multiselect_filter, 'housing', housing_selected)
                        .pipe(multiselect_filter, 'loan', loan_selected)
                        .pipe(multiselect_filter, 'contact', contact_selected)
                        .pipe(multiselect_filter, 'month', month_selected)
                        .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
                    )

            submit_button = st.form_submit_button(label='Aplicar')

        # Dados filtrados
        st.write('## Após os filtros')
        st.write(bank.head())

        df_xlsx = to_excel(bank)
        st.download_button(label='📥 Download tabela filtrada em EXCEL',
                           data=df_xlsx,
                           file_name='bank_filtered.xlsx')
        st.markdown("---")

        # Proporções
        bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).to_frame(name='y') * 100
        bank_raw_target_perc = bank_raw_target_perc.sort_index()

        try:
            bank_target_perc = bank.y.value_counts(normalize=True).to_frame(name='y') * 100
            bank_target_perc = bank_target_perc.sort_index()
        except Exception as e:
            bank_target_perc = None
            st.error(f'Erro no filtro: {e}')

        col1, col2 = st.columns(2)

        df_xlsx = to_excel(bank_raw_target_perc)
        col1.write('### Proporção original')
        col1.write(bank_raw_target_perc)
        col1.download_button(label='📥 Download',
                             data=df_xlsx,
                             file_name='bank_raw_y.xlsx')

        if bank_target_perc is not None and not bank_target_perc.empty:
            df_xlsx = to_excel(bank_target_perc)
            col2.write('### Proporção da tabela com filtros')
            col2.write(bank_target_perc)
            col2.download_button(label='📥 Download',
                                 data=df_xlsx,
                                 file_name='bank_y.xlsx')
        else:
            col2.write('### Proporção da tabela com filtros')
            col2.info('Sem dados filtrados válidos para exibir.')

        st.markdown("---")

        # Gráficos
        st.write('## Proporção de aceite')
        fig, ax = plt.subplots(1, 2, figsize=(8, 3))

        if graph_type == 'Barras':
            sns.barplot(x=bank_raw_target_perc.index,
                        y='y',
                        data=bank_raw_target_perc,
                        ax=ax[0])
            ax[0].bar_label(ax[0].containers[0])
            ax[0].set_title('Dados brutos', fontweight="bold")

            if bank_target_perc is not None and not bank_target_perc.empty:
                sns.barplot(x=bank_target_perc.index,
                            y='y',
                            data=bank_target_perc,
                            ax=ax[1])
                ax[1].bar_label(ax[1].containers[0])
                ax[1].set_title('Dados filtrados', fontweight="bold")
            else:
                ax[1].text(0.5, 0.5, 'Sem dados filtrados', ha='center', va='center')
                ax[1].set_axis_off()
        else:
            bank_raw_target_perc.plot(kind='pie', autopct='%.2f', y='y', ax=ax[0])
            ax[0].set_title('Dados brutos', fontweight="bold")

            if bank_target_perc is not None and not bank_target_perc.empty:
                bank_target_perc.plot(kind='pie', autopct='%.2f', y='y', ax=ax[1])
                ax[1].set_title('Dados filtrados', fontweight="bold")
            else:
                ax[1].text(0.5, 0.5, 'Sem dados filtrados', ha='center', va='center')
                ax[1].set_axis_off()

        st.pyplot(fig)


if __name__ == '__main__':
    main()