INSERT INTO pima.project_staff_roles AS t (
  id, staff_id, project_id, tns_id, role,
  status, commcare_location_id, commcare_case_id, send_to_commcare,
  created_at, updated_at, last_updated_by_id, created_by_id,
  send_to_commcare_status, from_sf, sf_id
) VALUES (
  :id, :staff_id, :project_id, :tns_id, :role,
  :status, :commcare_location_id, :commcare_case_id, :create_in_commcare,
  :created_at, :updated_at, :system_user, :system_user,
  :send_to_commcare_status, TRUE, :sf_id
)
ON CONFLICT ON CONSTRAINT project_staff_roles_sf_id_key DO UPDATE SET
  staff_id              = EXCLUDED.staff_id,
  project_id            = EXCLUDED.project_id,
  tns_id                = EXCLUDED.tns_id,
  role                  = EXCLUDED.role,
  status                = EXCLUDED.status,
  commcare_location_id  = EXCLUDED.commcare_location_id,
  commcare_case_id      = EXCLUDED.commcare_case_id,
  send_to_commcare      = EXCLUDED.send_to_commcare,
  created_at            = LEAST(t.created_at, EXCLUDED.created_at),
  updated_at            = EXCLUDED.updated_at,
  last_updated_by_id    = EXCLUDED.last_updated_by_id,
  created_by_id         = EXCLUDED.created_by_id,
  send_to_commcare_status = EXCLUDED.send_to_commcare_status,
  from_sf               = TRUE,
  sf_id                 = EXCLUDED.sf_id;
