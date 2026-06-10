from fastapi import FastAPI
import pymysql

app = FastAPI(
    title="SmartTech Analytics API",
    description="API para consultar os smartphones analisados pelo robô e pela IA",
    version="1.0.0"
)


DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'db_smarttech',
    'cursorclass': pymysql.cursors.DictCursor  
}


@app.get("/")
def ler_raiz():
    return {"status": "API Online", "mensagem": "Use a rota /smartphones para ver os dados."}


@app.get("/smartphones")
def listar_smartphones():
    try:
        conexao = pymysql.connect(**DB_CONFIG)
        with conexao.cursor() as cursor:
            # Comando SQL para buscar tudo do banco
            cursor.execute("SELECT * FROM tb_smartphones ORDER BY id DESC")
            resultados = cursor.fetchall()
        conexao.close()
        return resultados
    except Exception as e:
        return {"erro": f"Falha ao conectar ao banco de dados: {e}"}
