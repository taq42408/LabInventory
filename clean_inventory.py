import pandas as pd

# Your inventory file
file_path = r"C:\Users\taq3\Downloads\McArt Lab Inventory.xlsx"

# Load the inventory
print("Loading inventory...")
df = pd.read_excel(file_path)

print(f"Before cleaning: {len(df)} items")

# Count how many "Unknown" items
unknown_items = df[df['Item name'].str.contains('Unknown', case=False, na=False)]
print(f"Found {len(unknown_items)} items with 'Unknown' in name")

# Show first few unknowns
if len(unknown_items) > 0:
    print("\nFirst 5 Unknown items:")
    for i, (_, row) in enumerate(unknown_items.head(5).iterrows(), 1):
        print(f"  {i}. {row['Item name']} - Stock: {row['Stock']}")
    
    # Ask for confirmation
    print(f"\n⚠️ This will DELETE {len(unknown_items)} items permanently!")
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm == 'DELETE':
        # Remove all rows where Item name contains "Unknown"
        df_cleaned = df[~df['Item name'].str.contains('Unknown', case=False, na=False)]
        
        print(f"After cleaning: {len(df_cleaned)} items")
        print(f"Removed: {len(df) - len(df_cleaned)} items")
        
        # Save the cleaned inventory
        df_cleaned.to_excel(file_path, index=False)
        print("\n✅ Inventory cleaned and saved!")
        
        # Also create a backup
        backup_path = file_path.replace('.xlsx', '_backup_before_clean.xlsx')
        df.to_excel(backup_path, index=False)
        print(f"📁 Backup saved to: {backup_path}")
    else:
        print("❌ Cancelled - no changes made")
else:
    print("No Unknown items found!")