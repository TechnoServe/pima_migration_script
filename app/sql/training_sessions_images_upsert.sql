INSERT INTO pima.images AS t (id, image_reference_type, image_reference_id,
                              image_url, verification_status, submission_id,
                              is_deleted, deleted_at, created_by_id, last_updated_by_id)
VALUES (:id, :image_reference_type, :image_reference_id,
        :image_url, :verification_status, :submission_id,
        :is_deleted, :deleted_at,
        :system_user, :system_user)
ON CONFLICT ON CONSTRAINT image_submisison_id_key DO UPDATE SET image_reference_type = EXCLUDED.image_reference_type,
                                                                image_reference_id   = EXCLUDED.image_reference_id,
                                                                image_url            = EXCLUDED.image_url,
                                                                verification_status  = EXCLUDED.verification_status,
                                                                submission_id        = EXCLUDED.submission_id,
                                                                is_deleted           = EXCLUDED.is_deleted,
                                                                deleted_at           = EXCLUDED.deleted_at,
                                                                last_updated_by_id   = EXCLUDED.last_updated_by_id
