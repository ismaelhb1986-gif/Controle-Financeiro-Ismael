import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import calendar
from datetime import datetime

# Configuração inicial
st.set_page_config(page_title="Controle Financeiro", layout="wide", page_icon="💰")

# --- CUSTOMIZAÇÃO DE CSS AVANÇADA (ESTILO FINTECH + RESPONSIVIDADE) ---
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500&display=swap');

        /* --- 1. REGRAS DE RESPONSIVIDADE E ZOOM MOBILE (NOVO) --- */
        html, body {
            max-width: 100%;
            overflow-x: hidden;
            touch-action: manipulation;
        }

        @media (max-width: 768px) {
            html, body, [class*="st-"] { font-size: 14px !important; }
            h1 { font-size: 1.5rem !important; }
            h2 { font-size: 1.3rem !important; }
            h3 { font-size: 1.1rem !important; }
            
            /* Permite que as tabelas tenham barra de rolagem no celular */
            .stDataFrame, div[data-testid="stDataFrameResizable"] {
                width: 100% !important;
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch;
            }
            
            /* Reduz o respiro interno (padding) dos formulários para não espremer no celular */
            [data-testid="stForm"] { padding: 15px !important; }
        }

        /* --- 2. Reset de Fundo, Margens e Fontes Globais --- */
        .stApp {
            background-color: #f8fafc !important; 
            font-family: 'Inter', sans-serif !important;
        }
        
        .block-container {
            padding-top: 3rem !important;
            padding-bottom: 2rem !important;
        }
        header[data-testid="stHeader"] { background-color: transparent !important; }

        /* --- 3. Centralizar Títulos e Ajustar Fonte --- */
        h1 {
            text-align: center !important;
            font-family: 'Poppins', sans-serif !important;
            color: #0f766e !important;
            font-weight: 600 !important;
        }
        
        /* --- 4. Barra Lateral (Sidebar) --- */
        [data-testid="stSidebar"] {
            background-color: #e0f2fe !important;
            border-right: 1px solid #bae6fd !important;
        }
        
        /* --- 5. Estilização dos Formulários (Efeito Cartão) --- */
        [data-testid="stForm"] {
            background-color: #ffffff !important;
            border-radius: 16px !important;
            border: 1px solid #f1f5f9 !important;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01) !important;
            padding: 30px !important;
        }

        /* --- 6. Ajuste das caixas seletoras e Inputs --- */
        div[data-baseweb="select"] > div, 
        div[data-testid="stNumberInput"] input, 
        div[data-testid="stTextInput"] input {
            background-color: #f1f5f9 !important;
            border-radius: 8px !important;
            border: 1px solid #e2e8f0 !important;
            color: #334155 !important;
        }
        
        div[data-testid="stNumberInput"] button {
            background-color: #f1f5f9 !important;
            border: none !important;
        }

        /* --- 7. Estilização de Botões --- */
        .stButton button[kind="primary"] {
            background-color: #0f766e !important;
            color: white !important;
            border-radius: 8px !important;
            font-family: 'Poppins', sans-serif !important;
            font-weight: 500 !important;
            border: none !important;
            transition: all 0.3s ease;
        }
        .stButton button[kind="primary"]:hover {
            background-color: #115e59 !important;
            box-shadow: 0 4px 6px -1px rgba(15, 118, 110, 0.4) !important;
        }
    </style>
