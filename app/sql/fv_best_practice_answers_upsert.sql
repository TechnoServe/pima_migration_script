INSERT INTO pima.fv_best_practice_answers AS a (
  from_sf,
  sf_id,
  is_deleted,
  deleted_at,
  created_at,
  updated_at,

  id,
  submission_id,
  fv_best_practice_id,
  question_key,

  answer_text,
  answer_numeric,
  answer_boolean,
  answer_url,

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
  :fv_best_practice_id,
  :question_key,

  :answer_text,
  :answer_numeric,
  :answer_boolean,
  :answer_url,

  :system_user,
  :system_user
)
ON CONFLICT ON CONSTRAINT fv_best_practice_answers_sf_id_key DO UPDATE SET
  is_deleted          = EXCLUDED.is_deleted,
  deleted_at          = EXCLUDED.deleted_at,
  created_at          = LEAST(a.created_at, EXCLUDED.created_at),
  updated_at          = EXCLUDED.updated_at,

  submission_id       = EXCLUDED.submission_id,
  fv_best_practice_id = EXCLUDED.fv_best_practice_id,
  question_key        = EXCLUDED.question_key,

  answer_text         = EXCLUDED.answer_text,
  answer_numeric      = EXCLUDED.answer_numeric,
  answer_boolean      = EXCLUDED.answer_boolean,
  answer_url          = EXCLUDED.answer_url,

  last_updated_by_id  = EXCLUDED.last_updated_by_id;