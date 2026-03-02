import streamlit as st
import pandas as pd
import json
import glob
from datetime import datetime
from pathlib import Path

import altair as alt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import log

# Definindo este módulo no log e nome do arquivo de saída
logger = log.logging.getLogger("app")
log.set_file(f"{Path(__file__).stem}.log")

# Configuração da página
st.set_page_config(page_title="Desafio #1", layout="wide")
st.subheader("🐌 Desafio Corpinho Fitness 2026")


# Layout da página em Abas
tab1, tab2 = st.tabs(["📈 Dashboard", "🎲 Base de Dados (editável)"])

# Carrega os arquivos de dados em um único DataFrame
@st.cache_data
def load_data():
    logger.debug("load_data()")
    all_data = []
    files = glob.glob("data_*.json")
    logger.debug(files)

    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = json.load(f)
                # reformata os dados
                name = content['name']
                for bio in content['biometrics']:
                    bio['name'] = name # para facilitar o agrupamento
                    bio['date'] = pd.to_datetime(bio['date'], format='%Y-%m-%d') # ISO
                    all_data.append(bio)
        except Exception as e:
            logger.exception(". ", f"Erro ao ler {file}: {e}")
            st.error(f"Erro ao ler {file}: {e}")
   
    return pd.DataFrame(all_data)

@st.cache_data
def load_fake_data():
    logger.debug("load_fake_data()")
    data = {
        "name":               ["Neia",      "Simone",    "Aline",     "Giba",      "Giba",      "Flavio",    "Barros",    "Giba",      "Giba",      "Giba",      "Giba",      "Giba",      "Giba",      "Giba",      "Giba",      "Giba",      "Giba"],
        "date":               ["2026-02-01","2026-02-01","2026-02-01","2026-02-10","2026-02-10","2026-02-01","2026-02-01","2026-02-04","2026-02-09","2026-02-10","2026-02-15","2026-02-17","2026-02-19","2026-02-22","2026-02-22","2026-02-26","2026-02-26"],
        "total_weight":       [71.75,       79.50,       60.15,       112.90,      112.60,      94.15,       103.65,      114.95,      114.00,      110.90,      110.50,      109.10,      109.85,      109.45,      109.00,      108.05,      107.70],
        "fat_pct":            [0,           0,           0,           31.00,       36.10,       0,           0,           35.30,       35.40,       35.60,       35.80,       35.80,       35.70,       36.00,       36.10,       36.80,       37.00],
        "fat_weight":         [0,           0,           0,           0,           40.70,       0,           0,           0,           0,           0,           0,           0,           0,           0,           0,           0,           0],
        "nofat_pct":          [0,           0,           0,           30.60,       0,           0,           0,           0,           0,           0,           0,           0,           0,           0,           0,           0,           0],
        "nofat_weight":       [0,           0,           0,           0,           65.70,       0,           0,           0,           0,           0,           0,           0,           0,           0,           0,           0,           0],
        "water_weight":       [0,           0,           0,           0,           48.10,       0,           0,           0,           0,           0,           0,           0,           0,           0,           0,           0,           0],
    }
    data['date'] = pd.to_datetime(data['date'])
    return pd.DataFrame(data)

#@st.cache_data
def load_csv_data():
    logger.debug("load_csv_data()")
    file = "dados.csv"
    try:
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])
    except FileNotFoundError:
        logger.exception(". ", f"Erro ao ler {file}: {e}")
        st.error(f"Erro ao ler {file}: {e}")
        df= None

    return df

# Gráfico: Comparativo de Peso 
def chart_weight_all(df:pd.DataFrame):
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('date:T', title='Data de Medição'),
        y=alt.Y('total_weight:Q', title='Peso (kg)', scale=alt.Scale(zero=False)),
        color=alt.Color('name:N', legend=alt.Legend(title="Usuário")),
        tooltip=['name', 'date', 'total_weight', 'fat_pct', 'fat_weight', 'nofat_pct', 'nofat_weight']
    ).properties(
        height=300
    ).interactive()
    return chart

