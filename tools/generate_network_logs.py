import random
import time

# Konfiguracja generowania danych
NUM_LINES = 10000
OUTPUT_FILE = "mock_network_logs.log"

IP_POOL = [f"192.168.1.{i}" for i in range(10, 200)]
BRUTE_FORCE_ATTACKER_IP = "203.0.113.5"
SQL_INJECTION_ATTACKER_IP = "198.51.100.12"

URLS = ["/index.html", "/assets/style.css", "/api/v1/status", "/news/post-1", "/contact"]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

def generate_log_line(ip, method, url, status, size):
    timestamp = time.strftime("%d/%b/%Y:%H:%M:%S +0000", time.gmtime(time.time() - random.randint(0, 3600)))
    ua = random.choice(USER_AGENTS)
    return f'{ip} - - [{timestamp}] "{method} {url} HTTP/1.1" {status} {size} "{ua}"\n'

with open(OUTPUT_FILE, "w") as f:
    for i in range(NUM_LINES):
        # Wstrzykiwanie ataku Brute Force (Wiele błędów 401 z jednego IP pod koniec pliku)
        if 5000 < i < 5035:
            f.write(generate_log_line(BRUTE_FORCE_ATTACKER_IP, "POST", "/wp-login.php", 401, 234))
        # Wstrzykiwanie ataku SQL Injection
        elif i == 7500:
            f.write(generate_log_line(SQL_INJECTION_ATTACKER_IP, "GET", "/api/users?id=1+union+select+from+users", 200, 1045))
        # Standardowy, bezpieczny ruch sieciowy
        else:
            ip = random.choice(IP_POOL)
            url = random.choice(URLS)
            status = random.choices([200, 304, 404], weights=[85, 12, 3])[0]
            size = random.randint(150, 5000) if status == 200 else 0
            f.write(generate_log_line(ip, "GET", url, status, size))

print(f"Sukces! Wygenerowano plik: {OUTPUT_FILE} ({NUM_LINES} linii)")