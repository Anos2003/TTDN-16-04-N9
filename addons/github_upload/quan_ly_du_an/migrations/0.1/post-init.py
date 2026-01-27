# -*- coding: utf-8 -*-

def migrate(cr, version):
    # Add muc_do_uu_tien column if it doesn't exist
    cr.execute("""
        ALTER TABLE du_an
        ADD COLUMN IF NOT EXISTS muc_do_uu_tien VARCHAR
        DEFAULT 'medium';
    """)
    
    # Add other missing columns if needed
    cr.execute("""
        ALTER TABLE du_an
        ADD COLUMN IF NOT EXISTS chi_phi_da_su_dung NUMERIC
        DEFAULT 0;
    """)
    
    cr.execute("""
        ALTER TABLE du_an
        ADD COLUMN IF NOT EXISTS tien_do_chi_phi NUMERIC
        DEFAULT 0;
    """)
