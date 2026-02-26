MERGE INTO pima.observation_results AS t
USING (
  SELECT 
    CAST(:id AS UUID) AS id,
    CAST(:submission_id AS VARCHAR) AS submission_id,
    CAST(:observation_id AS UUID) AS observation_id,
    CAST(:criterion AS VARCHAR) AS criterion,
    CAST(:question_key AS VARCHAR) AS question_key,
    CAST(:result_text AS VARCHAR) AS result_text,
    CAST(:result_numeric AS NUMERIC) AS result_numeric,
    CAST(:result_boolean AS BOOLEAN) AS result_boolean,
    CAST(:result_url AS VARCHAR) AS result_url,
    CAST(:created_at AS TIMESTAMP) AS created_at,
    CAST(:updated_at AS TIMESTAMP) AS updated_at,
    CAST(:system_user AS UUID) AS system_user,
    CAST(:sf_id AS VARCHAR) AS sf_id,
    CAST(:is_deleted AS BOOLEAN) AS is_deleted,
    CAST(:deleted_at AS TIMESTAMP) AS deleted_at
) AS s
ON t.submission_id = s.submission_id
WHEN MATCHED THEN
  UPDATE SET
    submission_id         = s.submission_id,
    observation_id        = s.observation_id,
    criterion             = s.criterion,
    question_key          = s.question_key,
    result_text           = s.result_text,
    result_numeric        = s.result_numeric,
    result_boolean        = s.result_boolean,
    result_url             = s.result_url,
    updated_at             = s.updated_at,
    last_updated_by_id     = s.system_user,
    from_sf                = TRUE,
    is_deleted             = s.is_deleted,
    deleted_at             = s.deleted_at,
    sf_id                  = s.sf_id
WHEN NOT MATCHED THEN
  INSERT (
  id,
  submission_id,
  observation_id,
  criterion,
  question_key,
  result_text,
  result_numeric,
  result_boolean,
  result_url,
  created_at,
  updated_at,
  created_by_id,
  last_updated_by_id,
  from_sf,
  sf_id,
  is_deleted,
  deleted_at
) VALUES (
  :id,
  :submission_id,
  :observation_id,
  :criterion,
  :question_key,
  :result_text,
  :result_numeric,
  :result_boolean,
  :result_url,
  :created_at,
  :updated_at,
  :system_user,
  :system_user,
  TRUE,
  :sf_id,
  :is_deleted,
  :deleted_at
);