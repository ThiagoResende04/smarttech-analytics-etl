import os
import time
import pymysql
from playwright.sync_api import sync_playwright
from google import genai

# ==========================================
# CONFIGURAÇÕES DE CREDENCIAIS E CONEXÃO
# ==========================================
API_KEY_GEMINI = os.environ.get("GEMINI_API_KEY") or "SUA_CHAVE_API_AQUI"
client = genai.Client(api_key=API_KEY_GEMINI)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'db_smarttech'
}


# ==========================================
# 1. FUNÇÃO PARA INICIALIZAR O BANCO DE DADOS
# ==========================================
def inicializar_banco():

    print("🗄️ [Banco de Dados] Verificando estrutura da tabela...")
    try:
        conexao = pymysql.connect(**DB_CONFIG)
        with conexao.cursor() as cursor:
            sql_criar_tabela = """
            CREATE TABLE IF NOT EXISTS tb_smartphones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(255) NOT NULL,
                preco DECIMAL(10, 2) NOT NULL,
                categoria_ia VARCHAR(50),
                avaliacao_ia VARCHAR(50),
                insight_ia TEXT,
                data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(sql_criar_tabela)
        conexao.commit()
        conexao.close()
        print("✅ [Banco de Dados] Tabela 'tb_smartphones' pronta para uso!")
    except Exception as e:
        print(f"❌ [Banco de Dados] Erro ao inicializar: {e}")
        os._exit(1)


# ==========================================
# 2. FUNÇÃO DE CONTINGÊNCIA (FALLBACK LOCAL CORRIGIDO)
# ==========================================
def simular_analise_local(titulo, preco):

    titulo_lower = titulo.lower()

    if any(k in titulo_lower for k in ["iphone 15", "iphone 16", "galaxy s24", "galaxy s25", "ultra"]):
        categoria = "Premium / Top de Linha"
    elif any(k in titulo_lower for k in ["pro", "max", "plus", "256gb", "edge", "fusion"]):
        categoria = "Intermediário Avançado"
    else:
        categoria = "Entrada / Custo-benefício"

    if preco > 4500:
        avaliacao = "Preço Elevado"
        insight = "Dispositivo premium. Recomendado monitorar gráficos de preço antes de fechar."
    elif 2000 <= preco <= 4500:
        avaliacao = "Preço de Mercado"
        insight = "Valor condizente com a média para a categoria técnica do aparelho."
    else:
        avaliacao = "Bom Custo-Benefício"
        insight = "Aparelho acessível. Ótima opção para tarefas diárias e rotina."

    # 📌 CORREÇÃO: Ajustado de category_ia para categoria para evitar NameError
    return {"categoria": categoria, "avaliacao": avaliacao, "insight": insight}


# ==========================================
# 3. FUNÇÃO DE INTEGRAÇÃO COM INTELIGÊNCIA ARTIFICIAL
# ==========================================
def analisar_produto_com_ia(titulo, preco):

    print(f"🤖 IA analisando: {titulo[:35]}...")

    prompt = f"""
    Baseado no nome do smartphone e no preço fornecido, responda estritamente no formato abaixo, separado por ponto e vírgula (;):
    CATEGORIA;AVALIAÇÃO_PREÇO;INSIGHT

    Produto: {titulo}
    Preço: R$ {preco}

    Regras de Negócio:
    - CATEGORIA: Classifique em (Entrada, Intermediário ou Premium).
    - AVALIAÇÃO_PREÇO: Classifique em (Barato, Justo ou Caro).
    - INSIGHT: Uma breve recomendação se vale a pena comprar baseado na ficha técnica presumida pelo título.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        resposta = response.text.strip()
        partes = resposta.split(";")

        if len(partes) == 3:
            return {
                "categoria": partes[0].strip(),
                "avaliacao": partes[1].strip(),
                "insight": partes[2].strip()
            }
    except Exception as e:
        print(f"⚠️ Instabilidade na API de IA ({str(e)[:40]}...). Acionando heurística local...")

    return simular_analise_local(titulo, preco)


