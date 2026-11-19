# -*- coding: utf-8 -*-
"""Gera o relatório estatístico em PDF a partir de resultados/resultados.json e figuras/.
Uso: python gerar_relatorio.py   (rode antes o notebook/script de análise)."""
import os, json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(AQUI, ".."))
R = json.load(open(os.path.join(BASE, "resultados", "resultados.json"), encoding="utf-8"))
INT = json.load(open(os.path.join(BASE, "integrantes.json"), encoding="utf-8"))
SAIDA = os.path.join(BASE, "relatorio", "Relatorio_Estatistico_MLAM.pdf")
FIG = lambda n: os.path.join(BASE, "figuras", n)

# ---------- fontes (DejaVu suporta acentos, letras gregas e símbolos matemáticos) ----------
def achar_fonte(nome):
    for pasta in ["/usr/share/fonts/truetype/dejavu", "C:/Windows/Fonts", "/Library/Fonts", os.path.expanduser("~/.fonts")]:
        p = os.path.join(pasta, nome)
        if os.path.exists(p): return p
    return None
F, FB, FI = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"
if achar_fonte("DejaVuSans.ttf") and achar_fonte("DejaVuSans-Bold.ttf") and achar_fonte("DejaVuSans-Oblique.ttf"):
    pdfmetrics.registerFont(TTFont("DV", achar_fonte("DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DV-B", achar_fonte("DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("DV-I", achar_fonte("DejaVuSans-Oblique.ttf")))
    pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-B")
    F, FB, FI = "DV", "DV-B", "DV-I"

AZUL = colors.HexColor("#08519c"); CINZA = colors.HexColor("#f0f4f8")
st = {
    "corpo": ParagraphStyle("corpo", fontName=F, fontSize=9.6, leading=14, alignment=TA_JUSTIFY, spaceAfter=6),
    "h1": ParagraphStyle("h1", fontName=FB, fontSize=14, leading=18, textColor=AZUL, spaceBefore=12, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName=FB, fontSize=11.2, leading=15, textColor=AZUL, spaceBefore=9, spaceAfter=4),
    "leg": ParagraphStyle("leg", fontName=FI, fontSize=8.2, leading=11, alignment=TA_CENTER, textColor=colors.HexColor("#444444"), spaceAfter=8),
    "cel": ParagraphStyle("cel", fontName=F, fontSize=8.2, leading=10.5),
    "celb": ParagraphStyle("celb", fontName=FB, fontSize=8.2, leading=10.5, textColor=colors.white),
    "tit": ParagraphStyle("tit", fontName=FB, fontSize=22, leading=28, textColor=AZUL, alignment=TA_CENTER, spaceAfter=8),
    "sub": ParagraphStyle("sub", fontName=F, fontSize=12, leading=17, alignment=TA_CENTER, spaceAfter=4),
    "eq": ParagraphStyle("eq", fontName=F, fontSize=9.2, leading=13, backColor=CINZA, borderPadding=6, spaceBefore=4, spaceAfter=10, leftIndent=6, rightIndent=6),
    "bul": ParagraphStyle("bul", fontName=F, fontSize=9.6, leading=14, alignment=TA_JUSTIFY, leftIndent=14, bulletIndent=2, spaceAfter=3),
}

def n(x, d=2): return f"{x:.{d}f}".replace(".", ",")
def pv(p): return "< 0,001" if p < 0.001 else n(p, 4)
def pct(x, d=1): return n(100 * x, d) + "%"
def P(t, s="corpo"): return Paragraph(t, st[s])
def B(t): return Paragraph(t, st["bul"], bulletText="•")
def H1(t): return Paragraph(t, st["h1"])
def H2(t): return Paragraph(t, st["h2"])

def fig(nome, largura_cm, legenda):
    w, h = ImageReader(FIG(nome)).getSize()
    L = largura_cm * cm
    return KeepTogether([Image(FIG(nome), width=L, height=L * h / w), Paragraph(legenda, st["leg"])])

def tabela(linhas, larguras, cab=True, alinhar_dir=True):
    dados = [[Paragraph(str(c), st["celb"] if (cab and i == 0) else st["cel"]) for c in l] for i, l in enumerate(linhas)]
    t = Table(dados, colWidths=[w * cm for w in larguras], repeatRows=1 if cab else 0)
    est = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b0bec5")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if cab:
        est += [("BACKGROUND", (0, 0), (-1, 0), AZUL)] + [("BACKGROUND", (0, i), (-1, i), CINZA) for i in range(2, len(dados), 2)]
    t.setStyle(TableStyle(est)); return t

def com_legenda(tab, legenda):
    return KeepTogether([tab, Spacer(1, 3), Paragraph(legenda, st["leg"])])

def rodape(c, doc):
    c.saveState(); c.setFont(F, 8); c.setFillColor(colors.HexColor("#666666"))
    c.drawString(2 * cm, 1.2 * cm, "Global Solution – MLAM | Relatório estatístico – CitizenTech")
    c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}"); c.restoreState()

q02, q03, q04, q05, q06, base = R["q02"], R["q03"], R["q04"], R["q05"], R["q06"], R["base"]
LAB = {"expectativa_vida": "Expectativa de vida (anos)", "medicos_mil": "Médicos por mil habitantes",
       "ensino_superior": "Matrícula no ensino superior (%)", "fertilidade": "Taxa de fertilidade (filhos por mulher)",
       "urbanizacao": "Urbanização (% da população em cidades)"}
def rm_txt(i): return f"RM {i['rm']}" if i.get("rm") else "RM: a preencher"
S = []

# ============================ CAPA ============================
S += [Spacer(1, 3.2 * cm), P("RELATÓRIO ESTATÍSTICO", "sub"),
      P("O que se associa a uma vida mais longa nas comunidades?", "tit"),
      P("Análise de indicadores de saúde, educação e urbanização de 195 países, em Python", "sub"), Spacer(1, 1.2 * cm),
      P("Global Solution – 2º semestre | Disciplina MLAM | Desafio CitizenTech", "sub"), Spacer(1, 1.2 * cm)]
for i in INT: S.append(P(f"<b>{i['nome']}</b> – {rm_txt(i)}", "sub"))
S += [Spacer(1, 1.6 * cm), P("Novembro de 2026", "sub"), Spacer(1, 1.5 * cm),
      P("<i>Todos os dados, códigos (notebook em Python), figuras e este relatório estão no repositório GitHub da entrega. "
        "As etapas aqui descritas são reproduzíveis executando o notebook <b>codigo/analise_mlam.ipynb</b>.</i>", "leg"), PageBreak()]

# ============================ RESUMO ============================
S += [H1("Resumo executivo")]
S.append(P(f"Este relatório investiga quais fatores de saúde, educação e demografia estão associados à <b>expectativa de vida</b>, "
           f"indicador-síntese da qualidade de vida de uma comunidade, usando dados reais de {base['n_total']} países (Kaggle, 2023). "
           f"Para o modelo completo foram usados {q05['n']} países com todas as variáveis disponíveis. Principais achados:"))
S += [B(f"<b>A fertilidade é o fator mais fortemente associado.</b> Correlação de {n(q05['cor'][0][3],2)} com a expectativa de vida. "
        f"No modelo múltiplo, cada filho a mais por mulher se associa a {n(abs(q05['coef'][3]['b']),2)} anos a menos de expectativa de vida (p {pv(q05['coef'][3]['p'])}), "
        f"mantidas as demais variáveis constantes."),
      B(f"<b>Quatro variáveis explicam {pct(q05['r2'],0)} das diferenças entre países</b> (R² = {n(q05['r2'],3)}; R² ajustado = {n(q05['r2a'],3)}; "
        f"F({q05['gl1']}; {q05['gl2']}) = {n(q05['F'],1)}; p {pv(q05['pF'])}): médicos por mil habitantes, ensino superior, fertilidade e urbanização."),
      B(f"<b>Médicos por mil habitantes têm retornos decrescentes.</b> A reta simples associa +{n(q04['b1'],2)} anos por médico a mais (r = {n(q04['r'],2)}; R² = {n(q04['r2'],3)}), "
        f"mas a nuvem de pontos é curva: o ganho é maior onde há poucos médicos e se achata depois. Com as outras variáveis no modelo, o efeito cai para +{n(q05['coef'][1]['b'],2)} ano por médico."),
      B(f"<b>É possível classificar países em expectativa de vida alta ou baixa com {pct(q06['acuracia'],1)} de acerto</b> em dados de teste "
        f"(a referência de chutar sempre a classe mais comum é {pct(q06['base_majoritaria'],1)}). Fertilidade e urbanização foram as únicas variáveis significativas nesse modelo."),
      B(f"<b>Brasil:</b> o modelo prevê {n(q05['brasil']['previsto'],1)} anos e o valor observado é {n(q05['brasil']['observado'],1)} anos "
        f"(o observado está {n(abs(q05['brasil']['observado']-q05['brasil']['previsto']),1)} ano abaixo do previsto, dentro da margem de erro do modelo).")]
S.append(P("<b>Cuidado de interpretação:</b> os resultados mostram <i>associações</i> entre países em um único ano. Eles não provam que alterar uma variável "
           "cause mudança na expectativa de vida, e não devem ser transferidos automaticamente para cidades ou municípios (ver Limitações)."))

# ============================ 1 CONTEXTO ============================
S += [H1("1. Contextualização do problema")]
S.append(P("O desafio CitizenTech propõe usar tecnologia e dados para enfrentar problemas das cidades, do campo e das comunidades. "
           "Uma pergunta central para quem planeja políticas públicas locais é: <b>onde investir para que as pessoas vivam mais e melhor?</b> "
           "A expectativa de vida resume em um único número o efeito combinado de saúde, educação, renda e condições de vida, e por isso é um bom indicador de qualidade de vida."))
S.append(P("O objetivo deste trabalho é: (i) descrever a distribuição da expectativa de vida; (ii) testar hipóteses sobre sua média; "
           "(iii) medir quanto ela se associa a oferta de médicos, escolaridade superior, fertilidade e urbanização; (iv) construir um modelo para estimar a expectativa de vida e outro para classificar "
           "países em grupos de expectativa alta ou baixa; e (v) extrair recomendações para a tomada de decisão, indicando as limitações de cada análise."))

# ============================ 2 DADOS ============================
S += [H1("2. Descrição dos dados")]
S.append(P("<b>Fonte:</b> <i>Global Country Information Dataset 2023</i> (Nidula Elgiriyewithana), disponível no Kaggle: "
           "https://www.kaggle.com/datasets/nelgiriyewithana/countries-of-the-world-2023. O autor informa que a base foi compilada de múltiplas fontes de dados. "
           f"O arquivo usado, <i>world-data-2023.csv</i>, tem {base['n_total']} países (linhas) e 35 colunas, e está no repositório (pasta <i>dados</i>). "
           "A base é real, e não foi gerada artificialmente. Foi escolhida por ser aberta, ter muitas variáveis quantitativas ligadas à qualidade de vida (saúde, educação, demografia, urbanização) e permitir "
           "todas as análises solicitadas."))
S.append(P("<b>Tratamento:</b> as colunas numéricas estavam gravadas como texto (por exemplo, “58.10%” e “652,230”). Foram removidos os símbolos %, $ e as vírgulas de milhar, e os valores convertidos para número. "
           "Foi criada a variável <b>urbanização</b> = população urbana ÷ população total × 100. Os valores ausentes não foram imputados: em cada análise usamos apenas os países com dados completos nas variáveis envolvidas. "
           "Todo o tratamento está no código e gera o arquivo <i>dados/base_tratada.csv</i>."))
linhas = [["Variável", "N válido", "Média", "Desvio padrão", "Mínimo", "Mediana", "Máximo"]]
for c in ["expectativa_vida", "medicos_mil", "ensino_superior", "fertilidade", "urbanizacao"]:
    d = base["descritivas"][c]
    linhas.append([LAB[c], int(d["count"]), n(d["mean"]), n(d["std"]), n(d["min"]), n(d["50%"]), n(d["max"])])
S.append(com_legenda(tabela(linhas, [5.0, 1.6, 1.7, 2.1, 1.9, 2.0, 1.9]), "Tabela 1. Estatísticas descritivas das variáveis usadas (países com dado disponível em cada variável)."))
S.append(P(f"Dos {base['n_total']} países, {base['n_completos']} têm as cinco variáveis completas e compõem as análises multivariadas (itens 5 e 6). "
           f"A expectativa de vida ausente em {base['ausentes']['expectativa_vida']} países, ensino superior em {base['ausentes']['ensino_superior']}, fertilidade e médicos em {base['ausentes']['fertilidade']} cada e urbanização em {base['ausentes']['urbanizacao']}."))

# ============================ 3 PROCEDIMENTOS ============================
S += [H1("3. Procedimentos adotados")]
S += [B("<b>Ferramentas:</b> Python (pandas, numpy, scipy, matplotlib, seaborn e scikit-learn). A regressão linear (mínimos quadrados) e a logística (máxima verossimilhança por Newton-Raphson) foram implementadas com numpy e scipy, e os resultados seguem as fórmulas usuais."),
      B("<b>Significância:</b> 5% nas análises de regressão e correlação; nos testes de hipótese, os níveis definidos no enunciado (6% e 9%)."),
      B("<b>Reprodutibilidade:</b> sementes aleatórias fixas (sorteio das amostras do item 3 e divisão treino/teste do item 6), e todos os números deste relatório são lidos de <i>resultados/resultados.json</i>, gerado pelo notebook."),
      B("<b>Variável de interesse (Y):</b> expectativa de vida, em anos. <b>Explicativas:</b> médicos por mil habitantes, matrícula bruta no ensino superior (%), taxa de fertilidade e urbanização. "
        "Usamos a fertilidade no lugar da taxa de natalidade porque as duas têm correlação de cerca de 0,98 e juntas causariam multicolinearidade.")]

# ============================ 4 RESULTADOS ============================
S += [H1("4. Resultados e interpretações")]

# 4.1
S += [H2("4.1 Distribuição Normal de Probabilidade (expectativa de vida)")]
S.append(P(f"Assumindo distribuição normal com média {n(q02['media'])} anos, mediana {n(q02['mediana'])} anos e desvio padrão amostral {n(q02['desvio'])} anos (n = {q02['n']}):"))
S.append(com_legenda(tabela([["Evento", "Probabilidade", "Classificação"],
                             [f"a) P(X &lt; média = {n(q02['media'])})", f"{n(q02['p_a'],4)} ({pct(q02['p_a'],2)})", q02["classe_a"]],
                             [f"b) P(X &gt; mediana = {n(q02['mediana'])})", f"{n(q02['p_b'],4)} ({pct(q02['p_b'],2)})", q02["classe_b"]]], [5.2, 4.0, 7.6]),
                     "Tabela 2. Probabilidades pela normal. Critério: &lt; 25% improvável; 25% a &lt; 50% pouco provável; 50% equiprovável; &gt; 50% a 75% provável; &gt; 75% muito provável."))
S.append(fig("fig02_normal.png", 12.5, "Figura 1. Histograma da expectativa de vida com a curva normal ajustada, a média e a mediana."))
S.append(P(f"<b>Interpretação.</b> Em qualquer normal, metade dos valores fica abaixo da média, e por isso o evento (a) é equiprovável. No evento (b), a mediana ({n(q02['mediana'])}) é maior que a média ({n(q02['media'])}), "
           f"então a chance de um país superar a mediana é de {pct(q02['p_b'],1)}, um pouco abaixo de 50%. Esse desvio é um sinal de assimetria à esquerda: poucos países de expectativa muito baixa puxam a média para baixo. "
           f"O teste de Shapiro-Wilk (W = {n(q02['shapiro_W'],3)}; p {pv(q02['shapiro_p'])}) rejeita a normalidade estrita. A suposição do enunciado é, portanto, uma aproximação, e as probabilidades devem ser lidas como ordens de grandeza."))

# 4.2
S += [H2("4.2 Testes de hipóteses para a média")]
a, b = q03["a"], q03["b"]
S.append(P(f"Referência: média populacional μ<sub>0</sub> = {n(q03['mu0'],3)} anos e desvio padrão populacional σ = {n(q03['sigma'],3)} anos (calculados sobre todos os países). Teste Z com H<sub>0</sub>: μ = μ<sub>0</sub>, "
           "usando amostras aleatórias sem reposição (semente fixa)."))
S.append(com_legenda(tabela([["", "a) H<sub>1</sub>: μ &lt; μ<sub>0</sub>", "b) H<sub>1</sub>: μ &gt; μ<sub>0</sub>"],
                             ["Nível de significância", "6%", "9%"], ["Tamanho da amostra", a["n"], b["n"]],
                             ["Média amostral (anos)", n(a["xbar"], 3), n(b["xbar"], 3)], ["Estatística z calculada", n(a["z"], 4), n(b["z"], 4)],
                             ["Valor crítico de z", n(a["z_crit"], 4), n(b["z_crit"], 4)], ["p-valor", n(a["p_valor"], 4), n(b["p_valor"], 4)],
                             ["Decisão", "Não rejeita H<sub>0</sub>" if not a["rejeita"] else "Rejeita H<sub>0</sub>", "Não rejeita H<sub>0</sub>" if not b["rejeita"] else "Rejeita H<sub>0</sub>"]],
                            [5.2, 5.6, 5.6]), "Tabela 3. Resultados dos testes Z para a média."))
S.append(fig("fig03_testes.png", 14.5, "Figura 2. Região de rejeição (em vermelho) e valor de z calculado em cada teste."))
S.append(P(f"<b>Interpretação.</b> No teste (a), a média amostral ({n(a['xbar'],2)}) está pouco abaixo da referência, mas o z = {n(a['z'],2)} fica longe do valor crítico ({n(a['z_crit'],2)}), e <b>não se rejeita H<sub>0</sub></b>. "
           f"No teste (b), o z = {n(b['z'],4)} supera o crítico ({n(b['z_crit'],4)}) por margem mínima, e o p-valor ({n(b['p_valor'],4)}) fica praticamente igual a α (0,09), de modo que a decisão técnica é <b>rejeitar H<sub>0</sub></b>, mas com evidência muito frágil. "
           f"Como as amostras foram sorteadas da própria base que define μ<sub>0</sub>, H<sub>0</sub> é verdadeira por construção e essa rejeição é um falso positivo (erro tipo I), esperado em cerca de 9% das amostras. "
           f"Uma simulação com 10.000 amostras confirmou o comportamento: rejeição de {pct(q03['taxa_a'],1)} em (a) e {pct(q03['taxa_b'],1)} em (b), próximas de α (um pouco menores porque a amostragem é sem reposição de uma população finita). "
           "A lição prática é não tomar decisões em cima de p-valores colados no limite."))

# 4.3
S += [H2("4.3 Análise bivariada: médicos por mil habitantes e expectativa de vida")]
S.append(P(f"Foram usados {q04['n']} países com as duas variáveis. X = médicos por mil habitantes; Y = expectativa de vida."))
S.append(fig("fig04a_dispersao.png", 11.5, "Figura 3. Diagrama de dispersão entre médicos por mil habitantes e expectativa de vida."))
S.append(P("<b>a) Dispersão.</b> A relação é positiva: países com mais médicos tendem a ter maior expectativa de vida. A nuvem, porém, não é uma reta: a expectativa de vida sobe rápido entre 0 e cerca de 2 médicos por mil habitantes e depois se achata, "
           "com muita variação entre países de mesmo nível de médicos."))
S.append(P(f"<b>b) Covariância e correlação.</b> Covariância = {n(q04['cov'],3)} (positiva, X e Y variam no mesmo sentido; seu valor depende das unidades). Correlação de Pearson r = {n(q04['r'],3)} (p {pv(q04['p_r'])}): "
           "associação linear positiva e forte (cerca de 0,70), estatisticamente significativa."))
S.append(fig("fig04c_correlacao.png", 7.2, "Figura 4. Gráfico (mapa de calor) da correlação linear de Pearson."))
S.append(P("<b>c) Gráfico da correlação.</b> O mapa de calor mostra o mesmo coeficiente (0,70) entre as duas variáveis: quanto mais vermelho, mais forte a correlação positiva."))
S.append(fig("fig04d_reta.png", 11.5, "Figura 5. Reta de regressão linear simples sobre o diagrama de dispersão."))
S.append(P(f"<b>d) Reta de regressão.</b> Expectativa de vida = {n(q04['b0'],3)} + {n(q04['b1'],3)} × (médicos por mil habitantes). "
           f"Cada médico a mais por mil habitantes se associa, em média, a {n(q04['b1'],2)} anos a mais de expectativa de vida; o intercepto ({n(q04['b0'],1)} anos) é o valor esperado para um país com praticamente nenhum médico."))
S.append(com_legenda(tabela([["Medida", "Valor"], ["R²", n(q04["r2"], 4)], ["R² ajustado", n(q04["r2a"], 4)],
                             [f"Teste F (1; {q04['gl2']} g.l.)", f"{n(q04['F'],2)} (p {pv(q04['pF'])})"],
                             ["Coeficiente de X: erro-padrão / t / p", f"{n(q04['se_b1'],3)} / {n(q04['t_b1'],2)} / {pv(q04['p_b1'])}"]], [8.5, 8.0]),
                     "Tabela 4. Adequação do modelo de regressão simples."))
S.append(P(f"<b>e) Adequação.</b> O teste F (p {pv(q04['pF'])}) mostra que o modelo é significativamente melhor que simplesmente usar a média. O R² de {n(q04['r2'],3)} indica que a oferta de médicos explica cerca de {pct(q04['r2'],0)} da variação da expectativa de vida, e o restante depende de outros fatores. "
           "Como a relação é curva, a reta superestima a expectativa de vida nos países com muitos médicos (por exemplo, prevê mais de 90 anos para 8 médicos por mil habitantes, quando o valor observado nesse extremo é de cerca de 79). "
           "Portanto, o modelo é útil para a faixa central dos dados, mas não para extrapolar."))
S.append(P(f"<b>f) Previsão.</b> Para {n(q04['x0'],1)} médicos por mil habitantes, o modelo estima <b>{n(q04['pred'],1)} anos</b>, com intervalo de predição de 95% de {n(q04['pred_li'],1)} a {n(q04['pred_ls'],1)} anos. "
           "O intervalo largo (cerca de 20 anos) mostra que, sozinha, a oferta de médicos prevê pouco o valor de um país específico."))

# 4.4
S += [H2("4.4 Regressão linear múltipla")]
S.append(P(f"Foram usados {q05['n']} países completos. Y = expectativa de vida; X = médicos por mil habitantes, ensino superior (%), fertilidade e urbanização (%)."))
S.append(fig("fig05a_dispersao.png", 14.0, "Figura 6. Matriz de dispersão entre a expectativa de vida e as variáveis explicativas."))
S.append(P("<b>a) Dispersão.</b> A fertilidade mostra a relação negativa mais nítida e quase linear com a expectativa de vida. Médicos e ensino superior têm relação positiva, com concentração de países perto de zero (distribuições assimétricas à direita) e curvatura. "
           "A urbanização tem relação positiva mais dispersa."))
ordem = q05["ordem_matriz"]
curto = ["Exp. vida", "Médicos", "Ens. sup.", "Fertilid.", "Urbaniz."]
S.append(com_legenda(tabela([[""] + curto] + [[curto[i]] + [n(v, 2) for v in q05["cov"][i]] for i in range(5)], [2.6] + [2.8] * 5), "Tabela 5. Matriz de covariância."))
S.append(com_legenda(tabela([[""] + curto] + [[curto[i]] + [n(v, 3) for v in q05["cor"][i]] for i in range(5)], [2.6] + [2.8] * 5), "Tabela 6. Matriz de correlação linear de Pearson."))
cor = q05["cor"][0]
S.append(P(f"<b>b) Covariância e correlação.</b> As covariâncias entre a expectativa de vida e as demais variáveis têm o mesmo sinal das correlações (positivas para médicos, ensino superior e urbanização; negativa para fertilidade), mas dependem das unidades e por isso não permitem comparar a força. "
           f"Pelas correlações: fertilidade {n(cor[3],3)} (negativa, muito forte), ensino superior {n(cor[2],3)}, médicos {n(cor[1],3)} e urbanização {n(cor[4],3)} (positivas, de forte a muito forte). "
           "As variáveis explicativas também se correlacionam entre si (por exemplo, médicos e ensino superior: 0,72), o que pede cuidado na leitura dos coeficientes."))
S.append(fig("fig05c_correlacao.png", 10.5, "Figura 7. Gráfico (mapa de calor) da correlação linear de Pearson entre as variáveis."))
S.append(P("<b>c) Gráfico da correlação.</b> A primeira linha do mapa mostra que a fertilidade (azul escuro) é a variável mais correlacionada com a expectativa de vida, seguida por ensino superior, médicos e urbanização (vermelho)."))
linhas = [["Termo", "Coeficiente", "Erro-padrão", "t", "p-valor"]] + [[c["nome"], n(c["b"], 4), n(c["se"], 4), n(c["t"], 2), pv(c["p"])] for c in q05["coef"]]
S.append(com_legenda(tabela(linhas, [5.4, 2.8, 2.8, 2.6, 2.8]), "Tabela 7. Coeficientes da regressão linear múltipla."))
S.append(P(f"<b>d) Equação.</b> {q05['equacao'].replace('×', ' × ')}.", "eq"))
c = q05["coef"]
S.append(P(f"<b>Interpretação dos coeficientes</b> (mantidas as demais variáveis constantes): cada filho a mais por mulher se associa a {n(abs(c[3]['b']),2)} anos a menos (p {pv(c[3]['p'])}), o maior efeito do modelo; "
           f"cada médico a mais por mil habitantes, a +{n(c[1]['b'],2)} ano (p = {n(c[1]['p'],3)}); cada ponto percentual a mais de matrícula no ensino superior, a +{n(c[2]['b'],3)} ano, ou cerca de {n(c[2]['b']*10,1)} ano a cada 10 pontos (p = {n(c[2]['p'],3)}); "
           f"e cada ponto percentual a mais de população urbana, a +{n(c[4]['b'],3)} ano, ou cerca de {n(c[4]['b']*10,1)} ano a cada 10 pontos (p = {n(c[4]['p'],3)}). "
           f"Note que o efeito dos médicos cai de {n(q04['b1'],2)} (modelo simples) para {n(c[1]['b'],2)}: parte do que parecia efeito dos médicos reflete o fato de que países com mais médicos também têm menos filhos por mulher, mais ensino superior e mais urbanização."))
v = q05["vif"]
S.append(P(f"<b>e) Adequação.</b> R² = {n(q05['r2'],4)} e R² ajustado = {n(q05['r2a'],4)}: o modelo explica cerca de {pct(q05['r2'],0)} da variação da expectativa de vida, bem mais que a regressão simples ({pct(q04['r2'],0)}). "
           f"O teste F (F({q05['gl1']}; {q05['gl2']}) = {n(q05['F'],2)}; p {pv(q05['pF'])}) indica que o conjunto das variáveis é significativo, e os quatro coeficientes são significativos a 5%. "
           f"Os fatores de inflação da variância (VIF) vão de {n(min(v.values()),2)} a {n(max(v.values()),2)}, abaixo de 5, o que indica multicolinearidade moderada e aceitável."))
br = q05["brasil"]; nv = q05["novo"]
S.append(P(f"<b>f) Previsão com quatro variáveis explicativas.</b> Para um país hipotético com {n(nv['medicos_mil'],1)} médicos por mil habitantes, {n(nv['ensino_superior'],0)}% de matrícula no ensino superior, fertilidade de {n(nv['fertilidade'],1)} filhos por mulher e {n(nv['urbanizacao'],0)}% de urbanização, "
           f"o modelo prevê <b>{n(q05['pred_novo'],1)} anos</b> (intervalo de predição de 95%: {n(q05['pred_novo_li'],1)} a {n(q05['pred_novo_ls'],1)}). "
           f"Como verificação, para o Brasil (médicos {n(br['medicos_mil'],2)} por mil, ensino superior {n(br['ensino_superior'],1)}%, fertilidade {n(br['fertilidade'],2)}, urbanização {n(br['urbanizacao'],1)}%) o modelo prevê {n(br['previsto'],1)} anos, contra {n(br['observado'],1)} observados."))

# 4.5
S += [H2("4.5 Regressão logística binária")]
S.append(P(f"<b>Variável resposta:</b> expectativa de vida <i>alta</i> (1) se o país tem expectativa de vida igual ou superior à mediana da base ({n(q06['corte'],1)} anos), e <i>baixa</i> (0) caso contrário ({pct(q06['prop_alta'],0)} dos países em cada classe). "
           f"<b>Explicativas:</b> médicos por mil habitantes, ensino superior, fertilidade e urbanização. A base de {q05['n']} países foi dividida em treino ({q06['n_treino']}) e teste ({q06['n_teste']}), de forma estratificada e com semente fixa."))
linhas = [["Termo", "Coeficiente", "Erro-padrão", "z", "p-valor", "Razão de chances"]] + [[c["nome"], n(c["b"], 4), n(c["se"], 4), n(c["z"], 2), pv(c["p"]), n(c["or"], 3)] for c in q06["coef"]]
S.append(com_legenda(tabela(linhas, [4.6, 2.4, 2.4, 1.8, 2.2, 3.0]), "Tabela 8. Coeficientes da regressão logística (estimados no conjunto de treino)."))
S.append(P(f"<b>a) Equação.</b> {q06['equacao'].replace('×', ' × ')}. A probabilidade de expectativa de vida alta é P = 1 ÷ (1 + e<super>−logit</super>). Pseudo-R² de McFadden = {n(q06['mcfadden'],3)}.", "eq"))
cc = q06["coef"]
S.append(P(f"<b>Interpretação.</b> A razão de chances de cada variável mostra por quanto se multiplicam as chances de expectativa de vida alta quando ela aumenta em uma unidade. "
           f"Cada filho a mais por mulher multiplica as chances por {n(cc[3]['or'],2)} (redução de cerca de {pct(1-cc[3]['or'],0)}; p {pv(cc[3]['p'])}), e cada ponto percentual a mais de urbanização, por {n(cc[4]['or'],3)} (aumento de cerca de {n((cc[4]['or']-1)*100,1)}%; p = {n(cc[4]['p'],3)}). "
           f"Médicos (p = {n(cc[1]['p'],3)}) e ensino superior (p = {n(cc[2]['p'],3)}) não foram significativos neste modelo: a informação que carregam já está, em boa parte, na fertilidade e na urbanização, com as quais se correlacionam."))
cmx = q06["confusao"]
S.append(fig("fig06b_confusao.png", 7.0, "Figura 8. Matriz de confusão no conjunto de teste."))
S.append(com_legenda(tabela([["", "Previsto: baixa", "Previsto: alta"], ["Real: baixa", cmx[0][0], cmx[0][1]], ["Real: alta", cmx[1][0], cmx[1][1]]], [4.0, 4.0, 4.0]),
                     "Tabela 9. Matriz de confusão (teste)."))
S.append(P(f"<b>b) Matriz de confusão e acurácia.</b> Dos {q06['n_teste']} países de teste, {cmx[0][0]+cmx[1][1]} foram classificados corretamente: acurácia de <b>{pct(q06['acuracia'],1)}</b>, sensibilidade de {pct(q06['sensibilidade'],1)} (acerto entre os de expectativa alta) "
           f"e especificidade de {pct(q06['especificidade'],1)} (acerto entre os de expectativa baixa). Um classificador que chutasse sempre a classe mais comum acertaria {pct(q06['base_majoritaria'],1)}, então o modelo traz ganho real. "
           f"A acurácia no treino foi maior ({pct(q06['acuracia_treino'],1)}), o que sugere leve sobreajuste; com apenas {q06['n_teste']} países de teste, a margem de erro da acurácia é de aproximadamente ±10 pontos percentuais."))
linhas = [["País", "Médicos/mil", "Ens. sup. (%)", "Fertilidade", "Urban. (%)", "P(alta)", "Classe"]]
for nome, d in q06["classificacoes"].items():
    vv = d["valores"]; linhas.append([nome, n(vv["medicos_mil"], 2), n(vv["ensino_superior"], 1), n(vv["fertilidade"], 2), n(vv["urbanizacao"], 1), pct(d["prob"], 1), d["classe"]])
S.append(com_legenda(tabela(linhas, [3.8, 1.9, 2.1, 2.2, 1.9, 1.9, 1.7]), "Tabela 10. Classificações com as quatro variáveis explicativas."))
S.append(P(f"<b>c) Classificação.</b> O país A (poucos médicos, baixa escolaridade superior, alta fertilidade e baixa urbanização) tem probabilidade quase nula de expectativa alta; o país B (perfil oposto) tem {pct(q06['classificacoes']['País B (hipotético)']['prob'],1)}. "
           f"O Brasil é classificado como <i>alta</i> ({pct(q06['classificacoes']['Brasil (dados reais)']['prob'],1)}), o que coincide com o observado ({n(q06['brasil_observado'],1)} anos, acima do corte de {n(q06['corte'],1)})."))

# ============================ 5 INSIGHTS ============================
S += [H1("5. Insights e recomendações para a tomada de decisão")]
S += [B("<b>Monitorar a fertilidade como marcador de desenvolvimento.</b> É o indicador que mais separa comunidades de maior e menor expectativa de vida, e reflete acesso a saúde reprodutiva e materno-infantil, escolaridade e renda. "
        "Isso <b>não</b> significa que reduzir a fertilidade, por si só, aumente a longevidade: o dado aponta onde olhar, e não qual política causaria o efeito."),
      B("<b>Ampliar a cobertura médica onde ela é mais baixa.</b> A curva de médicos x expectativa de vida é mais inclinada na faixa baixa (até cerca de 2 por mil habitantes) e se achata depois, o que sugere que o primeiro reforço de cobertura rende mais que o décimo. "
        "Essa é uma leitura visual do gráfico; confirmá-la exigiria um modelo não linear."),
      B("<b>Tratar urbanização e escolaridade como parte de um pacote.</b> Ambas se associam positivamente à longevidade, mas com efeito individual pequeno (cerca de 0,4 ano a cada 10 pontos percentuais) e muito entrelaçadas com saúde e fertilidade. Políticas urbanas e educacionais tendem a funcionar em conjunto com saúde, e não isoladamente."),
      B(f"<b>Usar o modelo como triagem, não como veredito.</b> Comparar o valor observado com o previsto ajuda a apontar localidades que estão abaixo do esperado para seu perfil (o Brasil está {n(abs(br['observado']-br['previsto']),1)} ano abaixo, diferença pequena diante da margem do modelo). "
        "Esses casos merecem investigação local."),
      B("<b>Próximo passo natural para o CitizenTech:</b> repetir a análise com dados municipais (por exemplo, IBGE e DATASUS), que é a escala em que as decisões de cidades e comunidades são tomadas.")]

# ============================ 6 LIMITAÇÕES ============================
S += [H1("6. Limitações das análises")]
S += [B("<b>Associação, não causa.</b> Os dados são observacionais e de um único ano; não há como separar causa e efeito, e podem existir fatores omitidos (renda, saneamento, conflitos, qualidade do sistema de saúde)."),
      B("<b>Nível de país.</b> Cada observação é um país inteiro. Relações entre países não valem necessariamente entre cidades, bairros ou indivíduos (falácia ecológica), e países muito diferentes pesam igual, independentemente de população."),
      B(f"<b>Tamanho e qualidade da amostra.</b> São {q05['n']} países completos (de {base['n_total']}); os ausentes foram excluídos, sem imputação, e a base foi compilada de fontes diversas, de modo que anos de referência e métodos de coleta podem diferir entre variáveis."),
      B(f"<b>Normalidade.</b> O enunciado pede para assumir normalidade, mas o teste de Shapiro-Wilk a rejeita para a expectativa de vida (p {pv(q02['shapiro_p'])}); as probabilidades e os testes dos itens 2 e 3 são aproximações."),
      B("<b>Linearidade.</b> A relação com médicos é curva, e a reta simples superestima os extremos. Os modelos lineares são aproximações úteis na faixa central dos dados, e não devem ser usados para extrapolar. Não foram feitos testes formais de heterocedasticidade ou normalidade dos resíduos."),
      B(f"<b>Classificação.</b> A variável binária foi criada cortando a expectativa de vida na mediana, o que descarta informação; a acurácia vem de apenas {q06['n_teste']} países de teste (margem de cerca de ±10 pontos percentuais) e o modelo mostrou leve sobreajuste."),
      B("<b>Testes de hipótese.</b> As amostras vêm da mesma base que define a média de referência, então o exercício ilustra o procedimento, mas não testa uma afirmação real sobre uma população externa.")]

# ============================ 7 CONCLUSÃO ============================
S += [H1("7. Conclusão")]
S.append(P(f"Com dados reais de {base['n_total']} países, mostramos que a expectativa de vida está fortemente associada à fertilidade (negativamente) e, em menor grau, à oferta de médicos, ao ensino superior e à urbanização (positivamente). "
           f"Um modelo linear com essas quatro variáveis explica {pct(q05['r2'],0)} das diferenças entre países, e um modelo logístico classifica corretamente cerca de {pct(q06['acuracia'],0)} dos países de teste entre expectativa de vida alta e baixa. "
           "Para o CitizenTech, o resultado indica indicadores a monitorar e perfis de comunidade a priorizar, ao mesmo tempo em que reforça a necessidade de dados em escala municipal e de modelos que capturem relações não lineares antes de qualquer decisão de investimento."))

# ============================ 8 REPRODUTIBILIDADE ============================
S += [H1("8. Reprodutibilidade")]
S.append(P("Repositório: <i>dados/</i> (base original e base tratada), <i>codigo/</i> (notebook <i>analise_mlam.ipynb</i> com saídas preservadas, script equivalente <i>analise_mlam.py</i> e este gerador de relatório), "
           "<i>figuras/</i>, <i>resultados/resultados.json</i> e <i>relatorio/</i>. Dependências: Python 3.10+, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn e reportlab (arquivo <i>requirements.txt</i>)."))

doc = SimpleDocTemplate(SAIDA, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
                        title="Relatório Estatístico – Global Solution MLAM", author=", ".join(i["nome"] for i in INT))
doc.build(S, onFirstPage=lambda c, d: None, onLaterPages=rodape)
print("Relatório gerado em", SAIDA)
