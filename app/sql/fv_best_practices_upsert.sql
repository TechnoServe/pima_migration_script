WITH matched AS (
    SELECT
        b.id
    FROM pima.fv_best_practices b
    WHERE (:sf_id IS NOT NULL AND b.sf_id = :sf_id)
       OR (:submission_id IS NOT NULL AND b.submission_id = :submission_id)
),
resolved AS (
    SELECT COUNT(*) AS match_count
    FROM matched
),
target AS (
    SELECT id
    FROM matched
    LIMIT 1
),
updated AS (
    UPDATE pima.fv_best_practices b
    SET
        is_deleted         = :is_deleted,
        deleted_at         = :deleted_at,
        created_at         = LEAST(b.created_at, :created_at),
        updated_at         = :updated_at,
        submission_id      = COALESCE(:submission_id, b.submission_id),
        farm_visit_id      = :farm_visit_id,
        best_practice_type = :best_practice_type,
        is_bp_verified     = :is_bp_verified,
        last_updated_by_id = :system_user,
        from_sf            = TRUE,
        sf_id              = COALESCE(b.sf_id, :sf_id)
    WHERE b.id = (SELECT id FROM target)
      AND (SELECT match_count FROM resolved) = 1
    RETURNING b.id, 'updated'::text AS action
),
inserted AS (
    INSERT INTO pima.fv_best_practices (
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
    )
    SELECT
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
    WHERE (SELECT match_count FROM resolved) = 0
    RETURNING id, 'inserted'::text AS action
)
SELECT * FROM updated
UNION ALL
SELECT * FROM inserted
UNION ALL
SELECT NULL::uuid AS id, 'duplicate_conflict'::text AS action
WHERE (SELECT match_count FROM resolved) > 1;