""", unsafe_allow_html=True)


# --- TELA DE LOGIN / BLOQUEIO DE ACESSO ---
def check_password():
    """Retorna True se o usuário digitou a senha correta."""
    def password_entered():
        if st.session_state["password"] == st.secrets["acesso"]["senha_app"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Apaga a senha da memória por segurança
        else:
            st.session_state["password_correct"] = False

    # Margem superior para empurrar o login mais para o meio da tela
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; color: #0f766e;'>🔒 Acesso Restrito</h2>", unsafe_allow_html=True)
        # Cria 3 colunas: 30% vazia na esquerda, 40% pro campo de senha, 30% vazia na direita
        _, col_center, _ = st.columns([3, 4, 3])
        with col_center:
            st.text_input("Digite sua senha para acessar o Fluxo de Caixa:", type="password", on_change=password_entered, key="password")
        return False
        
    elif not st.session_state["password_correct"]:
        st.markdown("<h2 style='text-align: center; color: #0f766e;'>🔒 Acesso Restrito</h2>", unsafe_allow_html=True)
        _, col_center, _ = st.columns([3, 4, 3])
        with col_center:
            st.text_input("Digite sua senha para acessar o Fluxo de Caixa:", type="password", on_change=password_entered, key="password")
            st.error("😕 Senha incorreta. Tente novamente.")
        return False
        
    else:
        # Senha correta!
        return True

# Se a senha não estiver correta, o st.stop() impede que o resto do app carregue.
if not check_password():
    st.stop()

# Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÕES AUXILIARES ---
def get_data(sheet_name):
    return conn.read(worksheet=sheet_name, ttl=0)

def save_data(sheet_name, df):
    conn.update(worksheet=sheet_name, data=df)
    st.cache_data.clear()

# --- MENU LATERAL ---
st.sidebar.title("Navegação")
menu = st.sidebar.radio(
    "Ir para:",
    ["Calendário", "Lançamentos", "Relatório", "Cartões de Crédito", "Recorrentes", "Cadastros"]
)

# --- TELA 1: CALENDÁRIO ---
if menu == "Calendário":
    st.title("💸 Fluxo de Caixa")
    
    _, col_mes, col_ano, _ = st.columns([3, 2, 2, 3])
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    
    mes_sel = col_mes.selectbox("Mês", list(range(1, 13)), index=mes_atual-1)
    ano_sel = col_ano.number_input("Ano", min_value=2020, max_value=2030, value=ano_atual)

    st.markdown("<br><br>", unsafe_allow_html=True)

    df_fluxo = get_data("Fluxo_Caixa")
    df_config = get_data("Cadastros")
    
    saldo_inicial = 0.0
    if not df_config.empty and "Saldo_Inicial" in df_config.columns:
        if pd.notna(df_config["Saldo_Inicial"].iloc[0]):
            saldo_inicial = float(df_config["Saldo_Inicial"].iloc[0])
    
    if not df_fluxo.empty and "Data_Efetivacao" in df_fluxo.columns:
        df_fluxo['Data_Efetivacao'] = pd.to_datetime(df_fluxo['Data_Efetivacao'])
        df_fluxo = df_fluxo.sort_values('Data_Efetivacao')
        
        df_fluxo['Saldo_Acumulado'] = saldo_inicial + df_fluxo['Valor'].cumsum()
        
        calendar.setfirstweekday(calendar.SUNDAY)
        cal = calendar.monthcalendar(ano_sel, mes_sel)
        dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        
        cols = st.columns(7)
        for i, dia_nome in enumerate(dias_semana):
            cols[i].markdown(f"<div style='text-align:center; font-weight:600; font-family:Poppins; color:#64748b; padding-bottom:10px;'>{dia_nome}</div>", unsafe_allow_html=True)

        for semana in cal:
            cols = st.columns(7)
            for i, dia in enumerate(semana):
                if dia == 0:
                    cols[i].markdown('<div style="height: 110px; background-color: transparent; border-radius: 12px; border: 1px dashed #cbd5e1; margin-bottom: 15px;"></div>', unsafe_allow_html=True)
                else:
                    data_dia = datetime(ano_sel, mes_sel, dia)
                    
                    saldo_dia = df_fluxo[df_fluxo['Data_Efetivacao'] <= data_dia]['Saldo_Acumulado'].last_valid_index()
                    valor_saldo = df_fluxo.loc[saldo_dia, 'Saldo_Acumulado'] if saldo_dia is not None else saldo_inicial
                    
                    df_mov_dia = df_fluxo[df_fluxo['Data_Efetivacao'] == data_dia]
                    movimento_dia = df_mov_dia['Valor'].sum() if not df_mov_dia.empty else 0.0
                    
                    cor_texto = "#9f1239" if valor_saldo < 0 else "#0f766e"
                    bg_cor = "#fff1f2" if valor_saldo < 0 else "#f0fdfa"
                    borda = "#fecdd3" if valor_saldo < 0 else "#ccfbf1"
                    
                    if movimento_dia > 0:
                        cor_mov = "#059669"
                        sinal_mov = "+"
                    elif movimento_dia < 0:
                        cor_mov = "#e11d48"
                        sinal_mov = ""
                    else:
                        cor_mov = "#94a3b8"
                        sinal_mov = ""
                        
                    texto_movimento = f"{sinal_mov}R$ {movimento_dia:,.2f}" if movimento_dia != 0 else "-"
                    
                    cols[i].markdown(
                        f"""
                        <div style="border: 1px solid {borda}; padding: 10px; border-radius: 12px; background-color: {bg_cor}; height: 110px; margin-bottom: 15px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <span style="font-size: 14px; color: #475569; font-weight: 700;">{dia}</span>
                                <span style="font-size: 11px; color: {cor_mov}; font-weight: 600;">{texto_movimento}</span>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Saldo</span><br>
                                <span style="font-weight: 700; color: {cor_texto}; font-size: 13px; font-family: 'Inter', sans-serif;">R$ {valor_saldo:,.2f}</span>
                            </div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
    else:
        st.info("Nenhum lançamento encontrado para calcular o fluxo de caixa.")

