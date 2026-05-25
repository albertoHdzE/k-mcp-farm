# -*- coding: utf-8 -*-
"""
Database MCP Server
Exposes a SQLite database as MCP tools over SSE transport.
Tools: list_tables, describe_table, run_query

Run:  python db_mcp_server.py
Then register http://localhost:8765/sse as a Gateway in ContextForge.
"""

import sqlite3
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

DB_PATH = Path(__file__).parent / "demo.db"
PORT = 8765

mcp = FastMCP("database-server", host="0.0.0.0", port=PORT)


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _seed_demo_db() -> None:
    """Create and populate demo tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS departments (
        id   INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        budget REAL
    );

    CREATE TABLE IF NOT EXISTS employees (
        id            INTEGER PRIMARY KEY,
        name          TEXT NOT NULL,
        email         TEXT UNIQUE,
        department_id INTEGER REFERENCES departments(id),
        role          TEXT,
        salary        REAL,
        hire_date     TEXT
    );

    CREATE TABLE IF NOT EXISTS projects (
        id          INTEGER PRIMARY KEY,
        title       TEXT NOT NULL,
        status      TEXT CHECK(status IN ('active','completed','paused')),
        owner_id    INTEGER REFERENCES employees(id),
        start_date  TEXT,
        budget      REAL
    );

    CREATE TABLE IF NOT EXISTS project_assignments (
        project_id  INTEGER REFERENCES projects(id),
        employee_id INTEGER REFERENCES employees(id),
        hours_week  INTEGER,
        PRIMARY KEY (project_id, employee_id)
    );
    """)

    if c.execute("SELECT COUNT(*) FROM departments").fetchone()[0] == 0:
        c.executemany("INSERT INTO departments VALUES (?,?,?)", [
            (1, "Engineering",  850000),
            (2, "Marketing",    320000),
            (3, "Security",     410000),
            (4, "Data Science", 620000),
        ])
        c.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?,?)", [
            (1,  "Alice Johnson",  "alice@corp.com",  1, "Senior Engineer",    125000, "2021-03-15"),
            (2,  "Bob Martinez",   "bob@corp.com",    1, "DevOps Engineer",     98000, "2022-07-01"),
            (3,  "Carol White",    "carol@corp.com",  2, "Marketing Lead",      87000, "2020-11-20"),
            (4,  "David Kim",      "david@corp.com",  3, "Security Analyst",    105000, "2023-01-10"),
            (5,  "Eve Patel",      "eve@corp.com",    4, "ML Engineer",         118000, "2021-09-05"),
            (6,  "Frank Lee",      "frank@corp.com",  1, "Backend Engineer",     92000, "2023-06-14"),
        ])
        c.executemany("INSERT INTO projects VALUES (?,?,?,?,?,?)", [
            (1, "Gateway Rollout",   "active",    1, "2024-01-01", 200000),
            (2, "Brand Refresh",     "completed", 3, "2023-06-01",  80000),
            (3, "Threat Model 2025", "active",    4, "2024-09-01", 150000),
            (4, "LLM Pipeline",      "active",    5, "2024-11-01", 300000),
        ])
        c.executemany("INSERT INTO project_assignments VALUES (?,?,?)", [
            (1, 1, 30), (1, 2, 20), (1, 6, 25),
            (3, 4, 35), (4, 5, 40), (4, 1, 10),
        ])

    conn.commit()
    conn.close()


@mcp.tool()
def list_tables() -> str:
    """List all tables available in the database."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    conn.close()
    tables = [r["name"] for r in rows]
    return json.dumps({"tables": tables})


@mcp.tool()
def describe_table(table_name: str) -> str:
    """Return column names, types, and constraints for a given table.

    Args:
        table_name: Name of the table to describe.
    """
    conn = _get_conn()
    try:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()  # nosec B608
    finally:
        conn.close()
    if not rows:
        return json.dumps({"error": f"Table '{table_name}' not found."})
    columns = [
        {"cid": r["cid"], "name": r["name"], "type": r["type"],
         "notnull": bool(r["notnull"]), "pk": bool(r["pk"])}
        for r in rows
    ]
    return json.dumps({"table": table_name, "columns": columns})


@mcp.tool()
def run_query(sql: str) -> str:
    """Execute a read-only SELECT query and return results as JSON.

    Args:
        sql: A SELECT statement to run against the demo database.
    """
    sql_stripped = sql.strip().upper()
    if not sql_stripped.startswith("SELECT"):
        return json.dumps({"error": "Only SELECT statements are allowed."})
    conn = _get_conn()
    try:
        rows = conn.execute(sql).fetchall()   # nosec B608
        results = [dict(r) for r in rows]
    except Exception as exc:
        conn.close()
        return json.dumps({"error": str(exc)})
    conn.close()
    return json.dumps({"rows": results, "count": len(results)})


if __name__ == "__main__":
    _seed_demo_db()
    print(f"Database MCP Server starting on http://localhost:{PORT}/sse")
    print(f"Database: {DB_PATH}")
    mcp.run(transport="sse")