# ==========================================
# 4. FUNÇÃO PARA SALVAR REGISTRO NO BANCO DE DADOS
# ==========================================
def salvar_no_banco(titulo, preco, ia_data):

    try:
        conexao = pymysql.connect(**DB_CONFIG)
        with conexao.cursor() as cursor:
            comando_sql = """
            INSERT INTO tb_smartphones (titulo, preco, categoria_ia, avaliacao_ia, insight_ia)
            VALUES (%s, %s, %s, %s, %s)
            """
            valores = (titulo, preco, ia_data["categoria"], ia_data["avaliacao"], ia_data["insight"])
            cursor.execute(comando_sql, valores)

        conexao.commit()
        conexao.close()
        print(f"💾 [SQL] Gravado no banco: {titulo[:25]}... -> R$ {preco}")
    except Exception as e:
        print(f"❌ [SQL] Falha ao persistir registro: {e}")


# ==========================================
# 5. ORQUESTRAÇÃO DO ROBÔ (WEB SCRAPING)
# ==========================================
def rodar_pipeline_dados():
    print("\n=== INICIANDO PIPELINE DE DADOS: SMARTTECH ANALYTICS ===")
    inicializar_banco()

    with sync_playwright() as p:
        print("\nIniciando motor de navegação Chrome...")
        navegador = p.chromium.launch(headless=False, channel="chrome")
        contexto = navegador.new_context(
            viewport={"width": 1366, "height": 768},
            locale="pt-BR",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        pagina = contexto.new_page()

        url_alvo = "https://www.amazon.com.br/s?k=smartphone"
        print(f"Acessando e-commerce alvo: {url_alvo}")
        pagina.goto(url_alvo)

        print("\n" + "=" * 60)
        print("PAUSA DE SEGURANÇA (MODO HÍBRIDO):")
        print("Aguarde a listagem de celulares carregar na tela.")
        print("Quando os smartphones aparecerem com os preços, volte aqui.")
        print("=" * 60)

        input("\n--> Celulares visíveis na tela? Aperte ENTER para processar o pipeline: ")

        print("\nVarrendo a estrutura DOM da página...")

        blocos_produtos = pagina.locator("div[data-component-type='s-search-result']").all()
        if not blocos_produtos:
            blocos_produtos = pagina.locator(".s-result-item[data-asin]").all()

        produtos_processados = 0

        for bloco in blocos_produtos:
            try:
                titulo = bloco.locator("h2").inner_text().strip()
                titulo_lower = titulo.lower()
                palavras_chave = ["celular", "smartphone", "iphone", "galaxy", "xiaomi", "redmi", "pova", "motorola",
                                  "moto g", "realme"]
                ignore_list = ["capa", "capinha", "pelicula", "fone", "carregador", "suporte", "cabo"]

                if any(k in titulo_lower for k in palavras_chave) and not any(i in titulo_lower for i in ignore_list):

                    preco_final = None

                    try:
                        if bloco.locator(".a-price-whole").count() > 0:
                            texto_reais = bloco.locator(".a-price-whole").first.inner_text()
                            texto_reais = texto_reais.replace(".", "").replace(",", "").replace("\n", "").strip()
                            try:
                                texto_centavos = bloco.locator(".a-price-fraction").first.inner_text().strip()
                            except:
                                texto_centavos = "00"
                            preco_final = float(f"{texto_reais}.{texto_centavos}")
                    except:
                        pass

                    if not preco_final:
                        try:
                            if bloco.locator(".a-offscreen").count() > 0:
                                texto_preco = bloco.locator(".a-offscreen").first.inner_text()
                                texto_preco = texto_preco.replace("R$", "").replace(".", "").strip()
                                texto_reais, texto_centavos = texto_preco.split(",")
                                preco_final = float(f"{texto_reais.strip()}.{texto_centavos.strip()}")
                        except:
                            continue

                    if not preco_final or preco_final <= 0:
                        continue

                    print("-" * 50)
                    dados_ia = analisar_produto_com_ia(titulo, preco_final)
                    salvar_no_banco(titulo, preco_final, dados_ia)

                    produtos_processados += 1
                    time.sleep(4)

                if produtos_processados >= 15:  # Coleta até 15 smartphones para popular o banco
                    break
            except Exception:
                continue

        print("\n🏁 Pipeline finalizado com sucesso!")
        print(f"Foram analisados e inseridos {produtos_processados} smartphones no banco de dados.")
        navegador.close()
        os._exit(0)


if __name__ == "__main__":
    rodar_pipeline_dados()