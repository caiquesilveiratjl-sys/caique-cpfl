"""
INCISO III - versão Streamlit

Instalar:  pip install streamlit pillow
Rodar:     streamlit run app.py
"""

import random
import time

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

NOME_APP = "INCISO III"
SUBTITULO = "Automatize orçamento em poucos cliques"
IMG_W, IMG_H = 440, 250

st.set_page_config(page_title=NOME_APP, page_icon="🧾", layout="centered")


# ----------------------------------------------------------------------
# Simulações (trocar pelo código real: SAP, Excel, PDF)
# ----------------------------------------------------------------------
def gerar_imagem_teste(w=IMG_W, h=IMG_H):
    cor = tuple(random.randint(40, 190) for _ in range(3))
    img = Image.new("RGB", (w, h), cor)
    d = ImageDraw.Draw(img)

    for _ in range(6):
        x1 = random.randint(0, w - 100)
        y1 = random.randint(0, h - 80)
        d.rectangle(
            [x1, y1, x1 + random.randint(40, 140), y1 + random.randint(30, 100)],
            outline="white",
            width=2,
        )

    try:
        fonte = ImageFont.truetype("arial.ttf", 72)
    except OSError:
        try:
            fonte = ImageFont.load_default(size=72)
        except TypeError:
            fonte = ImageFont.load_default()

    texto = "TESTE"
    box = d.textbbox((0, 0), texto, font=fonte)
    tw, th = box[2] - box[0], box[3] - box[1]
    d.text(
        ((w - tw) / 2 - box[0], (h - th) / 2 - box[1]),
        texto,
        font=fonte,
        fill="white",
    )
    return img


def extrair_anexo(nota):
    # TODO: baixar o anexo da nota no SAP e devolver a imagem real
    time.sleep(1.2)
    return gerar_imagem_teste()


def processar_orcamento(nota, tipo, log, prog):
    # TODO: trocar cada etapa pelo código real
    etapas = [
        f"Abrindo nota {nota} na IQS2",
        "Lendo região e medida de construção",
        f"Selecionando orçamento tipo {tipo}",
        "Abrindo transação de design",
        "Preenchendo campos",
        "Anexando planilha do orçamento",
        "Rodando orçamento",
        "Lendo proporcional da Memória de Cálculo",
        "Preenchendo memorial",
        "Gerando PDF do memorial",
        "Anexando PDF na nota",
        "Encerrando medidas e gravando 310",
        "Salvando projeto",
    ]
    total = len(etapas)
    for i, etapa in enumerate(etapas, start=1):
        log(etapa + "...")
        time.sleep(0.7)
        log(etapa + " OK")
        prog(i / total)


# ----------------------------------------------------------------------
# Estado da sessão (cada usuário tem o seu)
# ----------------------------------------------------------------------
DEFAULTS = {
    "iniciado": False,
    "nota_extraida": None,   # nota cujo anexo foi extraído
    "imagem": None,
    "tipo": None,
    "log": [],
    "progresso": 0.0,
    "concluido": False,
    "nota_concluida": None,
    "erro": None,
}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


def resetar_abaixo():
    """Equivalente ao esconder_abaixo(): limpa tudo depois da nota."""
    st.session_state.nota_extraida = None
    st.session_state.imagem = None
    st.session_state.tipo = None
    st.session_state.log = []
    st.session_state.progresso = 0.0
    st.session_state.concluido = False
    st.session_state.nota_concluida = None
    st.session_state.erro = None


def novo_orcamento():
    resetar_abaixo()
    st.session_state.nota = ""
    st.session_state.tipo_radio = None


def ao_mudar_nota():
    # Se a nota mudou depois de extraída, esconde os passos seguintes
    if st.session_state.nota_extraida is not None:
        if st.session_state.nota.strip() != st.session_state.nota_extraida:
            resetar_abaixo()
            st.session_state.tipo_radio = None


# ----------------------------------------------------------------------
# Tela 1: inicial
# ----------------------------------------------------------------------
if not st.session_state.iniciado:
    st.markdown(
        f"""
        <div style="text-align:center; padding-top:120px;">
            <h1 style="font-size:56px; margin-bottom:0;">{NOME_APP}</h1>
            <p style="font-size:18px; opacity:.7; margin-bottom:36px;">{SUBTITULO}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, col, _ = st.columns([1, 1, 1])
    with col:
        if st.button("Iniciar", type="primary", use_container_width=True):
            st.session_state.iniciado = True
            st.rerun()
    st.stop()


# ----------------------------------------------------------------------
# Tela 2: principal
# ----------------------------------------------------------------------
st.title(NOME_APP)
st.caption(SUBTITULO)

# ---- passo 1: nota ----
with st.container(border=True):
    st.subheader("1. Número da nota")
    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    nota = c1.text_input(
        "Número da nota",
        key="nota",
        placeholder="Ex.: 300123456",
        label_visibility="collapsed",
        on_change=ao_mudar_nota,
    ).strip()
    extrair = c2.button("Extrair anexo", disabled=not nota, use_container_width=True)

if extrair and nota:
    resetar_abaixo()
    st.session_state.tipo_radio = None
    try:
        with st.spinner("Extraindo anexo..."):
            st.session_state.imagem = extrair_anexo(nota)
        st.session_state.nota_extraida = nota
    except Exception as e:
        st.session_state.erro = f"Falha ao extrair anexo: {e}"

if st.session_state.erro:
    st.error(st.session_state.erro)

# ---- passo 2: imagem + tipo ----
if st.session_state.imagem is not None:
    with st.container(border=True):
        st.subheader("2. Anexo da obra e tipo de orçamento")
        col_img, col_tipo = st.columns([3, 2])
        col_img.image(st.session_state.imagem, use_container_width=True)
        with col_tipo:
            tipo = st.radio(
                "Tipo de orçamento",
                options=[1, 2, 3, 4, 5],
                index=None,
                horizontal=True,
                key="tipo_radio",
            )
            st.session_state.tipo = tipo
            if tipo is None:
                st.caption("Escolha de 1 a 5")
            else:
                st.caption(f"Tipo {tipo} selecionado")

# ---- passo 3: gerar ----
gerar = False
if st.session_state.imagem is not None and st.session_state.tipo is not None:
    gerar = st.button(
        "Gerar orçamento",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.concluido,
    )

# ---- passo 4: status ----
mostrar_status = gerar or st.session_state.log
if mostrar_status:
    with st.container(border=True):
        st.subheader("Status")
        area_log = st.empty()
        barra = st.progress(st.session_state.progresso)

        def render_log():
            area_log.code("\n".join(st.session_state.log) or " ", language=None)

        if gerar:
            st.session_state.log = []
            st.session_state.progresso = 0.0
            st.session_state.concluido = False
            render_log()

            def log(t):
                st.session_state.log.append(f"[{time.strftime('%H:%M:%S')}] {t}")
                render_log()

            def prog(p):
                st.session_state.progresso = p
                barra.progress(p)

            try:
                processar_orcamento(
                    st.session_state.nota_extraida, st.session_state.tipo, log, prog
                )
                log("Processo concluído")
                st.session_state.concluido = True
                st.session_state.nota_concluida = st.session_state.nota_extraida
            except Exception as e:
                msg = f"Falha no processo: {e}"
                log(msg)
                st.session_state.erro = msg
                st.error(msg)
        else:
            render_log()

        if st.session_state.concluido:
            st.success(
                f"Orçamento da nota {st.session_state.nota_concluida} gerado com sucesso."
            )
            st.button("Novo orçamento", on_click=novo_orcamento)
