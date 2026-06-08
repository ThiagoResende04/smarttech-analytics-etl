# 📱 SmartTech Analytics - ETL Pipeline com Python, Playwright, Gemini AI & MySQL

O **SmartTech Analytics** é uma aplicação completa de engenharia de dados que realiza o processo de **ETL (Extract, Transform, Load)** focado no mercado de smartphones. O robô extrai dados reais em tempo real da Amazon Brasil, utiliza Inteligência Artificial para análise mercadológica e persiste os dados de forma estruturada em um banco de dados relacional.

---

## 🛠️ Arquitetura do Pipeline (ETL)

1. **Extração (Extract):** Navegação e raspagem automatizada na Amazon utilizando **Playwright** com seletores de redundância dinâmicos.
2. **Transformação (Transform):** Higienização de strings de valores para conversão em `float`, filtragem seletiva de anúncios correlacionados (limpeza de ruídos como capinhas/películas) e enriquecimento de dados via LLM (**Google Gemini 2.5 Flash**).
3. **Carga (Load):** Conexão robusta via **PyMySQL** com banco de dados **MySQL** local para gravação estruturada usando boas práticas de comandos SQL estruturados.

---

## 🛡️ Diferenciais Técnicos Aplicados

* **Heurística de Fallback (Resiliência):** Caso a API de Inteligência Artificial sofra instabilidades (`503 UNAVAILABLE`) ou atinja o limite de requisições gratuitas (`429 RESOURCE_EXHAUSTED`), o pipeline chaveia automaticamente para um motor lógico local baseado em palavras-chave e regras de negócio para evitar a perda ou interrupção do fluxo de dados.
* **Persistência Relacional:** Criação automática de tabelas estruturadas (DDL) e inserção limpa de registros através do Python executando instruções parametrizadas para evitar falhas.

---

## 📋 Pré-requisitos e Dependências

```bash
pip install playwright pymysql google-genai
playwright install chrome

