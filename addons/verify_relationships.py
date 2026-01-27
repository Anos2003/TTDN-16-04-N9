#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Relationship Verification Script
Validates that all One2many fields have corresponding Many2one inverse fields
"""

import os
import re

def check_one2many_many2one_pairs():
    """Check all One2many declarations have matching Many2one inverse fields"""
    
    relationships = [
        {
            'name': 'du.an → du.an.phase',
            'one2many_file': '/mnt/extra-addons/du_an/models/du_an.py',
            'one2many_field': 'phase_ids',
            'inverse_field': 'du_an_id',
            'many2one_file': '/mnt/extra-addons/du_an/models/du_an_phase.py',
            'target_model': 'du.an.phase'
        },
        {
            'name': 'du.an → du.an.member',
            'one2many_file': '/mnt/extra-addons/du_an/models/du_an.py',
            'one2many_field': 'member_ids',
            'inverse_field': 'du_an_id',
            'many2one_file': '/mnt/extra-addons/du_an/models/du_an_member.py',
            'target_model': 'du.an.member'
        },
        {
            'name': 'cong.viec → cong.viec.subtask',
            'one2many_file': '/mnt/extra-addons/cong_viec/models/cong_viec.py',
            'one2many_field': 'subtask_ids',
            'inverse_field': 'cong_viec_id',
            'many2one_file': '/mnt/extra-addons/cong_viec/models/cong_viec_subtask.py',
            'target_model': 'cong.viec.subtask'
        },
        {
            'name': 'cong.viec → cong.viec.assignment',
            'one2many_file': '/mnt/extra-addons/cong_viec/models/cong_viec.py',
            'one2many_field': 'assignment_ids',
            'inverse_field': 'cong_viec_id',
            'many2one_file': '/mnt/extra-addons/cong_viec/models/cong_viec_assignment.py',
            'target_model': 'cong.viec.assignment'
        },

    ]
    
    print("=" * 80)
    print("ONE2MANY/MANY2ONE RELATIONSHIP VERIFICATION")
    print("=" * 80)
    
    all_ok = True
    
    for rel in relationships:
        print(f"\n✓ Checking: {rel['name']}")
        print(f"  One2many field: {rel['one2many_field']}")
        print(f"  Inverse field: {rel['inverse_field']}")
        
        # Check One2many field exists
        with open(rel['one2many_file'], 'r', encoding='utf-8') as f:
            content = f.read()
            pattern = rf"{rel['one2many_field']}\s*=\s*fields\.One2many\(['\"]" + re.escape(rel['target_model']) + rf"['\"],\s*['\"]" + re.escape(rel['inverse_field'])
            if re.search(pattern, content):
                print(f"  ✅ One2many '{rel['one2many_field']}' correctly points to '{rel['inverse_field']}'")
            else:
                print(f"  ❌ ERROR: One2many field not found or inverse field name mismatch!")
                all_ok = False
        
        # Check Many2one field exists
        with open(rel['many2one_file'], 'r', encoding='utf-8') as f:
            content = f.read()
            if f"{rel['inverse_field']} = fields.Many2one" in content:
                print(f"  ✅ Many2one '{rel['inverse_field']}' exists on target model")
            else:
                print(f"  ❌ ERROR: Many2one '{rel['inverse_field']}' NOT FOUND!")
                all_ok = False
    
    print("\n" + "=" * 80)
    if all_ok:
        print("✅ ALL RELATIONSHIPS VERIFIED - NO ERRORS")
    else:
        print("❌ ERRORS FOUND - SEE ABOVE")
    print("=" * 80)
    
    return all_ok

if __name__ == '__main__':
    success = check_one2many_many2one_pairs()
    exit(0 if success else 1)
