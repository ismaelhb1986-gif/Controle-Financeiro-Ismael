import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
import pandas as pd
import calendar
import os
import hashlib
from datetime import datetime, timedelta, timezone

# Configuração inicial
st.set_page_config(page_title="Controle Financeiro", layout="wide", page_icon="💰")

# --- CUSTOMIZAÇÃO DE CSS AVANÇADA (ESTILO FINTECH + RESPONSIVIDADE) ---
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500&display=swap');

        /* --- 1. REGRAS DE RESPONSIVIDADE E ZOOM MOBILE --- */
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
        /* Sidebar escondida — navegação migrou para o menu horizontal no topo */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        /* Quando a sidebar está escondida, o conteúdo principal pode usar largura total */
        section[data-testid="stMain"] > div.block-container,
        .main .block-container {
            margin-left: auto !important;
            margin-right: auto !important;
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

        /* --- 8. CALENDÁRIO RESPONSIVO COM ROLAGEM HORIZONTAL --- */
        .calendar-scroll-wrapper {
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            padding-bottom: 12px;
            scrollbar-width: thin;
            scrollbar-color: #cbd5e1 #f1f5f9;
        }
        .calendar-scroll-wrapper::-webkit-scrollbar {
            height: 8px;
        }
        .calendar-scroll-wrapper::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 4px;
        }
        .calendar-scroll-wrapper::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 4px;
        }
        
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, minmax(135px, 1fr));
            gap: 10px;
            min-width: 945px;
        }
        
        .calendar-header {
            text-align: center;
            font-weight: 600;
            font-family: 'Poppins', sans-serif;
            color: #64748b;
            padding-bottom: 8px;
            font-size: 13px;
        }
        
        .calendar-cell {
            padding: 10px;
            border-radius: 12px;
            height: 110px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
            box-sizing: border-box;
        }
        
        .calendar-cell-empty {
            background-color: transparent;
            border: 1px dashed #cbd5e1;
        }
        
        .calendar-cell-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        
        .calendar-day-number {
            font-size: 14px;
            color: #475569;
            font-weight: 700;
        }
        
        .calendar-movement {
            font-size: 11px;
            font-weight: 600;
        }
        
        .calendar-cell-bottom {
            text-align: right;
        }
        
        .calendar-saldo-label {
            font-size: 10px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .calendar-saldo-valor {
            font-weight: 700;
            font-size: 13px;
            font-family: 'Inter', sans-serif;
        }

        @media (max-width: 768px) {
            .calendar-grid {
                grid-template-columns: repeat(7, 120px);
                min-width: 870px;
                gap: 8px;
            }
            .calendar-cell {
                height: 100px;
                padding: 8px;
            }
            .calendar-day-number { font-size: 13px; }
            .calendar-movement { font-size: 10px; }
            .calendar-saldo-valor { font-size: 12px; }
            .calendar-saldo-label { font-size: 9px; }
        }

        /* --- 9. Filtros em expander — sem CSS adicional necessário --- */
    </style>
""", unsafe_allow_html=True)


# --- TELA DE LOGIN / BLOQUEIO DE ACESSO ---
def get_last_update_info():
    """Retorna string com data/hora da última modificação do arquivo app.py (fuso de Brasília)."""
    try:
        mtime = os.path.getmtime(__file__)
        # Brasília = UTC-3
        dt_brasilia = datetime.fromtimestamp(mtime, tz=timezone.utc).astimezone(timezone(timedelta(hours=-3)))
        return dt_brasilia.strftime("%d/%m/%Y às %H:%M")
    except Exception:
        return "indisponível"

def get_auth_token(senha):
    """Gera um token determinístico baseado na senha."""
    return hashlib.sha256(f"{senha}|fluxo_caixa_v1".encode()).hexdigest()[:32]

def password_entered():
    senha_digitada = st.session_state.get("password", "")
    
    if senha_digitada == st.secrets["senhas"]["senha_pessoal"]:
        st.session_state["password_correct"] = True
        st.session_state["url_planilha"] = st.secrets["planilhas"]["url_pessoal"]
        st.query_params["auth"] = get_auth_token(senha_digitada)
    elif senha_digitada == st.secrets["senhas"]["senha_maqueli"]:
        st.session_state["password_correct"] = True
        st.session_state["url_planilha"] = st.secrets["planilhas"]["url_maqueli"]
        st.query_params["auth"] = get_auth_token(senha_digitada)
    else:
        st.session_state["password_correct"] = False
        
    if "password" in st.session_state:
        del st.session_state["password"]

def render_login_screen(error_message=None):
    st.markdown("<h2 style='text-align: center; color: #0f766e;'>🔒 Acesso Restrito</h2>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([4, 3, 4])
    with col_center:
        st.markdown("""
            <style>
                div[data-testid="stTextInput"] {
                    max-width: 320px;
                    margin: 0 auto;
                }
            </style>
        """, unsafe_allow_html=True)
        st.text_input(
            "Digite sua senha para acessar o Fluxo de Caixa:",
            type="password",
            on_change=password_entered,
            key="password"
        )
        if error_message:
            st.error(error_message)
    
    ultima_atualizacao = get_last_update_info()
    st.markdown(
        f"""
        <div style='text-align: center; margin-top: 40px; padding: 12px;
                    font-size: 12px; color: #94a3b8; font-family: Inter, sans-serif;'>
            <span style='opacity: 0.7;'>🔄 Última atualização do código:</span><br>
            <span style='font-weight: 600; color: #64748b;'>{ultima_atualizacao}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

def check_password():
    if st.session_state.get("password_correct") is True:
        return True
    
    token_url = st.query_params.get("auth", "")
    if token_url:
        if token_url == get_auth_token(st.secrets["senhas"]["senha_pessoal"]):
            st.session_state["password_correct"] = True
            st.session_state["url_planilha"] = st.secrets["planilhas"]["url_pessoal"]
            return True
        elif token_url == get_auth_token(st.secrets["senhas"]["senha_maqueli"]):
            st.session_state["password_correct"] = True
            st.session_state["url_planilha"] = st.secrets["planilhas"]["url_maqueli"]
            return True

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.session_state.get("password_correct") is False:
        render_login_screen(error_message="😕 Senha incorreta. Tente novamente.")
    else:
        render_login_screen()
    return False

if not check_password():
    st.stop()

# 1. Estabelece a conexão base
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÕES AUXILIARES ---
def get_data(sheet_name):
    return conn.read(spreadsheet=st.session_state["url_planilha"], worksheet=sheet_name, ttl=600)

def save_data(sheet_name, df):
    df_safe = df.copy()
    df_safe = df_safe.fillna("")
    conn.update(spreadsheet=st.session_state["url_planilha"], worksheet=sheet_name, data=df_safe)
    st.cache_data.clear()

def formatar_br(valor):
    try:
        if pd.isna(valor) or valor == "": return "0,00"
        return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "0,00"

def parse_br_to_float(v):
    if pd.isna(v) or v == "": return 0.0
    if isinstance(v, (int, float)): return float(v)
    v = str(v).strip()
    if not v: return 0.0
    v = v.replace('.', '').replace(',', '.')
    try:
        return float(v)
    except Exception:
        return 0.0

# --- MENU DE NAVEGAÇÃO HORIZONTAL ---
menu = option_menu(
    menu_title=None,
    options=["Calendário", "Lançamentos", "Relatório", "Cartões", "Recorrentes", "Cadastros"],
    icons=["calendar3", "bank", "file-earmark-text", "credit-card", "arrow-repeat", "gear"],
    orientation="horizontal",
    default_index=0,
    styles={
        "container": {
            "padding": "6px 4px",
            "background-color": "#ffffff",
            "border-radius": "12px",
            "border": "1px solid #f1f5f9",
            "box-shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.04)",
            "margin-bottom": "16px",
            "max-width": "100%",
        },
        "nav": {
            "flex-wrap": "nowrap",
            "overflow-x": "auto",
            "overflow-y": "hidden",
            "scrollbar-width": "none",
            "-ms-overflow-style": "none",
            "padding-bottom": "0",
        },
        "nav-item": {
            "flex": "0 0 auto",
        },
        "icon": {
            "font-size": "16px",
        },
        "nav-link": {
            "font-size": "13px",
            "font-family": "Poppins, sans-serif",
            "font-weight": "500",
            "color": "#475569",
            "text-align": "center",
            "margin": "0 2px",
            "padding": "8px 14px",
            "border-radius": "8px",
            "white-space": "nowrap",
            "--hover-color": "#f1f5f9",
        },
        "nav-link-selected": {
            "background-color": "#0f766e",
            "color": "#ffffff",
            "font-weight": "500",
        },
    },
)

# --- TELA 1: CALENDÁRIO ---
if menu == "Calendário":
    st.title("💸 Fluxo de Caixa")
    
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    
    nomes_meses_pt = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    periodos = []
    for offset in range(-12, 25):  
        m = mes_atual + offset
        a = ano_atual + (m - 1) // 12
        m = ((m - 1) % 12) + 1
        if 2020 <= a <= 2030:
            periodos.append((m, a))
    
    periodos = list(dict.fromkeys(periodos))
    
    try:
        idx_default = periodos.index((mes_atual, ano_atual))
    except ValueError:
        idx_default = 0
    
    st.markdown("""
        <style>
            .calendar-period-anchor { display: none; }
            div[data-testid="stElementContainer"]:has(> div > div > .calendar-period-anchor) ~ div div[data-testid="stSelectbox"] {
                max-width: 180px;
                margin: 0 auto;
            }
        </style>
        <div class="calendar-period-anchor"></div>
    """, unsafe_allow_html=True)
    
    _, col_periodo, _ = st.columns([3, 2, 3])
    with col_periodo:
        periodo_sel = st.selectbox(
            "Período",
            options=periodos,
            index=idx_default,
            format_func=lambda p: f"{nomes_meses_pt[p[0]-1]}/{p[1]}",
            label_visibility="collapsed"
        )
    mes_sel, ano_sel = periodo_sel
    
    st.markdown("<br>", unsafe_allow_html=True)

    df_fluxo = get_data("Fluxo_Caixa")
    df_config = get_data("Cadastros")
    
    saldo_inicial = 0.0
    if not df_config.empty and "Saldo_Inicial" in df_config.columns:
        if pd.notna(df_config["Saldo_Inicial"].iloc[0]) and str(df_config["Saldo_Inicial"].iloc[0]).strip() != "":
            saldo_inicial = float(df_config["Saldo_Inicial"].iloc[0])
    
    if not df_fluxo.empty and "Data_Efetivacao" in df_fluxo.columns:
        df_fluxo['Data_Efetivacao'] = pd.to_datetime(df_fluxo['Data_Efetivacao'])
        df_fluxo = df_fluxo.sort_values('Data_Efetivacao')
        df_fluxo['Saldo_Acumulado'] = saldo_inicial + pd.to_numeric(df_fluxo['Valor'], errors='coerce').fillna(0).cumsum()
        
        calendar.setfirstweekday(calendar.SUNDAY)
        cal = calendar.monthcalendar(ano_sel, mes_sel)
        dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        
        html_parts = ['<div class="calendar-scroll-wrapper"><div class="calendar-grid">']
        
        for dia_nome in dias_semana:
            html_parts.append(f'<div class="calendar-header">{dia_nome}</div>')
        
        for semana in cal:
            for dia in semana:
                if dia == 0:
                    html_parts.append('<div class="calendar-cell calendar-cell-empty"></div>')
                else:
                    data_dia = datetime(ano_sel, mes_sel, dia)
                    
                    saldo_dia = df_fluxo[df_fluxo['Data_Efetivacao'] <= data_dia]['Saldo_Acumulado'].last_valid_index()
                    valor_saldo = df_fluxo.loc[saldo_dia, 'Saldo_Acumulado'] if saldo_dia is not None else saldo_inicial
                    
                    df_mov_dia = df_fluxo[df_fluxo['Data_Efetivacao'] == data_dia]
                    movimento_dia = pd.to_numeric(df_mov_dia['Valor'], errors='coerce').fillna(0).sum() if not df_mov_dia.empty else 0.0
                    
                    cor_texto = "#9f1239" if valor_saldo < 0 else "#0f766e"
                    bg_cor = "#fff1f2" if valor_saldo < 0 else "#f0fdfa"
                    borda = "#fecdd3" if valor_saldo < 0 else "#ccfbf1"
                    
                    if movimento_dia > 0:
                        cor_mov = "#2563eb"  # ← ALTERADO: azul para entradas
                        sinal_mov = "+"
                    elif movimento_dia < 0:
                        cor_mov = "#e11d48"
                        sinal_mov = ""
                    else:
                        cor_mov = "#94a3b8"
                        sinal_mov = ""
                        
                    texto_movimento = f"{sinal_mov}R$ {formatar_br(movimento_dia)}" if movimento_dia != 0 else "-"
                    
                    html_parts.append(
                        f'<div class="calendar-cell" style="background-color:{bg_cor}; border:1px solid {borda};">'
                            f'<div class="calendar-cell-top">'
                                f'<span class="calendar-day-number">{dia}</span>'
                                f'<span class="calendar-movement" style="color:{cor_mov};">{texto_movimento}</span>'
                            f'</div>'
                            f'<div class="calendar-cell-bottom">'
                                f'<span class="calendar-saldo-label">Saldo</span><br>'
                                f'<span class="calendar-saldo-valor" style="color:{cor_texto};">R$ {formatar_br(valor_saldo)}</span>'
                            f'</div>'
                        f'</div>'
                    )
        
        html_parts.append('</div></div>')
        st.markdown("".join(html_parts), unsafe_allow_html=True)
        
        st.markdown(
            "<p style='text-align:center; font-size:11px; color:#94a3b8; margin-top:8px;'>"
            "💡 No celular, deslize horizontalmente para ver a semana completa"
            "</p>",
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
        categorias = [c for c in categorias if str(c).strip() != ""]
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
                
                cat = c2.selectbox("Categoria", categorias, index=None, placeholder="🔍 Digite para buscar...")
                
                desc = st.text_input("Descrição")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Salvar Registro", type="primary", use_container_width=True):
                    if valor is None or cat is None:
                        st.error("Por favor, preencha o Valor e a Categoria.")
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
                        st.toast("✅ Lançamento registrado com sucesso!", icon="💸")
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

        # Competência atual para uso como valor padrão
        competencia_atual = datetime.now().strftime('%m/%Y')

        opcoes_comp = df_fluxo["Competencia"].dropna().unique().tolist()
        opcoes_comp = [c for c in opcoes_comp if str(c).strip() != ""]
        opcoes_comp.sort(key=lambda x: datetime.strptime(x, '%m/%Y'), reverse=True)
        default_comp = [competencia_atual] if competencia_atual in opcoes_comp else []

        opcoes_cat = df_fluxo["Categoria"].dropna().unique().tolist() if "Categoria" in df_fluxo.columns else []
        opcoes_cat = [c for c in opcoes_cat if str(c).strip() != ""]

        opcoes_origem = df_fluxo["Origem"].dropna().unique().tolist() if "Origem" in df_fluxo.columns else []
        opcoes_origem = [c for c in opcoes_origem if str(c).strip() != ""]

        opcoes_cartao = df_fluxo["Cartao"].dropna().unique().tolist() if "Cartao" in df_fluxo.columns else []
        opcoes_cartao = [c for c in opcoes_cartao if str(c).strip() != ""]

        with st.expander("🔍 Filtros", expanded=False):
            filtro_comp = st.multiselect(
                "Competência",
                opcoes_comp,
                default=default_comp,
                placeholder="Selecione..."
            )
            filtro_cat = st.multiselect("Categoria", opcoes_cat, placeholder="Selecione...")
            filtro_origem = st.multiselect("Origem", opcoes_origem, placeholder="Selecione...")
            filtro_cartao = st.multiselect("Cartão", opcoes_cartao, placeholder="Selecione...")

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
        
        df_filtrado["Valor"] = df_filtrado["Valor"].apply(formatar_br)

        st.subheader("📋 Resultados")
        
        col_config = {
            "ID": None,
            "Excluir": st.column_config.CheckboxColumn("Excluir", default=False),
            "Data_Ocorrencia": st.column_config.DateColumn("Data Ocorrência", format="DD/MM/YYYY"),
            "Data_Efetivacao": st.column_config.DateColumn("Data Efetivação", format="DD/MM/YYYY"),
            "Valor": st.column_config.TextColumn("Valor (R$)") 
        }

        df_editado = st.data_editor(
            df_filtrado,
            column_config=col_config,
            use_container_width=False,
            num_rows="fixed",
            key="editor_fluxo"
        )

        if st.button("Salvar Alterações", type="primary"):
            df_editado["Valor"] = df_editado["Valor"].apply(parse_br_to_float)
            
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
elif menu == "Cartões":
    st.title("💳 Faturas de Cartão")
    
    df_cadastros = get_data("Cadastros")
    colunas_reais = {c.lower(): c for c in df_cadastros.columns}
    
    if "cartao" in colunas_reais and "categoria" in colunas_reais:
        cartoes = df_cadastros[colunas_reais["cartao"]].dropna().unique().tolist()
        cartoes = [c for c in cartoes if str(c).strip() != ""]
        categorias = df_cadastros[colunas_reais["categoria"]].dropna().unique().tolist()
        categorias = [c for c in categorias if str(c).strip() != ""]
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
                cat_sel = c1.selectbox("Categoria", categorias, index=None, placeholder="🔍 Digite para buscar...")
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
                    if valor_total is None or cat_sel is None:
                        st.error("Por favor, preencha o Valor Total e a Categoria.")
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
                        st.toast("✅ Compra de cartão registrada com sucesso!", icon="💳")
                        st.success(f"Compra registrada! {parcelas} parcela(s) lançada(s) com sucesso.")

# --- TELA 5: RECORRENTES ---
elif menu == "Recorrentes":
    st.title("🔁 Custos e Receitas Fixas")

    df_cadastros = get_data("Cadastros")
    colunas_reais = {c.lower(): c for c in df_cadastros.columns}
    categorias = df_cadastros[colunas_reais["categoria"]].dropna().unique().tolist() if "categoria" in colunas_reais else []
    categorias = [c for c in categorias if str(c).strip() != ""]

    try:
        df_recorrentes = get_data("Recorrentes")
        df_fluxo = get_data("Fluxo_Caixa")
    except Exception:
        st.error("⚠️ Crie a aba 'Recorrentes'.")
        st.stop()
        
    if df_recorrentes.empty:
        df_recorrentes = pd.DataFrame(columns=["ID", "Descricao", "Categoria", "Tipo", "Valor_Base", "Dia_Vencimento"])

    _, col_center, _ = st.columns([1.5, 7, 1.5])
    
    with col_center:
        # 1. BLOCO: CADASTRAR NOVO RECORRENTE
        with st.expander("➕ Cadastrar Novo Recorrente", expanded=False):
            with st.form("form_recorrente", clear_on_submit=True):
                st.markdown("<h3 style='text-align:center; color:#334155; font-family:Poppins; margin-bottom:20px; font-size:18px;'>Nova Conta Recorrente</h3>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                desc_rec = c1.text_input("Descrição (Ex: Aluguel)")
                
                cat_rec = c2.selectbox("Categoria", categorias, index=None, placeholder="🔍 Digite para buscar...")
                
                c3, c4, c5 = st.columns([2, 2, 2])
                tipo_rec = c3.selectbox("Tipo", ["Saída", "Entrada"])
                valor_rec = c4.number_input("Valor Base (R$)", min_value=0.01, step=10.0, format="%.2f", value=None)
                dia_venc = c5.number_input("Dia Vencimento (1 a 31)", min_value=1, max_value=31, value=10)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Salvar no Catálogo", type="primary", use_container_width=True):
                    if not desc_rec or valor_rec is None or cat_rec is None:
                        st.error("Preencha a Descrição, Valor Base e Categoria.")
                    else:
                        novo_rec = pd.DataFrame([{"ID": datetime.now().strftime("%Y%m%d%H%M%S"), "Descricao": desc_rec, "Categoria": cat_rec, "Tipo": tipo_rec, "Valor_Base": valor_rec, "Dia_Vencimento": dia_venc}])
                        df_recorrentes = pd.concat([df_recorrentes, novo_rec], ignore_index=True)
                        save_data("Recorrentes", df_recorrentes)
                        st.success("Item salvo no catálogo!")
                        st.rerun()

        # 2. BLOCO: EDITAR CATÁLOGO
        st.markdown("---")
        st.subheader("📋 Editar Catálogo")
        if not df_recorrentes.empty:
            df_edit_rec = df_recorrentes.copy()
            df_edit_rec["Excluir"] = False
            df_edit_rec["Dia_Vencimento"] = pd.to_numeric(df_edit_rec["Dia_Vencimento"], errors="coerce").astype(int)
            
            df_edit_rec["Valor_Base"] = df_edit_rec["Valor_Base"].apply(formatar_br)
            
            col_config_rec = {
                "ID": None, 
                "Excluir": st.column_config.CheckboxColumn("Excluir", default=False, width="small"), 
                "Valor_Base": st.column_config.TextColumn("Valor (R$)"),
                "Dia_Vencimento": st.column_config.NumberColumn("Dia Venc.", min_value=1, max_value=31), 
                "Tipo": st.column_config.SelectboxColumn("Tipo", options=["Saída", "Entrada"]), 
                "Categoria": st.column_config.SelectboxColumn("Categoria", options=categorias)
            }
            
            df_editado_rec = st.data_editor(df_edit_rec, column_config=col_config_rec, use_container_width=False, num_rows="fixed", key="editor_recorrentes")
            
            if st.button("Salvar Alterações e Atualizar Fluxo", type="primary"):
                df_editado_rec["Valor_Base"] = df_editado_rec["Valor_Base"].apply(parse_br_to_float)
                
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

        # 3. BLOCO: INJETAR PREVISÕES
        st.markdown("---")
        st.subheader("📅 Projetar Previsões Futuras")
        
        opcoes_itens = ["Todos"] + df_recorrentes["Descricao"].tolist() if not df_recorrentes.empty else ["Todos"]
        
        col_item, col_proj1, col_proj2, col_proj3 = st.columns([3, 2, 2, 2])
        itens_selecionados = col_item.multiselect("Itens a Projetar", opcoes_itens, default=["Todos"], placeholder="🔍 Escolha ou digite...")
        
        meses_projetar = col_proj1.selectbox("Qtd. de Meses", [3, 6, 12, 24, 36], index=2)
        mes_inicio = col_proj2.selectbox("Mês Início", list(range(1, 13)), index=datetime.now().month-1)
        ano_inicio = col_proj3.number_input("Ano Início", min_value=2020, max_value=2030, value=datetime.now().year)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Injetar Previsões", type="primary", use_container_width=True):
            if df_recorrentes.empty:
                st.warning("Cadastre itens primeiro.")
            elif not itens_selecionados:
                st.warning("Por favor, selecione pelo menos um item ou 'Todos'.")
            else:
                novos_lancamentos = []
                hoje = datetime.now()
                
                if "Todos" in itens_selecionados:
                    df_alvo = df_recorrentes
                else:
                    df_alvo = df_recorrentes[df_recorrentes["Descricao"].isin(itens_selecionados)]
                
                for _, row in df_alvo.iterrows():
                    try:
                        dia_venc = int(float(row["Dia_Vencimento"]))
                        valor_base = float(row["Valor_Base"])
                        rec_id = str(row["ID"])
                    except:
                        continue 
                    
                    valor_final = -valor_base if row["Tipo"] == "Saída" else valor_base
                    for i in range(meses_projetar):
                        mes_alvo, ano_alvo = mes_inicio + i, ano_inicio
                        ano_alvo += (mes_alvo - 1) // 12
                        mes_alvo = (mes_alvo - 1) % 12 + 1
                        dia_efetivo = min(dia_venc, calendar.monthrange(ano_alvo, mes_alvo)[1])
                        id_rastreavel = f"REC_{rec_id}_{ano_alvo}{mes_alvo:02d}"
                        
                        if not (not df_fluxo.empty and "ID" in df_fluxo.columns and id_rastreavel in df_fluxo["ID"].values):
                            novos_lancamentos.append({
                                "ID": id_rastreavel, 
                                "Data_Ocorrencia": hoje.strftime("%Y-%m-%d"), 
                                "Data_Efetivacao": datetime(ano_alvo, mes_alvo, dia_efetivo).strftime("%Y-%m-%d"), 
                                "Tipo": row["Tipo"], 
                                "Categoria": row["Categoria"], 
                                "Descricao": row["Descricao"], 
                                "Valor": valor_final, 
                                "Status": "Previsão (Recorrente)", 
                                "Origem": "Recorrente", 
                                "Cartao": ""
                            })
                if novos_lancamentos:
                    df_fluxo_atualizado = pd.concat([df_fluxo, pd.DataFrame(novos_lancamentos)], ignore_index=True) if not df_fluxo.empty else pd.DataFrame(novos_lancamentos)
                    save_data("Fluxo_Caixa", df_fluxo_atualizado)
                    
                    st.toast(f"✅ {len(novos_lancamentos)} previsões criadas com sucesso!", icon="🎉")
                    st.success(f"✅ Sucesso! {len(novos_lancamentos)} previsões foram geradas no seu Fluxo de Caixa. Acesse a aba 'Calendário' ou 'Relatório' para visualizar.")
                else:
                    st.toast("ℹ️ As previsões já estavam em dia.", icon="ℹ️")
                    st.info("As previsões para os itens e período selecionados já estavam projetadas no seu fluxo de caixa.")

# --- TELA 6: CADASTROS ---
elif menu == "Cadastros":
    st.title("⚙️ Configurações")
    df_cadastros = get_data("Cadastros")
    
    st.subheader("💰 Saldo de Partida")
    saldo_atual = float(df_cadastros["Saldo_Inicial"].iloc[0]) if "Saldo_Inicial" in df_cadastros.columns and not df_cadastros.empty and pd.notna(df_cadastros["Saldo_Inicial"].iloc[0]) and str(df_cadastros["Saldo_Inicial"].iloc[0]).strip() != "" else 0.0
    
    col_saldo, _ = st.columns([3, 7])
    novo_saldo_ini = col_saldo.number_input("Saldo Atual em Conta", value=saldo_atual)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏷️ Categorias")
        df_cat = df_cadastros[["Categoria"]].dropna() if "Categoria" in df_cadastros.columns else pd.DataFrame(columns=["Categoria"])
        df_cat.index = range(1, len(df_cat) + 1)
        df_cat["Excluir"] = False
        res_cat = st.data_editor(
            df_cat,
            num_rows="dynamic",
            use_container_width=False,
            hide_index=True,
            column_config={
                "Categoria": st.column_config.TextColumn("Categoria", width="medium"),
                "Excluir": st.column_config.CheckboxColumn("Excluir", default=False, width="small"),
            },
            key="ed_cat"
        )
    
    with col2:
        st.subheader("💳 Cartões")
        colunas_cartao = ["Cartao", "Vencimento_Cartao", "Melhor_Dia_Compra"]
        if "Cartao" in df_cadastros.columns:
            df_cart = df_cadastros[[c for c in colunas_cartao if c in df_cadastros.columns]].dropna(how="all")
            if "Melhor_Dia_Compra" not in df_cart.columns: df_cart["Melhor_Dia_Compra"] = None
        else: df_cart = pd.DataFrame(columns=colunas_cartao)
        df_cart.index = range(1, len(df_cart) + 1)
        df_cart["Excluir"] = False
        
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
