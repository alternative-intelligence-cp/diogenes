import os, sqlite3, sys, time
d = os.path.dirname(os.path.abspath(__file__)); db = os.path.join(d, 'probe.db')
time.sleep(float(sys.argv[1])); end = time.time() + float(sys.argv[2]); i = 0
while time.time() < end:
    i += 1
    c = sqlite3.connect(db, timeout=10, isolation_level=None); c.execute('PRAGMA busy_timeout=10000')
    c.execute("UPDATE lease SET holder=NULL, expires_at=0, round=? WHERE id='t'", (i,)); c.close()
    time.sleep(0.5)
open(os.path.join(d, f'done.referee.{i}'), 'w').write(str(i))
