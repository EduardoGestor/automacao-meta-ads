import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime, timedelta

# 📌 Carregar Secrets do GitHub Actions
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN_TROPA")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID_TROPA")
GOOGLE_SHEET_TAB = os.getenv("GOOGLE_SHEET_TAB_TROPA")
LOG_EXECUTION = os.getenv("LOG_EXECUTION_TROPA", "false").lower() == "true"

# 📌 Configuração do Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credenciais_path = "/content/automacao-meta-ads.json"

# 📌 Autenticar no Google Sheets
creds = ServiceAccountCredentials.from_json_keyfile_name(credenciais_path, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(GOOGLE_SHEET_TAB)

# 📌 Configuração do Meta Ads API
AD_ACCOUNT_ID = "act_1916809535407174"
API_VERSION = "v18.0"

# 📌 Data de busca: Ontem
hoje = datetime.today()
data_ontem = hoje - timedelta(days=1)
data_formatada = data_ontem.strftime("%Y-%m-%d")
data_numerica = (data_ontem - datetime(1899, 12, 30)).days  # Formato do Google Sheets

# 📌 Buscar a Coluna Correta no Google Sheets
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
        erro_msg = f"⚠️ Erro ao buscar API: {jsonData['error']['message']}"
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
