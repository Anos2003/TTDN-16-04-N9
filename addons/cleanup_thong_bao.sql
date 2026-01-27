-- Cleanup script for thong_bao module and related orphaned data
-- Run this in PostgreSQL to clean up orphaned data

-- First, get all model IDs that need to be deleted
DO $$ 
DECLARE
    model_ids integer[];
BEGIN
    -- Collect all model IDs to delete
    SELECT array_agg(id) INTO model_ids FROM ir_model 
    WHERE model LIKE 'thong_bao%' OR model LIKE 'thong.bao%' OR model LIKE '%nhac%';
    
    -- Delete ACL records first
    DELETE FROM ir_model_access WHERE model_id = ANY(model_ids);
    
    -- Delete field definitions
    DELETE FROM ir_model_fields WHERE model_id = ANY(model_ids);
    
    -- Delete field constraints
    DELETE FROM ir_model_constraint WHERE model = ANY(
        SELECT model FROM ir_model WHERE id = ANY(model_ids)
    );
    
    -- Delete relations
    DELETE FROM ir_model_relation WHERE model = ANY(
        SELECT model FROM ir_model WHERE id = ANY(model_ids)
    );
    
    -- Delete model data records
    DELETE FROM ir_model_data WHERE model LIKE 'thong_bao%' OR model LIKE 'thong.bao%' OR model LIKE '%nhac%';
END $$;

-- Delete UI views
DELETE FROM ir_ui_view WHERE model LIKE 'thong_bao%' OR model LIKE 'thong.bao%' OR model LIKE '%nhac%';

-- Delete actions and references to these models
DELETE FROM ir_actions_act_window WHERE res_model LIKE 'thong_bao%' OR res_model LIKE 'thong.bao%' OR res_model LIKE '%nhac%';
DELETE FROM ir_actions WHERE res_model LIKE 'thong_bao%' OR res_model LIKE 'thong.bao%' OR res_model LIKE '%nhac%';

-- Delete menu items (be careful with this)
DELETE FROM ir_ui_menu WHERE name LIKE '%Thong%' OR name LIKE '%thong%' OR name LIKE '%nhac%';

-- Delete the models themselves
DELETE FROM ir_model WHERE model LIKE 'thong_bao%' OR model LIKE 'thong.bao%' OR model LIKE '%nhac%';

-- Clean up any orphaned field definitions that reference deleted models
DELETE FROM ir_model_fields WHERE model_id NOT IN (SELECT id FROM ir_model);

COMMIT;
