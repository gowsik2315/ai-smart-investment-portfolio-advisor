import sqlite3

conn = sqlite3.connect('investment_advisor.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(financial_profiles)')
rows = cursor.fetchall()

print('\n' + '='*60)
print('FINANCIAL_PROFILES TABLE SCHEMA')
print('='*60)
for row in rows:
    col_name = row[1]
    col_type = row[2]
    required = 'NOT NULL' if row[3] else 'NULLABLE'
    print(f'{col_name:25} {col_type:15} {required}')

print('='*60)

# Check for specific columns
required_columns = ['monthly_income', 'monthly_savings', 'risk_tolerance', 'financial_goal']
print('\nChecking required columns:')
existing_cols = [row[1] for row in rows]
for col in required_columns:
    status = '✓' if col in existing_cols else '✗'
    print(f'{status} {col}')

conn.close()
