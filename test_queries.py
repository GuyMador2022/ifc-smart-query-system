import duckdb

# Connect to database
conn = duckdb.connect('guy_mador_shiba.duckdb')

print("=== Testing Area Query ===")

# Test our new query
sql_query = """SELECT 
    ROUND(SUM(CAST(JSON_EXTRACT(NominalValue, '$.value') AS DECIMAL)), 2) as total_area_sqm
FROM IfcPropertySingleValue 
WHERE Name IN ('TotalArea', 'ProjectedArea', 'Area')
AND NominalValue IS NOT NULL"""

try:
    result = conn.execute(sql_query).fetchall()
    print(f"Total area: {result[0][0]} square meters")
except Exception as e:
    print(f"Error: {e}")

# Also test wall count
print("\n=== Testing Wall Count ===")
try:
    result = conn.execute("SELECT COUNT(*) as wall_count FROM IfcWall").fetchall()
    print(f"Total walls: {result[0][0]}")
except Exception as e:
    print(f"Error: {e}")

# Test materials
print("\n=== Testing Materials ===")
try:
    result = conn.execute("SELECT DISTINCT Name as material_name FROM IfcMaterial WHERE Name IS NOT NULL ORDER BY Name LIMIT 5").fetchall()
    print("Materials found:")
    for row in result:
        print(f"- {row[0]}")
except Exception as e:
    print(f"Error: {e}")

conn.close()