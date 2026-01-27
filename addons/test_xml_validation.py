#!/usr/bin/env python3
"""
Test XML validation script for Odoo 15.0
Run this to verify all XML files can be loaded by Odoo
"""

import sys
import os

# Add Odoo to path
sys.path.insert(0, '/usr/lib/python3/dist-packages')

try:
    from lxml import etree
    print("✓ lxml imported successfully\n")
except ImportError as e:
    print(f"✗ Cannot import lxml: {e}\n")
    sys.exit(1)

# Test each module
modules = ['nhan_su', 'quan_ly_du_an', 'quan_ly_cong_viec', 'thong_bao']

print("="*70)
print("TESTING XML FILES FOR ODOO 15.0 COMPATIBILITY")
print("="*70)

all_passed = True

for module_name in modules:
    print(f"\n📦 Module: {module_name}")
    print("-"*70)
    
    manifest_path = f"/mnt/extra-addons/{module_name}/__manifest__.py"
    
    # Read manifest
    try:
        with open(manifest_path, 'r') as f:
            manifest = eval(f.read())
    except Exception as e:
        print(f"  ❌ Cannot read manifest: {e}")
        all_passed = False
        continue
    
    print(f"  Version: {manifest.get('version', 'N/A')}")
    print(f"  Data files: {len(manifest.get('data', []))}")
    
    # Test each XML file
    for data_file in manifest.get('data', []):
        if not data_file.endswith('.xml'):
            continue
        
        filepath = f"/mnt/extra-addons/{module_name}/{data_file}"
        
        if not os.path.exists(filepath):
            print(f"  ❌ {data_file}: File not found")
            all_passed = False
            continue
        
        try:
            # Parse with Odoo-like parser
            parser = etree.XMLParser(
                remove_blank_text=True,
                resolve_entities=False,
                no_network=True
            )
            tree = etree.parse(filepath, parser)
            root = tree.getroot()
            
            # Validate structure
            if root.tag != 'odoo':
                print(f"  ❌ {data_file}: Root is <{root.tag}> not <odoo>")
                all_passed = False
                continue
            
            # Check for data tags (should not exist in Odoo 15)
            children = [c for c in root if not isinstance(c, etree._Comment)]
            has_data = any(c.tag == 'data' for c in children)
            
            if has_data:
                print(f"  ❌ {data_file}: Contains <data> tags (not compatible with Odoo 15)")
                all_passed = False
            else:
                print(f"  ✅ {data_file}: Valid ({len(children)} elements)")
                
        except etree.XMLSyntaxError as e:
            print(f"  ❌ {data_file}: XML Syntax Error")
            print(f"     {e}")
            all_passed = False
        except Exception as e:
            print(f"  ❌ {data_file}: {e}")
            all_passed = False

print("\n" + "="*70)
if all_passed:
    print("✅ ALL FILES PASSED - Ready for Odoo 15.0")
    print("\nNext steps:")
    print("  1. Restart Odoo service")
    print("  2. Update App List in Odoo")
    print("  3. Upgrade the modules")
else:
    print("❌ SOME FILES FAILED - Please fix the issues above")
print("="*70)

sys.exit(0 if all_passed else 1)
