import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime, timedelta

# 🔑 **Chave JSON embutida diretamente no script**
GOOGLE_SERVICE_ACCOUNT = {
    "type": "service_account",
    "project_id": "automacao-meta-ads",
    "private_key_id": "115f4b58ec921d7c84130fcb58be75631ba13d15",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCw6dze5zD34AyO\nuSHCl4afeqIgKlCxaxan4bGqph1WCannLrQ6FZUGeShFxZgS3XyC6JkYZjpVu0/+\nzL0wXb6b1FRr8P9syVLAko4avhMfBW7tIIsiHDay51Dj8Zv4mfBBRqbMeO3EuZaU\nFuNoyj9a2VyMP+97X2MhF3dOXau63gCAolTqhOwY+aULX7Sw6ORclbRPl+7eZqWn\n/6WTxlLDzkHHAJmEE0A8AQKB751dwboorU7guapSWRwP47765XafR6Zi2QkDLNDt\n4h1IRzpMZ6k7Hy4UX71sMblEsb/vom8AWrFVsy97PxjTPhLYAiaRbu+PRCm4d4py\nEOorX5tFAgMBAAECggEAHjPmycU1dnPxIOKZUWPWD17707r1qLxsE0A0OTp/0qL2\ntymhijMKDJ9dkT/RHRNkAONd060MM3u1hf4FJH80ndzrhrwPl05tisPab9VYZVjj\nnacLKckgS32zMR8b7h61xiceLdVNXmMCwoh/zXGNzGBEbQszQuA/h7Q+YYobWdzo\n29IC0L0QopkVeR52PUcJ88B23/wbyRUID+sKUKMrnZoF1wtOBDBDXSUoHQ1Qa4Tl\nf3UI8+ce8v1eN5JiPxupRESrOO7p07DTQnZTA60i3ZSQyQfvjnMb83te8GH0W5l5\ncQrSFwP/p0OpGv4GPA/3uujOj/SsARnblLdX1GPJUQKBgQDmUFVo3ROES+DCLnJ7\n4tRy7Drskv++97/myX3SiAyoIYdYwHZbrLhisLH4Y45kWjxfXZI7fvhOXC+6e4Uj\nfnMv0CiuF4MDoTXb10SV+mlGgztBlfMwxcww+mYISVH//Va31Ee0kRtWIelC0Jzs\nqNmlqNavaw0+k50uaILv6bMouQKBgQDEpOc27HaaLjtgiqwYbGVjugsqBYnP1/0y\nXyyN61l4dj1zUIhdLSmRYGskeO56Gf5wSBoYChv+KO0wXVy5T6vNJ4KmTJdikrhG\n6hOGRkdT/nPdOgFcYOw/Z0Bz+fJIh/wXB7vU/mM7K0rSah2aanXPfrPJvVZ7uG+s\npOSaRFYo7QKBgEnb71f+tdiSYNTFAm/aUVk9irP9fEiouQDxEwmmGbD9d6MtrYc+\nv67ejWRjwPFLwtqubkvoLwcqJyA9pne4gIYP0kvqPFi4pUYIJfWW5ZX4VdN1nBTD\nCfWXB4uWv9ZBT0MKr6gndMXNgDmuHvUCPTIUEC0XPpsXyattVrhLkOn5AoGACRj3\n+XqHIirxZE4GGDsrlamNyqvm7E650BLHJOm2gfQ2c5dON8FXIvqq+kz9+3goZVlw\nm5wcH24VSx+Goqwk7qDdUoRInK7dB6rcrGGj+ybShXGhjnyNcYF9YeA2bVSdPROG\nhRwfyyT9mS5/oB08xhS+jJ7N2Xt27y3RxbFTqyECgYBhjDt5/wVMFOTDkGrs760H\nMoAwPwiRR7ehoQS3/YvLBKxK42wOwcdvuIExj8a0Xw37MlOwnC7kiypP5StMjJHK\n2jzRcUF4U5zxcLFfS/w9heS8Xv1tPkCT82z5z1NuRghmPPc4RFaseCC8GxrMax23\nkOlFJkzEDTm7pDMPDYloVQ==\n-----END PRIVATE KEY-----\n",
    "client_email": "google-sheets-api@automacao-meta-ads.iam.gserviceaccount.com",
    "client_id": "113736604810452032719",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-sheets-api%40automacao-meta-ads.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# 📌 Autenticação no Google Sheets
CREDENTIALS_PATH = "automacao-meta-ads.json"
with open(CREDENTIALS_PATH, "w", encoding="utf-8") as f:
    json.dump(GOOGLE_SERVICE_ACCOUNT, f, indent=2)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
client = gspread.authorize(creds)

# 📌 Configuração da Planilha
GOOGLE_SHEET_ID = "1rbf0kSbJGUyChRxKZWc5qaHurcUdYKxsivI41DivEJM"
GOOGLE_SHEET_TAB = "FEV/2025"

# 📌 Abrir Planilha
sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(GOOGLE_SHEET_TAB)
print("✅ Conexão bem-sucedida com o Google Sheets!")

