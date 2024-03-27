# sliqestress

concurrently write to sqlite database to see how fast you can reach the
"database-locked" situation.


```
python3 sqlitestress.py -d test.db -i 2000 -w 10
Worker: 10
Every 5th process inserts: 2000 values
rows: 8717
rows: 16717
rows: 24722
Error during process 28 database is locked
Error during process 28 database is locked
Error during process 28 database is locked
Error during process 28 database is locked
Error during process 28 database is locked
Error during process 28 database is locked
```
