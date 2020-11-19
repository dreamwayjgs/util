import psycopg2
import select
import json
import requests
import traceback
from datetime import datetime

channel_name = "channel"


def create_trigger(conn, trg_name: str, table: str):
    sql_create_fn = f"""CREATE OR REPLACE FUNCTION notify_event() RETURNS TRIGGER AS $$
  DECLARE
    record RECORD;
    payload JSON;
  BEGIN
    IF (TG_OP = 'DELETE') THEN
      record = OLD;
    ELSE
      record = NEW;
    END IF;
    payload = json_build_object('table', TG_TABLE_NAME,
                                'action', TG_OP,
                                'data', row_to_json(record));
    PERFORM pg_notify('{channel_name}', payload::text);
    RETURN NULL;
  END;
$$ LANGUAGE plpgsql;"""
    sql_trigger = """CREATE TRIGGER {}
  AFTER INSERT ON {}
  FOR EACH ROW EXECUTE PROCEDURE notify_event();""".format(
        trg_name, table
    )

    curs = conn.cursor()
    curs.execute(sql_create_fn)
    curs.execute(sql_trigger)
    print("execute listening")
    conn.commit()


def listen_trigger(conn, trg_name: str, table: str, timeout: int = 5):
    curs = conn.cursor()
    curs.execute(f"LISTEN {channel_name};")
    while True:
        if select.select([conn], [], [], timeout) == ([], [], []):
            print("TIMEOUT")
        else:
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                print(datetime.now().isoformat())
                print("Got NOTIFY:", notify.pid, notify.channel, notify.payload)

                try:
                    headers = {"Content-Type": "application/json"}
                    r = requests.put("http://127.0.0.1:5000/position/update", headers=headers, data=notify.payload)
                    if r.status_code == 200:
                        print("MSG SENT", r.status_code)
                    else:
                        print("Request FAILED", r.status_code)
                except Exception:
                    traceback.print_exc()
                    print("Server no response")


def drop_trigger(conn, trg_name: str, table: str):
    sql_drop = """DROP TRIGGER IF EXISTS {} ON {};""".format(trg_name, table)
    curs = conn.cursor()
    curs.execute(sql_drop)
    print("trigger dropped")
    conn.commit()


def main():
    connectin_url = ""
    assert connectin_url, "Postgres Server Info needed"
    try:
        conn = psycopg2.connect(connectin_url)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        # curs = conn.cursor()
        # curs.execute("""SELECT table_name FROM information_schema.tables
        #      WHERE table_schema = 'public'""")
        # for table in curs.fetchall():
        #   print(table)

        # drop_trigger(conn, 'notify_event', 'tc_positions')
        conn.commit()

    except psycopg2.Error as e:
        print(e)
        exit()

    try:
        create_trigger(conn, "notify_event", "tc_positions", 5)
    except Exception:
        traceback.print_exc()
        print("unable to create a trigger")


if __name__ == "__main__":
    print("Run", datetime.now().isoformat())
    main()
