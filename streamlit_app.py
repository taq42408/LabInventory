import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import os

# Page configuration
st.set_page_config(
    page_title="Lab Inventory Manager",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .alert-box {
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .out-of-stock {
        background-color: #ff4444;
        color: white;
        padding: 10px;
        border-radius: 5px;
    }
    .low-stock {
        background-color: #ffcc00;
        color: #333;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

class InventoryApp:
    def __init__(self):
        self.file_path = r"C:\Users\taq3\Downloads\McArt Lab Inventory.xlsx"
        self.df = None
        
        # Email alerts (use your Gmail)
        self.email_enabled = st.sidebar.checkbox("Enable Email Alerts", value=True)
        if self.email_enabled:
            self.email_recipient = st.sidebar.text_input("Recipient Email", "oropel42408@gmail.com")
            self.email_sender = st.sidebar.text_input("Sender Email", "oropel42408@gmail.com")
            self.email_password = st.sidebar.text_input("kqkcnxyzuthozonf", type="kqkcnxyzuthozonf")
        else:
            self.email_recipient = None
            self.email_sender = None
            self.email_password = None
        
        self.load_inventory()
    
    def load_inventory(self):
        """Load your Excel inventory"""
        try:
            self.df = pd.read_excel(self.file_path)
            if 'QR Code' not in self.df.columns:
                self.df['QR Code'] = ""
            self.df['QR Code'] = self.df['QR Code'].fillna("").astype(str)
            self.df['Stock'] = pd.to_numeric(self.df['Stock'], errors='coerce').fillna(0)
            return True
        except Exception as e:
            st.error(f"Error loading inventory: {e}")
            return False
    
    def save_inventory(self):
        """Save back to Excel"""
        try:
            self.df.to_excel(self.file_path, index=False)
            return True
        except Exception as e:
            st.error(f"Error saving: {e}")
            return False
    
    def send_email_alert(self, low_items, out_of_stock):
        """Send email alert for low stock items"""
        if not self.email_enabled or not self.email_password:
            return
        
        if len(low_items) == 0 and len(out_of_stock) == 0:
            return
        
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
        </body>
        </html>
        """
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_sender
            msg['To'] = self.email_recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_sender, self.email_password)
            server.send_message(msg)
            server.quit()
            
            st.success(f"📧 Email alert sent to {self.email_recipient}")
            return True
        except Exception as e:
            st.error(f"Failed to send email: {e}")
            return False

# Initialize app
app = InventoryApp()

# Sidebar navigation
st.sidebar.title("🔬 Lab Inventory Manager")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["📷 Scan Barcode", "📋 View Inventory", "⚠️ Low Stock Alerts", 
     "📊 Reports", "➕ Add New Item", "🔍 Search"]
)

# Main content area
if page == "📷 Scan Barcode":
    st.title("📷 Scan Barcode")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        barcode = st.text_input("Scan or type barcode:", key="barcode_input", autocomplete="off")
        scan_button = st.button("🔍 Find Item", use_container_width=True)
    
    if scan_button and barcode:
        item = app.find_item_by_barcode(barcode) if hasattr(app, 'find_item_by_barcode') else None
        
        if item is not None:
            st.success(f"✅ Found: {item['Item name']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Stock", int(item['Stock']))
                st.write(f"**Location:** {item['Location']}")
                st.write(f"**Status:** {item['Status']}")
            with col2:
                st.write(f"**Item ID:** {item['Item ID']}")
                st.write(f"**Vendor:** {item.get('Purchase Website', 'N/A')}")
            
            # Stock update buttons
            st.markdown("---")
            st.subheader("Update Stock")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("➕ Add 1", use_container_width=True):
                    app.update_stock(item, 1)
                    app.save_inventory()
                    st.rerun()
            with col2:
                if st.button("➕ Add 5", use_container_width=True):
                    app.update_stock(item, 5)
                    app.save_inventory()
                    st.rerun()
            with col3:
                if st.button("➖ Remove 1", use_container_width=True):
                    app.update_stock(item, -1)
                    app.save_inventory()
                    st.rerun()
            with col4:
                if st.button("➖ Remove 5", use_container_width=True):
                    app.update_stock(item, -5)
                    app.save_inventory()
                    st.rerun()
        else:
            st.error("❌ Item not found!")
            st.info("Would you like to add this barcode to an existing item or create a new one?")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Add to Existing Item"):
                    st.session_state.show_add_to_existing = True
            with col2:
                if st.button("Create New Item"):
                    st.session_state.show_create_new = True

elif page == "📋 View Inventory":
    st.title("📋 Inventory Items")
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("🔍 Search by name:", "")
    with col2:
        location_filter = st.selectbox("📍 Filter by location:", ["All"] + sorted(app.df['Location'].dropna().unique().tolist()))
    with col3:
        stock_filter = st.selectbox("📊 Stock status:", ["All", "Low Stock (≤2)", "Out of Stock (0)", "In Stock (>2)"])
    
    # Apply filters
    filtered_df = app.df.copy()
    if search_term:
        filtered_df = filtered_df[filtered_df['Item name'].str.contains(search_term, case=False, na=False)]
    if location_filter != "All":
        filtered_df = filtered_df[filtered_df['Location'] == location_filter]
    if stock_filter == "Low Stock (≤2)":
        filtered_df = filtered_df[filtered_df['Stock'] <= 2]
    elif stock_filter == "Out of Stock (0)":
        filtered_df = filtered_df[filtered_df['Stock'] == 0]
    elif stock_filter == "In Stock (>2)":
        filtered_df = filtered_df[filtered_df['Stock'] > 2]
    
    st.write(f"Showing {len(filtered_df)} of {len(app.df)} items")
    
    # Display as table
    display_df = filtered_df[['Item name', 'Stock', 'Location', 'Status', 'QR Code']].copy()
    display_df['Stock'] = display_df['Stock'].astype(int)
    st.dataframe(display_df, use_container_width=True)

elif page == "⚠️ Low Stock Alerts":
    st.title("⚠️ Low Stock Alerts")
    st.markdown("---")
    
    low_items = app.df[app.df['Stock'] <= 2]
    out_of_stock = app.df[app.df['Stock'] == 0]
    
    if len(out_of_stock) > 0:
        st.markdown("### 🚨 Out of Stock")
        for _, item in out_of_stock.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="out-of-stock">
                <b>{item['Item name']}</b><br>
                Location: {item['Location']}<br>
                Status: {item['Status']}
                </div>
                """, unsafe_allow_html=True)
    
    if len(low_items) > 0:
        low_with_stock = low_items[low_items['Stock'] > 0]
        if len(low_with_stock) > 0:
            st.markdown("### ⚠️ Low Stock (1-2 remaining)")
            for _, item in low_with_stock.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="low-stock">
                    <b>{item['Item name']}</b> - Only {int(item['Stock'])} left<br>
                    Location: {item['Location']}<br>
                    Status: {item['Status']}
                    </div>
                    """, unsafe_allow_html=True)
    
    if len(out_of_stock) == 0 and len(low_items) == 0:
        st.success("✅ No low stock items! Everything is well-stocked.")
    
    # Send email button
    if st.button("📧 Send Alert Email Now"):
        app.send_email_alert(low_items, out_of_stock)

elif page == "📊 Reports":
    st.title("📊 Inventory Reports")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Items", len(app.df))
    with col2:
        st.metric("Total Stock", int(app.df['Stock'].sum()))
    with col3:
        st.metric("Low Stock Items", len(app.df[app.df['Stock'] <= 2]))
    with col4:
        st.metric("Out of Stock", len(app.df[app.df['Stock'] == 0]))
    
    st.markdown("---")
    
    # Stock distribution chart
    st.subheader("Stock Distribution")
    stock_bins = pd.cut(app.df['Stock'], bins=[0, 1, 2, 5, 10, float('inf')], labels=['0', '1-2', '3-5', '6-10', '10+'])
    stock_counts = stock_bins.value_counts()
    st.bar_chart(stock_counts)
    
    # Top items by vendor
    st.subheader("Items by Vendor")
    vendor_counts = app.df['Purchase Website'].value_counts().head(10)
    st.dataframe(vendor_counts)

elif page == "➕ Add New Item":
    st.title("➕ Add New Item")
    st.markdown("---")
    
    with st.form("new_item_form"):
        name = st.text_input("Item Name *", placeholder="e.g., Eppendorf Pipette")
        location = st.text_input("Location *", placeholder="Shelf A3, Freezer 2, etc.")
        stock = st.number_input("Initial Stock", min_value=0, value=1)
        vendor = st.text_input("Vendor/Supplier", placeholder="Fisher Scientific, VWR, etc.")
        status = st.selectbox("Status", ["Active", "Inactive", "Maintenance", "Broken"])
        notes = st.text_area("Notes", placeholder="Any additional information")
        barcode = st.text_input("Barcode (scan now or enter later)")
        
        submitted = st.form_submit_button("➕ Add Item", use_container_width=True)
        
        if submitted and name:
            # Generate item ID
            name_code = re.sub(r'[^a-zA-Z]', '', name)[:3].upper()
            timestamp = datetime.now().strftime("%y%m%d%H%M")
            item_id = f"{name_code}-{timestamp}"
            
            new_item = pd.DataFrame([{
                'Item ID': item_id,
                'Item name': name,
                'Location': location,
                'QR Code': barcode,
                'FORM_ID': '',
                'Stock': stock,
                'Status': status,
                'Purchase Date': datetime.now().strftime("%Y-%m-%d"),
                'Purchase Website': vendor,
                'Notes': notes
            }])
            
            app.df = pd.concat([app.df, new_item], ignore_index=True)
            if app.save_inventory():
                st.success(f"✅ Added {name} (ID: {item_id})")
                st.balloons()

elif page == "🔍 Search":
    st.title("🔍 Search Inventory")
    st.markdown("---")
    
    search_query = st.text_input("Search by item name:", placeholder="Type partial name...")
    
    if search_query:
        results = app.df[app.df['Item name'].str.contains(search_query, case=False, na=False)]
        if len(results) > 0:
            st.write(f"Found {len(results)} items:")
            for _, item in results.iterrows():
                with st.expander(f"{item['Item name']} - Stock: {int(item['Stock'])}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Location:** {item['Location']}")
                        st.write(f"**Status:** {item['Status']}")
                    with col2:
                        st.write(f"**Item ID:** {item['Item ID']}")
                        st.write(f"**Vendor:** {item.get('Purchase Website', 'N/A')}")
                    if item['Notes']:
                        st.write(f"**Notes:** {item['Notes']}")
        else:
            st.warning("No items found")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"""
**Lab Inventory System**  
Version 1.0  
Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
""")

if st.sidebar.button("💾 Save Inventory Now"):
    if app.save_inventory():
        st.sidebar.success("Saved!")