import psycopg2
from pg_trigger import drop_trigger


def main():
    connectin_url = ""
    assert connectin_url, "Postgres Server Info needed"
    conn = psycopg2.connect(connectin_url)
    drop_trigger(conn, "notify_event", "tc_positions")
    conn.commit()


if __name__ == "__main__":
    main()