# --- TELA 2: LANÇAMENTOS ---
elif menu == "Lançamentos":
    st.title("🏦 Movimento Bancário")
    
    df_cadastros = get_data("Cadastros")
    colunas_reais = {c.lower(): c for c in df_cadastros.columns}
    
    if "categoria" in colunas_reais:
        nome_coluna_correto = colunas_reais["categoria"]
        categorias = df_cadastros[nome_coluna_correto].dropna().unique().tolist()
    else:
        categorias = []

    if not categorias:
        st.warning("⚠️ Nenhuma categoria encontrada na planilha.")
    else:
        _, col_form, _ = st.columns([2, 6, 2])
        
        with col_form:
            with st.form("novo_lancamento", clear_on_submit=True):
                st.markdown("<h3 style='text-align:center; color:#334155; font-family:Poppins; margin-bottom:20px; font-size:20px;'>Novo Registro</h3>", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                data = c1.date_input("Data", datetime.now(), format="DD/MM/YYYY")
                tipo = c1.selectbox("Tipo", ["Saída", "Entrada"])
                
                valor = c2.number_input("Valor (R$)", min_value=0.01, step=10.0, value=None, format="%.2f")
                cat = c2.selectbox("Categoria", categorias)
                
                desc = st.text_input("Descrição")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Salvar Registro", type="primary", use_container_width=True):
                    if valor is None:
                        st.error("Por favor, preencha o campo Valor.")
                    else:
                        valor_final = -valor if tipo == "Saída" else valor
                        novo = pd.DataFrame([{
                            "ID": datetime.now().strftime("%Y%m%d%H%M%S"),
                            "Data_Ocorrencia": data.strftime("%Y-%m-%d"),
                            "Data_Efetivacao": data.strftime("%Y-%m-%d"),
                            "Tipo": tipo,
                            "Categoria": cat,
                            "Descricao": desc,
                            "Valor": valor_final,
                            "Status": "Efetivado",
                            "Origem": "Movimento Banco",
                            "Cartao": ""                 
                        }])
                        df_atual = get_data("Fluxo_Caixa")
                        if df_atual.empty or len(df_atual.columns) == 0:
                            df_atualizado = novo
                        else:
                            df_atualizado = pd.concat([df_atual, novo], ignore_index=True)
                        save_data("Fluxo_Caixa", df_atualizado)
                        st.success("Lançado com sucesso!")

# --- TELA 3: RELATÓRIO (EXTRATO / EDIÇÃO) ---
elif menu == "Relatório":
    st.title("📝 Relatório e Edição")
    st.write("Filtre as informações, visualize os totais e edite ou exclua lançamentos.")

    df_fluxo = get_data("Fluxo_Caixa")

    if df_fluxo.empty or len(df_fluxo.columns) == 0:
        st.info("Nenhum lançamento encontrado no fluxo de caixa.")
    else:
        df_fluxo["Excluir"] = False

        if "Data_Efetivacao" in df_fluxo.columns:
            df_fluxo["Data_Efetivacao"] = pd.to_datetime(df_fluxo["Data_Efetivacao"]).dt.date
        if "Data_Ocorrencia" in df_fluxo.columns:
            df_fluxo["Data_Ocorrencia"] = pd.to_datetime(df_fluxo["Data_Ocorrencia"]).dt.date

        df_fluxo["Competencia"] = pd.to_datetime(df_fluxo["Data_Efetivacao"]).dt.strftime('%m/%Y')

        st.subheader("🔍 Filtros")
        f1, f2, f3, f4 = st.columns(4)
        
        opcoes_comp = df_fluxo["Competencia"].dropna().unique().tolist()
        opcoes_comp.sort(key=lambda x: datetime.strptime(x, '%m/%Y'), reverse=True)
        filtro_comp = f1.multiselect("Competência (Mês/Ano)", opcoes_comp)
        
        opcoes_cat = df_fluxo["Categoria"].dropna().unique().tolist() if "Categoria" in df_fluxo.columns else []
        filtro_cat = f2.multiselect("Categoria", opcoes_cat)
        
        opcoes_origem = df_fluxo["Origem"].dropna().unique().tolist() if "Origem" in df_fluxo.columns else []
        filtro_origem = f3.multiselect("Origem", opcoes_origem)
        
        opcoes_cartao = df_fluxo["Cartao"].dropna().unique().tolist() if "Cartao" in df_fluxo.columns else []
        opcoes_cartao = [c for c in opcoes_cartao if str(c).strip() != ""] 
        filtro_cartao = f4.multiselect("Cartão", opcoes_cartao)

        df_filtrado = df_fluxo.copy()
        
        if filtro_comp:
            df_filtrado = df_filtrado[df_filtrado["Competencia"].isin(filtro_comp)]
        if filtro_cat:
            df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(filtro_cat)]
        if filtro_origem:
            df_filtrado = df_filtrado[df_filtrado["Origem"].isin(filtro_origem)]
        if filtro_cartao:
            df_filtrado = df_filtrado[df_filtrado["Cartao"].isin(filtro_cartao)]

        df_filtrado = df_filtrado.drop(columns=["Competencia"])
        df_filtrado = df_filtrado.sort_values(by="Data_Efetivacao", ascending=False).reset_index(drop=True)
        df_filtrado.index = range(1, len(df_filtrado) + 1)

        st.subheader("📋 Resultados")
        
        col_config = {
            "ID": None, 
            "Excluir": st.column_config.CheckboxColumn("Excluir", default=False),
            "Data_Ocorrencia": st.column_config.DateColumn("Data Ocorrência", format="DD/MM/YYYY"),
            "Data_Efetivacao": st.column_config.DateColumn("Data Efetivação", format="DD/MM/YYYY"),
            "Valor": st.column_config.NumberColumn("Valor (R$)", format="%.2f")
        }

        # AJUSTE: use_container_width alterado de True para False aqui
        df_editado = st.data_editor(
            df_filtrado,
            column_config=col_config,
            use_container_width=False,
            num_rows="fixed",
            key="editor_fluxo"
        )

        if st.button("Salvar Alterações", type="primary"):
            df_editado["Excluir"] = df_editado["Excluir"].fillna(False)
            
            ids_excluir = df_editado[df_editado["Excluir"] == True]["ID"].tolist()
            df_atualizar = df_editado[df_editado["Excluir"] == False].drop(columns=["Excluir"])
            
            df_atualizar["Data_Ocorrencia"] = pd.to_datetime(df_atualizar["Data_Ocorrencia"]).dt.strftime('%Y-%m-%d')
            df_atualizar["Data_Efetivacao"] = pd.to_datetime(df_atualizar["Data_Efetivacao"]).dt.strftime('%Y-%m-%d')
            
            df_fluxo_final = df_fluxo.copy().drop(columns=["Excluir", "Competencia"], errors='ignore')
            df_fluxo_final["Data_Ocorrencia"] = pd.to_datetime(df_fluxo_final["Data_Ocorrencia"]).dt.strftime('%Y-%m-%d')
            df_fluxo_final["Data_Efetivacao"] = pd.to_datetime(df_fluxo_final["Data_Efetivacao"]).dt.strftime('%Y-%m-%d')
            
            df_fluxo_final = df_fluxo_final[~df_fluxo_final["ID"].isin(ids_excluir)]
            
            df_fluxo_final = df_fluxo_final.set_index("ID")
            df_atualizar = df_atualizar.set_index("ID")
            df_fluxo_final.update(df_atualizar)
            
            df_fluxo_final = df_fluxo_final.reset_index()
            save_data("Fluxo_Caixa", df_fluxo_final)
            
            st.success("Extrato atualizado com sucesso!")
            st.rerun()

