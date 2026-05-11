import pandas as pd
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

class InventoryApp:
    def __init__(self):
        self.file_path = r"C:\Users\taq3\Downloads\McArt Lab Inventory.xlsx"
        self.df = None
     
        # EMAIL ALERTS (Gmail)
        self.email_enabled = True
        self.email_recipient = "oropel42408@gmail.com"
        self.email_sender = "oropel42408@gmail.com"
        self.email_password = "kqkcnxyzuthozonf"  
        
        self.load_inventory()
        
    def load_inventory(self):
        """Load your Excel inventory"""
        try:
            self.df = pd.read_excel(self.file_path)
            # Make sure QR Code column exists and is string type
            if 'QR Code' not in self.df.columns:
                self.df['QR Code'] = ""
            self.df['QR Code'] = self.df['QR Code'].fillna("").astype(str)
            
            # Fix Stock column - replace nan with 0
            self.df['Stock'] = pd.to_numeric(self.df['Stock'], errors='coerce').fillna(0)
            
            print(f"✅ Loaded {len(self.df)} items from inventory")
            
            # SHOW LOW STOCK ALERTS IMMEDIATELY
            self.show_low_stock_alerts()
            
            return True
        except Exception as e:
            print(f"❌ Error loading: {e}")
            return False
    
    def show_low_stock_alerts(self):
        """Show low stock alerts when app starts"""
        low_items = self.df[self.df['Stock'] <= 2]
        out_of_stock = self.df[self.df['Stock'] == 0]
        
        print("\n" + "="*60)
        print("⚠️  LOW STOCK ALERTS ⚠️")
        print("="*60)
        
        if len(out_of_stock) > 0:
            print(f"\n🚨 OUT OF STOCK - {len(out_of_stock)} items:")
            print("-"*40)
            for _, item in out_of_stock.iterrows():
                item_name = str(item['Item name']) if pd.notna(item['Item name']) else "Unknown"
                print(f"   • {item_name}")
                if pd.notna(item['Location']):
                    print(f"     Location: {item['Location']}")
            
        if len(low_items) > 0:
            # Filter out items that are already counted as out of stock (stock = 0)
            low_with_stock = low_items[low_items['Stock'] > 0]
            if len(low_with_stock) > 0:
                print(f"\n⚠️  LOW STOCK (1-2 units remaining) - {len(low_with_stock)} items:")
                print("-"*40)
                for _, item in low_with_stock.iterrows():
                    item_name = str(item['Item name']) if pd.notna(item['Item name']) else "Unknown"
                    print(f"   • {item_name} - Only {int(item['Stock'])} left")
                    if pd.notna(item['Location']):
                        print(f"     Location: {item['Location']}")
        
        if len(out_of_stock) == 0 and len(low_items) == 0:
            print("\n✅ All items have sufficient stock!")
        
        print("\n" + "="*60)
        
        # Save alert to a log file AND send email
        if len(low_items) > 0 or len(out_of_stock) > 0:
            self.save_alert_log(low_items, out_of_stock)
            self.send_email_alert(low_items, out_of_stock)
    
    def save_alert_log(self, low_items, out_of_stock):
        """Save alerts to a log file for record keeping"""
        alert_file = f"low_stock_alerts_{datetime.now().strftime('%Y%m%d')}.txt"
        
        with open(alert_file, 'w') as f:
            f.write(f"LOW STOCK ALERTS - {datetime.now()}\n")
            f.write("="*60 + "\n\n")
            
            if len(out_of_stock) > 0:
                f.write(f"OUT OF STOCK ({len(out_of_stock)} items):\n")
                f.write("-"*40 + "\n")
                for _, item in out_of_stock.iterrows():
                    f.write(f"• {item['Item name']}\n")
                    if pd.notna(item['Location']):
                        f.write(f"  Location: {item['Location']}\n")
                f.write("\n")
            
            if len(low_items) > 0:
                low_with_stock = low_items[low_items['Stock'] > 0]
                if len(low_with_stock) > 0:
                    f.write(f"LOW STOCK ({len(low_with_stock)} items):\n")
                    f.write("-"*40 + "\n")
                    for _, item in low_with_stock.iterrows():
                        f.write(f"• {item['Item name']} - Only {int(item['Stock'])} left\n")
                        if pd.notna(item['Location']):
                            f.write(f"  Location: {item['Location']}\n")
                    f.write("\n")
        
        print(f"📝 Alert log saved to: {alert_file}")
    
    def send_email_alert(self, low_items, out_of_stock):
        """Send email alert for low stock items"""
        if not self.email_enabled:
            return
        
        # Don't send if no low items
        if len(low_items) == 0 and len(out_of_stock) == 0:
            return
        
        # Build email content
        subject = "⚠️ LAB INVENTORY ALERT - Low Stock Detected"
        
        body = f"""
        <html>
        <body>
        <h2>⚠️ Lab Inventory Alert</h2>
        <p><b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h3>🚨 OUT OF STOCK ({len(out_of_stock)} items):</h3>
        """
        
        if len(out_of_stock) > 0:
            body += "<ul>"
            for _, item in out_of_stock.iterrows():
                item_name = str(item['Item name']) if pd.notna(item['Item name']) else "Unknown"
                location = str(item['Location']) if pd.notna(item['Location']) else "Unknown"
                body += f"<li><b>{item_name}</b> - Location: {location}</li>"
            body += "</ul>"
        else:
            body += "<p>None! Good job keeping stock up!</p>"
        
        low_with_stock = low_items[low_items['Stock'] > 0]
        body += f"""
        <h3>⚠️ LOW STOCK (1-2 units left):</h3>
        """
        
        if len(low_with_stock) > 0:
            body += "<ul>"
            for _, item in low_with_stock.iterrows():
                item_name = str(item['Item name']) if pd.notna(item['Item name']) else "Unknown"
                stock = int(item['Stock'])
                location = str(item['Location']) if pd.notna(item['Location']) else "Unknown"
                body += f"<li><b>{item_name}</b> - Only {stock} left - Location: {location}</li>"
            body += "</ul>"
        else:
            body += "<p>No items currently low!</p>"
        
        body += """
        <hr>
        <p><i>Sent from Lab Inventory Management System</i></p>
        <p><small>To stop these alerts, set email_enabled = False in config</small></p>
        </body>
        </html>
        """
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_sender
            msg['To'] = self.email_recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to Gmail
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_sender, self.email_password)
            
            # Send
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Email alert sent to {self.email_recipient}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def save_inventory(self):
        """Save back to Excel"""
        try:
            self.df.to_excel(self.file_path, index=False)
            print(f"✅ Saved to {self.file_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving: {e}")
            return False
    
    def scan_barcode(self):
        """Read from USB barcode scanner"""
        print("\n📷 Ready to scan...")
        print("(Just scan the barcode - it will auto-submit)")
        print("(Press Enter without scanning to go back)")
        
        barcode = input().strip()
        
        if barcode:
            print(f"✅ Scanned: {barcode}")
            return barcode
        return None
    
    def find_item_by_barcode(self, barcode):
        """Search for item by QR Code"""
        match = self.df[self.df['QR Code'] == barcode]
        if not match.empty:
            return match.iloc[0]
        return None
    
    def show_item_details(self, item):
        """Display full item information"""
        print("\n" + "="*60)
        print(f"🔍 ITEM FOUND")
        print("="*60)
        print(f"Item ID:     {item['Item ID'] if pd.notna(item['Item ID']) else 'N/A'}")
        print(f"Name:        {item['Item name']}")
        print(f"Location:    {item['Location'] if pd.notna(item['Location']) else 'N/A'}")
        print(f"Stock:       {int(item['Stock'])}")
        print(f"Status:      {item['Status'] if pd.notna(item['Status']) else 'N/A'}")
        
        if pd.notna(item.get('QR Code')) and item['QR Code']:
            print(f"QR Code:     {item['QR Code']}")
        
        if pd.notna(item.get('Purchase Date')):
            print(f"Purchased:   {item['Purchase Date']}")
        if pd.notna(item.get('Purchase Website')):
            print(f"Vendor:      {item['Purchase Website']}")
        if pd.notna(item.get('Notes')):
            print(f"Notes:       {item['Notes']}")
        print("="*60)
        
        # Show alert if this specific item is low stock
        if item['Stock'] <= 2:
            if item['Stock'] == 0:
                print(f"\n🚨 ALERT: This item is OUT OF STOCK!")
            else:
                print(f"\n⚠️ ALERT: Only {int(item['Stock'])} left! Time to reorder.")
            print("="*60)
    
    def update_stock(self, item, change):
        """Update stock quantity"""
        current_stock = item['Stock']
        new_stock = current_stock + change
        
        if new_stock < 0:
            print(f"❌ Cannot reduce below 0! Current stock: {current_stock}")
            return False
        
        idx = item.name
        self.df.loc[idx, 'Stock'] = new_stock
        
        print(f"\n✅ Stock updated: {current_stock} → {new_stock}")
        
        if new_stock <= 2:
            if new_stock == 0:
                print(f"🚨 ALERT: Item is now OUT OF STOCK!")
                # Send immediate alert for this item
                item_df = self.df[self.df['Item name'] == item['Item name']]
                self.send_email_alert(item_df, item_df[item_df['Stock'] == 0])
            else:
                print(f"⚠️ ALERT: Item is now LOW STOCK ({new_stock} remaining)")
                item_df = self.df[self.df['Item name'] == item['Item name']]
                self.send_email_alert(item_df, pd.DataFrame())
        
        return True
    
    def create_new_item(self, barcode):
        """Create a brand new item with the scanned barcode"""
        print("\n" + "="*60)
        print("➕ CREATE NEW ITEM")
        print("="*60)
        print(f"Barcode: {barcode}")
        print("-"*40)
        
        # Get all the details from user
        name = input("Item name: ").strip()
        while not name:
            print("❌ Item name is required!")
            name = input("Item name: ").strip()
        
        location = input("Location (e.g., 'Shelf A3', 'Freezer 2'): ").strip()
        if not location:
            location = "Unknown"
        
        initial_stock = input("Initial quantity (0 if none): ").strip()
        try:
            initial_stock = int(initial_stock) if initial_stock else 0
        except:
            initial_stock = 0
        
        min_stock = input("Minimum stock alert level (default 2): ").strip()
        try:
            min_stock = int(min_stock) if min_stock else 2
        except:
            min_stock = 2
        
        vendor = input("Vendor/supplier (optional): ").strip()
        if not vendor:
            vendor = "Unknown"
        
        status = input("Status (e.g., 'Active', 'Broken', 'Maintenance'): ").strip()
        if not status:
            status = "Active"
        
        notes = input("Notes (optional): ").strip()
        
        # Generate a simple Item ID
        name_code = re.sub(r'[^a-zA-Z]', '', name)[:3].upper()
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        item_id = f"{name_code}-{timestamp}"
        
        print(f"\n📝 Auto-generated Item ID: {item_id}")
        
        # Create the new item row
        new_item = pd.DataFrame([{
            'Item ID': item_id,
            'Item name': name,
            'Location': location,
            'QR Code': barcode,
            'FORM_ID': '',
            'Stock': initial_stock,
            'Status': status,
            'Purchase Date': datetime.now().strftime("%Y-%m-%d"),
            'Purchase Website': vendor,
            'Notes': notes
        }])
        
        # Add to dataframe
        self.df = pd.concat([self.df, new_item], ignore_index=True)
        self.save_inventory()
        
        print("\n" + "="*60)
        print("✅ NEW ITEM ADDED SUCCESSFULLY!")
        print("="*60)
        print(f"Item: {name}")
        print(f"ID: {item_id}")
        print(f"Barcode: {barcode}")
        print(f"Stock: {initial_stock}")
        print(f"Location: {location}")
        print("="*60)
        
        # Ask if they want to print a label
        print_label = input("\nPrint barcode label? (y/n): ").lower()
        if print_label == 'y':
            self.print_label(name, barcode)
        
        return True
    
    def add_barcode_to_item(self, barcode):
        """Add a barcode to an existing item"""
        print("\n📝 ADD BARCODE TO EXISTING ITEM")
        print("="*60)
        
        # Show all items with numbers
        print("\nSelect item by number:\n")
        for i, (idx, row) in enumerate(self.df.iterrows(), 1):
            has_qr = "✓" if row['QR Code'] and row['QR Code'] != "" else " "
            item_name = str(row['Item name']) if pd.notna(row['Item name']) else "Unknown"
            if len(item_name) > 45:
                item_name = item_name[:42] + "..."
            stock_value = int(row['Stock']) if pd.notna(row['Stock']) else 0
            stock_alert = "⚠️" if stock_value <= 2 else " "
            print(f"{i:3}. [{has_qr}] {stock_alert} {item_name:48} | Stock: {stock_value:3}")
        
        print("\n" + "="*60)
        
        try:
            choice = input("\nEnter item number (or 'search' to search by name): ")
            
            if choice.lower() == 'search':
                search = input("Search for item name: ")
                matches = self.df[self.df['Item name'].str.contains(search, case=False, na=False)]
                
                if len(matches) == 0:
                    print("No items found")
                    return
                
                print(f"\nFound {len(matches)} items:")
                for i, (idx, row) in enumerate(matches.iterrows(), 1):
                    item_name = str(row['Item name']) if pd.notna(row['Item name']) else "Unknown"
                    if len(item_name) > 50:
                        item_name = item_name[:47] + "..."
                    print(f"{i:3}. {item_name}")
                
                choice = input("\nEnter item number: ")
                idx = matches.iloc[int(choice)-1].name
                
            else:
                item_num = int(choice) - 1
                if item_num < 0 or item_num >= len(self.df):
                    print("Invalid item number")
                    return
                idx = self.df.iloc[item_num].name
            
            # Add the barcode
            self.df.loc[idx, 'QR Code'] = barcode
            item_name = self.df.loc[idx, 'Item name']
            print(f"\n✅ Added barcode to: {item_name}")
            print(f"   Barcode: {barcode}")
            
            # Ask if they want to print a label
            print_label = input("\nPrint barcode label? (y/n): ").lower()
            if print_label == 'y':
                self.print_label(item_name, barcode)
            
            self.save_inventory()
            
        except (ValueError, IndexError) as e:
            print(f"Invalid selection: {e}")
    
    def print_label(self, item_name, barcode):
        """Placeholder for label printing"""
        print(f"📄 Would print label for: {item_name}")
        print(f"   Barcode: {barcode}")
        print("   (Label printing will be added in next version)")
    
    def scan_workflow(self):
        """Main workflow: scan -> find -> update"""
        barcode = self.scan_barcode()
        if not barcode:
            return
        
        item = self.find_item_by_barcode(barcode)
        
        if item is None:
            print(f"\n❌ No item found with this barcode")
            print(f"   Scanned: {barcode}")
            
            print("\nWhat would you like to do?")
            print("1. Try scanning again")
            print("2. Add this barcode to an EXISTING item")
            print("3. ✨ Create a NEW item with this barcode")
            print("4. Go back to menu")
            
            choice = input("\nChoice (1-4): ")
            
            if choice == '2':
                self.add_barcode_to_item(barcode)
            elif choice == '3':
                self.create_new_item(barcode)
            return
        
        # Found the item
        self.show_item_details(item)
        
        print("\n📦 What would you like to do?")
        print("1. Add stock (received items)")
        print("2. Remove stock (used/checked out)")
        print("3. Just view (no changes)")
        
        action = input("\nChoice (1-3): ")
        
        if action == '1':
            qty = int(input("How many to ADD? "))
            self.update_stock(item, qty)
            self.save_inventory()
        elif action == '2':
            qty = int(input("How many to REMOVE? "))
            self.update_stock(item, -qty)
            self.save_inventory()
        elif action == '3':
            print("No changes made")
    
    def check_low_stock(self):
        """Show all items with low stock (≤ 2) - manual check"""
        print("\n⚠️  LOW STOCK CHECK")
        print("="*60)
        
        low_items = self.df[self.df['Stock'] <= 2]
        
        if len(low_items) == 0:
            print("✅ No items are low on stock!")
        else:
            print(f"Found {len(low_items)} items with low stock:\n")
            for _, item in low_items.iterrows():
                item_name = str(item['Item name']) if pd.notna(item['Item name']) else "Unknown"
                if item['Stock'] == 0:
                    print(f"🚨 {item_name}")
                    print(f"   OUT OF STOCK! | Location: {item['Location']}")
                else:
                    print(f"⚠️  {item_name}")
                    print(f"   Only {int(item['Stock'])} left | Location: {item['Location']}")
                print()
    
    def view_all_items(self):
        """Show all inventory items"""
        print("\n📋 ALL INVENTORY ITEMS")
        print("="*80)
        
        for i, (_, item) in enumerate(self.df.iterrows(), 1):
            stock_status = "⚠️" if item['Stock'] <= 2 else "✓"
            has_qr = "📷" if item['QR Code'] and item['QR Code'] != "" else " "
            item_name = str(item['Item name']) if pd.notna(item['Item name']) else "Unknown"
            if len(item_name) > 45:
                item_name = item_name[:42] + "..."
            print(f"{stock_status} {has_qr} {i:3}. {item_name:45} | Stock: {int(item['Stock']):3} | Loc: {str(item['Location'])[:15]}")
        
        input("\nPress Enter to continue...")
    
    def generate_report(self):
        """Generate inventory report"""
        print("\n📊 INVENTORY REPORT")
        print("="*60)
        
        total_items = len(self.df)
        total_stock = self.df['Stock'].sum()
        low_stock = len(self.df[self.df['Stock'] <= 2])
        out_of_stock = len(self.df[self.df['Stock'] == 0])
        with_barcodes = len(self.df[self.df['QR Code'] != ""])
        
        print(f"Total unique items: {total_items}")
        print(f"Total units in stock: {int(total_stock)}")
        print(f"Items low on stock: {low_stock}")
        print(f"Items out of stock: {out_of_stock}")
        print(f"Items with barcodes: {with_barcodes}")
        print(f"Items needing barcodes: {total_items - with_barcodes}")
        
        report_file = f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(report_file, 'w') as f:
            f.write(f"Inventory Report - {datetime.now()}\n")
            f.write("="*60 + "\n")
            f.write(f"Total items: {total_items}\n")
            f.write(f"Total stock: {total_stock}\n")
            f.write(f"Low stock: {low_stock}\n")
            f.write(f"Out of stock: {out_of_stock}\n")
            f.write(f"With barcodes: {with_barcodes}\n")
            
            # Add low stock details to report
            if low_stock > 0:
                f.write("\n\nLOW STOCK ITEMS:\n")
                f.write("-"*40 + "\n")
                low_items = self.df[self.df['Stock'] <= 2]
                for _, item in low_items.iterrows():
                    f.write(f"• {item['Item name']} - {int(item['Stock'])} left\n")
        
        print(f"\n✅ Report saved to: {report_file}")
    
    def run(self):
        """Main menu"""
        print("\n" + "="*50)
        print("     LAB INVENTORY MANAGEMENT SYSTEM")
        print("="*50)
        
        while True:
            print("\n" + "="*50)
            print("MAIN MENU")
            print("="*50)
            print("1. 📷 SCAN barcode (check in/out items)")
            print("2. 📋 View all items (shows which have barcodes)")
            print("3. ⚠️  Check low stock")
            print("4. 📊 Generate report")
            print("5. 🔍 Search by name")
            print("6. 💾 Save inventory now")
            print("0. Exit")
            print("-"*50)
            
            choice = input("Your choice: ")
            
            if choice == '1':
                self.scan_workflow()
            elif choice == '2':
                self.view_all_items()
            elif choice == '3':
                self.check_low_stock()
            elif choice == '4':
                self.generate_report()
            elif choice == '5':
                search = input("Search for: ")
                results = self.df[self.df['Item name'].str.contains(search, case=False, na=False)]
                if len(results) > 0:
                    print(f"\nFound {len(results)} items:")
                    for _, item in results.iterrows():
                        has_qr = "✓" if item['QR Code'] and item['QR Code'] != "" else "❌"
                        item_name = str(item['Item name']) if pd.notna(item['Item name']) else "Unknown"
                        stock_status = "⚠️" if item['Stock'] <= 2 else "✓"
                        print(f"  {stock_status} {has_qr} {item_name} (Stock: {int(item['Stock'])}, Location: {item['Location']})")
                else:
                    print("No items found")
            elif choice == '6':
                self.save_inventory()
            elif choice == '0':
                print("\nGoodbye! Saving inventory...")
                self.save_inventory()
                break
            else:
                print("Invalid choice")
            
            if choice != '2':
                input("\nPress Enter to continue...")

# Run the app
if __name__ == "__main__":
    app = InventoryApp()
    app.run()