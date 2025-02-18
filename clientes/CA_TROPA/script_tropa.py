import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime, timedelta

# 🔐 **INSERIR AQUI SUA CHAVE JSON DIRETAMENTE NO SCRIPT** 
GOOGLE_CREDENTIALS_JSON = {
  "type": "service_account",
  "project_id": "automacao-meta-ads",
  "private_key_id": "115f4b58ec921d7c84130fcb58be75631ba13d15",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCw6dze5zD34AyO\n...",
  "client_email": "google-sheets-api@automacao-meta-ads.iam.gserviceaccount.com",
  "client_id": "113736604810452032719",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-sheets-api%40automacao-meta-ads.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# 📌 Criar o arquivo JSON localmente
CREDENTIALS_PATH = "automacao-meta-ads.json"

try:
    with open(CREDENTIALS_PATH, "w", encoding="utf-8") as f:
        json.dump(GOOGLE_CREDENTIALS_JSON, f, indent=2)

    if not os.path.exists(CREDENTIALS_PATH) or os.stat(CREDENTIALS_PATH).st_size == 0:
        raise FileNotFoundError(f"❌ ERRO: O arquivo {CREDENTIALS_PATH} não foi criado corretamente!")

    print("✅ Arquivo de credenciais JSON criado e validado!")

except json.JSONDecodeError as e:
    print(f"❌ ERRO: Falha ao decodificar JSON das credenciais: {e}")
    exit(1)
except Exception as e:
    print(f"❌ ERRO inesperado ao salvar credenciais: {e}")
    exit(1)

# 📌 Autenticar no Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
client = gspread.authorize(creds)

# 📌 Configuração do Meta Ads API
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN_TROPA")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID_TROPA")
GOOGLE_SHEET_TAB = os.getenv("GOOGLE_SHEET_TAB_TROPA")
LOG_EXECUTION = os.getenv("LOG_EXECUTION_TROPA", "false").lower() == "true"

AD_ACCOUNT_ID = "act_1916809535407174"
API_VERSION = "v22.0"

# 📌 Data de busca: Ontem
hoje = datetime.today()
data_ontem = hoje - timedelta(days=1)
data_formatada = data_ontem.strftime("%Y-%m-%d")
data_numerica = (data_ontem - datetime(1899, 12, 30)).days

# 📌 Buscar a Coluna Correta no Google Sheets
sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(GOOGLE_SHEET_TAB)
datas_na_planilha = sheet.row_values(2, value_render_option='UNFORMATTED_VALUE')
coluna_dia = None

for idx, valor in enumerate(datas_na_planilha):
    if isinstance(valor, (int, float)) and int(valor) == data_numerica:
        coluna_dia = idx + 1
        break

if coluna_dia:
    print(f"📅 Coluna encontrada para {data_formatada}: {coluna_dia}")

    # 📌 Buscar Dados no Meta Ads API
    url = f"https://graph.facebook.com/{API_VERSION}/{AD_ACCOUNT_ID}/insights"
    params = {
        "fields": "spend,impressions,inline_link_clicks,inline_link_click_ctr,actions",
        "time_range": f'{{"since":"{data_formatada}","until":"{data_formatada}"}}',
        "level": "account",
        "access_token": META_ACCESS_TOKEN,
    }

    response = requests.get(url, params=params)
    jsonData = response.json()

    if "error" in jsonData:
        erro_msg = f"⚠️ Erro ao buscar API: {jsonData['error']['message']} - Tipo: {jsonData['error']['type']}"
        print(erro_msg)
        log_data = f"{datetime.now()} - ERRO - {erro_msg}\n"
    else:
        # 📌 Processar Dados
        totalSpend = sum(float(item.get("spend", 0)) for item in jsonData.get("data", []))
        totalImpressions = sum(int(item.get("impressions", 0)) for item in jsonData.get("data", []))
        totalClicks = sum(int(item.get("inline_link_clicks", 0)) for item in jsonData.get("data", []))

        ctr = (totalClicks / totalImpressions) * 100 if totalImpressions > 0 else 0

        # 📌 Atualizar Planilha
        sheet.update_cell(3, coluna_dia, f"R$ {totalSpend:,.2f}")  # Investimento
        sheet.update_cell(4, coluna_dia, str(totalImpressions))  # Impressões
        sheet.update_cell(5, coluna_dia, f"{ctr:.2f}%")  # CTR

        print(f"✅ Dados inseridos: R$ {totalSpend:,.2f}, {totalImpressions} impressões, CTR {ctr:.2f}%")
        log_data = f"{datetime.now()} - SUCESSO - Dados inseridos para {data_formatada}\n"

    # 📌 Salvar Log
    if LOG_EXECUTION:
        with open("logs.txt", "a") as log_file:
            log_file.write(log_data)
else:
    print(f"⚠️ Nenhuma coluna encontrada para {data_formatada}")
