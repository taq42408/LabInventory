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
        
        # Email alerts setup in sidebar
        st.sidebar.title("📧 Email Alerts")
        self.email_enabled = st.sidebar.checkbox("Enable Email Alerts", value=False)
        
        if self.email_enabled:
            self.email_recipient = st.sidebar.text_input("Recipient Email", "oropel42408@gmail.com")
            self.email_sender = st.sidebar.text_input("Sender Email", "oropel42408@gmail.com")
            self.email_password = st.sidebar.text_input("App Password", type="password")
        else:
            self.email_recipient = None
            self.email_sender = None
            self.email_password = None
        
        self.load_inventory()
    
    def load_inventory(self):
        """Load your Excel inventory"""
        try:
            # For cloud deployment, we need a different approach
            # Since the Excel file won't be on the cloud server
            st.warning("⚠️ Note: This is the cloud version. Your Excel file must be accessible.")
            
            # Try to load from current directory first
            if os.path.exists("inventory.xlsx"):
                self.df = pd.read_excel("inventory.xlsx")
            elif os.path.exists(self.file_path):
                self.df = pd.read_excel(self.file_path)
            else:
                # Create sample data for demonstration
                st.info("No inventory file found. Creating sample data...")
                self.df = pd.DataFrame({
                    'Item ID': ['SAMPLE-001', 'SAMPLE-002'],
                    'Item name': ['Sample Pipette', 'Sample Gloves'],
                    'Location': ['Bench A', 'Shelf B'],
                    'QR Code': ['123456', '789012'],
                    'FORM_ID': ['', ''],
                    'Stock': [5, 10],
                    'Status': ['Active', 'Active'],
                    'Purchase Date': [datetime.now(), datetime.now()],
                    'Purchase Website': ['VWR', 'Fisher'],
                    'Notes': ['', '']
                })
            
            if 'QR Code' not in self.df.columns:
                self.df['QR Code'] = ""
            self.df['QR Code'] = self.df['QR Code'].fillna("").astype(str)
            self.df['Stock'] = pd.to_numeric(self.df['Stock'], errors='coerce').fillna(0)
            
            st.success(f"✅ Loaded {len(self.df)} items from inventory")
            return True
        except Exception as e:
            st.error(f"Error loading inventory: {e}")
            return False
    
    def save_inventory(self):
        """Save back to Excel (only works locally)"""
        try:
            self.df.to_excel(self.file_path, index=False)
            return True
        except Exception as e:
            st.warning(f"Cannot save to cloud: {e}")
            return False
    
    def find_item_by_barcode(self, barcode):
        """Search for item by QR Code"""
        match = self.df[self.df['QR Code'] == barcode]
        if not match.empty:
            return match.iloc[0]
        return None

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
        item = app.find_item_by_barcode(barcode)
        
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
                if st.button("➕ Add 1", key="add1", use_container_width=True):
                    old_stock = item['Stock']
                    new_stock = old_stock + 1
                    app.df.loc[item.name, 'Stock'] = new_stock
                    st.rerun()
            with col2:
                if st.button("➕ Add 5", key="add5", use_container_width=True):
                    app.df.loc[item.name, 'Stock'] += 5
                    st.rerun()
            with col3:
                if st.button("➖ Remove 1", key="rem1", use_container_width=True):
                    app.df.loc[item.name, 'Stock'] = max(0, app.df.loc[item.name, 'Stock'] - 1)
                    st.rerun()
            with col4:
                if st.button("➖ Remove 5", key="rem5", use_container_width=True):
                    app.df.loc[item.name, 'Stock'] = max(0, app.df.loc[item.name, 'Stock'] - 5)
                    st.rerun()
        else:
            st.error("❌ Item not found!")

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
                st.markdown(f"""
                <div class="low-stock">
                <b>{item['Item name']}</b> - Only {int(item['Stock'])} left<br>
                Location: {item['Location']}<br>
                Status: {item['Status']}
                </div>
                """, unsafe_allow_html=True)
    
    if len(out_of_stock) == 0 and len(low_items) == 0:
        st.success("✅ No low stock items! Everything is well-stocked.")

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
    try:
        stock_bins = pd.cut(app.df['Stock'], bins=[0, 1, 2, 5, 10, float('inf')], 
                            labels=['0', '1-2', '3-5', '6-10', '10+'])
        stock_counts = stock_bins.value_counts()
        st.bar_chart(stock_counts)
    except:
        st.info("Not enough data for chart")

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
        barcode = st.text_input("Barcode (optional)", placeholder="Scan barcode or enter manually")
        
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
