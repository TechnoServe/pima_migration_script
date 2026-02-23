INSERT INTO pima.fv_best_practices AS b (
  from_sf,
  sf_id,
  is_deleted,
  deleted_at,
  created_at,
  updated_at,

  id,
  submission_id,
  farm_visit_id,
  best_practice_type,
  is_bp_verified,

  created_by_id,
  last_updated_by_id
) VALUES (
  TRUE,
  :sf_id,
  :is_deleted,
  :deleted_at,
  :created_at,
  :updated_at,

  :id,
  :submission_id,
  :farm_visit_id,
  :best_practice_type,
  :is_bp_verified,

  :system_user,
  :system_user
)
ON CONFLICT ON CONSTRAINT fv_best_practices_sf_id_key DO UPDATE SET
  is_deleted         = EXCLUDED.is_deleted,
  deleted_at         = EXCLUDED.deleted_at,
  created_at         = LEAST(b.created_at, EXCLUDED.created_at),
  updated_at         = EXCLUDED.updated_at,

  submission_id      = EXCLUDED.submission_id,
  farm_visit_id      = EXCLUDED.farm_visit_id,
  best_practice_type = EXCLUDED.best_practice_type,
  is_bp_verified     = EXCLUDED.is_bp_verified,

  last_updated_by_id = EXCLUDED.last_updated_by_id,
  from_sf            = TRUE,
  sf_id              = EXCLUDED.sf_id;