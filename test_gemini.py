import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import requests

print("=== INICIANDO TESTE ===")

# Carrega variáveis do .env
load_dotenv()
print("Arquivo .env carregado")

# Configura a API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"Chave API: {'*****' + GEMINI_API_KEY[-4:] if GEMINI_API_KEY else 'NÃO ENCONTRADA'}")

if not GEMINI_API_KEY:
    print("Erro: Chave API não encontrada no arquivo .env")
    exit(1)

# Teste de conexão básica antes da chamada principal
print("Verificando conexão com a API...")
try:
    response = requests.get("https://generativelanguage.googleapis.com/v1beta/models", 
                          params={"key": GEMINI_API_KEY},
                          timeout=10)
    print(f"Status da verificação: {response.status_code}")
    if response.status_code == 200:
        print("Conexão com a API estabelecida com sucesso")
    else:
        print(f"Erro na verificação: {response.text[:200]}")
except Exception as e:
    print(f"Falha na verificação de conexão: {str(e)}")
    exit(1)

try:
    print("Configurando API...")
    genai.configure(api_key=GEMINI_API_KEY, transport='rest')
    
    print("Criando modelo...")
    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    
    print("Enviando prompt...")
    time.sleep(1)
    
    # Chamada com timeout de 30 segundos
    response = model.generate_content(
        "Me explique em 1 frase como funciona o Gemini",
        request_options={"timeout": 30}
    )
    
    print("\n=== RESPOSTA DO GEMINI ===")
    print(response.text)
    print("=========================")

except Exception as e:
    print("\n=== ERRO DETALHADO ===")
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensagem: {str(e)}")
    
    # Log adicional para erros específicos do Gemini
    if hasattr(e, 'response') and e.response:
        print(f"Status HTTP: {e.response.status_code}")
        print(f"Resposta: {e.response.text[:200]}")
    
    print("=====================")
