INSERT INTO pima.projects AS t (
  id, program_id, project_unique_id, project_name, status,
  start_date, end_date, created_at, updated_at,
  created_by_id, last_updated_by_id, location_id, from_sf, sf_id
) VALUES (
  :id, :program_id, :project_unique_id, :project_name, :status,
  :start_date, :end_date, :created_at, :updated_at,
  :system_user, :system_user, :location_id, TRUE, :sf_id
)
ON CONFLICT ON CONSTRAINT projects_sf_id_key DO UPDATE SET
  program_id        = EXCLUDED.program_id,
  project_unique_id = EXCLUDED.project_unique_id,
  project_name      = EXCLUDED.project_name,
  status            = EXCLUDED.status,
  start_date        = EXCLUDED.start_date,
  end_date          = EXCLUDED.end_date,
  location_id          = EXCLUDED.location_id,
  created_at        = LEAST(t.created_at, EXCLUDED.created_at),
  updated_at        = EXCLUDED.updated_at,
  last_updated_by_id   = EXCLUDED.last_updated_by_id,
  from_sf           = TRUE,
  sf_id             = EXCLUDED.sf_id;
