import duckdb

# Connect to database
conn = duckdb.connect('guy_mador_shiba.duckdb')

print("=== Checking Property Tables ===")

# Check IfcPropertySingleValue structure
print("\nIfcPropertySingleValue columns:")
cols = conn.execute('DESCRIBE IfcPropertySingleValue').fetchall()
for c in cols:
    print(f"- {c[0]} ({c[1]})")

# Look for area-related properties
print("\nArea-related properties:")
try:
    data = conn.execute("SELECT Name, NominalValue FROM IfcPropertySingleValue WHERE Name ILIKE '%area%' LIMIT 10").fetchall()
    for row in data:
        print(f"{row[0]}: {row[1]}")
except Exception as e:
    print(f"Error: {e}")

# Look for any properties with numeric values
print("\nSample properties with numeric values:")
try:
    data = conn.execute("SELECT Name, NominalValue FROM IfcPropertySingleValue WHERE NominalValue IS NOT NULL LIMIT 10").fetchall()
    for row in data:
        print(f"{row[0]}: {row[1]}")
except Exception as e:
    print(f"Error: {e}")

conn.close()