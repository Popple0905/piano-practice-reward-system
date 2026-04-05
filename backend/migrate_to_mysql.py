"""
SQLite → MySQL 資料遷移腳本
用法：
  python migrate_to_mysql.py export          → 匯出 SQLite 資料為 migration_data.sql
  python migrate_to_mysql.py import <DB_URL> → 將 migration_data.sql 匯入指定 MySQL
"""
import sqlite3
import sys
import os
from datetime import datetime


TABLES_ORDER = [
    'parents',
    'children',
    'practice_records',
    'game_awards',
    'game_requests',
    'special_redemptions',
    'special_redemption_records',
]

SQLITE_DB = os.path.join(os.path.dirname(__file__), 'instance', 'piano_app.db')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'migration_data.sql')


def escape(val):
    """Escape a value for MySQL INSERT."""
    if val is None:
        return 'NULL'
    if isinstance(val, (int, float)):
        return str(val)
    # Escape single quotes and backslashes
    s = str(val).replace('\\', '\\\\').replace("'", "\\'")
    return f"'{s}'"


def export():
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    lines = []
    lines.append('-- Piano App: SQLite → MySQL migration')
    lines.append(f'-- Generated: {datetime.now().isoformat()}')
    lines.append('-- Run this AFTER Railway creates the tables (app startup does db.create_all())')
    lines.append('')
    lines.append('SET FOREIGN_KEY_CHECKS = 0;')
    lines.append('')

    total_rows = 0
    for table in TABLES_ORDER:
        cur.execute(f'SELECT * FROM {table}')
        rows = cur.fetchall()
        if not rows:
            lines.append(f'-- {table}: 0 rows (skipped)')
            lines.append('')
            continue

        columns = rows[0].keys()
        col_list = ', '.join(f'`{c}`' for c in columns)

        lines.append(f'-- {table}: {len(rows)} rows')
        for row in rows:
            values = ', '.join(escape(row[c]) for c in columns)
            lines.append(f'INSERT INTO `{table}` ({col_list}) VALUES ({values});')
        lines.append('')
        total_rows += len(rows)

    lines.append('SET FOREIGN_KEY_CHECKS = 1;')

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    conn.close()
    print(f'✅ 匯出完成：{OUTPUT_FILE}')
    print(f'   共 {total_rows} 筆資料，涵蓋 {len(TABLES_ORDER)} 個資料表')
    print()
    print('下一步：')
    print('  1. 在 Railway 建立 MySQL 服務，複製 DATABASE_URL')
    print('  2. 啟動 app 一次讓 db.create_all() 建立空白資料表')
    print('  3. 執行：python migrate_to_mysql.py import <DATABASE_URL>')


def import_data(db_url):
    import pymysql
    from urllib.parse import urlparse

    # Parse DATABASE_URL (support both mysql:// and mysql+pymysql://)
    url = db_url.replace('mysql+pymysql://', 'mysql://').replace('mysql://', '')
    # format: user:pass@host:port/db
    user_pass, rest = url.split('@', 1)
    user, password = user_pass.split(':', 1)
    host_port, db_name = rest.split('/', 1)
    if ':' in host_port:
        host, port = host_port.split(':', 1)
        port = int(port)
    else:
        host, port = host_port, 3306

    # Remove query params from db_name
    db_name = db_name.split('?')[0]

    print(f'連接到 MySQL: {host}:{port}/{db_name}')
    conn = pymysql.connect(host=host, port=port, user=user, password=password,
                           database=db_name, charset='utf8mb4')
    cur = conn.cursor()

    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        sql = f.read()

    statements = [s.strip() for s in sql.split('\n') if s.strip() and not s.startswith('--')]
    executed = 0
    for stmt in statements:
        if stmt:
            cur.execute(stmt)
            if stmt.startswith('INSERT'):
                executed += 1

    conn.commit()
    conn.close()
    print(f'✅ 匯入完成：{executed} 筆資料已寫入 MySQL')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == 'export':
        export()
    elif cmd == 'import' and len(sys.argv) == 3:
        import_data(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)
