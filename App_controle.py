import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime
import os
import io

#===============================
#Carregando o CSS3
#===============================
def load_css():
    with open(".streamlit/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#carrega o css
load_css()

st.set_page_config(page_title="App Controle de Contratos", page_icon="📊", layout="wide")

st.title("📈 Dashboard de Contratos")
st.markdown("Visualize a distribuição de contratos abaixo.")

# ==============================
# Upload da planilha
# ==============================
with st.sidebar:
    st.header("📤 Carregar Planilha")
    upload_file = st.file_uploader(
        "Arraste sua planilha aqui",
        type=["xlsx", "csv", "xls"],
        help="Formatos suportados: Excel (.xlsx, .xls) e CSV (.csv)"
    )


# ==============================
# Função de carregamento
# ==============================
@st.cache_data
def carregar_tabela(arquivo, skiprows=0):
    ext = os.path.splitext(arquivo.name)[1].lower()

    try:
        if ext in [".csv", ".txt"]:
            df = pd.read_csv(arquivo, sep=";", skiprows=skiprows, low_memory=False, decimal=',')
        elif ext in [".xls", ".xlsx", ".xlsm", ".xlsb"]:
            df = pd.read_excel(arquivo, skiprows=skiprows)
        elif ext in [".ods", ".ots"]:
            df = pd.read_excel(arquivo, engine="odf", skiprows=skiprows)
        elif ext in [".xml", ".html"]:
            df = pd.read_html(arquivo)[0]
            if skiprows > 0:
                df = df.iloc[skiprows:].reset_index(drop=True)
        elif ext == ".json":
            df = pd.read_json(arquivo, orient="records")
            if skiprows > 0:
                df = df.iloc[skiprows:].reset_index(drop=True)
        else:
            raise ValueError(f"Formato de arquivo não suportado: {ext}")

        # Limpa nomes de colunas
        df.columns = [str(col).strip() for col in df.columns]

        return df

    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
        return None


def converter_datas(df):
    """Converte colunas de data para formato datetime"""
    colunas_data = ['INÍCIO', 'FIM', 'PRICE LIST-VIGÊNCIA']

    for coluna in colunas_data:
        if coluna in df.columns:
            try:
                # Tenta converter para datetime
                df[coluna] = pd.to_datetime(df[coluna], errors='coerce', dayfirst=True)
            except Exception as e:
                st.warning(f"⚠️ Não foi possível converter {coluna}: {e}")

    return df


# ==============================
# Funções para download
# ==============================
def limpar_dataframe_para_download(df):
    """Prepara dataframe para download limpando valores"""
    df_limpo = df.copy()

    # Substitui todos os valores nulos por string vazia
    df_limpo = df_limpo.fillna('')

    # Limpeza em todas as colunas
    for coluna in df_limpo.columns:
        # Converte para string e remove valores indesejados
        df_limpo[coluna] = df_limpo[coluna].astype(str)
        df_limpo[coluna] = df_limpo[coluna].replace(['None', 'nan', 'NaN', 'NaT', '<NA>'], '', regex=True)

        # Formata datas se for datetime no original
        if pd.api.types.is_datetime64_any_dtype(df[coluna]):
            mask = df[coluna].notna()
            df_limpo.loc[mask, coluna] = df.loc[mask, coluna].dt.strftime('%d/%m/%Y')

    return df_limpo


def converter_para_csv(df):
    """Converte DataFrame para CSV"""
    return df.to_csv(index=False, sep=';', encoding='utf-8-sig')


def converter_para_excel(df):
    """Converte DataFrame para Excel"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados_Contratos')
    return output.getvalue()


def converter_para_json(df):
    """Converte DataFrame para JSON"""
    return df.to_json(orient='records', indent=2, force_ascii=False)


# ==============================
# Interface principal
# ==============================
if upload_file is not None:
    try:
        # Configuração fixa para pular 4 linhas
        pular_linhas = 4

        # Carrega os dados
        df = carregar_tabela(upload_file, skiprows=pular_linhas)

        if df is None or df.empty:
            st.error("O arquivo está vazio ou não pôde ser processado.")
            st.stop()

        # CONVERTE COLUNAS DE DATA
        df = converter_datas(df)
        df = df.replace([None, ""], np.nan)

        # Mostrar preview dos dados
        st.subheader("👀 Preview dos Dados")
        st.dataframe(df.head(), use_container_width=True)

        # Mostrar informações sobre conversão de datas
        colunas_data = ['INÍCIO', 'FIM', 'PRICE LIST-VIGÊNCIA']
        for coluna in colunas_data:
            if coluna in df.columns and pd.api.types.is_datetime64_any_dtype(df[coluna]):
                dados_validos = df[coluna].notna().sum()
                st.sidebar.success(f"📅 {coluna}: {dados_validos} datas válidas")

        # ==============================
        # FILTROS NO SIDEBAR
        # ==============================
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎛️ Filtros")

        # Mantém a ordem original das colunas, mas remove as específicas
        colunas = df.columns.tolist()

        # Lista de colunas para REMOVER dos filtros
        colunas_remover = ['SALDO', 'PERCENTUAL TEÓRICO', 'PERCENTUAL SEGREGADO']

        # Filtra apenas as colunas que devem aparecer nos filtros
        colunas_filtro = [col for col in colunas if col not in colunas_remover]

        # Inicializa filtros apenas para as colunas que serão mostradas
        if "filtros" not in st.session_state:
            st.session_state["filtros"] = {col: [] for col in colunas_filtro}

        # Botão limpar filtros
        if st.sidebar.button("🧹 Limpar Filtros", use_container_width=True):
            # Limpa todos os filtros das colunas visíveis
            for coluna in colunas_filtro:
                st.session_state[f"multiselect_{coluna}"] = []
            st.session_state["filtros"] = {col: [] for col in colunas_filtro}
            st.rerun()

        # Criação dos filtros interligados (apenas para colunas selecionadas)
        for coluna in colunas_filtro:
            mascara_outras = pd.Series(True, index=df.index)
            for outra_col, escolhas in st.session_state["filtros"].items():
                if outra_col != coluna and escolhas:
                    if pd.api.types.is_datetime64_any_dtype(df[outra_col]):
                        # Para datas, converte as escolhas para datetime
                        datas_escolhidas = [pd.to_datetime(esc) for esc in escolhas]
                        mascara_outras &= df[outra_col].isin(datas_escolhidas)
                    else:
                        mascara_outras &= df[outra_col].astype(str).isin([str(v) for v in escolhas])

            temp_df = df[mascara_outras]

            # Prepara opções baseadas no tipo de dados
            if pd.api.types.is_datetime64_any_dtype(df[coluna]):
                # Para datas, formata bonitinho
                opcoes = sorted(temp_df[coluna].dropna().unique())
                opcoes_str = [d.strftime('%d/%m/%Y') for d in opcoes]
            else:
                opcoes = sorted(temp_df[coluna].dropna().astype(str).unique().tolist())
                opcoes_str = opcoes

            # Usa a chave única para cada multiselect
            escolha = st.sidebar.multiselect(
                f"**{coluna}:**",
                options=opcoes_str,
                default=st.session_state.get(f"multiselect_{coluna}", []),
                key=f"multiselect_{coluna}",
                placeholder=f"Selecione {coluna}..."
            )

            # Atualiza os filtros na session state
            st.session_state["filtros"][coluna] = escolha

        # Aplica filtros combinados
        mascara_final = pd.Series(True, index=df.index)
        for coluna, escolhas in st.session_state["filtros"].items():
            if escolhas:
                if pd.api.types.is_datetime64_any_dtype(df[coluna]):
                    # Para datas, converte de volta para datetime
                    datas_escolhidas = [pd.to_datetime(esc, dayfirst=True) for esc in escolhas]
                    mascara_final &= df[coluna].isin(datas_escolhidas)
                else:
                    mascara_final &= df[coluna].astype(str).isin([str(v) for v in escolhas])

        df_filtrado = df[mascara_final].copy()

        # Mostrar estatísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📈 Total de Registros", len(df))
        with col2:
            st.metric("✅ Filtrados", len(df_filtrado))
        with col3:
            st.metric("📊 % do Total", f"{(len(df_filtrado) / len(df) * 100):.1f}%" if len(df) > 0 else "0%")

        # ==============================
        # ANÁLISE VISUAL
        # ==============================
        if len(df_filtrado) > 0:
            st.markdown("---")
            st.subheader("📊 Análise Visual")

            # 1. GRÁFICO DE PIZZA - COLUNAS 2 E 7
            if df_filtrado.shape[1] >= 7:
                col_empresa = df_filtrado.columns[1]
                col_valor = df_filtrado.columns[6]

                # Converter valores da coluna 7 para numérico
                df_filtrado[col_valor] = pd.to_numeric(df_filtrado[col_valor], errors='coerce')

                df_grouped = (
                    df_filtrado.groupby(col_empresa)[col_valor]
                    .sum()
                    .reset_index()
                    .sort_values(by=col_valor, ascending=False)
                )

                if not df_grouped.empty:
                    fig_valores = px.pie(
                        df_grouped,
                        names=col_empresa,
                        values=col_valor,
                        title=f"Distribuição de {col_valor} por {col_empresa}",
                        hole=0.3
                    )
                    fig_valores.update_traces(textinfo='percent+label')
                    st.plotly_chart(fig_valores, use_container_width=True)
                else:
                    st.info("Nenhum valor numérico encontrado na coluna 7 para gerar o gráfico.")
            else:
                st.warning("A planilha precisa ter pelo menos 7 colunas para gerar este gráfico.")

            # 2. GRÁFICO DE GANTT PARA DATAS DE CONTRATOS
            st.markdown("---")
            st.subheader("📅 Linha do Tempo dos Contratos")

            if len(df_filtrado.columns) >= 4:
                col_inicio = df_filtrado.columns[2]  # Coluna 3
                col_fim = df_filtrado.columns[3]  # Coluna 4
                col_empresa = df_filtrado.columns[1]  # Coluna 2

                if (pd.api.types.is_datetime64_any_dtype(df_filtrado[col_inicio]) and
                        pd.api.types.is_datetime64_any_dtype(df_filtrado[col_fim])):

                    gantt_data = []
                    for idx, row in df_filtrado.iterrows():
                        if pd.notna(row[col_inicio]) and pd.notna(row[col_fim]):
                            gantt_data.append({
                                'Nome': f"{row[col_empresa]} - Contrato {idx}",
                                'Start': row[col_inicio],
                                'Finish': row[col_fim],
                                'Empresa': row[col_empresa],
                                'Duracao': (row[col_fim] - row[col_inicio]).days
                            })

                    if gantt_data:
                        df_gantt = pd.DataFrame(gantt_data)

                        fig_gantt = px.timeline(
                            df_gantt,
                            x_start="Start",
                            x_end="Finish",
                            y="Nome",
                            color="Empresa",
                            title="Linha do Tempo dos Contratos",
                            hover_data={"Duracao": True, "Empresa": True},
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                        fig_gantt.update_yaxes(autorange="reversed")
                        fig_gantt.update_layout(height=400, showlegend=True)
                        st.plotly_chart(fig_gantt, use_container_width=True)

                        # ==============================
                        # AVISO DE CONTRATOS PRÓXIMOS DO VENCIMENTO - VERSÃO COMPACTA
                        # ==============================

                        # Data atual
                        data_atual = pd.Timestamp.now()
                        data_limite = data_atual + pd.DateOffset(years=10)

                        # Filtra contratos
                        contratos_proximos_vencimento = []
                        contratos_vencidos = []

                        for idx, row in df_filtrado.iterrows():
                            if pd.notna(row[col_fim]):
                                if row[col_fim] < data_atual:
                                    contratos_vencidos.append({
                                        'Empresa': row[col_empresa],
                                        'Data_Fim': row[col_fim],
                                        'Dias_Atraso': (data_atual - row[col_fim]).days
                                    })
                                elif row[col_fim] <= data_limite:
                                    dias_para_vencer = (row[col_fim] - data_atual).days
                                    contratos_proximos_vencimento.append({
                                        'Empresa': row[col_empresa],
                                        'Data_Fim': row[col_fim],
                                        'Dias_Para_Vencer': dias_para_vencer
                                    })

                        # MÉTRICAS RÁPIDAS
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                "🔴 Vencidos",
                                len(contratos_vencidos),
                                help="Contratos com data de vencimento passada"
                            )

                        with col2:
                            # Conta contratos críticos (até 30 dias)
                            criticos = len([c for c in contratos_proximos_vencimento if c['Dias_Para_Vencer'] <= 30])
                            st.metric(
                                "🟠 Críticos",
                                criticos,
                                help="Vencem em até 30 dias"
                            )

                        with col3:
                            # Total próximos do vencimento
                            st.metric(
                                "🟡 Próximos 10 anos",
                                len(contratos_proximos_vencimento),
                                help="Vencem nos próximos 10 anos"
                            )

                        # ALERTAS EM CONTAINERS EXPANSÍVEIS
                        if contratos_vencidos or contratos_proximos_vencimento:
                            st.markdown("### ⚠️ Alertas de Vencimento")

                            # Contratos Vencidos - Expansível
                            if contratos_vencidos:
                                with st.expander(f"🔴 Contratos Vencidos ({len(contratos_vencidos)})", expanded=False):
                                    df_vencidos = pd.DataFrame(contratos_vencidos)
                                    df_vencidos['Data_Fim'] = df_vencidos['Data_Fim'].dt.strftime('%d/%m/%Y')
                                    df_vencidos = df_vencidos.sort_values('Dias_Atraso', ascending=False)

                                    for i, (_, contrato) in enumerate(df_vencidos.iterrows()):
                                        if i < 5:  # Mostra apenas os 5 primeiros
                                            st.write(f"**{contrato['Empresa']}** - {contrato['Data_Fim']} "
                                                     f"({contrato['Dias_Atraso']} dias atrás)")
                                        elif i == 5:
                                            st.caption(f"... e mais {len(contratos_vencidos) - 5} contratos vencidos")

                            # Contratos Próximos - Expansível
                            if contratos_proximos_vencimento:
                                with st.expander(f"🟡 Próximos do Vencimento ({len(contratos_proximos_vencimento)})",
                                                 expanded=False):
                                    # Agrupa por nível de urgência
                                    criticos = [c for c in contratos_proximos_vencimento if c['Dias_Para_Vencer'] <= 30]
                                    alertas = [c for c in contratos_proximos_vencimento if
                                               30 < c['Dias_Para_Vencer'] <= 90]
                                    atencao = [c for c in contratos_proximos_vencimento if
                                               90 < c['Dias_Para_Vencer'] <= 365]
                                    normais = [c for c in contratos_proximos_vencimento if c['Dias_Para_Vencer'] > 365]

                                    if criticos:
                                        st.write("**🔴 Críticos (até 30 dias):**")
                                        for contrato in sorted(criticos, key=lambda x: x['Dias_Para_Vencer'])[:3]:
                                            data_formatada = contrato['Data_Fim'].strftime('%d/%m/%Y')
                                            st.write(
                                                f"- {contrato['Empresa']} - {data_formatada} ({contrato['Dias_Para_Vencer']} dias)")

                                    if alertas:
                                        st.write("**🟠 Alertas (31-90 dias):**")
                                        for contrato in sorted(alertas, key=lambda x: x['Dias_Para_Vencer'])[:3]:
                                            data_formatada = contrato['Data_Fim'].strftime('%d/%m/%Y')
                                            st.write(
                                                f"- {contrato['Empresa']} - {data_formatada} ({contrato['Dias_Para_Vencer']} dias)")

                                    if atencao:
                                        st.write("**🟡 Atenção (3-12 meses):**")
                                        for contrato in sorted(atencao, key=lambda x: x['Dias_Para_Vencer'])[:3]:
                                            data_formatada = contrato['Data_Fim'].strftime('%d/%m/%Y')
                                            st.write(
                                                f"- {contrato['Empresa']} - {data_formatada} ({contrato['Dias_Para_Vencer']} dias)")

                                    # MOSTRAR CONTRATOS NORMAIS (VERDES) TAMBÉM
                                    if normais:
                                        st.write("**🟢 Normais (acima de 1 ano):**")
                                        # Mostra os 5 mais próximos entre os "normais"
                                        for contrato in sorted(normais, key=lambda x: x['Dias_Para_Vencer'])[:5]:
                                            data_formatada = contrato['Data_Fim'].strftime('%d/%m/%Y')
                                            st.write(
                                                f"- {contrato['Empresa']} - {data_formatada} ({contrato['Dias_Para_Vencer']} dias)")

                                        # Se tiver mais de 5, mostra contador
                                        if len(normais) > 5:
                                            st.caption(
                                                f"... e mais {len(normais) - 5} contratos com vencimento acima de 1 ano")

            # 3. GRÁFICO DE BARRAS - PORCENTAGENS POR EMPRESA
            st.markdown("---")
            st.subheader("🏢 Comparação de Porcentagens por Empresa")

            if len(df_filtrado.columns) >= 10:
                col_perc1 = df_filtrado.columns[8]  # Coluna 9
                col_perc2 = df_filtrado.columns[9]  # Coluna 10
                col_empresa = df_filtrado.columns[1]  # Coluna 2

                df_filtrado[col_perc1] = pd.to_numeric(df_filtrado[col_perc1], errors='coerce')
                df_filtrado[col_perc2] = pd.to_numeric(df_filtrado[col_perc2], errors='coerce')

                mask_validas = df_filtrado[col_perc1].notna() & df_filtrado[col_perc2].notna()
                df_comparacao = df_filtrado[mask_validas].copy()

                if len(df_comparacao) > 0:
                    df_empresas = df_comparacao.groupby(col_empresa).agg({
                        col_perc1: 'mean',
                        col_perc2: 'mean',
                        col_empresa: 'count'
                    }).rename(columns={col_empresa: 'QTD_CONTRATOS'}).reset_index()

                    # Mostra apenas as top 10 empresas por padrão
                    df_top = df_empresas.nlargest(10, col_perc1)

                    fig_barras = px.bar(
                        df_top,
                        x=col_empresa,
                        y=[col_perc1, col_perc2],
                        title=f"Comparação: {col_perc1} vs {col_perc2} por Empresa",
                        barmode='group',
                        color_discrete_sequence=['#FF6B6B', '#45B7D1'],
                        labels={'value': 'Porcentagem (%)', 'variable': 'Tipo'}
                    )
                    fig_barras.update_layout(yaxis_tickformat='.1%', xaxis_tickangle=-45)
                    st.plotly_chart(fig_barras, use_container_width=True)

            # Tabela completa COM TRATAMENTO DE NONE
            with st.expander("📋 Ver Dados Filtrados Completos"):
                # Aplica limpeza em todo o dataframe
                df_completo_limpo = limpar_dataframe_para_download(df_filtrado)

                st.dataframe(df_completo_limpo, use_container_width=True)
                st.caption(f"📊 Total de registros: {len(df_completo_limpo)}")

        else:
            st.warning("⚠️ Nenhum dado encontrado com os filtros atuais.")

        # ==============================
        # BOTÕES DE DOWNLOAD - SEMPRE NO FINAL
        # ==============================
        st.markdown("---")
        st.subheader("📥 Exportar Dados Completos")

        # Prepara dados limpos para download (DADOS COMPLETOS, NÃO FILTRADOS)
        df_para_download = limpar_dataframe_para_download(df)  # Usa df (completo) em vez de df_filtrado

        col_dl1, col_dl2, col_dl3 = st.columns(3)

        with col_dl1:
            # Download CSV
            csv_data = converter_para_csv(df_para_download)
            st.download_button(
                label="💾 Baixar CSV Completo",
                data=csv_data,
                file_name="contratos_completos.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_dl2:
            # Download Excel
            excel_data = converter_para_excel(df_para_download)
            st.download_button(
                label="📊 Baixar Excel Completo",
                data=excel_data,
                file_name="contratos_completos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col_dl3:
            # Download JSON
            json_data = converter_para_json(df_para_download)
            st.download_button(
                label="🔤 Baixar JSON Completo",
                data=json_data,
                file_name="contratos_completos.json",
                mime="application/json",
                use_container_width=True
            )

        st.info("💡 Os downloads incluem todos os dados da planilha original, não apenas os filtrados.")

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {str(e)}")

else:
    st.info("📁 Por favor, faça o upload de uma planilha para começar.")