# Gráfico: Comparativo individual 
def chart_weight_one(df:pd.DataFrame, name:str):
    df = df.loc[df["name"] == name]

    # Converter "dados para o formato "long"
    df_weights = df.melt(id_vars=["date"], 
                         value_vars=["total_weight","fat_weight","nofat_weight"],
                         var_name="type", value_name="kg")
    df_percents = df.melt(id_vars=["date"], 
                          value_vars=["fat_pct","nofat_pct"],
                          var_name="type", value_name="pct")

    # 1. Preparação dos dados (Exemplo de estrutura baseada no seu relato)
    # df_weights possui: date, kg, type
    # df_percents possui: date, pct, type

    def create_interactive_chart(df_weights, df_percents, name):
        # Criar figura com eixo Y secundário
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Série de Pesos - Linha contínua + Círculos
        for t in df_weights['type'].unique():
            data = df_weights[df_weights['type'] == t]
            fig.add_trace(
                go.Scatter(
                    x=data['date'], y=data['kg'], 
                    name=f"{t} (kg)",
                    mode='lines+markers',
                    marker=dict(symbol='circle', size=8)
                ), secondary_y=False
            )

        # Série de Percentuais - Linha tracejada + Diamantes
        for t in df_percents['type'].unique():
            data = df_percents[df_percents['type'] == t]
            fig.add_trace(
                go.Scatter(
                    x=data['date'], y=data['pct'], 
                    name=f"{t} (%)",
                    mode='lines+markers',
                    line=dict(dash='dot'), # Linha pontilhada para diferenciar
                    marker=dict(symbol='diamond', size=10)
                ), secondary_y=True
            )

        # Configurações de Layout e Melhorias de UX
        fig.update_layout(
            title=f"👤 Evolução: {name}",
            xaxis_title="Data",
            dragmode='pan',  # Clique e arraste para navegar (Pan)
            hovermode="x unified",
            template="plotly_white",
            legend=dict(orientation="h", y=-0.4), # Legenda abaixo para sobrar espaço
            margin=dict(l=10, r=10, t=50, b=50),
            height=350
        )
        
        # Configurar títulos dos eixos
        fig.update_yaxes(title_text="Peso (kg)", secondary_y=False, zeroline=False)
        fig.update_yaxes(title_text="Percentual (%)", secondary_y=True, zeroline=False)

        # Ativar o zoom automático e manter escalas proporcionais
        fig.update_xaxes(rangeslider_visible=False)

        return fig

    # No seu loop de exibição do Streamlit:
    st.plotly_chart(create_interactive_chart(df_weights, df_percents, name), use_container_width=True)

    return None

# Gráfico: Comparativo de Peso 
def chart_weight_one_altair2(df:pd.DataFrame, name:str):
    df = df.loc[df["name"] == name]

    # Converter "dados para o formato "long"
    df_weights = df.melt(id_vars=["date"], 
                         value_vars=["total_weight","fat_weight","nofat_weight"],
                         var_name="type", value_name="kg")
    df_percents = df.melt(id_vars=["date"], 
                          value_vars=["fat_pct","nofat_pct"],
                          var_name="type", value_name="pct")

    # 1. Criar UMA única seleção de intervalo para o eixo X (o que sincroniza o tempo)
    # Se você quiser zoom no Y também, usamos 'scales' bind para o componente principal
    selection = alt.selection_interval(bind='scales')#, encodings=['x'])


    # 2. Criar o gráfico base (compartilhado)
    base = alt.Chart(df_weights).encode(
        x=alt.X("date:T", title="Data")
    ).add_params(
        selection
    )

    # 3. Layer de Pesos (Eixo Y Esquerdo - ENCODING COMPLETO)
    # Note que aqui usamos o df_weights específico
    layer_weights = alt.Chart(df_weights).mark_line(point=True).encode(
        x=alt.X("date:T"),
        y=alt.Y("kg:Q", title="Peso (kg)", scale=alt.Scale(zero=False)),
        color=alt.Color("type:N", legend=alt.Legend(title="Pesos", orient="top-left"))
    )

    # 4. Layer de Percentuais (Eixo Y Direito - ENCODING COMPLETO)
    # Note que aqui usamos o df_percents específico
    layer_percents = alt.Chart(df_percents).mark_line(
        strokeDash=[5,5], 
        point=alt.OverlayMarkDef(shape="diamond", size=80)
    ).encode(
        x=alt.X("date:T"),
        y=alt.Y("pct:Q", title="Percentual (%)", axis=alt.Axis(orient="right"), scale=alt.Scale(zero=False)),
        color=alt.Color("type:N", legend=alt.Legend(title="Percentuais", orient="top-right"))
    )

    # 5. A GRANDE SACADA: Unir as camadas e forçar a resolução
    # O segredo é que o layer final herda a seleção do eixo X
    final_chart = alt.layer(
        layer_weights, 
        layer_percents
    ).resolve_scale(
        y='independent'
    ).add_params(
        selection # Aplicamos a seleção no objeto unificado
    ).properties(
        title=f"📊 Evolução: {name} (Zoom Habilitado)",
        width='container',
        height=450
    )

    st.altair_chart(final_chart, use_container_width=True)

    return final_chart

