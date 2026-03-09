WITH matched AS (
    SELECT
        f.id,
        f.sf_id,
        f.commcare_case_id
    FROM pima.farmers f
    WHERE (:sf_id IS NOT NULL AND f.sf_id = :sf_id)
       OR (:commcare_case_id IS NOT NULL AND f.commcare_case_id = :commcare_case_id)
),
resolved AS (
    SELECT
        COUNT(*) AS match_count,
        MIN(id) AS target_id
    FROM matched
),
updated AS (
    UPDATE pima.farmers f
    SET
        household_id                = :household_id,
        farmer_group_id             = :farmer_group_id,
        tns_id                      = :tns_id,
        commcare_case_id            = COALESCE(:commcare_case_id, f.commcare_case_id),
        first_name                  = :first_name,
        middle_name                 = :middle_name,
        last_name                   = :last_name,
        other_id                    = :other_id,
        gender                      = :gender,
        age                         = :age,
        phone_number                = :phone_number,
        is_primary_household_member = :is_primary_household_member,
        status                      = :status,
        send_to_commcare            = :send_to_commcare,
        send_to_commcare_status     = :send_to_commcare_status,
        status_notes                = :status_notes,
        last_updated_by_id          = :system_user,
        from_sf                     = TRUE,
        sf_id                       = COALESCE(f.sf_id, :sf_id),
        is_deleted                  = :is_deleted,
        deleted_at                  = :deleted_at,
        created_at                  = LEAST(f.created_at, :created_at),
        updated_at                  = :updated_at
    WHERE f.id = (
        SELECT target_id
        FROM resolved
        WHERE match_count = 1
    )
    RETURNING f.id, 'updated'::text AS action
),
inserted AS (
    INSERT INTO pima.farmers (
        id,
        household_id,
        farmer_group_id,
        tns_id,
        commcare_case_id,
        first_name,
        middle_name,
        last_name,
        other_id,
        gender,
        age,
        phone_number,
        is_primary_household_member,
        status,
        send_to_commcare,
        send_to_commcare_status,
        status_notes,
        created_by_id,
        last_updated_by_id,
        from_sf,
        sf_id,
        is_deleted,
        deleted_at,
        created_at,
        updated_at
    )
    SELECT
        :id,
        :household_id,
        :farmer_group_id,
        :tns_id,
        :commcare_case_id,
        :first_name,
        :middle_name,
        :last_name,
        :other_id,
        :gender,
        :age,
        :phone_number,
        :is_primary_household_member,
        :status,
        :send_to_commcare,
        :send_to_commcare_status,
        :status_notes,
        :system_user,
        :system_user,
        TRUE,
        :sf_id,
        :is_deleted,
        :deleted_at,
        :created_at,
        :updated_at
    WHERE (SELECT match_count FROM resolved) = 0
    RETURNING id, 'inserted'::text AS action
)
SELECT *
FROM updated
UNION ALL
SELECT *
FROM inserted
UNION ALL
SELECT
    NULL::uuid AS id,
    'duplicate_conflict'::text AS action
WHERE (SELECT match_count FROM resolved) > 1;