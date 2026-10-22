# ════════════════════════════════════════════════════════════════════════
# ORÁCULO DA VIDA — Seu sistema de evolução pessoal (arquivo único)
# MeusAgentesIA.com.br
#
# Diagnosticar → Planejar → Executar → Acompanhar → Evoluir
#
# COMO PUBLICAR
#   Coloque SÓ este arquivo num repositório do GitHub e publique no
#   Streamlit Cloud. Não precisa de requirements.txt (usa só o que já vem
#   com o Streamlit: requests, pandas, altair). Cada pessoa entra com o
#   próprio nome e a própria chave Groq.
#
# REGRA DO SISTEMA: números, cálculos, históricos e percentuais são feitos
# pelo APP. A IA só interpreta esses dados e orienta — nunca inventa
# resultados que a pessoa não registrou.
# ════════════════════════════════════════════════════════════════════════
import io
import json
import re
import uuid
import zipfile
from datetime import date, datetime, timedelta

import altair as alt
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Oráculo da Vida", page_icon="🔮", layout="wide")

MODELO = "openai/gpt-oss-120b"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
SITE = "https://meusagentesia.com.br"

PILARES = {
    "financas":   ("💰", "Finanças",                     "saldo mensal, dívidas, reserva, patrimônio"),
    "nutricao":   ("🥗", "Emagrecimento e Nutrição",     "peso, cintura, consistência dos hábitos"),
    "mente":      ("🧠", "Mente e Equilíbrio Emocional", "humor, estresse percebido, práticas realizadas"),
    "saude":      ("💪", "Saúde, Energia e Condicionamento", "horas de sono, treinos, energia percebida"),
    "produtiv":   ("⏱️", "Produtividade e Disciplina",   "tarefas prioritárias concluídas, atrasos"),
    "conhec":     ("📚", "Conhecimento e Desenvolvimento", "horas de estudo, conteúdos concluídos"),
    "carreira":   ("🚀", "Carreira, Negócios e Renda",   "entregas, projetos, vendas, renda"),
    "relac":      ("❤️", "Relacionamentos e Vida Social", "compromissos pessoais cumpridos"),
    "casa":       ("🏠", "Casa, Rotina e Organização",   "pendências resolvidas, compromissos em dia"),
    "proposito":  ("🌟", "Propósito, Sonhos e Qualidade de Vida", "marcos alcançados, satisfação pessoal"),
}
FREQ = {"diaria": "Todo dia", "semanal": "Toda semana", "unica": "Uma vez"}

REGRA_IA = (
    "Você é o ORÁCULO DA VIDA, um planejador pessoal inteligente e acolhedor, que ajuda a pessoa a "
    "diagnosticar, planejar, executar, acompanhar e evoluir nas áreas da vida. Escreva em português do Brasil, "
    "de forma clara, prática e motivadora, sem exageros. REGRAS: 1) Use SOMENTE os dados fornecidos; nunca "
    "invente que a pessoa gastou, ganhou, emagreceu ou fez algo que não esteja registrado. Se faltar dado, diga "
    "o que falta registrar. 2) Os números e percentuais já vêm calculados pelo aplicativo: interprete-os, não os "
    "recalcule de outro jeito. 3) Proponha ações pequenas, realistas e mensuráveis. 4) Saúde e emagrecimento: "
    "nada de dietas extremas, jejuns prolongados, metas de perda rápida ou exercícios perigosos; sugira procurar "
    "médico/nutricionista quando apropriado; não diagnostique. 5) Finanças: eduque e planeje; não recomende "
    "produtos de investimento específicos como certeza; sugira profissional para decisões complexas. "
    "6) Emoções: acolha; se houver sinais de sofrimento intenso ou risco, recomende ajuda profissional e o CVV (188)."
)