# Gráfico: Comparativo de Peso 
def chart_weight_one_altair1(df:pd.DataFrame, name:str):
    df = df.loc[df["name"] == name]

    # Converter "dados para o formato "long"
    df_weights = df.melt(id_vars=["date"], 
                         value_vars=["total_weight","fat_weight","nofat_weight"],
                         var_name="type", value_name="kg")
    df_percents = df.melt(id_vars=["date"], 
                          value_vars=["fat_pct","nofat_pct"],
                          var_name="type", value_name="pct")

    # Criar a seleção de intervalo para zoom e pan para que funcionem de forma síncrona para ambos os eixos Y (kg e %).
    selection = alt.selection_interval(bind='scales')

    # O parâmetro 'encodings' garante que o zoom afete X e Y simultaneamente
    zoom_selection = alt.selection_interval(bind='scales', encodings=['x', 'y'])

    # Layer de Pesos (Eixo Y Esquerdo)
    # Criamos a base, adicionamos a linha e depois o ponto
    base_weights = alt.Chart(df_weights).encode(
        x=alt.X("date:T", title="Data"),
        y=alt.Y("kg:Q", title="Peso (kg)", scale=alt.Scale(zero=False)),
        color=alt.Color("type:N")#, legend=alt.Legend(orient="bottom-left"))
    ).add_params(zoom_selection) # <--- Zoom para o eixo Y esquerdo
#    line_weights = base_weights.mark_line()
#    points_weights = base_weights.mark_point(size=60, filled=True).encode(
#        tooltip=["date:T", "type:N", "kg:Q"]
#    )
#    layer_weights = alt.layer(line_weights, points_weights)
    layer_weights = alt.layer(
        base_weights.mark_line(),
        base_weights.mark_point(size=60, filled=True)
    )

    # Layer de Percentuais (Eixo Y Direito)
    base_percents = alt.Chart(df_percents).encode(
        x="date:T",
        y=alt.Y("pct:Q", title="Percentual (%)", axis=alt.Axis(orient="right"), scale=alt.Scale(zero=False)),
        color=alt.Color("type:N")#, legend=alt.Legend(orient="bottom-right"))
    ).add_params(zoom_selection) # <--- Zoom para o eixo Y esquerdo
#    line_percents = base_percents.mark_line(strokeDash=[5,5])
#    points_percents = base_percents.mark_point(size=80, shape="diamond", filled=True).encode(
#        tooltip=["date:T", "type:N", "pct:Q"]
#    )
#    layer_percents = alt.layer(line_percents, points_percents)
    layer_percents = alt.layer(
        base_percents.mark_line(strokeDash=[5,5]),
        base_percents.mark_point(size=80, shape="diamond", filled=True)
    )

    # Combinar os dois gráficos
#    chart = alt.layer(
#        layer_weights, layer_percents
#    ).resolve_scale(
#        y='independent'  # Permite escalas diferentes para kg e %
#    ).add_params(
#        selection        # Habilita o zoom interativo em ambos os eixos
#    ).properties(
#        title=f"👤 Evolução Individual: {name}"
#        #,height=400
##        width='container',
##        height=450
#    )#.interactive()

    # 4. A CHAVE PARA O ZOOM: Combinar, Resolver e Adicionar Parâmetros no Final
    chart = alt.layer(
        layer_weights, 
        layer_percents
    ).resolve_scale(
        y='independent'
#    ).add_params(
#        selection # <--- Aplicar ao layer final unificado
    ).properties(
        title=f"📊 Evolução: {name}",
        width='container',
        height=450
    )    
    return chart


