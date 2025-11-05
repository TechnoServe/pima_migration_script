INSERT INTO pima.users AS t (
  id, first_name, last_name,
  email, username, password,
  tns_id, phone_number, job_title,
  user_role, status, commcare_mobile_worker_id,
  created_at, updated_at, last_updated_by,
  created_by, from_sf, sf_id
) VALUES (
  :id, :first_name, :last_name,
  :email, :username, :password,
  :tns_id, :phone_number, :job_title,
  :user_role, :status, :commcare_mobile_worker_id,
  :created_at, :updated_at, :system_user,
  :system_user, TRUE, :sf_id
)
ON CONFLICT ON CONSTRAINT users_sf_id_key DO UPDATE SET
  first_name = EXCLUDED.first_name,
  last_name  = EXCLUDED.last_name,
  email      = EXCLUDED.email,
  username   = EXCLUDED.username,
  password   = EXCLUDED.password,
  tns_id     = EXCLUDED.tns_id,
  phone_number = EXCLUDED.phone_number,
  job_title    = EXCLUDED.job_title,
  user_role    = EXCLUDED.user_role,
  status       = EXCLUDED.status,
  commcare_mobile_worker_id = EXCLUDED.commcare_mobile_worker_id,
  updated_at   = EXCLUDED.updated_at,
  last_updated_by = EXCLUDED.last_updated_by,
  from_sf = TRUE,
  sf_id   = EXCLUDED.sf_id;
