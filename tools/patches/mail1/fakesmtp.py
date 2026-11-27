import socket, ssl, threading, json, base64, sys, os
LOG = '/home/claude/mailtest/received.jsonl'
USERS = {'press@collaborativearchitecture.com': 'goodpass', 'enquiry@collaborativearchitecture.com': 'goodpass', 'studio@collaborativearchitecture.com': 'goodpass'}
ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH); ctx.load_cert_chain('/home/claude/mailtest/srv.crt', '/home/claude/mailtest/srv.key')
def handle(conn, starttls):
    f = conn.makefile('rwb', buffering=0)
    def send(s): f.write((s + '\r\n').encode())
    def line(): 
        l = f.readline()
        return l.decode(errors='replace').rstrip('\r\n') if l else None
    send('220 smtp.test ESMTP fake')
    st = {'auth': None, 'from': None, 'rcpt': [], 'tls': not starttls, 'port': 587 if starttls else 465}
    while True:
        l = line()
        if l is None: return
        u = l.upper()
        if u.startswith('EHLO'):
            send('250-smtp.test'); send('250-AUTH LOGIN PLAIN'); send('250 STARTTLS' if starttls and not st['tls'] else '250 8BITMIME')
        elif u == 'STARTTLS' and starttls:
            send('220 go ahead'); conn = ctx.wrap_socket(conn, server_side=True); f = conn.makefile('rwb', buffering=0); st['tls'] = True
        elif u == 'AUTH LOGIN':
            if not st['tls']: send('530 must STARTTLS'); continue
            send('334 VXNlcm5hbWU6'); user = base64.b64decode(line()).decode(); send('334 UGFzc3dvcmQ6'); pw = base64.b64decode(line()).decode()
            if USERS.get(user) == pw: st['auth'] = user; send('235 2.7.0 Accepted')
            else: send('535-5.7.8 Username and Password not accepted.'); send('535 5.7.8 BadCredentials')
        elif u.startswith('MAIL FROM'):
            if not st['auth']: send('530 5.7.0 Authentication Required'); continue
            st['from'] = l[10:].strip('<> '); send('250 OK')
        elif u.startswith('RCPT TO'):
            st['rcpt'].append(l[8:].strip('<> ')); send('250 OK')
        elif u == 'DATA':
            send('354 go'); data = []
            while True:
                d = line()
                if d is None or d == '.': break
                data.append(d)
            hdr = {}
            for d in data:
                if d == '': break
                if ':' in d: k, v = d.split(':', 1); hdr[k.strip()] = v.strip()
            body = base64.b64decode(''.join(data[data.index('') + 1:])).decode(errors='replace') if '' in data else ''
            with open(LOG, 'a') as o: o.write(json.dumps({'port': st['port'], 'auth': st['auth'], 'mail_from': st['from'], 'rcpt': st['rcpt'], 'From': hdr.get('From'), 'To': hdr.get('To'), 'Reply-To': hdr.get('Reply-To'), 'Subject': hdr.get('Subject'), 'body': body[:120]}) + '\n')
            send('250 2.0.0 OK queued')
        elif u == 'QUIT': send('221 bye'); return
        else: send('250 OK')
def serve(port, starttls):
    s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); s.bind(('127.0.0.1', port)); s.listen(20)
    while True:
        c, _ = s.accept()
        try:
            if not starttls: c = ctx.wrap_socket(c, server_side=True)
            threading.Thread(target=handle, args=(c, starttls), daemon=True).start()
        except Exception as e: c.close()
ports = sys.argv[1:] or ['465', '587']
for p in ports: threading.Thread(target=serve, args=(int(p), p == '587'), daemon=True).start()
threading.Event().wait()