# Gráfico: Comparativo de Peso 
def chart_weight_one_altair3(df:pd.DataFrame, name:str):
    df = df.loc[df["name"] == name]

    # Converter "dados para o formato "long"
    df_weights = df.melt(id_vars=["date"], 
                         value_vars=["total_weight","fat_weight","nofat_weight"],
                         var_name="type", value_name="kg")
    df_percents = df.melt(id_vars=["date"], 
                          value_vars=["fat_pct","nofat_pct"],
                          var_name="type", value_name="pct")

    # Gráfico de pesos (kg) - eixo y esquerdo
    line_weights = alt.Chart(df_weights).mark_line().encode(
        x="date:T",
        y=alt.Y("kg:Q", axis=alt.Axis(title="Peso (kg)")),
        color="type:N",
        #tooltip=["date:T","type:N","kg:Q"]
    )
    points_weights = alt.Chart(df_weights).mark_point(size=60).encode(
        x="date:T",
        y="kg:Q",
        color="type:N",
        tooltip=["date:T","type:N","kg:Q"]
    )

    # Gráfico de percentuais (%) - eixo y direito
    line_percents = alt.Chart(df_percents).mark_line(strokeDash=[3,5]).encode(
        x="date:T",
        y=alt.Y("pct:Q", axis=alt.Axis(title="Percentual (%)", orient="right")),
        color="type:N",
        shape=alt.Shape("type:N"),
        #tooltip=["date:T","type:N","pct:Q"]
    )
    points_percents = alt.Chart(df_percents).mark_point(size=60, shape="diamond").encode(
        x="date:T",
        y=alt.Y("pct:Q", axis=alt.Axis(title="Percentual (%)", orient="right")),
        color="type:N",
        tooltip=["date:T","type:N","pct:Q"]
    )

    # Combinar os dois gráficos
    chart = alt.layer(
        line_weights, 
        points_weights, 
        line_percents, 
        points_percents
    ).resolve_scale(
        y='independent'
    ).properties(
        title=f"👤 Evolução Individual: {name}"
        #,height=400
    )#.interactive()

    return chart



def run():
    logger.debug("run()")
#    df = load_data()
#    df = load_fake_data()
    df = load_csv_data()
    print(df)

    if df.empty:
        logger.warning("Nenhum dado encontrado.")
        st.warning("Nenhum dado encontrado.")
    else:

        # --- FILTRO NA BARRA LATERAL ---
        st.sidebar.subheader("Filtros de Visualização")

        # Filtro de Nomes
        all_names = sorted(df['name'].unique())
        filter_names = st.sidebar.multiselect("👤 Selecionar Pessoas", all_names, default=all_names)

        # Filtro de Data
        min_date = df['date'].min().to_pydatetime()
        max_date = df['date'].max().to_pydatetime()
        filter_date = st.sidebar.slider("Período", min_date, max_date, (min_date, max_date))

        # Aplicação dos filtros no DF principal
        mask = (df['name'].isin(filter_names)) & (df['date'] >= filter_date[0]) & (df['date'] <= filter_date[1])
        filtered_df = df.loc[mask]

        # --- PAGINA PRINCIPAL ---

        with tab1:
            st.write("📉 Evolução Geral")
            st.altair_chart(chart_weight_all(filtered_df), width='stretch')
            
            with st.expander("🎲 Base de Dados", expanded=False):
                st.write(filtered_df)
            print(filtered_df)

            #st.write("📈 Evolução Individual")
            names = filtered_df['name'].unique()
            for name in names:
                #st.altair_chart(chart_weight_one(filtered_df, name), width='stretch')
                chart_weight_one(filtered_df, name)        

        with tab2:

            # Tabela com os dados é editável
            df = edited_df = st.data_editor(
                df,
                num_rows="dynamic",   # permite adicionar/remover linhas
                use_container_width=True
            )
            
            if st.button("Salvar alterações"):
                edited_df.to_csv("dados.csv", index=False)
                st.success("Dados salvos em 'dados.csv'")
                st.rerun()


if __name__ == '__main__':
    print("-" * 40)
    run()