# ══════════════════════════════════════════════════════════════════════════
# ESTILO
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility:hidden; }
.stApp { background:#F7F7FB; }
.block-container { padding-top:1.1rem; }
h1, h2, h3, h4, p, li, label, span, div { color:#1E1B3A; }
.cab { background:linear-gradient(135deg,#4338CA,#7C3AED 60%,#A855F7); border-radius:18px; padding:20px 24px; margin-bottom:8px; }
.cab, .cab * { color:#FFFFFF !important; }
.cab h1 { margin:0; font-size:1.65em; } .cab p { margin:4px 0 0 0; opacity:.92; }
.card { background:#fff; border:1px solid #E6E4F2; border-radius:16px; padding:16px 18px; margin-bottom:12px; }
.passo { display:inline-block; background:#EDE9FE; color:#5B21B6 !important; border-radius:20px; padding:2px 12px;
         font-size:.78em; font-weight:700; margin-bottom:6px; letter-spacing:.3px; }
.metrica { background:#fff; border:1px solid #E6E4F2; border-radius:16px; padding:14px; text-align:center; }
.metrica b { font-size:1.75em; display:block; color:#4338CA !important; }
.metrica small { color:#6B6890 !important; }
.meta-card { background:#fff; border:1px solid #E6E4F2; border-radius:16px; padding:14px 16px; margin-bottom:10px; }
.barra { height:12px; border-radius:6px; background:#EEEAF8; overflow:hidden; margin:8px 0 4px 0; position:relative; }
.barra i { display:block; height:100%; border-radius:6px; }
.barra s { position:absolute; top:-3px; width:3px; height:18px; background:#1E1B3A; opacity:.55; }
.chip { display:inline-block; padding:2px 10px; border-radius:20px; font-size:.78em; font-weight:700; }
.ok   { background:#DCFCE7; color:#166534 !important; }
.atr  { background:#FEE2E2; color:#991B1B !important; }
.neu  { background:#E0E7FF; color:#3730A3 !important; }
.fim  { background:#FEF3C7; color:#92400E !important; }
.aviso { background:#FFFBEB; border:1px solid #FDE68A; border-radius:12px; padding:10px 14px; font-size:.9em; }
.aviso, .aviso * { color:#78350F !important; }
.stButton > button, [data-testid="stDownloadButton"] > button, [data-testid="stFormSubmitButton"] button { border-radius:10px; font-weight:600; }
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button { background:#4F46E5 !important; border-color:#4F46E5 !important; }
.stButton > button[kind="primary"] *, [data-testid="stFormSubmitButton"] button * { color:#fff !important; }
.stButton > button[kind="primary"]:hover { background:#4338CA !important; }
[data-testid="stMultiSelect"] [data-tag], [data-baseweb="tag"] { background:#4F46E5 !important; }
[data-testid="stMultiSelect"] [data-tag] *, [data-baseweb="tag"] * { color:#fff !important; }
.stTabs .react-aria-SelectionIndicator, [data-baseweb="tab-highlight"] { background:#4F46E5 !important; }
.stTabs [aria-selected="true"] p { color:#4F46E5 !important; }
[data-testid="stCheckbox"] input:checked + div, [data-testid="stCheckbox"] [data-checked="true"] { background:#4F46E5 !important; border-color:#4F46E5 !important; }
.rodape { text-align:center; color:#9A97B8 !important; font-size:.78em; margin-top:26px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# ESTADO (a "memória" do usuário — salva e aberta pelo arquivo .json)
# ══════════════════════════════════════════════════════════════════════════
PADRAO = {
    "o_nome": "", "o_chave": "",
    "perfil": {},           # diagnóstico: respostas das etapas 1-3
    "prioridades": [],      # chaves de PILARES (até 3)
    "diagnostico_ia": "",   # leitura da IA sobre o diagnóstico
    "metas": [],            # {id, pilar, titulo, unidade, inicial, alvo, inicio, prazo, prioridade, criada, concluida}
    "registros": [],        # {id, meta_id, data, valor, nota}
    "tarefas": [],          # {id, meta_id, texto, freq, criada, feitos:[datas iso], ativa}
    "revisoes": [],         # {id, semana, data, funcionou, obstaculos, humor, energia, resumo_app, analise}
    "chat": [],             # [{role, content}]
    "ver": 0,
}
for _k, _v in PADRAO.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v.copy() if isinstance(_v, (dict, list)) else _v
S = st.session_state
HOJE = date.today()


def novo_id() -> str:
    return uuid.uuid4().hex[:10]


def d(iso):  # texto ISO -> date
    try:
        return date.fromisoformat(str(iso)[:10])
    except ValueError:
        return HOJE


def br(dt) -> str:
    return d(dt).strftime("%d/%m/%Y")


def num(v, casas=2) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return str(v)
    if v.is_integer():
        return f"{int(v):,}".replace(",", ".")
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def nome_pilar(chave: str) -> str:
    e, n, _ = PILARES.get(chave, ("•", chave, ""))
    return f"{e} {n}"


# ══════════════════════════════════════════════════════════════════════════
# MOTOR DE ACOMPANHAMENTO (cálculos feitos pelo app, nunca pela IA)
# ══════════════════════════════════════════════════════════════════════════
def valor_atual(meta: dict) -> float:
    regs = sorted([r for r in S.registros if r["meta_id"] == meta["id"]], key=lambda r: (r["data"], r.get("criado", "")))
    return float(regs[-1]["valor"]) if regs else float(meta["inicial"])


def analise_meta(meta: dict) -> dict:
    """Progresso, progresso esperado pela data, ritmo necessário e situação."""
    ini, alvo = float(meta["inicial"]), float(meta["alvo"])
    atual = valor_atual(meta)
    total = alvo - ini
    progresso = 0.0 if total == 0 else max(0.0, min(1.0, (atual - ini) / total))
    d0, d1 = d(meta["inicio"]), d(meta["prazo"])
    dias_tot = max(1, (d1 - d0).days)
    dias_pass = max(0, min(dias_tot, (HOJE - d0).days))
    esperado = dias_pass / dias_tot
    dias_rest = max(0, (d1 - HOJE).days)
    falta = alvo - atual
    semanas_rest = max(dias_rest / 7, 1 / 7)
    por_semana = falta / semanas_rest if dias_rest > 0 else falta
    por_mes = falta / max(dias_rest / 30.4, 1 / 30.4) if dias_rest > 0 else falta
    if meta.get("concluida") or progresso >= 1:
        situ, classe = "Meta atingida 🎉", "fim"
    elif HOJE > d1:
        situ, classe = "Prazo vencido", "atr"
    elif progresso + 0.05 >= esperado:
        situ, classe = "No ritmo", "ok"
    else:
        situ, classe = "Abaixo do ritmo", "atr"
    n_regs = len([r for r in S.registros if r["meta_id"] == meta["id"]])
    return {"atual": atual, "progresso": progresso, "esperado": esperado, "dias_rest": dias_rest,
            "falta": falta, "por_semana": por_semana, "por_mes": por_mes, "situacao": situ,
            "classe": classe, "registros": n_regs}


def semana_ini(dt: date) -> date:
    return dt - timedelta(days=dt.weekday())


def tarefa_feita(t: dict, dia: date) -> bool:
    feitos = [d(x) for x in t.get("feitos", [])]
    if t["freq"] == "diaria":
        return dia in feitos
    if t["freq"] == "semanal":
        return any(semana_ini(f) == semana_ini(dia) for f in feitos)
    return bool(feitos)


def taxa_semana(ref: date = None) -> tuple:
    """(feitas, previstas) na semana de ref, contando cada dia para tarefas diárias."""
    ref = ref or HOJE
    ini = semana_ini(ref)
    fim_dia = min(ini + timedelta(days=6), HOJE)
    feitas = previstas = 0
    for t in S.tarefas:
        if not t.get("ativa", True):
            continue
        criada = d(t["criada"])
        if t["freq"] == "diaria":
            dia = max(ini, criada)
            while dia <= fim_dia:
                previstas += 1
                feitas += 1 if dia in [d(x) for x in t.get("feitos", [])] else 0
                dia += timedelta(days=1)
        elif t["freq"] == "semanal":
            if criada <= fim_dia:
                previstas += 1
                feitas += 1 if tarefa_feita(t, ref) else 0
    return feitas, previstas


def sequencia_dias() -> int:
    """Dias seguidos (até hoje) com pelo menos uma tarefa concluída."""
    dias = {d(x) for t in S.tarefas for x in t.get("feitos", [])}
    seq, dia = 0, HOJE
    if dia not in dias:
        dia -= timedelta(days=1)
    while dia in dias:
        seq += 1
        dia -= timedelta(days=1)
    return seq


def resumo_dados() -> dict:
    """Pacote compacto e fiel do que foi registrado — é isso que a IA recebe."""
    metas = []
    for m in S.metas:
        a = analise_meta(m)
        metas.append({
            "pilar": PILARES.get(m["pilar"], ("", m["pilar"], ""))[1], "meta": m["titulo"], "unidade": m["unidade"],
            "inicial": m["inicial"], "alvo": m["alvo"], "atual": a["atual"], "inicio": m["inicio"], "prazo": m["prazo"],
            "progresso_%": round(a["progresso"] * 100, 1), "esperado_pela_data_%": round(a["esperado"] * 100, 1),
            "situacao": a["situacao"], "falta": round(a["falta"], 2), "ritmo_necessario_por_semana": round(a["por_semana"], 2),
            "dias_restantes": a["dias_rest"], "qtd_registros": a["registros"],
            "ultimos_registros": [{"data": r["data"], "valor": r["valor"], "nota": r.get("nota", "")}
                                  for r in sorted([r for r in S.registros if r["meta_id"] == m["id"]], key=lambda r: r["data"])[-5:]],
        })
    f, p = taxa_semana()
    return {
        "hoje": HOJE.isoformat(), "nome": S.o_nome,
        "prioridades": [PILARES[k][1] for k in S.prioridades if k in PILARES],
        "diagnostico": S.perfil, "metas": metas,
        "tarefas_ativas": [{"tarefa": t["texto"], "frequencia": FREQ[t["freq"]], "feita_no_periodo_atual": tarefa_feita(t, HOJE)}
                           for t in S.tarefas if t.get("ativa", True)],
        "tarefas_semana": {"feitas": f, "previstas": p, "taxa_%": round(f / p * 100, 1) if p else None},
        "dias_seguidos_com_tarefas": sequencia_dias(),
        "ultimas_revisoes": [{"semana": r["semana"], "funcionou": r["funcionou"], "obstaculos": r["obstaculos"],
                              "humor_0a10": r["humor"], "energia_0a10": r["energia"]} for r in S.revisoes[-3:]],
    }


# ══════════════════════════════════════════════════════════════════════════
# IA (Groq via HTTP)
# ══════════════════════════════════════════════════════════════════════════
class ErroIA(Exception):
    pass


def ia(mensagens, json_mode=False, temperatura=0.6) -> str:
    if isinstance(mensagens, str):
        mensagens = [{"role": "user", "content": mensagens}]
    corpo = {"model": MODELO, "messages": [{"role": "system", "content": REGRA_IA}] + mensagens, "temperature": temperatura}
    if json_mode:
        corpo["response_format"] = {"type": "json_object"}
    try:
        r = requests.post(GROQ_URL, json=corpo, timeout=180,
                          headers={"Authorization": f"Bearer {S.o_chave}", "Content-Type": "application/json"})
    except requests.RequestException as e:
        raise ErroIA(f"Sem conexão com a IA agora. Tente de novo. ({e.__class__.__name__})")
    if r.status_code == 401:
        raise ErroIA("🔑 Sua chave Groq não foi aceita. Clique em Sair e entre com uma chave válida.")
    if r.status_code == 429:
        raise ErroIA("⏳ Limite de uso da sua chave Groq atingido. Espere um pouco e tente de novo.")
    if r.status_code == 400 and json_mode:
        mensagens[-1]["content"] += "\n\nResponda SOMENTE com JSON válido."
        return ia(mensagens, json_mode=False, temperatura=temperatura)
    if r.status_code != 200:
        raise ErroIA(f"A IA não respondeu (código {r.status_code}). Tente de novo em instantes.")
    try:
        txt = r.json()["choices"][0]["message"]["content"] or ""
    except (ValueError, KeyError, IndexError):
        raise ErroIA("A IA devolveu uma resposta inesperada. Tente de novo.")
    return re.sub(r"<think>.*?</think>", "", txt, flags=re.S).strip()


def ia_json(prompt: str) -> dict:
    txt = ia(prompt, json_mode=True)
    achado = re.search(r"\{.*\}", txt, flags=re.S)
    for tentativa in (txt, achado.group(0) if achado else ""):
        if tentativa:
            try:
                return json.loads(tentativa)
            except ValueError:
                pass
    raise ErroIA("A IA respondeu fora do formato esperado. Clique de novo.")


def rodar(fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except ErroIA as e:
        st.error(str(e))
        return None


# ══════════════════════════════════════════════════════════════════════════
# EXPORTAÇÃO (texto, Excel sem biblioteca extra, memória .json)
# ══════════════════════════════════════════════════════════════════════════
def _xml(t) -> str:
    t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(t))[:32000]
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _col(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def xlsx_bytes(abas: list) -> bytes:
    folhas = []
    for _, linhas in abas:
        xml, larg = [], {}
        for i, linha in enumerate(linhas, 1):
            cels = []
            for j, v in enumerate(linha, 1):
                ref = f"{_col(j)}{i}"
                if isinstance(v, bool) or v is None:
                    v = "" if v is None else ("Sim" if v else "Não")
                if isinstance(v, (int, float)):
                    est = 1 if i == 1 else (2 if isinstance(v, float) else 4)
                    cels.append(f'<c r="{ref}" s="{est}"><v>{v}</v></c>')
                    tam = len(str(v))
                else:
                    sv = str(v)
                    est = 1 if i == 1 else (3 if (len(sv) > 60 or "\n" in sv) else 4)
                    cels.append(f'<c r="{ref}" s="{est}" t="inlineStr"><is><t xml:space="preserve">{_xml(sv)}</t></is></c>')
                    tam = max((len(x) for x in sv.splitlines()), default=0)
                larg[j] = max(larg.get(j, 10), min(tam + 2, 70))
            xml.append(f'<row r="{i}">{"".join(cels)}</row>')
        cols = "".join(f'<col min="{j}" max="{j}" width="{w}" customWidth="1"/>' for j, w in sorted(larg.items()))
        cong = ('<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" '
                'state="frozen"/></sheetView></sheetViews>') if len(linhas) > 1 else ""
        folhas.append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                      + cong + (f"<cols>{cols}</cols>" if cols else "") + f'<sheetData>{"".join(xml)}</sheetData></worksheet>')
    n = len(folhas)
    R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
          '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
          + "".join(f'<Override PartName="/xl/worksheets/sheet{k}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for k in range(1, n + 1))
          + "</Types>")
    rels = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="{R}/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    usados, nomes = set(), []
    for nome, _ in abas:
        b = re.sub(r"[\[\]:*?/\\]", " ", nome).strip()[:28] or "Dados"
        f, c = b, 2
        while f.lower() in usados:
            f, c = f"{b[:25]} {c}", c + 1
        usados.add(f.lower())
        nomes.append(f)
    wb = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="{R}"><sheets>'
          + "".join(f'<sheet name="{_xml(nomes[k - 1])}" sheetId="{k}" r:id="rId{k}"/>' for k in range(1, n + 1)) + "</sheets></workbook>")
    wbr = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
           + "".join(f'<Relationship Id="rId{k}" Type="{R}/worksheet" Target="worksheets/sheet{k}.xml"/>' for k in range(1, n + 1))
           + f'<Relationship Id="rId{n + 1}" Type="{R}/styles" Target="styles.xml"/></Relationships>')
    est = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
           '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font></fonts>'
           '<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
           '<fill><patternFill patternType="solid"><fgColor rgb="FF4F46E5"/><bgColor indexed="64"/></patternFill></fill></fills>'
           '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
           '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
           '<cellXfs count="5"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
           '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>'
           '<xf numFmtId="4" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment vertical="top"/></xf>'
           '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
           '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top"/></xf></cellXfs>'
           '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct); z.writestr("_rels/.rels", rels); z.writestr("xl/workbook.xml", wb)
        z.writestr("xl/_rels/workbook.xml.rels", wbr); z.writestr("xl/styles.xml", est)
        for k, x in enumerate(folhas, 1):
            z.writestr(f"xl/worksheets/sheet{k}.xml", x)
    return buf.getvalue()


def limpar_md(t: str) -> str:
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", str(t or ""))
    return re.sub(r"(?m)^\s{0,3}#{1,6}\s+", "", t).strip()


ROT_PERFIL = {
    "financas": "Situação financeira", "saude": "Saúde e disposição", "tempo": "Como organiza o tempo",
    "dificuldades": "Principais dificuldades", "incomoda": "O que mais incomoda", "metas3": "Três maiores metas",
    "dias90": "O que quer conquistar em 90 dias", "ano": "O que quer mudar em um ano", "urgencia": "Área mais urgente",
    "tempo_disp": "Tempo disponível", "renda": "Renda e compromissos", "recursos": "Recursos disponíveis",
    "abandono": "O que faz abandonar um plano",
}


def relatorio_txt() -> str:
    L = ["=" * 64, "🔮 ORÁCULO DA VIDA — RELATÓRIO DE EVOLUÇÃO", f"Nome: {S.o_nome}",
         f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", "=" * 64, ""]
    if S.prioridades:
        L += ["■ PRIORIDADES", "-" * 64] + [f"- {nome_pilar(k)}" for k in S.prioridades] + [""]
    if S.perfil:
        L += ["■ DIAGNÓSTICO", "-" * 64] + [f"{ROT_PERFIL.get(k, k)}: {v}" for k, v in S.perfil.items() if str(v).strip()] + [""]
    if S.diagnostico_ia:
        L += ["■ LEITURA DO ORÁCULO", "-" * 64, limpar_md(S.diagnostico_ia), ""]
    if S.metas:
        L += [f"■ METAS ({len(S.metas)})", "-" * 64]
        for i, m in enumerate(S.metas, 1):
            a = analise_meta(m)
            L += [f"{i}) {nome_pilar(m['pilar'])} — {m['titulo']}",
                  f"   De {num(m['inicial'])} para {num(m['alvo'])} {m['unidade']} · {br(m['inicio'])} até {br(m['prazo'])}",
                  f"   Atual: {num(a['atual'])} {m['unidade']} · Progresso: {a['progresso'] * 100:.0f}% · Esperado pela data: {a['esperado'] * 100:.0f}%",
                  f"   Situação: {a['situacao']} · Falta: {num(abs(a['falta']))} {m['unidade']} · Ritmo necessário: {num(abs(a['por_semana']))} {m['unidade']}/semana", ""]
    if S.registros:
        L += [f"■ REGISTROS ({len(S.registros)})", "-" * 64]
        titulos = {m["id"]: m["titulo"] for m in S.metas}
        for r in sorted(S.registros, key=lambda r: r["data"]):
            L.append(f"{br(r['data'])} · {titulos.get(r['meta_id'], '?')}: {num(r['valor'])}" + (f" — {r['nota']}" if r.get("nota") else ""))
        L.append("")
    if S.tarefas:
        f, p = taxa_semana()
        L += [f"■ TAREFAS ({len(S.tarefas)}) — semana atual: {f}/{p} concluídas", "-" * 64]
        for t in S.tarefas:
            L.append(f"- [{FREQ[t['freq']]}] {t['texto']} · feita {len(t.get('feitos', []))} vez(es)" + ("" if t.get("ativa", True) else " (pausada)"))
        L.append("")
    for r in S.revisoes:
        L += [f"■ REVISÃO DA SEMANA {r['semana']}", "-" * 64, f"Humor: {r['humor']}/10 · Energia: {r['energia']}/10",
              f"O que funcionou: {r['funcionou']}", f"Obstáculos: {r['obstaculos']}", "", limpar_md(r.get("analise", "")), ""]
    return "\n".join(L)


def relatorio_xlsx() -> bytes:
    titulos = {m["id"]: m["titulo"] for m in S.metas}
    abas = [("Resumo", [["Item", "Valor"], ["Nome", S.o_nome], ["Gerado em", datetime.now().strftime("%d/%m/%Y %H:%M")],
                        ["Prioridades", ", ".join(PILARES[k][1] for k in S.prioridades if k in PILARES)]]
             + [[ROT_PERFIL.get(k, k), v] for k, v in S.perfil.items() if str(v).strip()])]
    if S.metas:
        linhas = [["Pilar", "Meta", "Unidade", "Inicial", "Alvo", "Atual", "Início", "Prazo", "Progresso %", "Esperado %", "Situação",
                   "Falta", "Ritmo/semana", "Registros"]]
        for m in S.metas:
            a = analise_meta(m)
            linhas.append([PILARES.get(m["pilar"], ("", m["pilar"], ""))[1], m["titulo"], m["unidade"], float(m["inicial"]), float(m["alvo"]),
                           float(a["atual"]), br(m["inicio"]), br(m["prazo"]), round(a["progresso"] * 100, 1), round(a["esperado"] * 100, 1),
                           a["situacao"], round(float(a["falta"]), 2), round(float(a["por_semana"]), 2), a["registros"]])
        abas.append(("Metas", linhas))
    if S.registros:
        abas.append(("Registros", [["Data", "Meta", "Valor", "Observação"]] + [[br(r["data"]), titulos.get(r["meta_id"], "?"), float(r["valor"]),
                                                                              r.get("nota", "")] for r in sorted(S.registros, key=lambda r: r["data"])]))
    if S.tarefas:
        abas.append(("Tarefas", [["Tarefa", "Meta", "Frequência", "Criada", "Vezes feita", "Ativa"]] + [
            [t["texto"], titulos.get(t.get("meta_id"), "—"), FREQ[t["freq"]], br(t["criada"]), len(t.get("feitos", [])), t.get("ativa", True)] for t in S.tarefas]))
    if S.revisoes:
        abas.append(("Revisões", [["Semana", "Data", "Humor", "Energia", "O que funcionou", "Obstáculos", "Análise do Oráculo"]] + [
            [r["semana"], br(r["data"]), r["humor"], r["energia"], r["funcionou"], r["obstaculos"], limpar_md(r.get("analise", ""))] for r in S.revisoes]))
    return xlsx_bytes(abas)


CHAVES_MEMORIA = ["perfil", "prioridades", "diagnostico_ia", "metas", "registros", "tarefas", "revisoes", "chat"]


def memoria_json() -> bytes:
    dados = {k: S[k] for k in CHAVES_MEMORIA}
    dados.update({"_app": "oraculo_da_vida", "_versao": 1, "_nome": S.o_nome, "_salvo_em": datetime.now().isoformat(timespec="seconds")})
    return json.dumps(dados, ensure_ascii=False, indent=2).encode("utf-8")


# ══════════════════════════════════════════════════════════════════════════
# GUIA PARA INICIANTES (rodapé)
# ══════════════════════════════════════════════════════════════════════════
GUIA = [
    ("🧰 O que você precisa", """
- Um computador ou celular com internet.
- Uma **chave Groq** (grátis — veja o próximo item).
- 10 minutos para o diagnóstico inicial. Depois, **2 minutos por dia** para marcar tarefas e registrar resultados.
"""),
    ("🔑 Como criar sua chave Groq (grátis)", """
1. Acesse **console.groq.com/keys** e entre com sua conta Google.
2. Clique em **Create API Key**, dê um nome e confirme.
3. Copie o código que começa com **gsk_** e cole na tela de entrada do Oráculo.
Guarde a chave no bloco de notas. Não compartilhe com ninguém.
"""),
    ("🧭 Passo 1 — Diagnóstico", """
Escolha **até 3 áreas** que quer melhorar agora e responda às perguntas (pode responder curto).
Clique em **🔮 Gerar meu plano de evolução**: o Oráculo lê suas respostas e **sugere metas** com números e prazos.
Clique em **➕ Adicionar** nas sugestões que fizerem sentido — elas vão para a aba **Metas**.
"""),
    ("🎯 Passo 2 — Metas", """
Cada meta tem um **ponto de partida**, um **alvo** e um **prazo**. Ex.: *Reserva de emergência: de 0 para 3.000 reais até 30/04*.
O app calcula sozinho o **progresso**, quanto **deveria** estar pela data e **quanto falta por semana**.
Em cada meta, clique em **🧩 Criar plano de ação**: o Oráculo cria tarefas pequenas (diárias e semanais) que vão para a aba **Hoje**.
Funciona para metas de **diminuir** também (ex.: peso de 90 para 84 kg, dívida de 5.000 para 0).
"""),
    ("✅ Passo 3 — Hoje (todo dia)", """
Abra a aba **Hoje** e marque o que você fez. Tarefas **diárias** voltam todo dia; **semanais** valem para a semana.
A sequência 🔥 conta quantos dias seguidos você concluiu pelo menos uma tarefa.
"""),
    ("📈 Passo 4 — Registrar resultados", """
Sempre que tiver um número novo (pesou, guardou dinheiro, leu horas…), vá em **Registrar** e lance o valor **atual** da meta.
Ex.: se a reserva era 0 e agora tem 500, registre **500** (o total, não só o que entrou).
O gráfico mostra a linha **planejada** e a linha **real**: se a real ficar abaixo, o Oráculo te ajuda a ajustar.
"""),
    ("🗓️ Passo 5 — Revisão semanal", """
Uma vez por semana (domingo é ótimo), abra **Revisão**, conte o que funcionou e o que atrapalhou, dê nota para humor e energia
e clique em **🔮 Analisar minha semana**. O Oráculo compara o **planejado com o realizado** e sugere ajustes.
Você decide quais ajustes aplicar.
"""),
    ("💬 Conversar com o Oráculo", """
Na aba **Conversa**, pergunte o que quiser ("como acelero minha reserva?", "estou sem energia, o que ajusto?").
O Oráculo responde olhando **as suas metas e registros** — ele não inventa números que você não lançou.
"""),
    ("💾 Como não perder nada (IMPORTANTE)", """
O app **não guarda sozinho** quando você fecha a página. Ao terminar, abra **💾 Minha memória** (topo, à direita)
e clique em **Salvar minha memória (.json)**. No dia seguinte, entre e use **Abrir minha memória** com esse arquivo:
tudo volta — metas, registros, tarefas, revisões e conversas.
"""),
    ("🛡️ Cuidados", """
- Saúde: o Oráculo não substitui médico, nutricionista ou educador físico. Nada de dietas extremas.
- Finanças: é planejamento e educação, não recomendação de investimento.
- Emoções: se estiver passando por um momento muito difícil, procure ajuda profissional. CVV: **188** (24h, gratuito).
"""),
]


def mostrar_guia():
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("## 📘 Como usar — guia para iniciantes")
        st.caption("Abra cada item na ordem. Em 1 semana você já tem seu primeiro relatório de evolução.")
        for t, c in GUIA:
            with st.expander(t):
                st.markdown(c)
        txt = "\n\n".join(f"{t.upper()}\n{'-' * 50}\n{limpar_md(c)}" for t, c in GUIA)
        st.download_button("📥 Baixar este guia (.txt)", data=txt.encode("utf-8"), file_name="guia_oraculo_da_vida.txt",
                           mime="text/plain", key="dl_guia")


# ══════════════════════════════════════════════════════════════════════════
# TELA DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════
if not S.o_chave:
    _, meio, _ = st.columns([1, 2, 1])
    with meio:
        st.markdown("""<div style="text-align:center;padding:18px 0 4px 0;">
          <div style="font-size:3.4em;">🔮</div><h1 style="margin:0;">Oráculo da Vida</h1>
          <p style="color:#6B6890 !important;">Seu sistema de evolução pessoal: diagnosticar, planejar, executar, acompanhar e evoluir.</p>
        </div>""", unsafe_allow_html=True)
        nome = st.text_input("👤 Seu nome", placeholder="Como quer ser chamado?", key="o_inp_nome")
        chave = st.text_input("🔑 Sua chave Groq API", type="password", placeholder="gsk_...", key="o_inp_chave")
        if st.button("✨ ENTRAR", type="primary", width="stretch"):
            if len(nome.strip()) < 2:
                st.warning("Digite um nome com pelo menos 2 letras.")
            elif not chave.strip().startswith("gsk_"):
                st.warning("A chave Groq começa com **gsk_**. Confira e cole novamente.")
            else:
                S.o_nome, S.o_chave = nome.strip(), chave.strip()
                st.rerun()
        st.markdown(f"""<div class="card" style="font-size:.9em;line-height:1.7;">
        🔑 <b>Não tem chave?</b> Crie grátis em <a href="https://console.groq.com/keys" target="_blank">console.groq.com/keys</a>.<br>
        🔒 Sua chave fica só nesta sessão do navegador.<br>
        💾 Já usa o Oráculo? Depois de entrar, abra sua memória salva em <b>💾 Minha memória</b>.<br>
        🤖 Mais agentes em <a href="{SITE}" target="_blank">MeusAgentesIA.com.br</a>.</div>""", unsafe_allow_html=True)
    mostrar_guia()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════
# CABEÇALHO + MEMÓRIA
# ══════════════════════════════════════════════════════════════════════════
hora = datetime.now().hour
saud = "Bom dia" if hora < 12 else ("Boa tarde" if hora < 18 else "Boa noite")
c_cab, c_mem = st.columns([3, 2])
with c_cab:
    st.markdown(f"""<div class="cab"><h1>🔮 Oráculo da Vida</h1>
    <p>{saud}, {S.o_nome}! Vamos avançar? Seu progresso, suas metas, sua evolução.</p></div>""", unsafe_allow_html=True)
with c_mem:
    with st.expander("💾 Minha memória: salvar, abrir, recomeçar ou sair"):
        st.download_button("💾 Salvar minha memória (.json)", data=memoria_json(),
                           file_name=f"oraculo_da_vida_{re.sub(r'[^a-z0-9]+', '_', S.o_nome.lower())}_{HOJE.isoformat()}.json",
                           mime="application/json", width="stretch")
        arq = st.file_uploader("📂 Abrir minha memória", type=["json"], key=f"up_mem_{S.ver}")
        if arq is not None and st.button("Carregar esta memória", width="stretch"):
            try:
                dados = json.loads(arq.getvalue().decode("utf-8"))
                if dados.get("_app") != "oraculo_da_vida":
                    raise ValueError
                for k in CHAVES_MEMORIA:
                    if k in dados:
                        S[k] = dados[k]
                S.ver += 1
                st.success("Memória carregada!")
                st.rerun()
            except Exception:
                st.error("Esse arquivo não é uma memória do Oráculo da Vida.")
        st.divider()
        if not S.get("_conf_reset"):
            if st.button("🆕 Recomeçar do zero", width="stretch"):
                S["_conf_reset"] = True
                st.rerun()
        else:
            st.warning("Isso apaga metas, registros, tarefas e revisões desta tela. **Salve a memória antes** se quiser guardar.")
            r1, r2 = st.columns(2)
            if r1.button("✅ Sim, recomeçar", width="stretch", key="b_reset_sim"):
                ver = S.ver
                for k, v in PADRAO.items():
                    if k not in ("o_nome", "o_chave"):
                        S[k] = v.copy() if isinstance(v, (dict, list)) else v
                S.ver, S["_conf_reset"] = ver + 1, False
                st.rerun()
            if r2.button("✖ Cancelar", width="stretch", key="b_reset_nao"):
                S["_conf_reset"] = False
                st.rerun()
        st.divider()
        if st.button("🚪 Sair", width="stretch"):
            for k in list(S.keys()):
                del S[k]
            st.rerun()

abas = st.tabs(["🏠 Painel", "🧭 Diagnóstico", "🎯 Metas", "✅ Hoje", "📈 Registrar", "🗓️ Revisão", "💬 Conversa", "📑 Relatório"])


def barra_html(prog: float, esperado: float = None, cor: str = "#6366F1") -> str:
    marca = f'<s style="left:calc({min(100, esperado * 100):.1f}% - 1px)" title="onde deveria estar pela data"></s>' if esperado is not None else ""
    return f'<div class="barra"><i style="width:{prog * 100:.1f}%;background:{cor}"></i>{marca}</div>'


def cor_classe(c: str) -> str:
    return {"ok": "#22C55E", "atr": "#EF4444", "fim": "#F59E0B"}.get(c, "#6366F1")


# ══════════════════════════════════════════════════════════════════════════
# 1. PAINEL
# ══════════════════════════════════════════════════════════════════════════
with abas[0]:
    if not S.metas and not S.prioridades:
        st.markdown("""<div class="card"><h3 style="margin-top:0">👋 Bem-vindo! Comece em 3 passos</h3>
        <ol><li>Abra <b>🧭 Diagnóstico</b>, escolha até 3 áreas e responda às perguntas.</li>
        <li>Aceite as metas sugeridas (ou crie as suas em <b>🎯 Metas</b>).</li>
        <li>Todos os dias, marque o que fez em <b>✅ Hoje</b> e registre seus números em <b>📈 Registrar</b>.</li></ol>
        <p>Já usou antes? Abra sua memória em <b>💾 Minha memória</b>, no topo.</p></div>""", unsafe_allow_html=True)
    else:
        ativas = [m for m in S.metas if not m.get("concluida")]
        analises = {m["id"]: analise_meta(m) for m in S.metas}
        no_ritmo = sum(1 for m in ativas if analises[m["id"]]["classe"] in ("ok", "fim"))
        f, p = taxa_semana()
        media = (sum(a["progresso"] for a in analises.values()) / len(analises)) if analises else 0
        cols = st.columns(5)
        for col, (rot, val, sub) in zip(cols, [
            ("Metas ativas", len(ativas), f"{no_ritmo} no ritmo"),
            ("Progresso médio", f"{media * 100:.0f}%", "de todas as metas"),
            ("Tarefas da semana", f"{f}/{p}" if p else "—", f"{(f / p * 100):.0f}% concluídas" if p else "crie um plano de ação"),
            ("Sequência", f"🔥 {sequencia_dias()}", "dia seguido" if sequencia_dias() == 1 else "dias seguidos"),
            ("Revisões", len(S.revisoes), "semanas avaliadas"),
        ]):
            col.markdown(f'<div class="metrica"><b>{val}</b>{rot}<br><small>{sub}</small></div>', unsafe_allow_html=True)
        st.write("")
        if S.prioridades:
            st.markdown("**Suas prioridades:** " + " · ".join(nome_pilar(k) for k in S.prioridades))
        st.markdown("### 📊 Minha evolução")
        if not S.metas:
            st.info("Crie sua primeira meta na aba **🎯 Metas** para ver sua evolução aqui.")
        c1, c2 = st.columns(2)
        for i, m in enumerate(S.metas):
            a = analises[m["id"]]
            with (c1 if i % 2 == 0 else c2):
                st.markdown(f"""<div class="meta-card">
                <div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;">
                  <b>{nome_pilar(m['pilar'])}</b><span class="chip {a['classe']}">{a['situacao']}</span></div>
                <div style="margin-top:4px">{m['titulo']}</div>
                {barra_html(a['progresso'], a['esperado'], cor_classe(a['classe']))}
                <small>{a['progresso'] * 100:.0f}% · atual <b>{num(a['atual'])}</b> de {num(m['alvo'])} {m['unidade']}
                · deveria estar em {a['esperado'] * 100:.0f}% · {a['dias_rest']} dias restantes
                {'· ritmo necessário ' + num(abs(a['por_semana'])) + ' ' + m['unidade'] + '/semana' if a['classe'] in ('ok', 'atr') and a['dias_rest'] > 0 else ''}</small>
                </div>""", unsafe_allow_html=True)
        alertas = [m for m in ativas if analises[m["id"]]["classe"] == "atr"]
        sem_reg = [m for m in ativas if analises[m["id"]]["registros"] == 0 and (HOJE - d(m["inicio"])).days >= 7]
        if alertas or sem_reg:
            st.markdown("### 🔔 Atenção")
            for m in alertas:
                a = analises[m["id"]]
                st.warning(f"**{m['titulo']}** está abaixo do ritmo: {a['progresso'] * 100:.0f}% feito, deveria estar em "
                           f"{a['esperado'] * 100:.0f}%. Para chegar no prazo: **{num(abs(a['por_semana']))} {m['unidade']} por semana**.")
            for m in sem_reg:
                st.info(f"**{m['titulo']}** está há mais de 7 dias sem registro. Lance o valor atual em **📈 Registrar**.")


# ══════════════════════════════════════════════════════════════════════════
# 2. DIAGNÓSTICO
# ══════════════════════════════════════════════════════════════════════════
with abas[1]:
    st.markdown('<span class="passo">DIAGNOSTICAR</span>', unsafe_allow_html=True)
    st.markdown("### 🧭 Entender sua vida antes de planejar")
    st.caption("Escolha até 3 áreas e responda o que quiser. Respostas curtas já ajudam. Você pode voltar e mudar quando quiser.")
    opcoes = list(PILARES)
    prios = st.multiselect("O que você quer melhorar agora? (até 3)", opcoes, default=[k for k in S.prioridades if k in opcoes],
                           format_func=nome_pilar, max_selections=3, key=f"prios_{S.ver}")
    P = S.perfil
    v = S.ver
    with st.expander("1️⃣ Onde estou?", expanded=not P):
        fin = st.text_area("Como está sua situação financeira?", P.get("financas", ""), height=70, key=f"pf1_{v}")
        sau = st.text_area("Como está sua saúde e sua disposição?", P.get("saude", ""), height=70, key=f"pf2_{v}")
        tem = st.text_area("Como você organiza seu tempo hoje?", P.get("tempo", ""), height=70, key=f"pf3_{v}")
        dif = st.text_area("Quais são suas principais dificuldades?", P.get("dificuldades", ""), height=70, key=f"pf4_{v}")
        inc = st.text_area("O que mais te incomoda atualmente?", P.get("incomoda", ""), height=70, key=f"pf5_{v}")
    with st.expander("2️⃣ Onde quero chegar?", expanded=not P):
        m3 = st.text_area("Quais são suas três maiores metas?", P.get("metas3", ""), height=70, key=f"pf6_{v}")
        d90 = st.text_area("O que você quer conquistar em 90 dias?", P.get("dias90", ""), height=70, key=f"pf7_{v}")
        ano = st.text_area("O que deseja mudar em um ano?", P.get("ano", ""), height=70, key=f"pf8_{v}")
        urg = st.text_input("Qual área tem maior urgência?", P.get("urgencia", ""), key=f"pf9_{v}")
    with st.expander("3️⃣ Quais são minhas condições reais?", expanded=not P):
        tdisp = st.text_input("Quanto tempo você tem por dia para suas metas?", P.get("tempo_disp", ""), placeholder="Ex.: 30 minutos de manhã", key=f"pf10_{v}")
        ren = st.text_area("Renda e compromissos financeiros (opcional)", P.get("renda", ""), height=60, key=f"pf11_{v}")
        rec = st.text_area("Que recursos você pode usar? (academia, livros, apoio da família…)", P.get("recursos", ""), height=60, key=f"pf12_{v}")
        aba = st.text_area("O que costuma te fazer abandonar um plano?", P.get("abandono", ""), height=60, key=f"pf13_{v}")
    b1, b2 = st.columns([1, 1])
    with b1:
        salvar_diag = st.button("💾 Salvar diagnóstico", width="stretch", key="b_salvar_diag")
    with b2:
        gerar_plano = st.button("🔮 Gerar meu plano de evolução", type="primary", width="stretch", key="b_plano")
    if salvar_diag or gerar_plano:
        S.prioridades = prios
        S.perfil = {"financas": fin, "saude": sau, "tempo": tem, "dificuldades": dif, "incomoda": inc, "metas3": m3, "dias90": d90,
                    "ano": ano, "urgencia": urg, "tempo_disp": tdisp, "renda": ren, "recursos": rec, "abandono": aba}
        if salvar_diag:
            st.success("✅ Diagnóstico salvo.")
    if gerar_plano:
        if not prios:
            st.warning("Escolha pelo menos uma área para melhorar.")
        else:
            with st.spinner("O Oráculo está lendo seu diagnóstico…"):
                dados = rodar(ia_json, f"""Diagnóstico da pessoa (dados informados por ela):
{json.dumps({"prioridades": [PILARES[k][1] for k in prios], "respostas": S.perfil}, ensure_ascii=False)}
Hoje é {HOJE.isoformat()}.
Responda SOMENTE em JSON:
{{"leitura": "texto em markdown: 1) como você vê a situação atual, 2) pontos fortes, 3) principais riscos de abandono e como evitar, 4) por onde começar esta semana",
 "metas": [{{"pilar": "uma destas chaves: {', '.join(prios)}", "titulo": "meta clara e específica",
   "unidade": "unidade de medida (ex.: reais, kg, cm, horas, livros, treinos, %)", "inicial": número de partida (use o que a pessoa informou; se não informou, use 0 e diga na leitura que ela deve ajustar),
   "alvo": número alvo realista, "prazo_dias": número de dias (entre 30 e 180), "por_que": "uma frase"}}]}}
Sugira de 1 a 2 metas por área escolhida. Metas de saúde devem ser seguras e graduais.""")
            if dados:
                S.diagnostico_ia = str(dados.get("leitura", ""))
                S["sug_metas"] = [dict(m, sid=novo_id()) for m in dados.get("metas", []) if isinstance(m, dict)]
    if S.diagnostico_ia:
        st.markdown("#### 🔮 Leitura do Oráculo")
        st.markdown(f'<div class="card">', unsafe_allow_html=True)
        st.markdown(S.diagnostico_ia)
        st.markdown("</div>", unsafe_allow_html=True)
    if S.get("sug_metas"):
        st.markdown("#### 🎯 Metas sugeridas — ajuste os números e adicione as que fizerem sentido")
        for i, sm in enumerate(S["sug_metas"]):
            with st.container(border=True):
                pil = sm.get("pilar") if sm.get("pilar") in PILARES else (prios[0] if prios else "proposito")
                st.markdown(f"**{nome_pilar(pil)}** · {sm.get('por_que', '')}")
                q1, q2, q3, q4, q5 = st.columns([3, 1.2, 1.1, 1.1, 1.1])
                tit = q1.text_input("Meta", sm.get("titulo", ""), key=f"sg_t_{sm.get('sid', i)}")
                uni = q2.text_input("Unidade", sm.get("unidade", ""), key=f"sg_u_{sm.get('sid', i)}")
                try:
                    ini0, alv0, pz0 = float(sm.get("inicial", 0) or 0), float(sm.get("alvo", 0) or 0), int(sm.get("prazo_dias", 90) or 90)
                except (TypeError, ValueError):
                    ini0, alv0, pz0 = 0.0, 0.0, 90
                ini = q3.number_input("De", value=ini0, key=f"sg_i_{sm.get('sid', i)}")
                alv = q4.number_input("Para", value=alv0, key=f"sg_a_{sm.get('sid', i)}")
                pz = q5.number_input("Em (dias)", value=max(7, pz0), min_value=7, max_value=730, step=1, key=f"sg_p_{sm.get('sid', i)}")
                if st.button("➕ Adicionar às minhas metas", key=f"sg_add_{sm.get('sid', i)}"):
                    if ini == alv or not tit.strip():
                        st.warning("O valor de partida e o alvo precisam ser diferentes, e a meta precisa de um nome.")
                    else:
                        S.metas.append({"id": novo_id(), "pilar": pil, "titulo": tit.strip(), "unidade": uni.strip(), "inicial": ini,
                                        "alvo": alv, "inicio": HOJE.isoformat(), "prazo": (HOJE + timedelta(days=int(pz))).isoformat(),
                                        "prioridade": "Alta", "criada": HOJE.isoformat(), "concluida": False})
                        S["sug_metas"] = [x for x in S["sug_metas"] if x is not sm]
                        st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# 3. METAS
# ══════════════════════════════════════════════════════════════════════════
with abas[2]:
    st.markdown('<span class="passo">PLANEJAR</span>', unsafe_allow_html=True)
    st.markdown("### 🎯 Minhas metas")
    fv = S.get("form_meta_v", 0)
    with st.expander("➕ Criar uma meta", expanded=not S.metas):
        st.caption("Ex.: **Reserva de emergência** · de **0** para **3000** **reais** · prazo em 6 meses. "
                   "Para metas de diminuir (peso, dívida), coloque o alvo menor que o ponto de partida.")
        a1, a2 = st.columns([1.3, 2])
        pil_n = a1.selectbox("Área", list(PILARES), format_func=nome_pilar, key=f"nm_p_{fv}")
        tit_n = a2.text_input("Meta", placeholder="Ex.: Reserva de emergência", key=f"nm_t_{fv}")
        a3, a4, a5, a6 = st.columns(4)
        uni_n = a3.text_input("Unidade", placeholder="reais, kg, horas…", key=f"nm_u_{fv}")
        ini_n = a4.number_input("Ponto de partida", value=0.0, step=1.0, key=f"nm_i_{fv}")
        alv_n = a5.number_input("Alvo", value=0.0, step=1.0, key=f"nm_a_{fv}")
        pra_n = a6.date_input("Prazo", value=HOJE + timedelta(days=90), min_value=HOJE + timedelta(days=1), format="DD/MM/YYYY", key=f"nm_d_{fv}")
        if st.button("💾 Criar meta", type="primary", key=f"nm_ok_{fv}"):
            if not tit_n.strip():
                st.warning("Dê um nome para a meta.")
            elif ini_n == alv_n:
                st.warning("O ponto de partida e o alvo precisam ser diferentes.")
            else:
                S.metas.append({"id": novo_id(), "pilar": pil_n, "titulo": tit_n.strip(), "unidade": uni_n.strip(), "inicial": ini_n,
                                "alvo": alv_n, "inicio": HOJE.isoformat(), "prazo": pra_n.isoformat(), "prioridade": "Alta",
                                "criada": HOJE.isoformat(), "concluida": False})
                S["form_meta_v"] = fv + 1
                st.rerun()
    if not S.metas:
        st.info("Você ainda não tem metas. Crie uma acima ou use as sugestões do **🧭 Diagnóstico**.")
    for m in S.metas:
        a = analise_meta(m)
        with st.container(border=True):
            h1, h2 = st.columns([3, 1])
            h1.markdown(f"**{nome_pilar(m['pilar'])} · {m['titulo']}**")
            h2.markdown(f'<div style="text-align:right"><span class="chip {a["classe"]}">{a["situacao"]}</span></div>', unsafe_allow_html=True)
            st.markdown(barra_html(a["progresso"], a["esperado"], cor_classe(a["classe"])), unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Atual", f"{num(a['atual'])} {m['unidade']}", f"{num(a['atual'] - float(m['inicial']))} desde o início",
                      delta_color="inverse" if float(m["alvo"]) < float(m["inicial"]) else "normal")
            k2.metric("Alvo", f"{num(m['alvo'])} {m['unidade']}", f"prazo {br(m['prazo'])}", delta_color="off", delta_arrow="off")
            k3.metric("Progresso", f"{a['progresso'] * 100:.0f}%", f"deveria: {a['esperado'] * 100:.0f}%", delta_color="off", delta_arrow="off")
            k4.metric("Ritmo necessário", f"{num(abs(a['por_semana']))}/sem" if a["dias_rest"] > 0 else "—",
                      f"{num(abs(a['por_mes']))}/mês" if a["dias_rest"] > 0 else "prazo encerrado", delta_color="off", delta_arrow="off")
            tarefas_m = [t for t in S.tarefas if t.get("meta_id") == m["id"]]
            b1, b2, b3, b4 = st.columns(4)
            if b1.button("🧩 Criar plano de ação" if not tarefas_m else "🧩 Refazer plano de ação", key=f"pl_{m['id']}", width="stretch"):
                with st.spinner("Montando seu plano de ação…"):
                    dados = rodar(ia_json, f"""Crie um PLANO DE AÇÃO para esta meta (dados calculados pelo app):
{json.dumps(resumo_dados()['metas'][[x['id'] for x in S.metas].index(m['id'])], ensure_ascii=False)}
Diagnóstico da pessoa: {json.dumps(S.perfil, ensure_ascii=False)}
Responda SOMENTE em JSON: {{"estrategia": "2 a 4 frases sobre a estratégia",
"tarefas": [{{"texto": "ação pequena, concreta e verificável (até 80 caracteres)", "freq": "diaria|semanal|unica"}}],
"marcos": ["marco intermediário com data aproximada"]}}
Entre 3 e 6 tarefas, cabendo no tempo disponível informado. Comece pequeno.""")
                if dados:
                    for t in tarefas_m:
                        t["ativa"] = False
                    for t in dados.get("tarefas", []):
                        if isinstance(t, dict) and str(t.get("texto", "")).strip():
                            S.tarefas.append({"id": novo_id(), "meta_id": m["id"], "texto": str(t["texto"]).strip()[:120],
                                              "freq": t.get("freq") if t.get("freq") in FREQ else "semanal",
                                              "criada": HOJE.isoformat(), "feitos": [], "ativa": True})
                    m["estrategia"] = str(dados.get("estrategia", ""))
                    m["marcos"] = [str(x) for x in dados.get("marcos", [])][:6]
                    st.rerun()
            if b2.button("✅ Marcar como atingida" if not m.get("concluida") else "↩️ Reabrir meta", key=f"cc_{m['id']}", width="stretch"):
                m["concluida"] = not m.get("concluida")
                st.rerun()
            with b3.popover("✏️ Editar", width="stretch"):
                e_t = st.text_input("Meta", m["titulo"], key=f"ed_t_{m['id']}_{S.ver}")
                e_u = st.text_input("Unidade", m["unidade"], key=f"ed_u_{m['id']}_{S.ver}")
                e_a = st.number_input("Alvo", value=float(m["alvo"]), key=f"ed_a_{m['id']}_{S.ver}")
                e_d = st.date_input("Prazo", value=d(m["prazo"]), format="DD/MM/YYYY", key=f"ed_d_{m['id']}_{S.ver}")
                if st.button("Salvar alterações", key=f"ed_ok_{m['id']}"):
                    m.update({"titulo": e_t.strip() or m["titulo"], "unidade": e_u.strip(), "alvo": e_a, "prazo": e_d.isoformat()})
                    st.rerun()
            with b4.popover("🗑️ Excluir", width="stretch"):
                st.write("Excluir esta meta, os registros e as tarefas dela?")
                if st.button("Sim, excluir", key=f"del_{m['id']}"):
                    S.metas = [x for x in S.metas if x["id"] != m["id"]]
                    S.registros = [x for x in S.registros if x["meta_id"] != m["id"]]
                    S.tarefas = [x for x in S.tarefas if x.get("meta_id") != m["id"]]
                    st.rerun()
            if m.get("estrategia") or tarefas_m:
                with st.expander("🧩 Plano de ação"):
                    if m.get("estrategia"):
                        st.markdown(m["estrategia"])
                    for t in [t for t in tarefas_m if t.get("ativa", True)]:
                        st.markdown(f"- **{FREQ[t['freq']]}:** {t['texto']}")
                    if m.get("marcos"):
                        st.markdown("**Marcos:** " + " · ".join(m["marcos"]))


# ══════════════════════════════════════════════════════════════════════════
# 4. HOJE (execução)
# ══════════════════════════════════════════════════════════════════════════
with abas[3]:
    st.markdown('<span class="passo">EXECUTAR</span>', unsafe_allow_html=True)
    dias_sem = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
    st.markdown(f"### ✅ Hoje — {dias_sem[HOJE.weekday()]}, {HOJE.strftime('%d/%m')}")
    ativas_t = [t for t in S.tarefas if t.get("ativa", True)]
    titulos = {m["id"]: m["titulo"] for m in S.metas}
    if not ativas_t:
        st.info("Nenhuma tarefa ainda. Em **🎯 Metas**, clique em **🧩 Criar plano de ação**, ou crie uma tarefa abaixo.")
    else:
        f, p = taxa_semana()
        sq = sequencia_dias()
        st.markdown(f"**Semana:** {f} de {p} concluídas · 🔥 **{sq}** {'dia seguido' if sq == 1 else 'dias seguidos'}")
        st.markdown(barra_html(f / p if p else 0, None, "#22C55E"), unsafe_allow_html=True)
        for grupo, rot in (("diaria", "📅 Todo dia"), ("semanal", "🗓️ Esta semana"), ("unica", "📌 Uma vez")):
            itens = [t for t in ativas_t if t["freq"] == grupo]
            if not itens:
                continue
            st.markdown(f"#### {rot}")
            for t in itens:
                feito = tarefa_feita(t, HOJE)
                rotulo = (f"~~{t['texto']}~~" if feito else f"**{t['texto']}**") + f"  ·  :gray[{titulos.get(t.get('meta_id'), 'tarefa avulsa')}]"
                novo = st.checkbox(rotulo, value=feito, key=f"tk_{t['id']}_{HOJE.isoformat()}_{S.ver}")
                if novo != feito:
                    if novo:
                        t.setdefault("feitos", []).append(HOJE.isoformat())
                    else:
                        if t["freq"] == "diaria":
                            t["feitos"] = [x for x in t["feitos"] if x != HOJE.isoformat()]
                        elif t["freq"] == "semanal":
                            t["feitos"] = [x for x in t["feitos"] if semana_ini(d(x)) != semana_ini(HOJE)]
                        else:
                            t["feitos"] = []
                    st.rerun()
    with st.expander("➕ Criar tarefa"):
        tv = S.get("form_tar_v", 0)
        x1, x2, x3 = st.columns([3, 1.2, 1.6])
        tt = x1.text_input("Tarefa", placeholder="Ex.: Caminhar 20 minutos", key=f"nt_t_{tv}")
        tf = x2.selectbox("Frequência", list(FREQ), format_func=lambda k: FREQ[k], key=f"nt_f_{tv}")
        tm = x3.selectbox("Meta (opcional)", ["—"] + [m["id"] for m in S.metas], format_func=lambda k: "Avulsa" if k == "—" else titulos.get(k, k), key=f"nt_m_{tv}")
        if st.button("Adicionar tarefa", key=f"nt_ok_{tv}"):
            if tt.strip():
                S.tarefas.append({"id": novo_id(), "meta_id": None if tm == "—" else tm, "texto": tt.strip(), "freq": tf,
                                  "criada": HOJE.isoformat(), "feitos": [], "ativa": True})
                S["form_tar_v"] = tv + 1
                st.rerun()
            else:
                st.warning("Escreva a tarefa.")
    if ativas_t:
        with st.expander("⏸️ Pausar ou apagar tarefas"):
            for t in ativas_t:
                y1, y2, y3 = st.columns([3, 1, 1])
                y1.write(f"{FREQ[t['freq']]} · {t['texto']}")
                if y2.button("Pausar", key=f"pa_{t['id']}"):
                    t["ativa"] = False
                    st.rerun()
                if y3.button("Apagar", key=f"ap_{t['id']}"):
                    S.tarefas = [x for x in S.tarefas if x["id"] != t["id"]]
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# 5. REGISTRAR (acompanhar)
# ══════════════════════════════════════════════════════════════════════════
with abas[4]:
    st.markdown('<span class="passo">ACOMPANHAR</span>', unsafe_allow_html=True)
    st.markdown("### 📈 Registrar resultados")
    if not S.metas:
        st.info("Crie uma meta primeiro em **🎯 Metas**.")
    else:
        rv = S.get("form_reg_v", 0)
        ids = [m["id"] for m in S.metas]
        mapa = {m["id"]: m for m in S.metas}
        r1, r2, r3 = st.columns([2.2, 1, 1])
        mid = r1.selectbox("Meta", ids, format_func=lambda k: f"{nome_pilar(mapa[k]['pilar'])} · {mapa[k]['titulo']}", key=f"rg_m_{rv}")
        mm = mapa[mid]
        val = r2.number_input(f"Valor atual ({mm['unidade'] or 'número'})", value=float(valor_atual(mm)), step=1.0, key=f"rg_v_{rv}_{mid}")
        dt = r3.date_input("Data", value=HOJE, max_value=HOJE, format="DD/MM/YYYY", key=f"rg_d_{rv}")
        nota = st.text_input("Observação (opcional)", placeholder="Ex.: semana corrida, mas mantive a caminhada", key=f"rg_n_{rv}")
        st.caption("Registre o **valor total atual** da meta (ex.: a reserva inteira hoje), não só o que mudou.")
        if st.button("💾 Registrar", type="primary", key=f"rg_ok_{rv}"):
            S.registros.append({"id": novo_id(), "meta_id": mid, "data": dt.isoformat(), "valor": val, "nota": nota.strip(),
                                "criado": datetime.now().isoformat(timespec="seconds")})
            S["form_reg_v"] = rv + 1
            st.rerun()

        st.markdown("#### 📉 Planejado × realizado")
        mg = st.selectbox("Ver gráfico da meta", ids, format_func=lambda k: mapa[k]["titulo"], key="graf_meta")
        mg_m = mapa[mg]
        regs = sorted([r for r in S.registros if r["meta_id"] == mg], key=lambda r: (r["data"], r.get("criado", "")))
        plano = pd.DataFrame({"data": [d(mg_m["inicio"]), d(mg_m["prazo"])], "valor": [float(mg_m["inicial"]), float(mg_m["alvo"])], "linha": "Planejado"})
        real_pts = [{"data": d(mg_m["inicio"]), "valor": float(mg_m["inicial"])}] + [{"data": d(r["data"]), "valor": float(r["valor"])} for r in regs]
        real = pd.DataFrame(real_pts).groupby("data", as_index=False).last()
        real["linha"] = "Realizado"
        dfg = pd.concat([plano, real])
        dfg["data"] = pd.to_datetime(dfg["data"])
        graf = alt.Chart(dfg).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X("data:T", title=None, axis=alt.Axis(format="%d/%m")),
            y=alt.Y("valor:Q", title=mg_m["unidade"] or "valor", scale=alt.Scale(zero=False)),
            color=alt.Color("linha:N", scale=alt.Scale(domain=["Planejado", "Realizado"], range=["#A5B4FC", "#4F46E5"]), legend=alt.Legend(title=None, orient="top")),
            strokeDash=alt.condition(alt.datum.linha == "Planejado", alt.value([6, 4]), alt.value([0])),
            tooltip=[alt.Tooltip("data:T", format="%d/%m/%Y"), "valor:Q", "linha:N"],
        ).properties(height=300)
        st.altair_chart(graf, width="stretch")
        if regs:
            st.markdown("#### 🗂️ Histórico")
            for r in reversed(regs):
                h1, h2 = st.columns([5, 1])
                h1.markdown(f"**{br(r['data'])}** · {num(r['valor'])} {mg_m['unidade']}" + (f" — {r['nota']}" if r.get("nota") else ""))
                if h2.button("Apagar", key=f"rd_{r['id']}"):
                    S.registros = [x for x in S.registros if x["id"] != r["id"]]
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# 6. REVISÃO SEMANAL (evoluir)
# ══════════════════════════════════════════════════════════════════════════
with abas[5]:
    st.markdown('<span class="passo">EVOLUIR</span>', unsafe_allow_html=True)
    semana = f"{semana_ini(HOJE).strftime('%d/%m')} a {(semana_ini(HOJE) + timedelta(days=6)).strftime('%d/%m/%Y')}"
    st.markdown(f"### 🗓️ Revisão da semana ({semana})")
    f, p = taxa_semana()
    st.markdown(f"**O que o app já mediu:** tarefas da semana {f}/{p}" + (f" ({f / p * 100:.0f}%)" if p else "") +
                f" · 🔥 {sequencia_dias()} dias seguidos · {len(S.metas)} metas · "
                f"{sum(1 for r in S.registros if semana_ini(d(r['data'])) == semana_ini(HOJE))} registros nesta semana")
    rvv = S.get("form_rev_v", 0)
    fun = st.text_area("✅ O que funcionou nesta semana?", height=80, key=f"rv_f_{rvv}")
    obs = st.text_area("🚧 O que atrapalhou? (obstáculos)", height=80, key=f"rv_o_{rvv}")
    h1, h2 = st.columns(2)
    hum = h1.slider("🙂 Humor da semana (0 a 10)", 0, 10, 6, key=f"rv_h_{rvv}")
    ene = h2.slider("⚡ Energia da semana (0 a 10)", 0, 10, 6, key=f"rv_e_{rvv}")
    if st.button("🔮 Analisar minha semana", type="primary", key=f"rv_ok_{rvv}"):
        with st.spinner("Comparando o planejado com o realizado…"):
            dados = resumo_dados()
            res = rodar(ia, f"""Faça a REVISÃO SEMANAL desta pessoa.
Dados registrados e calculados pelo app: {json.dumps(dados, ensure_ascii=False)}
Relato da semana: o que funcionou: "{fun}". Obstáculos: "{obs}". Humor {hum}/10, energia {ene}/10.
Formato em markdown:
## 📊 Planejado × realizado (cite os números do app, meta a meta)
## 🏆 Vitórias da semana
## 🚧 Obstáculos e padrões que aparecem
## 🔧 Ajustes recomendados (máx. 5, concretos; diga se é para manter, reduzir ou aumentar cada tarefa/meta)
## 🎯 Foco da próxima semana (1 frase)""")
        if res:
            S.revisoes.append({"id": novo_id(), "semana": semana, "data": HOJE.isoformat(), "funcionou": fun, "obstaculos": obs,
                               "humor": hum, "energia": ene, "resumo_app": {"tarefas": f"{f}/{p}"}, "analise": res})
            S["form_rev_v"] = rvv + 1
            st.rerun()
    if S.revisoes:
        st.markdown("#### 📚 Minhas revisões")
        if len(S.revisoes) >= 2:
            dfr = pd.DataFrame([{"Semana": r["semana"][:5], "Humor": r["humor"], "Energia": r["energia"]} for r in S.revisoes]).set_index("Semana")
            st.line_chart(dfr, color=["#F59E0B", "#4F46E5"], height=220)
        for r in reversed(S.revisoes):
            with st.expander(f"Semana {r['semana']} · humor {r['humor']}/10 · energia {r['energia']}/10", expanded=(r is S.revisoes[-1])):
                st.markdown(r.get("analise", ""))


# ══════════════════════════════════════════════════════════════════════════
# 7. CONVERSA
# ══════════════════════════════════════════════════════════════════════════
with abas[6]:
    st.markdown("### 💬 Conversar com o Oráculo")
    st.caption("Ele responde olhando suas metas, tarefas e registros. Ex.: “Estou gastando mais do que ganho e não consigo emagrecer.”")
    for msg in S.chat:
        with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🔮"):
            st.markdown(msg["content"])
    pergunta = st.chat_input("Escreva para o Oráculo…")
    if pergunta:
        S.chat.append({"role": "user", "content": pergunta})
        contexto = f"Dados atuais da pessoa (registrados/calculados pelo app — use só isto): {json.dumps(resumo_dados(), ensure_ascii=False)}"
        hist = [{"role": "user", "content": contexto}, {"role": "assistant", "content": "Entendido. Vou usar apenas esses dados."}] + S.chat[-12:]
        with st.spinner("O Oráculo está pensando…"):
            res = rodar(ia, hist)
        if res:
            S.chat.append({"role": "assistant", "content": res})
        else:
            S.chat.pop()
        st.rerun()
    if S.chat and st.button("🧹 Limpar conversa", key="b_limpa_chat"):
        S.chat = []
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# 8. RELATÓRIO
# ══════════════════════════════════════════════════════════════════════════
with abas[7]:
    st.markdown("### 📑 Relatório e exportação")
    st.caption("Tudo o que você registrou, com os cálculos do app. Leve para um profissional, imprima ou guarde.")
    agora = datetime.now().strftime("%Y%m%d_%H%M")
    e1, e2, e3 = st.columns(3)
    e1.download_button("📄 Relatório (.txt)", data=relatorio_txt().encode("utf-8"), file_name=f"oraculo_relatorio_{agora}.txt",
                       mime="text/plain", width="stretch")
    e2.download_button("📊 Relatório (Excel)", data=relatorio_xlsx(), file_name=f"oraculo_relatorio_{agora}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
    e3.download_button("💾 Minha memória (.json)", data=memoria_json(), file_name=f"oraculo_memoria_{agora}.json",
                       mime="application/json", width="stretch")
    with st.expander("👀 Ver o relatório"):
        st.text(relatorio_txt())
    st.markdown("""<div class="aviso">🔒 <b>Seus dados são seus.</b> Nada fica guardado no servidor: a memória fica no arquivo .json
    que você baixa. Para apagar tudo, use <b>🆕 Recomeçar do zero</b> e exclua o arquivo do seu computador.</div>""", unsafe_allow_html=True)

mostrar_guia()
st.markdown(f'<div class="rodape">O Oráculo da Vida orienta e organiza; não substitui médicos, nutricionistas, psicólogos ou consultores financeiros.<br>'
            f'© 2026 <a href="{SITE}" target="_blank" style="color:#9A97B8;">MeusAgentesIA.com.br</a></div>', unsafe_allow_html=True)
