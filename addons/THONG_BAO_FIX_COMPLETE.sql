-- ==========================================
-- COMPLETE FIX FOR KeyError: 'thong.bao.nhac'
-- ==========================================
-- This script removes ALL orphaned references to thong_bao module
-- Run this directly in psql: psql -U odoo -d odoo -f THONG_BAO_FIX_COMPLETE.sql
-- IMPORTANT: Stop Odoo server BEFORE running this!

\echo '==================================================='
\echo 'STARTING COMPLETE THONG.BAO.NHAC CLEANUP'
\echo '==================================================='

BEGIN;

-- Step 1: Clean up ir_model_data records
\echo 'Step 1: Removing ir_model_data records...'
DELETE FROM ir_model_data 
WHERE module = 'thong_bao' 
   OR model LIKE 'thong.bao%' 
   OR model LIKE 'thong_bao%';

-- Step 2: Collect models to delete
\echo 'Step 2: Identifying models to delete...'
CREATE TEMP TABLE temp_models_delete AS
SELECT id, model 
FROM ir_model 
WHERE model LIKE 'thong_bao%' 
   OR model LIKE 'thong.bao%';

-- Step 3: Clean up selection field references
\echo 'Step 3: Removing selection field references...'
UPDATE ir_model_fields 
SET selection = '' 
WHERE selection LIKE '%thong.bao.nhac%'
   OR selection LIKE '%thong_bao%'
   OR selection LIKE '%thong.bao%';

-- Step 4: Delete field constraints
\echo 'Step 4: Removing field constraints...'
DELETE FROM ir_model_constraint 
WHERE model IN (SELECT model FROM temp_models_delete);

-- Step 5: Delete relations
\echo 'Step 5: Removing model relations...'
DELETE FROM ir_model_relation 
WHERE model IN (SELECT model FROM temp_models_delete)
   OR relation IN (SELECT model FROM temp_models_delete);

-- Step 6: Delete field access records
\echo 'Step 6: Removing field access records...'
DELETE FROM ir_model_access 
WHERE model_id IN (SELECT id FROM temp_models_delete);

-- Step 7: Delete fields
\echo 'Step 7: Removing model fields...'
DELETE FROM ir_model_fields 
WHERE model_id IN (SELECT id FROM temp_models_delete);

-- Step 8: Delete views
\echo 'Step 8: Removing UI views...'
DELETE FROM ir_ui_view 
WHERE model LIKE 'thong_bao%' 
   OR model LIKE 'thong.bao%'
   OR inherit_id IN (
       SELECT id FROM ir_ui_view 
       WHERE model LIKE 'thong_bao%' OR model LIKE 'thong.bao%'
   );

-- Step 9: Delete actions
\echo 'Step 9: Removing actions...'
DELETE FROM ir_actions_act_window 
WHERE res_model LIKE 'thong_bao%' 
   OR res_model LIKE 'thong.bao%';

DELETE FROM ir_actions 
WHERE res_model LIKE 'thong_bao%' 
   OR res_model LIKE 'thong.bao%';

-- Step 10: Delete menus
\echo 'Step 10: Removing menu items...'
DELETE FROM ir_ui_menu 
WHERE name LIKE '%Thong%' 
   OR name LIKE '%thong%'
   OR name LIKE '%nhac%'
   OR action LIKE '%thong_bao%'
   OR action LIKE '%thong.bao%';

-- Step 11: Delete models
\echo 'Step 11: Deleting models from ir_model...'
DELETE FROM ir_model 
WHERE id IN (SELECT id FROM temp_models_delete);

-- Step 12: Final cleanup of orphaned records
\echo 'Step 12: Cleaning up orphaned field definitions...'
DELETE FROM ir_model_fields 
WHERE model_id NOT IN (SELECT id FROM ir_model);

DELETE FROM ir_model_data 
WHERE model NOT IN (SELECT model FROM ir_model);

COMMIT;

\echo ''
\echo '==================================================='
\echo 'CLEANUP COMPLETED - VERIFICATION RESULTS'
\echo '==================================================='

-- Verify cleanup
\echo ''
\echo 'Remaining thong_bao records in ir_model_data:'
SELECT COUNT(*) as count FROM ir_model_data 
WHERE model LIKE 'thong%' OR module LIKE 'thong%';

\echo ''
\echo 'Remaining thong_bao models in ir_model:'
SELECT COUNT(*) as count FROM ir_model 
WHERE model LIKE 'thong.bao%' OR model LIKE 'thong_bao%';

\echo ''
\echo 'Selection fields with thong_bao references:'
SELECT COUNT(*) as count FROM ir_model_fields 
WHERE selection LIKE '%thong.bao%' OR selection LIKE '%thong_bao%';

\echo ''
\echo '==================================================='
\echo 'All counts should be 0 - If not, check errors above'
\echo '==================================================='
