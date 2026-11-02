#!/usr/bin/env python3
"""
Generate a SQL file that loads XML files into a staging table.

    python xml_to_sql.py ./xml_files > import.sql
    psql -d mydb -f import.sql

Staging table:

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
import re
import sys
from pathlib import Path

folder = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

print("""BEGIN;

CREATE TABLE IF NOT EXISTS xml_staging (
    id BIGSERIAL PRIMARY KEY, filename TEXT NOT NULL, doc XML NOT NULL
);
""")

for f in sorted(folder.glob("*.xml")):
    text = f.read_text(encoding="utf-8-sig")
    text = re.sub(r"^\s*<\?xml[^>]*\?>", "", text).strip()  # drop XML declaration

    tag = "xml"  # dollar-quote tag; extend until it doesn't clash with the content
    while f"${tag}$" in text:
        tag += "x"

    name = f.name.replace("'", "''")
    print(f"-- {f.name}")
    print(f"INSERT INTO xml_staging (filename, doc)")
    print(f"VALUES ('{name}', XMLPARSE(DOCUMENT ${tag}$")
    print(text)
    print(f"${tag}$));\n")

print("COMMIT;")
