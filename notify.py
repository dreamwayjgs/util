import psycopg2
import select
import requests

sql_create_fn = """CREATE OR REPLACE FUNCTION notify_event() RETURNS TRIGGER AS $$
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

    PERFORM pg_notify('channel', payload::text);

    RETURN NULL;
  END;
$$ LANGUAGE plpgsql;"""



def create_trigger(conn, trg_name:str, table:str, timeout:int):
  sql_trigger = """CREATE TRIGGER {}
  AFTER INSERT ON {}
  FOR EACH ROW EXECUTE PROCEDURE notify_event();""".format(trg_name, table)

  curs = conn.cursor()
  curs.execute(sql_create_fn)
  curs.execute(sql_trigger)
  print("execute listening")

  while True:
    if select.select([conn],[],[],timeout) == ([],[],[]):
      print('timeout')
    else:
      conn.poll()
      while conn.notifies:
        notify = conn.notifies.pop(0)
        print("Got NOTIFY:", notify.pid, notify.channel, notify.payload)
    
    r = requests.get('http://127.0.0.1:5000')
    print(r.text)


def drop_trigger(conn, trg_name:str, table:str):
  sql_drop = """DROP TRIGGER {} ON {};""".format(trg_name, table)
  curs = conn.cursor()
  curs.execute(sql_drop)
  print("trigger dropped")



try:
  conn = psycopg2.connect("~~")
  conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
  # curs = conn.cursor()
  # curs.execute("""SELECT table_name FROM information_schema.tables
  #      WHERE table_schema = 'public'""")
  # for table in curs.fetchall():
  #   print(table)

  # drop_trigger(conn, 'notify_event', 'tc_positions')

except psycopg2.Error as e:
  print(e)
  exit()


try:
  create_trigger(conn, 'notify_event', 'tc_positions', 5)


except:
  print("unable to create a trigger")