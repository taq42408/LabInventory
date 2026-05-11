import pandas as pd

# Your exact file path
file_path = r"C:\Users\taq3\Downloads\McArt Lab Inventory.xlsx"

print("Loading your Excel file...")
print(f"Looking for: {file_path}")

try:
    df = pd.read_excel(file_path)
    print("\n✅ File loaded successfully!")
    print(f"📊 Found {len(df)} items in inventory")
    
    print("\n📋 Your column names:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i}. {col}")
    
    print("\n📝 First 3 rows:")
    print(df.head(3))
    
except FileNotFoundError:
    print(f"\n❌ File not found at: {file_path}")
    print("Make sure the file name is exactly correct")
except Exception as e:
    print(f"\n❌ Error: {e}")
    