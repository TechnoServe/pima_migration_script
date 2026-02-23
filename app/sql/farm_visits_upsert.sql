INSERT INTO pima.farm_visits AS f (
  from_sf,
  sf_id,
  is_deleted,
  deleted_at,
  created_at,
  updated_at,

  id,
  visited_household_id,
  visited_primary_farmer_id,
  visited_secondary_farmer_id,

  submission_id,
  training_session_id,
  visiting_staff_id,

  date_visited,
  visit_comments,
  latest_visit,

  location_gps_latitude,
  location_gps_longitude,
  location_gps_altitude,

  created_by_id,
  last_updated_by_id,

  farm_visit_type
) VALUES (
  TRUE,
  :sf_id,
  :is_deleted,
  :deleted_at,
  :created_at,
  :updated_at,

  :id,
  :visited_household_id,
  :visited_primary_farmer_id,
  :visited_secondary_farmer_id,

  :submission_id,
  :training_session_id,
  :visiting_staff_id,

  :date_visited,
  :visit_comments,
  :latest_visit,

  :lat,
  :lon,
  :alt,

  :system_user,
  :system_user,

  :farm_visit_type
)
ON CONFLICT ON CONSTRAINT farm_visits_submission_id_key DO UPDATE SET
  is_deleted                = EXCLUDED.is_deleted,
  deleted_at                = EXCLUDED.deleted_at,
  created_at                = LEAST(f.created_at, EXCLUDED.created_at),
  updated_at                = EXCLUDED.updated_at,

  visited_household_id      = EXCLUDED.visited_household_id,
  visited_primary_farmer_id = EXCLUDED.visited_primary_farmer_id,
  visited_secondary_farmer_id = EXCLUDED.visited_secondary_farmer_id,

  training_session_id       = EXCLUDED.training_session_id,
  visiting_staff_id         = EXCLUDED.visiting_staff_id,

  date_visited              = EXCLUDED.date_visited,
  visit_comments            = EXCLUDED.visit_comments,
  latest_visit              = EXCLUDED.latest_visit,

  location_gps_latitude     = EXCLUDED.location_gps_latitude,
  location_gps_longitude    = EXCLUDED.location_gps_longitude,
  location_gps_altitude     = EXCLUDED.location_gps_altitude,

  last_updated_by_id        = EXCLUDED.last_updated_by_id,
  from_sf                   = TRUE,
  sf_id                     = EXCLUDED.sf_id,
  farm_visit_type           = EXCLUDED.farm_visit_type;