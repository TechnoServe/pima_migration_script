INSERT INTO pima.programs AS t (
  id, program_name, program_code, created_at, updated_at,
  last_updated_by_id, created_by_id, from_sf, sf_id
) VALUES (
  :id, :program_name, :program_code, :created_at, :updated_at,
  :system_user, :system_user, TRUE, :sf_id
)
ON CONFLICT ON CONSTRAINT programs_sf_id_key DO UPDATE SET
  program_name       = EXCLUDED.program_name,
  program_code       = EXCLUDED.program_code,
  updated_at         = EXCLUDED.updated_at,
  created_at         = LEAST(t.created_at, EXCLUDED.created_at),
  last_updated_by_id = EXCLUDED.last_updated_by_id,
  from_sf            = TRUE,
  sf_id              = EXCLUDED.sf_id;
