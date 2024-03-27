"""Little util to check how much concurrent writes your hardware
can handle"""

import sqlite3
import concurrent.futures
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dbfile", default=None, required=True, help="Path to db")
parser.add_argument(
    "-w", "--worker", default=4, required=False, help="amount of processes"
)
parser.add_argument(
    "-i", "--inserts", default=100, required=False, help="amount insert statements"
)
parser.add_argument(
    "-o",
    "--onlyinsert",
    default=False,
    required=False,
    action="store_true",
    help="execute only insert statements",
)
parser.add_argument(
    "-e",
    "--every",
    default=5,
    required=False,
    help="every X process inserts instead of selects, default: %(default)s)",
)
parser.add_argument(
    "-W",
    "--wal-mode",
    default="wal",
    choices=["wal", "wal2"],
    required=False,
    help="Wal mode to use, default:  %(default)s)",
)
parser.add_argument(
    "-B",
    "--busy-timeout",
    default=0,
    type=int,
    required=False,
    help="Set sqlite busy timeout in milliseconds, default:  %(default)s)",
)
parser.add_argument(
    "-c",
    "--cycles",
    default=500,
    required=False,
    help="amount of iterations, default: %(default)s)",
)
parser.add_argument(
    "-n",
    "--nodelete",
    default=False,
    action="store_true",
    required=False,
    help="do not remove table",
)

args = parser.parse_args()


def sqlite_doit(cnt, args):
    """write"""
    local_conn = sqlite3.connect(
        args.dbfile,
        # these two values have great impact on
        # database-locked situations
        isolation_level=None,
        timeout=10,
    )
    cursor = local_conn.cursor()
    cursor.execute(f"PRAGMA journal_mode={args.wal_mode}")
    if args.busy_timeout != 0:
        cursor.execute(f"pragma busy_timeout={args.busy_timeout}")

    if cnt % int(args.every):
        for _ in range(int(args.inserts)):
            cursor.execute("insert into test values('1')")
    else:
        if not args.onlyinsert:
            cursor.execute("select * from test")

    ret = cursor.fetchall()
    cursor.close()
    local_conn.close()

    return cnt, ret


def main():
    """main"""
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=int(args.worker)
    ) as executor:
        # setup db
        conn = sqlite3.connect(args.dbfile, isolation_level=None)
        dbcon = conn.cursor()
        dbcon.execute(f"PRAGMA journal_mode={args.wal_mode}")
        walmode = dbcon.fetchone()[0]
        print(f"WAL mode as returned by connection: {walmode}")
        if walmode != args.wal_mode:
            print(
                f"Warning: Wal mode {args.wal_mode} requested but Database defaults to: {walmode}"
            )
        if args.busy_timeout != 0:
            dbcon.execute(f"pragma busy_timeout={args.busy_timeout}")
            timeout = dbcon.fetchone()[0]
            print(f"Set Busy timeout value: {timeout} ms")
        try:
            if args.nodelete is False:
                dbcon.execute("drop table test")
        except:
            pass
        if args.nodelete is False:
            dbcon.execute("create table test (data varchar(10))")
        conn.close()
        conn = False

        print(f"Worker: {args.worker}")
        print(f"Every {args.every}th process inserts: {args.inserts} values")
        fut = {
            executor.submit(
                sqlite_doit,
                cnt,
                args,
            ): cnt
            for cnt in range(int(args.cycles))
        }
        for future in concurrent.futures.as_completed(fut):
            try:
                cnt, data = future.result()
            except sqlite3.OperationalError as exc:
                print(f"Error: {exc}")
            else:
                if cnt % 1000:
                    if (len(data)) > 0:
                        print(f"rows: {len(data)}")


if __name__ == "__main__":
    main()
