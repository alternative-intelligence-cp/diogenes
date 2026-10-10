import os, sqlite3, sys, time
me, free_s, total_s = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
d = os.path.dirname(os.path.abspath(__file__)); db = os.path.join(d, 'probe.db'); t0 = time.time()
def take(ttl, rnd=None):
    c = sqlite3.connect(db, timeout=5, isolation_level=None)
    c.execute('PRAGMA busy_timeout=5000'); c.execute('BEGIN IMMEDIATE')
    now = time.time()
    r = c.execute("UPDATE lease SET holder=?, fence=fence+1, expires_at=? WHERE id='t' AND (holder IS NULL OR expires_at<?)", (me, now + ttl, now)).rowcount
    if r and rnd is not None: c.execute("INSERT INTO wins SELECT round, ? FROM lease WHERE id='t'", (me,))
    c.execute('COMMIT'); c.close(); return r
def record(phase, rounds, wins, errors):
    c = sqlite3.connect(db, timeout=10, isolation_level=None); c.execute('PRAGMA busy_timeout=10000')
    c.execute('INSERT INTO results VALUES(?,?,?,?,?)', (me, phase, rounds, wins, errors)); c.close()
w = r = e = 0
while time.time() < t0 + free_s:                       # phase 1: free-running takes with a 1 ms TTL
    try: w += take(0.001); r += 1
    except sqlite3.Error as x: e += 1; last = repr(x)
record('free', r, w, e)
w = r = e = 0
while time.time() < t0 + total_s:                      # phase 2: both hammer a 60 s lease; only the referee frees it
    r += 1
    try: w += take(60, True)
    except sqlite3.Error as x: e += 1
    time.sleep(0.002)
record('contested', r, w, e)
open(os.path.join(d, f'done.{me}'), 'w').write('ok')
