import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega variaveis
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, "config", ".env"))

GEMINI_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()

def list_allowed_models():
    print(f"Chave detectada (inicio): {GEMINI_KEY[:10]}...")
    if not GEMINI_KEY:
        print("ERRO: Chave GEMINI_API_KEY nao encontrada no .env")
        return

    try:
        genai.configure(api_key=GEMINI_KEY)
        print("\nModelos disponiveis para esta chave:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"   -> {m.name}")
    except Exception as e:
        print(f"\nERRO ao listar modelos: {e}")

if __name__ == "__main__":
    list_allowed_models()
