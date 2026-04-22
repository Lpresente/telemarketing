import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys

# Criando a função para gerar gráficos
def plota_pivot_table(df, value, index, func, ylabel, xlabel, opcao='nada'):
    if opcao == 'nada':
        pd.pivot_table(df, values=value, index=index,
                       aggfunc=func).plot(figsize=[15, 5])
    elif opcao == 'sort':
        pd.pivot_table(df, values=value, index=index,
                       aggfunc=func).sort_values(value).plot(figsize=[15, 5])
    elif opcao == 'unstack':
        pd.pivot_table(df, values=value, index=index,
                       aggfunc=func).unstack().plot(figsize=[15, 5])
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    return None

# Configurando argumentos
print('O nome deste arquivo é:', os.path.basename(sys.argv[0]))

# Define o caminho da pasta com os dataframes
pasta = 'C:/Users/felip/Desktop/Nova pasta/exercicio 1'

# Verificando se o usuário inseriu o argumento corretamente
if len(sys.argv) < 2:
    print('Atenção! Nenhum argumento foi fornecido. Utilize a abreviação de cada mês para gerar sua análise.')
    # Lista todos os arquivos na pasta
    arquivos = os.listdir(pasta)
    print("Arquivos disponíveis:")
    for arquivo in arquivos:
        print(arquivo)
    sys.exit(1)

for mes in sys.argv[1:]:
    file_path = f'C:/Users/felip/Desktop/Nova pasta/exercicio 1/SINASC_RO_2019_{mes}.csv'
    if not os.path.exists(file_path):
        print(f"Arquivo {file_path} não encontrado.")
        continue  # Pulando para o próximo mês se o arquivo não for encontrado
    
    # Carregando Dataframe
    sinasc = pd.read_csv(file_path)
    print(f'Carregando dados para o mês {mes}:')

    max_data = sinasc.DTNASC.max()[:7]
    print(f'Diretório de saída para {mes}:{max_data}')  # Verificar se a pasta está correta

    # Configurando o diretório dos gráficos
    output_dir = os.path.join('C:/Users/felip/Desktop/Nova pasta/exercicio 2/output/', max_data)
    os.makedirs(output_dir, exist_ok=True)
    print(f"Diretório de saída criado: {output_dir}")

    # Gerando diversos gráficos
    plota_pivot_table(sinasc, 'IDADEMAE', 'DTNASC', 'count', 'quantidade de nascimento', 'data de nascimento')
    plt.savefig(os.path.join(output_dir, 'A) quantidade de nascimento.png'))
    plt.close()

    plota_pivot_table(sinasc, 'IDADEMAE', ['DTNASC', 'SEXO'], 'mean', 'media idade mae', 'data de nascimento', 'unstack')
    plt.savefig(os.path.join(output_dir, 'B) media idade mae por sexo.png'))
    plt.close()

    plota_pivot_table(sinasc, 'PESO', ['DTNASC', 'SEXO'], 'mean', 'media peso bebe', 'data de nascimento', 'unstack')
    plt.savefig(os.path.join(output_dir, 'C) media peso bebe por sexo.png'))
    plt.close()

    plota_pivot_table(sinasc, 'PESO', 'ESCMAE', 'median', 'apgar1 medio', 'gestacao', 'sort')
    plt.savefig(os.path.join(output_dir, 'D) media apgar1 por escolaridade mae.png'))
    plt.close()

    plota_pivot_table(sinasc, 'APGAR1', 'GESTACAO', 'mean', 'apgar1 medio', 'gestacao', 'sort')
    plt.savefig(os.path.join(output_dir, 'E) media apgar1 por gestacao.png'))
    plt.close()

    plota_pivot_table(sinasc, 'APGAR5', 'GESTACAO', 'mean', 'apgar5 medio', 'gestacao', 'sort')
    plt.savefig(os.path.join(output_dir, 'F) media apgar5 por gestacao.png'))
    plt.close()

    print(f"Gráficos para {mes} gerados com sucesso!")

print("Todos os gráficos foram gerados com sucesso!")
