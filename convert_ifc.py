#!/usr/bin/env python3
"""
Script to convert IFC file to DuckDB database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import ifcopenshell
from ifc2duckdb import Patcher

def main():
    # Path to the IFC file
    ifc_file_path = r"c:\Users\PC\Desktop\אפליקציות בפיתוח\ifc-2-duckdb-master\Guy_Mador - 01 - Shiba - V.3.0.ifc"
    
    # Output database path
    output_db = "guy_mador_shiba.duckdb"
    
    print(f"Converting IFC file: {ifc_file_path}")
    print(f"Output database: {output_db}")
    
    try:
        # Open IFC file
        print("Loading IFC file...")
        ifc_file = ifcopenshell.open(ifc_file_path)
        print(f"IFC file loaded successfully. Schema: {ifc_file.schema}")
        
        # Create patcher
        print("Creating patcher...")
        patcher = Patcher(
            ifc_file,
            database=output_db,
            full_schema=False,  # Only create tables for entities present in the file
            should_get_geometry=True,
            should_get_psets=True,
            should_get_inverses=True
        )
        
        # Convert to DuckDB
        print("Starting conversion...")
        patcher.patch()
        
        print(f"Conversion completed successfully!")
        print(f"Database created: {patcher.get_output()}")
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()