# --- TELA 4: CARTÕES DE CRÉDITO ---
elif menu == "Cartões de Crédito":
    st.title("💳 Faturas de Cartão")
    
    df_cadastros = get_data("Cadastros")
    colunas_reais = {c.lower(): c for c in df_cadastros.columns}
    
    if "cartao" in colunas_reais and "categoria" in colunas_reais:
        cartoes = df_cadastros[colunas_reais["cartao"]].dropna().unique().tolist()
        categorias = df_cadastros[colunas_reais["categoria"]].dropna().unique().tolist()
    else:
        cartoes = []
        categorias = []

    if not cartoes or not categorias:
        st.warning("⚠️ Cadastre pelo menos um Cartão e uma Categoria na aba 'Cadastros' antes de lançar compras.")
    else:
        _, col_form, _ = st.columns([2, 6, 2])
        
        with col_form:
            with st.form("form_cartao", clear_on_submit=True):
                st.markdown("<h3 style='text-align:center; color:#334155; font-family:Poppins; margin-bottom:20px; font-size:20px;'>Nova Compra no Crédito</h3>", unsafe_allow_html=True)
                
                colA, colB = st.columns(2)
                data_compra = colA.date_input("Data da Compra", datetime.now(), format="DD/MM/YYYY")
                cartao_sel = colB.selectbox("Cartão", cartoes)
                
                c1, c2 = st.columns(2)
                cat_sel = c1.selectbox("Categoria", categorias)
                desc = c2.text_input("Descrição da Compra (Opcional)")
                
                c3, c4 = st.columns(2)
                valor_total = c3.number_input("Valor Total (R$)", min_value=0.01, step=50.0, value=None, format="%.2f")
                parcelas = c4.number_input("Qtd. Parcelas", min_value=1, max_value=72, value=1, step=1)
                
                cartao_info = df_cadastros[df_cadastros[colunas_reais["cartao"]] == cartao_sel]
                col_melhor_dia = colunas_reais.get("melhor_dia_compra", "melhor_dia_compra")
                col_vencimento = colunas_reais.get("vencimento_cartao", "vencimento_cartao")
                
                try: melhor_dia = int(cartao_info[col_melhor_dia].iloc[0])
                except: melhor_dia = 15 
                try: dia_vencimento_sug = int(cartao_info[col_vencimento].iloc[0])
                except: dia_vencimento_sug = 10 
                
                d = data_compra.day
                m = data_compra.month
                y = data_compra.year
                
                offset = 1 if (melhor_dia < dia_vencimento_sug and d >= melhor_dia) else (2 if d >= melhor_dia else 1)
                sug_m, sug_y = m + offset, y
                if sug_m > 12: sug_m -= 12; sug_y += 1
                elif sug_m > 24: sug_m -= 24; sug_y += 2

                c5, c6 = st.columns(2)
                mes_comp = c5.selectbox("Mês da 1ª Parcela", list(range(1, 13)), index=sug_m-1)
                ano_comp = c6.number_input("Ano da 1ª Parcela", min_value=2020, max_value=2030, value=sug_y)
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Lançar Fatura", type="primary", use_container_width=True)
                
                if submit:
                    if valor_total is None:
                        st.error("Por favor, preencha o Valor Total da Compra.")
                    else:
                        valor_parcela_base = round(valor_total / parcelas, 2)
                        diferenca_centavos = round(valor_total - (valor_parcela_base * parcelas), 2)
                        
                        novos_lancamentos = []
                        for i in range(parcelas):
                            valor_desta_parcela = valor_parcela_base + diferenca_centavos if i == 0 else valor_parcela_base
                            mes_fatura = mes_comp + i
                            ano_fatura = ano_comp + (mes_fatura - 1) // 12
                            mes_fatura = (mes_fatura - 1) % 12 + 1
                            
                            ultimo_dia_mes = calendar.monthrange(ano_fatura, mes_fatura)[1]
                            data_vencimento = datetime(ano_fatura, mes_fatura, min(dia_vencimento_sug, ultimo_dia_mes))
                            
                            texto_parc = f"(Parc. {i+1}/{parcelas})" if parcelas > 1 else ""
                            desc_final = f"{desc} {texto_parc} - {cartao_sel}".strip()
                            
                            novos_lancamentos.append({
                                "ID": datetime.now().strftime("%Y%m%d%H%M%S") + f"_{i}",
                                "Data_Ocorrencia": data_compra.strftime("%Y-%m-%d"),
                                "Data_Efetivacao": data_vencimento.strftime("%Y-%m-%d"),
                                "Tipo": "Saída", "Categoria": cat_sel, "Descricao": desc_final,
                                "Valor": -valor_desta_parcela, "Status": "Previsão (Fatura)",
                                "Origem": "Cartão de Crédito", "Cartao": cartao_sel           
                            })
                        
                        df_novos = pd.DataFrame(novos_lancamentos)
                        df_atual = get_data("Fluxo_Caixa")
                        df_atualizado = df_novos if df_atual.empty else pd.concat([df_atual, df_novos], ignore_index=True)
                        save_data("Fluxo_Caixa", df_atualizado)
                        st.success(f"Compra registrada! {parcelas} parcela(s) lançada(s) com sucesso.")

