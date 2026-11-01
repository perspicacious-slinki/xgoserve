#!/usr/bin/env python3
"""
Load XML files into a Postgres staging table.

    pip install psycopg2-binary
    export PGHOST=localhost PGDATABASE=mydb PGUSER=me PGPASSWORD=secret
    python import_xml.py ./xml_files

Staging table (created automatically):

    CREATE TABLE IF NOT EXISTS xml_staging (
        id       BIGSERIAL PRIMARY KEY,
        filename TEXT NOT NULL,
        doc      XML  NOT NULL
    );

Sample XPath queries:

    -- All order IDs in each document
    SELECT filename, xpath('/orders/order/@id', doc) FROM xml_staging;

    -- Customer names as text
    SELECT filename, (xpath('//customer/text()', doc))::text[] FROM xml_staging;

    -- Documents containing an order over 100
    SELECT filename FROM xml_staging
    WHERE xpath_exists('/orders/order[total > 100]', doc);
"""
import sys
from pathlib import Path

import psycopg2

folder = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

conn = psycopg2.connect("")  # uses PG* environment variables
with conn, conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS xml_staging (
            id BIGSERIAL PRIMARY KEY, filename TEXT NOT NULL, doc XML NOT NULL)
    """)
    for f in sorted(folder.glob("*.xml")):
        cur.execute(
            "INSERT INTO xml_staging (filename, doc) VALUES (%s, XMLPARSE(DOCUMENT %s))",
            (f.name, f.read_text(encoding="utf-8-sig")),
        )
        print("loaded", f.name)
conn.close()
