-- ==========================================
-- FINAL CLEANUP SQL FOR KeyError: 'thong.bao.nhac'
-- ==========================================
-- Run this directly in psql or pgAdmin
-- IMPORTANT: Stop Odoo server BEFORE running this!

BEGIN;

-- Clean up ir_model_data records
DELETE FROM ir_model_data 
WHERE module = 'thong_bao' 
   OR model LIKE 'thong.bao%' 
   OR model LIKE 'thong_bao%';

-- Collect models to delete
CREATE TEMP TABLE temp_models_delete AS
SELECT id, model 
FROM ir_model 
WHERE model LIKE 'thong_bao%' 
   OR model LIKE 'thong.bao%';

-- Delete field constraints
DELETE FROM ir_model_constraint 
WHERE model IN (SELECT model FROM temp_models_delete);

-- Delete relations
DELETE FROM ir_model_relation 
WHERE model IN (SELECT model FROM temp_models_delete)
   OR relation IN (SELECT model FROM temp_models_delete);

-- Delete field access
DELETE FROM ir_model_access 
WHERE model_id IN (SELECT id FROM temp_models_delete);

-- Delete fields
DELETE FROM ir_model_fields 
WHERE model_id IN (SELECT id FROM temp_models_delete);

-- Delete views
DELETE FROM ir_ui_view 
WHERE model LIKE 'thong_bao%' 
   OR model LIKE 'thong.bao%'
   OR inherit_id IN (
       SELECT id FROM ir_ui_view 
       WHERE model LIKE 'thong_bao%' OR model LIKE 'thong.bao%'
   );

-- Delete actions
DELETE FROM ir_actions_act_window 
WHERE res_model LIKE 'thong_bao%' 
   OR res_model LIKE 'thong.bao%';

DELETE FROM ir_actions 
WHERE res_model LIKE 'thong_bao%' 
   OR res_model LIKE 'thong.bao%';

-- Delete menus
DELETE FROM ir_ui_menu 
WHERE name LIKE '%Thong%' 
   OR name LIKE '%thong%'
   OR name LIKE '%nhac%'
   OR action LIKE '%thong_bao%'
   OR action LIKE '%thong.bao%';

-- Delete models
DELETE FROM ir_model 
WHERE id IN (SELECT id FROM temp_models_delete);

-- Final cleanup
DELETE FROM ir_model_fields 
WHERE model_id NOT IN (SELECT id FROM ir_model);

DELETE FROM ir_model_data 
WHERE model NOT IN (SELECT model FROM ir_model);

COMMIT;

-- Verify cleanup
SELECT COUNT(*) as remaining_thong_bao_records FROM ir_model_data 
WHERE model LIKE 'thong%' OR module LIKE 'thong%';

SELECT COUNT(*) as remaining_thong_bao_models FROM ir_model 
WHERE model LIKE 'thong.bao%' OR model LIKE 'thong_bao%';