# --- TELA 5: RECORRENTES ---
elif menu == "Recorrentes":
    st.title("🔁 Custos e Receitas Fixas")

    df_cadastros = get_data("Cadastros")
    colunas_reais = {c.lower(): c for c in df_cadastros.columns}
    categorias = df_cadastros[colunas_reais["categoria"]].dropna().unique().tolist() if "categoria" in colunas_reais else []

    try:
        df_recorrentes = get_data("Recorrentes")
        df_fluxo = get_data("Fluxo_Caixa")
    except Exception:
        st.error("⚠️ Crie a aba 'Recorrentes'.")
        st.stop()
        
    if df_recorrentes.empty:
        df_recorrentes = pd.DataFrame(columns=["ID", "Descricao", "Categoria", "Tipo", "Valor_Base", "Dia_Vencimento"])

    # Envolvendo todo o conteúdo das recorrentes num contentor centralizado
    _, col_center, _ = st.columns([1.5, 7, 1.5])
    
    with col_center:
        with st.expander("➕ Cadastrar Novo Recorrente", expanded=False):
            with st.form("form_recorrente", clear_on_submit=True):
                st.markdown("<h3 style='text-align:center; color:#334155; font-family:Poppins; margin-bottom:20px; font-size:18px;'>Nova Conta Recorrente</h3>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                desc_rec = c1.text_input("Descrição (Ex: Aluguel)")
                cat_rec = c2.selectbox("Categoria", categorias)
                
                c3, c4, c5 = st.columns([2, 2, 2])
                tipo_rec = c3.selectbox("Tipo", ["Saída", "Entrada"])
                valor_rec = c4.number_input("Valor Base (R$)", min_value=0.01, step=10.0, format="%.2f", value=None)
                dia_venc = c5.number_input("Dia Vencimento (1 a 31)", min_value=1, max_value=31, value=10)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Salvar no Catálogo", type="primary", use_container_width=True):
                    if not desc_rec or valor_rec is None:
                        st.error("Preencha a Descrição e o Valor Base.")
                    else:
                        novo_rec = pd.DataFrame([{"ID": datetime.now().strftime("%Y%m%d%H%M%S"), "Descricao": desc_rec, "Categoria": cat_rec, "Tipo": tipo_rec, "Valor_Base": valor_rec, "Dia_Vencimento": dia_venc}])
                        df_recorrentes = pd.concat([df_recorrentes, novo_rec], ignore_index=True)
                        save_data("Recorrentes", df_recorrentes)
                        st.success("Item salvo no catálogo!")
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📅 Projetar Previsões Futuras")
        
        col_proj1, col_proj2, col_proj3, col_proj4 = st.columns([2, 2, 2, 3])
        meses_projetar = col_proj1.selectbox("Qtd. de Meses", [3, 6, 12, 24, 36], index=2)
        mes_inicio = col_proj2.selectbox("Mês Início", list(range(1, 13)), index=datetime.now().month-1)
        ano_inicio = col_proj3.number_input("Ano Início", min_value=2020, max_value=2030, value=datetime.now().year)
        
        col_proj4.markdown("<br>", unsafe_allow_html=True)
        if col_proj4.button("🚀 Injetar Previsões", type="primary", use_container_width=True):
            if df_recorrentes.empty: st.warning("Cadastre itens primeiro.")
            else:
                novos_lancamentos = []
                hoje = datetime.now()
                for _, row in df_recorrentes.iterrows():
                    try: dia_venc = int(float(row["Dia_Vencimento"])); valor_base = float(row["Valor_Base"]); rec_id = str(row["ID"])
                    except: continue 
                    
                    valor_final = -valor_base if row["Tipo"] == "Saída" else valor_base
                    for i in range(meses_projetar):
                        mes_alvo, ano_alvo = mes_inicio + i, ano_inicio
                        ano_alvo += (mes_alvo - 1) // 12
                        mes_alvo = (mes_alvo - 1) % 12 + 1
                        dia_efetivo = min(dia_venc, calendar.monthrange(ano_alvo, mes_alvo)[1])
                        id_rastreavel = f"REC_{rec_id}_{ano_alvo}{mes_alvo:02d}"
                        
                        if not (not df_fluxo.empty and "ID" in df_fluxo.columns and id_rastreavel in df_fluxo["ID"].values):
                            novos_lancamentos.append({"ID": id_rastreavel, "Data_Ocorrencia": hoje.strftime("%Y-%m-%d"), "Data_Efetivacao": datetime(ano_alvo, mes_alvo, dia_efetivo).strftime("%Y-%m-%d"), "Tipo": row["Tipo"], "Categoria": row["Categoria"], "Descricao": row["Descricao"], "Valor": valor_final, "Status": "Previsão (Recorrente)", "Origem": "Recorrente", "Cartao": ""})
                if novos_lancamentos:
                    df_fluxo_atualizado = pd.concat([df_fluxo, pd.DataFrame(novos_lancamentos)], ignore_index=True) if not df_fluxo.empty else pd.DataFrame(novos_lancamentos)
                    save_data("Fluxo_Caixa", df_fluxo_atualizado)
                    st.success(f"✅ {len(novos_lancamentos)} previsões criadas!")
                else: st.info("As previsões para este período já estavam projetadas.")

        st.markdown("---")
        st.subheader("📋 Editar Catálogo")
        if not df_recorrentes.empty:
            df_edit_rec = df_recorrentes.copy()
            df_edit_rec["Excluir"] = False
            df_edit_rec["Valor_Base"] = pd.to_numeric(df_edit_rec["Valor_Base"], errors="coerce")
            df_edit_rec["Dia_Vencimento"] = pd.to_numeric(df_edit_rec["Dia_Vencimento"], errors="coerce").astype(int)
            
            col_config_rec = {"ID": None, "Excluir": st.column_config.CheckboxColumn("Excluir", default=False, width="small"), "Valor_Base": st.column_config.NumberColumn("Valor (R$)", format="%.2f"), "Dia_Vencimento": st.column_config.NumberColumn("Dia Venc.", min_value=1, max_value=31), "Tipo": st.column_config.SelectboxColumn("Tipo", options=["Saída", "Entrada"]), "Categoria": st.column_config.SelectboxColumn("Categoria", options=categorias)}
            
            # AJUSTE: use_container_width alterado de True para False aqui também
            df_editado_rec = st.data_editor(df_edit_rec, column_config=col_config_rec, use_container_width=False, num_rows="fixed", key="editor_recorrentes")
            
            if st.button("Salvar Alterações e Atualizar Fluxo", type="primary"):
                df_editado_rec["Excluir"] = df_editado_rec["Excluir"].fillna(False)
                ids_excluir = df_editado_rec[df_editado_rec["Excluir"] == True]["ID"].astype(str).tolist()
                df_salvar = df_editado_rec[df_editado_rec["Excluir"] == False].drop(columns=["Excluir"])
                save_data("Recorrentes", df_salvar)
                
                if not df_fluxo.empty and "ID" in df_fluxo.columns:
                    df_fluxo["ID"] = df_fluxo["ID"].astype(str)
                    df_fluxo_novo = df_fluxo.copy()
                    df_fluxo_novo["Data_Efetivacao_dt"] = pd.to_datetime(df_fluxo_novo["Data_Efetivacao"]).dt.date
                    hoje_date = datetime.now().date()
                    
                    for rec_id in ids_excluir:
                        mascara_apagar = (df_fluxo_novo["ID"].str.startswith(f"REC_{rec_id}")) & (df_fluxo_novo["Status"] == "Previsão (Recorrente)") & (df_fluxo_novo["Data_Efetivacao_dt"] >= hoje_date)
                        df_fluxo_novo = df_fluxo_novo[~mascara_apagar]
                    
                    for _, row in df_salvar.iterrows():
                        mascara_atualizar = (df_fluxo_novo["ID"].str.startswith(f"REC_{str(row['ID'])}")) & (df_fluxo_novo["Status"] == "Previsão (Recorrente)") & (df_fluxo_novo["Data_Efetivacao_dt"] >= hoje_date)
                        if mascara_atualizar.any():
                            df_fluxo_novo.loc[mascara_atualizar, "Valor"] = -float(row["Valor_Base"]) if row["Tipo"] == "Saída" else float(row["Valor_Base"])
                            df_fluxo_novo.loc[mascara_atualizar, "Descricao"] = row["Descricao"]
                            df_fluxo_novo.loc[mascara_atualizar, "Categoria"] = row["Categoria"]
                            df_fluxo_novo.loc[mascara_atualizar, "Tipo"] = row["Tipo"]
                            
                            novas_datas = []
                            for d in pd.to_datetime(df_fluxo_novo.loc[mascara_atualizar, "Data_Efetivacao"]):
                                novas_datas.append(datetime(d.year, d.month, min(int(row["Dia_Vencimento"]), calendar.monthrange(d.year, d.month)[1])).strftime("%Y-%m-%d"))
                            df_fluxo_novo.loc[mascara_atualizar, "Data_Efetivacao"] = novas_datas

                    save_data("Fluxo_Caixa", df_fluxo_novo.drop(columns=["Data_Efetivacao_dt"]))
                st.success("Sincronizado com sucesso!")
                st.rerun()

# --- TELA 6: CADASTROS ---
elif menu == "Cadastros":
    st.title("⚙️ Configurações")
    df_cadastros = get_data("Cadastros")
    
    st.subheader("💰 Saldo de Partida")
    saldo_atual = float(df_cadastros["Saldo_Inicial"].iloc[0]) if "Saldo_Inicial" in df_cadastros.columns and not df_cadastros.empty and pd.notna(df_cadastros["Saldo_Inicial"].iloc[0]) else 0.0
    
    col_saldo, _ = st.columns([3, 7])
    novo_saldo_ini = col_saldo.number_input("Saldo Atual em Conta", value=saldo_atual)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏷️ Categorias")
        df_cat = df_cadastros[["Categoria"]].dropna() if "Categoria" in df_cadastros.columns else pd.DataFrame(columns=["Categoria"])
        df_cat.index = range(1, len(df_cat) + 1)
        df_cat["Excluir"] = False
        # AJUSTE: use_container_width alterado de True para False aqui na tabela de categorias
        res_cat = st.data_editor(df_cat, num_rows="dynamic", use_container_width=False, key="ed_cat")
    
    with col2:
        st.subheader("💳 Cartões")
        colunas_cartao = ["Cartao", "Vencimento_Cartao", "Melhor_Dia_Compra"]
        if "Cartao" in df_cadastros.columns:
            df_cart = df_cadastros[[c for c in colunas_cartao if c in df_cadastros.columns]].dropna(how="all")
            if "Melhor_Dia_Compra" not in df_cart.columns: df_cart["Melhor_Dia_Compra"] = None
        else: df_cart = pd.DataFrame(columns=colunas_cartao)
        df_cart.index = range(1, len(df_cart) + 1)
        df_cart["Excluir"] = False
        
        # O False impede que o Streamlit force a tabela a tentar caber na tela do celular espremendo as colunas
        res_cart = st.data_editor(df_cart, num_rows="dynamic", use_container_width=False, key="ed_cart")

    if st.button("Salvar Tudo", type="primary"):
        res_cat["Excluir"] = res_cat["Excluir"].fillna(False)
        res_cart["Excluir"] = res_cart["Excluir"].fillna(False)
        cat_salvas = res_cat[(res_cat["Excluir"] == False) & (res_cat["Categoria"].notna()) & (res_cat["Categoria"] != "")].drop(columns=["Excluir"]).reset_index(drop=True)
        cart_salvos = res_cart[(res_cart["Excluir"] == False) & (res_cart["Cartao"].notna()) & (res_cart["Cartao"] != "")].drop(columns=["Excluir"]).reset_index(drop=True)
        df_final = pd.concat([cat_salvas, cart_salvos], axis=1)
        if not df_final.empty: df_final.loc[0, "Saldo_Inicial"] = novo_saldo_ini
        else: df_final.loc[0, "Saldo_Inicial"] = novo_saldo_ini
        save_data("Cadastros", df_final)
        st.success("Configurações salvas!")
        st.rerun()