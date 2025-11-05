INSERT INTO pima.locations AS t (
  id, location_name, location_type, parent_location_id,
  created_at, updated_at, created_by_id, last_updated_by_id, from_sf, sf_id
) VALUES (
  :id, :name, :type, :parent_location_id,
  :created_at, :updated_at, :system_user, :system_user, TRUE, :sf_id
)
ON CONFLICT ON CONSTRAINT locations_sf_id_key DO UPDATE SET
  location_name = EXCLUDED.location_name,
  location_type = EXCLUDED.location_type,
  parent_location_id = EXCLUDED.parent_location_id,
  updated_at = EXCLUDED.updated_at,
  -- preserve the earliest creation time
  created_at = LEAST(t.created_at, EXCLUDED.created_at),
  last_updated_by_id = EXCLUDED.last_updated_by_id,
  from_sf = TRUE,
  sf_id = EXCLUDED.sf_id;

