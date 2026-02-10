INSERT INTO pima.farmer_groups AS t (
  id, project_id, responsible_staff_id,
  tns_id, commcare_case_id, ffg_name,
  send_to_commcare, created_at, updated_at,
  send_to_commcare_status, status, fv_aa_sampling_round,
  from_sf, sf_id, is_deleted, deleted_at,
  location_id, created_by_id, last_updated_by_id
) VALUES (
  :id, :project_id, :responsible_staff_id,
  :tns_id, :commcare_case_id, :ffg_name,
  :send_to_commcare, :created_at, :updated_at,
  :send_to_commcare_status, :status, :fv_aa_sampling_round,
  TRUE, :sf_id, :is_deleted, :deleted_at,
  :location_id, :system_user, :system_user
)
ON CONFLICT ON CONSTRAINT farmer_groups_sf_id_key DO UPDATE SET
  project_id             = EXCLUDED.project_id,
  responsible_staff_id   = EXCLUDED.responsible_staff_id,
  tns_id                 = EXCLUDED.tns_id,
  commcare_case_id       = EXCLUDED.commcare_case_id,
  ffg_name               = EXCLUDED.ffg_name,
  send_to_commcare       = EXCLUDED.send_to_commcare,
  created_at             = LEAST(t.created_at, EXCLUDED.created_at),
  updated_at             = EXCLUDED.updated_at,
  send_to_commcare_status= EXCLUDED.send_to_commcare_status,
  status                 = EXCLUDED.status,
  fv_aa_sampling_round   = EXCLUDED.fv_aa_sampling_round,
  from_sf                = TRUE,
  is_deleted             = EXCLUDED.is_deleted,
  deleted_at             = EXCLUDED.deleted_at,
  location_id            = EXCLUDED.location_id,
  last_updated_by_id     = EXCLUDED.last_updated_by_id,
  sf_id                  = EXCLUDED.sf_id;
