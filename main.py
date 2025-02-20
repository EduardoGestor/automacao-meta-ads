import os
import json
import subprocess
from datetime import datetime

# 🔹 Diretório base dos clientes
CLIENTES_DIR = "clientes/"

# 🔹 Criar pasta de logs se não existir
LOG_DIR = "logs/"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 🔹 Criar arquivo de log
log_file_path = os.path.join(LOG_DIR, "execucao.log")

def registrar_log(mensagem):
    """Função para registrar logs da execução"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{timestamp} - {mensagem}\n")
    print(mensagem)

# 🔹 Função para rodar os scripts de cada cliente
def executar_scripts():
    """Executa os scripts dos clientes encontrados na pasta `clientes/`"""
    
    clientes = [c for c in os.listdir(CLIENTES_DIR) if os.path.isdir(os.path.join(CLIENTES_DIR, c))]
    
    if not clientes:
        registrar_log("❌ Nenhum cliente encontrado na pasta 'clientes/'.")
        return

    for cliente in clientes:
        cliente_path = os.path.join(CLIENTES_DIR, cliente)
        script_path = os.path.join(cliente_path, "script.py")
        config_path = os.path.join(cliente_path, "config.json")

        if not os.path.exists(script_path) or not os.path.exists(config_path):
            registrar_log(f"⚠️ Cliente {cliente} não tem 'script.py' ou 'config.json'. Pulando...")
            continue

        # 🔹 Carregar Configurações do Cliente
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        
        # 🔹 Executar o script do cliente com as variáveis de ambiente
        env_vars = {
            "GOOGLE_SHEET_ID": config.get("GOOGLE_SHEET_ID"),
            "GOOGLE_SHEET_TAB": config.get("GOOGLE_SHEET_TAB"),
            "META_ACCESS_TOKEN": os.getenv("META_ACCESS_TOKEN")
        }

        try:
            registrar_log(f"🚀 Executando script para cliente: {cliente}")
            subprocess.run(["python", script_path], env={**os.environ, **env_vars}, check=True)
            registrar_log(f"✅ Concluído com sucesso para cliente: {cliente}")
        except subprocess.CalledProcessError:
            registrar_log(f"❌ Erro ao executar script para cliente: {cliente}")

if __name__ == "__main__":
    registrar_log("🔄 Iniciando execução dos scripts...")
    executar_scripts()
    registrar_log("🏁 Execução concluída!")
