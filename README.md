# 🔬 Lab Inventory System

<!-- This is a title with an emoji. It shows up big and bold at the top of your GitHub page -->

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

<!-- The badges above are little colored shields that show license type and Python version. They make your repo look professional! -->

## What is this? 📖

<!-- This section answers "Why would someone want this?" -->

An open-source laboratory inventory management system with barcode scanning, email alerts, and web interface. Perfect for research labs, academic institutions, and small businesses that need to track equipment and supplies.

**In plain English:** If you have a lab with stuff (pipettes, chemicals, gloves) and you want to know what you have, where it is, and when you're running low - this tool does that. Just scan barcodes with a USB scanner and it updates everything automatically.

## Features ✨

<!-- Bullet points are easy to scan. Emojis make it visual. -->

- 📷 **Barcode Scanning** - Works with any USB barcode scanner (just plug it in and scan)
- 📧 **Email Alerts** - Automatically emails you when stock runs low (so you don't forget to reorder)
- 🌐 **Web Interface** - Access from your phone, tablet, or any computer on your network
- 📊 **Real-time Reports** - See what you have, what's low, what's out of stock
- 🔍 **Search & Filter** - Find items instantly by name, location, or stock status
- 📱 **Mobile Friendly** - Works on phones in the lab (no app to install)
- 💾 **Excel Compatible** - Works with your existing inventory spreadsheets

## Quick Start 🚀

<!-- Make this as simple as possible - assume they know nothing! -->

### What you need before starting:
- A Windows computer (Mac/Linux works too, but instructions are for Windows)
- Your inventory Excel file (the one you already have)

### Step 1: Get the code

**Option A - Download the EXE (Easiest - no Python needed)**
1. Go to the "Releases" section on the right side of this page
2. Download `InventoryManager.exe`
3. Put it in the same folder as your inventory Excel file
4. Double-click to run!

**Option B - Run from source (For advanced users)**
```bash
git clone https://github.com/taq42408/LabInventory.git
cd LabInventory
pip install -r requirements.txt
python inventory_app.py
Step 2: First time setup
Place your Excel file in the same folder as the program

Default location: C:\Users\taq3\Downloads\McArt Lab Inventory.xlsx

Or change the path in the code (line 12 of inventory_app.py)

Run the program

Double-click InventoryManager.exe (if you downloaded the EXE)

OR run python inventory_app.py (if running from source)

Scan a barcode

Plug in your USB barcode scanner

Choose option 1 from the menu

Scan any barcode in your lab

The system will find the item or let you create a new one

Step 3: Set up email alerts (optional)
Go to your Google Account settings

Turn on "2-Step Verification"

Generate an "App Password" (select "Mail" and "Windows Computer")

Open the program, go to settings, and paste the 16-character password

That's it! The system will now email you whenever stock runs low.

How to Use 📱
<!-- Break down common tasks into simple steps -->
Scanning barcode to update stock
Open the program

Select option 1 (Scan barcode)

Scan any barcode with your USB scanner

Choose "Add stock" or "Remove stock"

Type the quantity

Done! Your Excel file is automatically updated

Adding a new item
Scan the new item's barcode

When it says "Item not found", choose option 3 (Create new item)

Enter the item name, location, and initial quantity

The system creates a unique ID and saves it

Checking what's low on stock
Open the program - it shows alerts immediately

OR choose option 3 from the menu to see all low stock items

Using the web interface on your phone
Run streamlit run streamlit_app.py on your computer

Look for the IP address shown (e.g., http://192.168.1.100:8501)

Type that address into your phone's browser

Bookmark it - now your phone is a wireless scanner!

Project Structure 📁
<!-- Help people understand where to find things -->
text
LabInventory/
│
├── inventory_app.py      # Main terminal version (runs in command prompt)
├── streamlit_app.py      # Web GUI version (beautiful interface)
├── clean_inventory.py    # Utility to remove "Unknown" items
├── requirements.txt      # List of Python packages needed
├── README.md            # This file
└── LICENSE              # GPL v3 - you can use this freely but must share changes
Common Problems & Solutions 🔧
<!-- Anticipate what will go wrong for new users -->
Problem: "Permission denied" when saving

Solution: Close Excel if you have the file open. The program needs exclusive access.

Problem: Scanner not working

Solution: Open Notepad and scan there first. If it types numbers, the scanner works. If not, check USB connection.

Problem: "No module named pandas" error

Solution: Run pip install -r requirements.txt to install all needed packages.

Problem: Email alerts not sending

Solution: You must use an "App Password" from Google, not your regular password. Generate one in Google Account settings.

For Developers 💻
<!-- Information for people who want to modify the code -->
Setting up development environment
bash
# Clone the repo
git clone https://github.com/taq42408/LabInventory.git
cd LabInventory

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
python inventory_app.py
Building your own EXE
bash
pip install pyinstaller
python -m PyInstaller --onefile --console --name "InventoryManager" inventory_app.py
The EXE will be in the dist folder.

Adding features
The code is modular - each function does one thing. Look for:

scan_barcode() - Handles scanner input

find_item_by_barcode() - Searches Excel

update_stock() - Changes quantities

send_email_alert() - Sends notifications

Contributing 🤝
<!-- Encourage others to help improve the project -->
Want to add a feature or fix a bug? Great!

Fork this repository (click the Fork button on GitHub)

Create a new branch (git checkout -b new-feature)

Make your changes

Commit (git commit -m "Add new feature")

Push (git push origin new-feature)

Open a Pull Request

Ideas for contributions:

Add label printing support

Create mobile app version

Add barcode generation for items without barcodes

Add multiple language support

Create Docker container for easy deployment

License 📄
<!-- Legal stuff - important to include! -->
This project is released under the GNU General Public License v3.0.
This means:

✅ You can use it for free, even commercially

✅ You can modify it and share your modifications

❌ You cannot sell it without sharing the source code

❌ You cannot make a closed-source version based on this code

See the LICENSE file for the full legal text.

Disclaimer ⚠️
This software is developed independently and is not officially supported by Cornell University. Use at your own discretion.

Questions or Issues? ❓
Open an issue on GitHub (click "Issues" tab above)

Email: taq3@cornell.edu

Check the "Common Problems" section above first!

Star History ⭐
If this project helps your lab, please star it on GitHub! It helps others find it.