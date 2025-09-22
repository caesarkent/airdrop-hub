# Optional Telegram notifier. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars.
import os, time, sqlite3, requests
DB = 'airdrops.db'
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
if not TOKEN or not CHAT_ID:
    print('Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to use notifier. Exiting.')
    exit(0)
def get_last():
    f = '.last_sent'
    if os.path.exists(f):
        try:
            return int(open(f).read().strip())
        except:
            return 0
    return 0
def set_last(i):
    open('.last_sent','w').write(str(i))
def fetch_new(last):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT id, title, description, network, url FROM airdrop WHERE id > ? ORDER BY id ASC', (last,))
    rows = cur.fetchall()
    conn.close()
    return rows
def send(text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    return requests.post(url, json={'chat_id': CHAT_ID, 'text': text})
last = get_last()
print('Starting notifier, last=', last)
while True:
    rows = fetch_new(last)
    for r in rows:
        aid, title, desc, net, url = r
        txt = f"New airdrop: {title}\nNetwork: {net}\n{url}\n{desc[:200]}"
        print('Sending:', txt)
        resp = send(txt)
        print('resp', resp.status_code)
        last = aid
        set_last(last)
    time.sleep(10)
