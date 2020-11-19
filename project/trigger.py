from pg_trigger import create_trigger, drop_trigger, listen_trigger
from config import get_config
import psycopg2
import argparse
import traceback


def main(args):
    pg_config = get_config("postgres")
    pg_url = "{drivername}://{username}:{password}@{host}:{port}/{database}".format(**pg_config)
    assert pg_url, "Postgres Server Info needed"
    try:
        conn = psycopg2.connect(pg_url)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        command = args.command
        if command == "create":
            create_trigger(conn, "tc_positions_trigger", "tc_positions")
        elif command == "status":
            # TODO GET trigger status with name or table
            # Sample query: select * from information_schema.triggers
            # REF: https://stackoverflow.com/questions/25202133/how-to-get-the-triggers-associated-with-a-view-or-a-table-in-postgresql/25202347
            pass
        elif command == "drop":
            drop_trigger(conn, "tc_positions_trigger", "tc_positions")
        else:
            listen_trigger(conn, "tc_positions_trigger", "tc_positions")
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", help="Trigger Command: create, status, or drop")
    args = parser.parse_args()
    main(args)
