from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://iot:secret@database:5434/device_db"
engine = create_engine(DATABASE_URL, echo=True)

with engine.connect() as conn:
    print("\n🔍 Current search_path:")
    result = conn.execute(text("SHOW search_path;"))
    for row in result:
        print(" -", row[0])

    print("\n🔍 Schemas visible to 'iot':")
    result = conn.execute(text("SELECT schema_name FROM information_schema.schemata ORDER BY schema_name;"))
    for row in result:
        print(" -", row[0])

    print("\n🔍 Tables in 'devices' schema:")
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'devices';"))
    for row in result:
        print(" -", row[0])
