# sliqestress

concurrently write to sqlite database to see how fast you can reach the
"database-locked" situation.


```
python3 sqlitestress.py -d test.db -i 200 -w 15
WAL mode as returned by connection: wal
Worker: 15
Every 5th process inserts: 200 values
rows: 400
rows: 1234
rows: 2034
[..]
rows: 25404
rows: 26148
rows: 26948
Error: database is locked
Error: database is locked
Error: database is locked
```
