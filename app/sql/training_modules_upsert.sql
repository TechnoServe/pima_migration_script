INSERT INTO pima.training_modules AS t (
  id, project_id, module_name, module_number,
  created_at, updated_at,
  current_module, sample_fv_aa_households, sample_fv_aa_households_status,
  from_sf, sf_id, is_deleted, deleted_at,
  current_previous, created_by_id, last_updated_by_id, status
) VALUES (
  :id, :project_id, :module_name, :module_number,
  :created_at, :updated_at,
  :current_module, :sample_fv_aa_households, :sample_fv_aa_households_status,
  TRUE, :sf_id, :is_deleted, :deleted_at,
  :current_previous, :system_user, :system_user, :status
)
ON CONFLICT ON CONSTRAINT training_modules_sf_id_key DO UPDATE SET
  project_id                  = EXCLUDED.project_id,
  module_name                 = EXCLUDED.module_name,
  module_number               = EXCLUDED.module_number,
  created_at                  = LEAST(t.created_at, EXCLUDED.created_at),
  updated_at                  = EXCLUDED.updated_at,
  current_module              = EXCLUDED.current_module,
  sample_fv_aa_households     = EXCLUDED.sample_fv_aa_households,
  sample_fv_aa_households_status = EXCLUDED.sample_fv_aa_households_status,
  from_sf                     = TRUE,
  is_deleted                  = EXCLUDED.is_deleted,
  deleted_at                  = EXCLUDED.deleted_at,
  current_previous            = EXCLUDED.current_previous,
  last_updated_by_id          = EXCLUDED.last_updated_by_id,
  status                      = EXCLUDED.status,
  sf_id                       = EXCLUDED.sf_id;
