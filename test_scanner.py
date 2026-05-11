# test_scanner.py - Just tests if your scanner works

print("🎯 BARCODE SCANNER TEST")
print("-" * 40)
print("Ready to scan...")
print("Point your USB scanner at a barcode and scan it")
print("(Press ENTER without scanning to quit)")
print()

while True:
    barcode = input("Scan now: ").strip()
    
    if barcode == "":
        print("Exiting test...")
        break
    
    print(f"✅ Scanned: {barcode}")
    print(f"Length: {len(barcode)} characters")
    print("-" * 40)