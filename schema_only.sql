--
-- PostgreSQL database dump
--

\restrict pJytBU8e19sKymeJ7NDlEkyj15l4qlExguBSgmvPVsEe4h2TFJKm82KAZ5CaEP4

-- Dumped from database version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: ops; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "ops";


--
-- Name: pima; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "pima";


--
-- Name: SCHEMA "public"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA "public" IS 'standard public schema';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "public";


--
-- Name: EXTENSION "pgcrypto"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "pgcrypto" IS 'cryptographic functions';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "postgis" WITH SCHEMA "public";


--
-- Name: EXTENSION "postgis"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "postgis" IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: attendance_status_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."attendance_status_enum" AS ENUM (
    'Present',
    'Absent'
);


--
-- Name: attended_last_months_training_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."attended_last_months_training_enum" AS ENUM (
    'Yes',
    'No',
    'No training was offered'
);


--
-- Name: check_type_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."check_type_enum" AS ENUM (
    'Training Observation',
    'Farm Visit'
);


--
-- Name: current_previous_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."current_previous_enum" AS ENUM (
    'Current',
    'Previous'
);


--
-- Name: farm_visit_type_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."farm_visit_type_enum" AS ENUM (
    'Farm Visit Full - ET',
    'Farm Visit Full - KE',
    'Farm Visit Full - PR',
    'Farm Visit Full - ZM',
    'Farm Visit',
    'Farm Visit Full',
    'Farm Visit Full - AI',
    'Farm Visit Full - BU'
);


--
-- Name: farmer_gender_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."farmer_gender_enum" AS ENUM (
    'Male',
    'Female'
);


--
-- Name: farmer_group_send_to_commcare_status_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."farmer_group_send_to_commcare_status_enum" AS ENUM (
    'Pending',
    'Processing',
    'Complete'
);


--
-- Name: farmer_group_status_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."farmer_group_status_enum" AS ENUM (
    'Active',
    'Inactive'
);


--
-- Name: farmer_send_to_commcare_status_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."farmer_send_to_commcare_status_enum" AS ENUM (
    'Pending',
    'Processing',
    'Complete'
);


--
-- Name: farmer_status_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."farmer_status_enum" AS ENUM (
    'Active',
    'Inactive'
);


--
-- Name: household_status_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."household_status_enum" AS ENUM (
    'Active',
    'Inactive'
);


--
-- Name: observation_type_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."observation_type_enum" AS ENUM (
    'Training',
    'Demo Plot'
);


--
-- Name: project_staff_role_send_to_commcare_status_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."project_staff_role_send_to_commcare_status_enum" AS ENUM (
    'Pending',
    'Processing',
    'Complete'
);


--
-- Name: project_staff_role_status_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."project_staff_role_status_enum" AS ENUM (
    'Active',
    'Inactive'
);


--
-- Name: project_status_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."project_status_enum" AS ENUM (
    'Active',
    'Inactive'
);


--
-- Name: training_module_status_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."training_module_status_enum" AS ENUM (
    'Active',
    'Inactive'
);


--
-- Name: training_session_send_to_commcare_status_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."training_session_send_to_commcare_status_enum" AS ENUM (
    'Pending',
    'Processing',
    'Complete'
);


--
-- Name: user_status_enum; Type: TYPE; Schema: pima; Owner: -
--

CREATE TYPE "pima"."user_status_enum" AS ENUM (
    'Active',
    'Inactive'
);


--
-- Name: farm_visit_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE "public"."farm_visit_type_enum" AS ENUM (
    'Farm Visit',
    'Farm Visit Full - ET',
    'Farm Visit Full - KE',
    'Farm Visit Full - PR',
    'Farm Visit Full - ZM'
);


--
-- Name: farmer_send_to_commcare_status_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE "public"."farmer_send_to_commcare_status_enum" AS ENUM (
    'Pending',
    'Processing',
    'Complete',
    'Failed'
);


SET default_tablespace = '';

SET default_table_access_method = "heap";

--
-- Name: etl_runs; Type: TABLE; Schema: ops; Owner: -
--

CREATE TABLE "ops"."etl_runs" (
    "run_id" "uuid" NOT NULL,
    "started_at" timestamp without time zone NOT NULL,
    "ended_at" timestamp without time zone,
    "operator_email" "text" NOT NULL,
    "status" "text" NOT NULL,
    "notes" "text"
);


--
-- Name: etl_tasks; Type: TABLE; Schema: ops; Owner: -
--

CREATE TABLE "ops"."etl_tasks" (
    "task_id" "uuid" NOT NULL,
    "run_id" "uuid" NOT NULL,
    "object_name" "text" NOT NULL,
    "started_at" timestamp without time zone NOT NULL,
    "ended_at" timestamp without time zone,
    "status" "text" NOT NULL,
    "rows_in" integer DEFAULT 0,
    "rows_out" integer DEFAULT 0,
    "error" "text"
);


--
-- Name: attendances; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."attendances" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "farmer_id" "uuid" NOT NULL,
    "training_session_id" "uuid" NOT NULL,
    "date_attended" "date",
    "submission_id" character varying,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL,
    "status" "pima"."attendance_status_enum" DEFAULT 'Absent'::"pima"."attendance_status_enum" NOT NULL
);


--
-- Name: checks; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."checks" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "farmer_id" "uuid" NOT NULL,
    "submission_id" character varying NOT NULL,
    "checker_id" "uuid" NOT NULL,
    "observation_id" "uuid",
    "farm_visit_id" "uuid",
    "training_session_id" "uuid" NOT NULL,
    "date_completed" "date" NOT NULL,
    "attended_trainings" boolean,
    "number_of_trainings_attended" integer,
    "attended_last_months_training" "pima"."attended_last_months_training_enum" NOT NULL,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL,
    "check_type" "pima"."check_type_enum" NOT NULL
);


--
-- Name: coffee_varieties; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."coffee_varieties" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "variety_name" character varying NOT NULL,
    "number_of_trees" integer NOT NULL,
    "submission_id" character varying NOT NULL,
    "farm_id" "uuid" NOT NULL,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL
);


--
-- Name: farm_visits; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."farm_visits" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "visited_household_id" "uuid",
    "visited_primary_farmer_id" "uuid",
    "visited_secondary_farmer_id" "uuid",
    "submission_id" character varying NOT NULL,
    "training_session_id" "uuid",
    "visiting_staff_id" "uuid" NOT NULL,
    "date_visited" "date" NOT NULL,
    "visit_comments" character varying,
    "latest_visit" boolean DEFAULT true NOT NULL,
    "location_gps_latitude" numeric(10,6),
    "location_gps_longitude" numeric(10,6),
    "location_gps_altitude" numeric(10,2),
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL,
    "farm_visit_type" "pima"."farm_visit_type_enum" NOT NULL
);


--
-- Name: farmer_groups; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."farmer_groups" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "project_id" "uuid" NOT NULL,
    "responsible_staff_id" "uuid" NOT NULL,
    "tns_id" character varying NOT NULL,
    "commcare_case_id" character varying NOT NULL,
    "ffg_name" character varying NOT NULL,
    "send_to_commcare" boolean DEFAULT false NOT NULL,
    "location_id" "uuid",
    "fv_aa_sampling_round" integer,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL,
    "send_to_commcare_status" "pima"."farmer_group_send_to_commcare_status_enum" DEFAULT 'Pending'::"pima"."farmer_group_send_to_commcare_status_enum" NOT NULL,
    "status" "pima"."farmer_group_status_enum" DEFAULT 'Active'::"pima"."farmer_group_status_enum" NOT NULL
);


--
-- Name: farmers; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."farmers" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "household_id" "uuid" NOT NULL,
    "farmer_group_id" "uuid" NOT NULL,
    "tns_id" character varying,
    "commcare_case_id" character varying NOT NULL,
    "first_name" character varying NOT NULL,
    "middle_name" character varying,
    "last_name" character varying NOT NULL,
    "other_id" character varying,
    "age" integer NOT NULL,
    "phone_number" character varying,
    "is_primary_household_member" boolean DEFAULT false,
    "send_to_commcare" boolean DEFAULT false NOT NULL,
    "status_notes" character varying,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL,
    "status" "pima"."farmer_status_enum" DEFAULT 'Active'::"pima"."farmer_status_enum" NOT NULL,
    "send_to_commcare_status" "pima"."farmer_send_to_commcare_status_enum" DEFAULT 'Pending'::"pima"."farmer_send_to_commcare_status_enum" NOT NULL,
    "gender" "pima"."farmer_gender_enum" NOT NULL,
    "farmer_status" character(100)
);


--
-- Name: farms; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."farms" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "submission_id" character varying NOT NULL,
    "farm_visit_id" "uuid" NOT NULL,
    "household_id" "uuid" NOT NULL,
    "farm_name" character varying NOT NULL,
    "location_gps_latitude" numeric(10,6) NOT NULL,
    "location_gps_longitude" numeric(10,6) NOT NULL,
    "location_gps_altitude" numeric(10,2) NOT NULL,
    "farm_size_coffee_trees" integer NOT NULL,
    "farm_size_land_measurements" numeric(10,6) NOT NULL,
    "main_coffee_field" boolean DEFAULT false NOT NULL,
    "planting_month_and_year" "date" NOT NULL,
    "planted_out_of_season" boolean DEFAULT false NOT NULL,
    "tns_id" character varying NOT NULL,
    "planted_out_of_season_comments" character varying,
    "planted_on_visit_date" boolean DEFAULT false NOT NULL,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL
);


--
-- Name: fv_best_practice_answers; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."fv_best_practice_answers" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "submission_id" character varying NOT NULL,
    "fv_best_practice_id" "uuid" NOT NULL,
    "question_key" character varying NOT NULL,
    "answer_text" character varying,
    "answer_numeric" numeric,
    "answer_boolean" boolean,
    "answer_url" character varying,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL
);


--
-- Name: fv_best_practices; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."fv_best_practices" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "submission_id" character varying NOT NULL,
    "farm_visit_id" "uuid" NOT NULL,
    "best_practice_type" character varying NOT NULL,
    "is_bp_verified" boolean DEFAULT false NOT NULL,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL
);


--
-- Name: households; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."households" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "farmer_group_id" "uuid" NOT NULL,
    "household_name" character varying NOT NULL,
    "household_number" integer NOT NULL,
    "tns_id" character varying,
    "commcare_case_id" character varying,
    "number_of_trees" integer DEFAULT 0,
    "farm_size" numeric DEFAULT '0'::numeric,
    "sampled_for_fv_aa" boolean DEFAULT false NOT NULL,
    "farm_size_before" numeric(10,6),
    "farm_size_after" numeric(10,6),
    "farm_size_since" numeric(10,6),
    "visited_for_fv_aa" boolean DEFAULT false NOT NULL,
    "fv_aa_sampling_round" integer DEFAULT 0 NOT NULL,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL,
    "status" "pima"."household_status_enum" DEFAULT 'Active'::"pima"."household_status_enum" NOT NULL
);


--
-- Name: images; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."images" (
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "image_reference_type" character varying,
    "image_reference_id" "uuid",
    "image_url" character varying,
    "verification_status" character varying,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL,
    "submission_id" character varying NOT NULL,
    "image_description" character varying
);


--
-- Name: locations; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."locations" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "location_name" character varying NOT NULL,
    "location_type" character varying NOT NULL,
    "parent_location_id" "uuid",
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL
);


--
-- Name: observation_results; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."observation_results" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "submission_id" character varying NOT NULL,
    "observation_id" "uuid" NOT NULL,
    "criterion" character varying,
    "question_key" character varying,
    "result_text" character varying,
    "result_numeric" numeric,
    "result_boolean" boolean,
    "result_url" character varying,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL
);


--
-- Name: observations; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."observations" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "submission_id" character varying,
    "observer_id" "uuid",
    "trainer_id" "uuid",
    "farmer_group_id" "uuid",
    "training_session_id" "uuid",
    "observation_date" "date" NOT NULL,
    "location_gps_latitude" numeric(10,6),
    "location_gps_longitude" numeric(10,6),
    "location_gps_altitude" numeric(10,2),
    "female_attendees" integer,
    "male_attendees" integer,
    "total_attendees" integer,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL,
    "comments" character varying,
    "observation_type" "pima"."observation_type_enum"
);


--
-- Name: programs; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."programs" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "program_name" character varying NOT NULL,
    "program_code" character varying NOT NULL,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL
);


--
-- Name: project_staff_roles; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."project_staff_roles" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "project_id" "uuid" NOT NULL,
    "staff_id" "uuid" NOT NULL,
    "commcare_location_id" character varying,
    "commcare_case_id" character varying NOT NULL,
    "tns_id" character varying,
    "role" character varying NOT NULL,
    "send_to_commcare" boolean DEFAULT false NOT NULL,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL,
    "status" "pima"."project_staff_role_status_enum" DEFAULT 'Active'::"pima"."project_staff_role_status_enum" NOT NULL,
    "send_to_commcare_status" "pima"."project_staff_role_send_to_commcare_status_enum" DEFAULT 'Pending'::"pima"."project_staff_role_send_to_commcare_status_enum" NOT NULL
);


--
-- Name: projects; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."projects" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "program_id" "uuid",
    "project_name" character varying NOT NULL,
    "project_unique_id" character varying NOT NULL,
    "location_id" "uuid",
    "start_date" "date",
    "end_date" "date",
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL,
    "status" "pima"."project_status_enum" DEFAULT 'Active'::"pima"."project_status_enum" NOT NULL
);


--
-- Name: training_modules; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."training_modules" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "project_id" "uuid",
    "module_name" character varying,
    "module_number" integer,
    "current_module" boolean DEFAULT false,
    "sample_fv_aa_households" boolean DEFAULT false,
    "sample_fv_aa_households_status" character varying,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL,
    "status" "pima"."training_module_status_enum" DEFAULT 'Active'::"pima"."training_module_status_enum" NOT NULL,
    "current_previous" "pima"."current_previous_enum",
    "module_date" "date"
);


--
-- Name: training_sessions; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."training_sessions" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "trainer_id" "uuid",
    "module_id" "uuid" NOT NULL,
    "farmer_group_id" "uuid" NOT NULL,
    "date_session_1" "date",
    "date_session_2" "date",
    "commcare_case_id" character varying NOT NULL,
    "male_attendees_session_1" integer,
    "female_attendees_session_1" integer,
    "total_attendees_session_1" integer,
    "male_attendees_session_2" integer,
    "female_attendees_session_2" integer,
    "total_attendees_session_2" integer,
    "male_attendees_agg" integer,
    "female_attendees_agg" integer,
    "total_attendees_agg" integer,
    "location_gps_latitude_session_1" numeric(10,6),
    "location_gps_longitude_session_1" numeric(10,6),
    "location_gps_altitude_session_1" numeric(10,2),
    "location_gps_latitude_session_2" numeric(10,6),
    "location_gps_longitude_session_2" numeric(10,6),
    "location_gps_altitude_session_2" numeric(10,2),
    "send_to_commcare" boolean DEFAULT false NOT NULL,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL,
    "send_to_commcare_status" "pima"."training_session_send_to_commcare_status_enum" DEFAULT 'Pending'::"pima"."training_session_send_to_commcare_status_enum" NOT NULL,
    "sampled" boolean DEFAULT false NOT NULL,
    "review_status" character varying
);


--
-- Name: upload_row_errors; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."upload_row_errors" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "upload_run_id" "uuid" NOT NULL,
    "row_number" integer NOT NULL,
    "farmer_id" "uuid",
    "tns_id" "text",
    "error_type" "text" NOT NULL,
    "error_message" "text" NOT NULL,
    "raw_row" "jsonb",
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- Name: upload_runs; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."upload_runs" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "project_id" "uuid" NOT NULL,
    "filename" "text" NOT NULL,
    "content_type" "text",
    "file_size_bytes" integer,
    "gcs_bucket" "text",
    "gcs_object_name" "text",
    "gcs_uri" "text",
    "error_gcs_object_name" "text",
    "error_gcs_uri" "text",
    "status" "text" DEFAULT 'uploading'::"text" NOT NULL,
    "progress" integer DEFAULT 0 NOT NULL,
    "total_rows" integer DEFAULT 0 NOT NULL,
    "success_count" integer DEFAULT 0 NOT NULL,
    "failed_count" integer DEFAULT 0 NOT NULL,
    "remaining_count" integer DEFAULT 0 NOT NULL,
    "uploaded_by_id" "uuid",
    "uploaded_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "completed_at" timestamp with time zone,
    "parent_upload_id" "uuid",
    "meta" "jsonb"
);


--
-- Name: users; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."users" (
    "from_sf" boolean DEFAULT false NOT NULL,
    "sf_id" character varying,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "first_name" character varying NOT NULL,
    "middle_name" character varying,
    "last_name" character varying NOT NULL,
    "email" character varying,
    "user_role" character varying,
    "username" character varying,
    "password" character varying,
    "tns_id" character varying NOT NULL,
    "phone_number" character varying,
    "job_title" character varying,
    "commcare_mobile_worker_id" character varying,
    "manager_id" "uuid",
    "created_by_id" "uuid",
    "last_updated_by_id" "uuid",
    "status" "pima"."user_status_enum" DEFAULT 'Active'::"pima"."user_status_enum"
);


--
-- Name: users_temp; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."users_temp" (
    "id" "uuid" NOT NULL,
    "manager_id" "uuid"
);


--
-- Name: wetmill_visits; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."wetmill_visits" (
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "wetmill_id" "uuid",
    "user_id" "uuid",
    "form_name" character varying NOT NULL,
    "visit_date" "date" NOT NULL,
    "entrance_photograph" character varying,
    "geo_location" "public"."geometry"(Point,4326),
    "submission_id" character varying NOT NULL,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL
);


--
-- Name: wetmills; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."wetmills" (
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "user_id" "uuid",
    "wet_mill_unique_id" character varying NOT NULL,
    "commcare_case_id" character varying,
    "name" character varying,
    "mill_status" character varying,
    "exporting_status" character varying,
    "programme" character varying,
    "country" character varying,
    "manager_name" character varying,
    "manager_role" character varying,
    "comments" "text",
    "wetmill_counter" integer,
    "ba_signature" character varying,
    "manager_signature" character varying,
    "tor_page_picture" character varying,
    "registration_date" "date",
    "office_entrance_picture" character varying,
    "office_gps" "public"."geometry"(Point,4326),
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL
);


--
-- Name: wv_survey_question_responses; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."wv_survey_question_responses" (
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "survey_response_id" "uuid" NOT NULL,
    "section_name" character varying,
    "question_name" character varying NOT NULL,
    "field_type" character varying NOT NULL,
    "submission_id" character varying NOT NULL,
    "value_text" "text",
    "value_number" double precision,
    "value_boolean" boolean,
    "value_date" timestamp without time zone,
    "value_gps" "public"."geometry"(Point,4326),
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL
);


--
-- Name: wv_survey_responses; Type: TABLE; Schema: pima; Owner: -
--

CREATE TABLE "pima"."wv_survey_responses" (
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" NOT NULL,
    "form_visit_id" "uuid" NOT NULL,
    "survey_type" character varying NOT NULL,
    "completed_date" "date",
    "general_feedback" "text",
    "submission_id" character varying NOT NULL,
    "created_by_id" "uuid" NOT NULL,
    "last_updated_by_id" "uuid" NOT NULL
);


--
-- Name: etl_runs etl_runs_pkey; Type: CONSTRAINT; Schema: ops; Owner: -
--

ALTER TABLE ONLY "ops"."etl_runs"
    ADD CONSTRAINT "etl_runs_pkey" PRIMARY KEY ("run_id");


--
-- Name: etl_tasks etl_tasks_pkey; Type: CONSTRAINT; Schema: ops; Owner: -
--

ALTER TABLE ONLY "ops"."etl_tasks"
    ADD CONSTRAINT "etl_tasks_pkey" PRIMARY KEY ("task_id");


--
-- Name: attendances attendances_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."attendances"
    ADD CONSTRAINT "attendances_pkey" PRIMARY KEY ("id");


--
-- Name: attendances attendances_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."attendances"
    ADD CONSTRAINT "attendances_sf_id_key" UNIQUE ("sf_id");


--
-- Name: attendances attendances_submission_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."attendances"
    ADD CONSTRAINT "attendances_submission_id_key" UNIQUE ("submission_id");


--
-- Name: checks checks_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."checks"
    ADD CONSTRAINT "checks_pkey" PRIMARY KEY ("id");


--
-- Name: checks checks_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."checks"
    ADD CONSTRAINT "checks_sf_id_key" UNIQUE ("sf_id");


--
-- Name: checks checks_submission_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."checks"
    ADD CONSTRAINT "checks_submission_id_key" UNIQUE ("submission_id");


--
-- Name: coffee_varieties coffee_varieties_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."coffee_varieties"
    ADD CONSTRAINT "coffee_varieties_pkey" PRIMARY KEY ("id");


--
-- Name: coffee_varieties coffee_varieties_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."coffee_varieties"
    ADD CONSTRAINT "coffee_varieties_sf_id_key" UNIQUE ("sf_id");


--
-- Name: coffee_varieties coffee_varieties_submission_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."coffee_varieties"
    ADD CONSTRAINT "coffee_varieties_submission_id_key" UNIQUE ("submission_id");


--
-- Name: farm_visits farm_visits_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farm_visits"
    ADD CONSTRAINT "farm_visits_pkey" PRIMARY KEY ("id");


--
-- Name: farm_visits farm_visits_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farm_visits"
    ADD CONSTRAINT "farm_visits_sf_id_key" UNIQUE ("sf_id");


--
-- Name: farm_visits farm_visits_submission_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farm_visits"
    ADD CONSTRAINT "farm_visits_submission_id_key" UNIQUE ("submission_id");


--
-- Name: farmer_groups farmer_groups_commcare_case_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmer_groups"
    ADD CONSTRAINT "farmer_groups_commcare_case_id_key" UNIQUE ("commcare_case_id");


--
-- Name: farmer_groups farmer_groups_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmer_groups"
    ADD CONSTRAINT "farmer_groups_pkey" PRIMARY KEY ("id");


--
-- Name: farmer_groups farmer_groups_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmer_groups"
    ADD CONSTRAINT "farmer_groups_sf_id_key" UNIQUE ("sf_id");


--
-- Name: farmers farmers_commcare_case_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmers"
    ADD CONSTRAINT "farmers_commcare_case_id_key" UNIQUE ("commcare_case_id");


--
-- Name: farmers farmers_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmers"
    ADD CONSTRAINT "farmers_pkey" PRIMARY KEY ("id");


--
-- Name: farmers farmers_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmers"
    ADD CONSTRAINT "farmers_sf_id_key" UNIQUE ("sf_id");


--
-- Name: farms farms_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farms"
    ADD CONSTRAINT "farms_pkey" PRIMARY KEY ("id");


--
-- Name: farms farms_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farms"
    ADD CONSTRAINT "farms_sf_id_key" UNIQUE ("sf_id");


--
-- Name: farms farms_submission_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farms"
    ADD CONSTRAINT "farms_submission_id_key" UNIQUE ("submission_id");


--
-- Name: farms farms_tns_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farms"
    ADD CONSTRAINT "farms_tns_id_key" UNIQUE ("tns_id");


--
-- Name: fv_best_practice_answers fv_best_practice_answers_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."fv_best_practice_answers"
    ADD CONSTRAINT "fv_best_practice_answers_pkey" PRIMARY KEY ("id");


--
-- Name: fv_best_practice_answers fv_best_practice_answers_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."fv_best_practice_answers"
    ADD CONSTRAINT "fv_best_practice_answers_sf_id_key" UNIQUE ("sf_id");


--
-- Name: fv_best_practice_answers fv_best_practice_answers_submission_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."fv_best_practice_answers"
    ADD CONSTRAINT "fv_best_practice_answers_submission_id_key" UNIQUE ("submission_id");


--
-- Name: fv_best_practices fv_best_practices_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."fv_best_practices"
    ADD CONSTRAINT "fv_best_practices_pkey" PRIMARY KEY ("id");


--
-- Name: fv_best_practices fv_best_practices_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."fv_best_practices"
    ADD CONSTRAINT "fv_best_practices_sf_id_key" UNIQUE ("sf_id");


--
-- Name: fv_best_practices fv_best_practices_submission_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."fv_best_practices"
    ADD CONSTRAINT "fv_best_practices_submission_id_key" UNIQUE ("submission_id");


--
-- Name: households households_commcare_case_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."households"
    ADD CONSTRAINT "households_commcare_case_id_key" UNIQUE ("commcare_case_id");


--
-- Name: households households_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."households"
    ADD CONSTRAINT "households_pkey" PRIMARY KEY ("id");


--
-- Name: households households_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."households"
    ADD CONSTRAINT "households_sf_id_key" UNIQUE ("sf_id");


--
-- Name: images image_submisison_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."images"
    ADD CONSTRAINT "image_submisison_id_key" UNIQUE ("submission_id");


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."images"
    ADD CONSTRAINT "images_pkey" PRIMARY KEY ("id");


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."locations"
    ADD CONSTRAINT "locations_pkey" PRIMARY KEY ("id");


--
-- Name: locations locations_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."locations"
    ADD CONSTRAINT "locations_sf_id_key" UNIQUE ("sf_id");


--
-- Name: observation_results observation_results_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."observation_results"
    ADD CONSTRAINT "observation_results_pkey" PRIMARY KEY ("id");


--
-- Name: observation_results observation_results_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."observation_results"
    ADD CONSTRAINT "observation_results_sf_id_key" UNIQUE ("sf_id");


--
-- Name: observations observations_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."observations"
    ADD CONSTRAINT "observations_pkey" PRIMARY KEY ("id");


--
-- Name: observations observations_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."observations"
    ADD CONSTRAINT "observations_sf_id_key" UNIQUE ("sf_id");


--
-- Name: programs programs_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."programs"
    ADD CONSTRAINT "programs_pkey" PRIMARY KEY ("id");


--
-- Name: programs programs_program_code_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."programs"
    ADD CONSTRAINT "programs_program_code_key" UNIQUE ("program_code");


--
-- Name: programs programs_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."programs"
    ADD CONSTRAINT "programs_sf_id_key" UNIQUE ("sf_id");


--
-- Name: project_staff_roles project_staff_roles_commcare_case_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."project_staff_roles"
    ADD CONSTRAINT "project_staff_roles_commcare_case_id_key" UNIQUE ("commcare_case_id");


--
-- Name: project_staff_roles project_staff_roles_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."project_staff_roles"
    ADD CONSTRAINT "project_staff_roles_pkey" PRIMARY KEY ("id");


--
-- Name: project_staff_roles project_staff_roles_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."project_staff_roles"
    ADD CONSTRAINT "project_staff_roles_sf_id_key" UNIQUE ("sf_id");


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."projects"
    ADD CONSTRAINT "projects_pkey" PRIMARY KEY ("id");


--
-- Name: projects projects_project_unique_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."projects"
    ADD CONSTRAINT "projects_project_unique_id_key" UNIQUE ("project_unique_id");


--
-- Name: projects projects_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."projects"
    ADD CONSTRAINT "projects_sf_id_key" UNIQUE ("sf_id");


--
-- Name: training_modules training_modules_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."training_modules"
    ADD CONSTRAINT "training_modules_pkey" PRIMARY KEY ("id");


--
-- Name: training_modules training_modules_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."training_modules"
    ADD CONSTRAINT "training_modules_sf_id_key" UNIQUE ("sf_id");


--
-- Name: training_sessions training_sessions_commcare_case_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."training_sessions"
    ADD CONSTRAINT "training_sessions_commcare_case_id_key" UNIQUE ("commcare_case_id");


--
-- Name: training_sessions training_sessions_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."training_sessions"
    ADD CONSTRAINT "training_sessions_pkey" PRIMARY KEY ("id");


--
-- Name: training_sessions training_sessions_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."training_sessions"
    ADD CONSTRAINT "training_sessions_sf_id_key" UNIQUE ("sf_id");


--
-- Name: upload_row_errors upload_row_errors_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."upload_row_errors"
    ADD CONSTRAINT "upload_row_errors_pkey" PRIMARY KEY ("id");


--
-- Name: upload_runs upload_runs_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."upload_runs"
    ADD CONSTRAINT "upload_runs_pkey" PRIMARY KEY ("id");


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."users"
    ADD CONSTRAINT "users_email_key" UNIQUE ("email");


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."users"
    ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");


--
-- Name: users users_sf_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."users"
    ADD CONSTRAINT "users_sf_id_key" UNIQUE ("sf_id");


--
-- Name: users_temp users_temp_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."users_temp"
    ADD CONSTRAINT "users_temp_pkey" PRIMARY KEY ("id");


--
-- Name: users users_tns_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."users"
    ADD CONSTRAINT "users_tns_id_key" UNIQUE ("tns_id");


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."users"
    ADD CONSTRAINT "users_username_key" UNIQUE ("username");


--
-- Name: wetmill_visits wetmill_visits_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wetmill_visits"
    ADD CONSTRAINT "wetmill_visits_pkey" PRIMARY KEY ("id");


--
-- Name: wetmills wetmills_commcare_case_id_key; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wetmills"
    ADD CONSTRAINT "wetmills_commcare_case_id_key" UNIQUE ("commcare_case_id");


--
-- Name: wetmills wetmills_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wetmills"
    ADD CONSTRAINT "wetmills_pkey" PRIMARY KEY ("id");


--
-- Name: wv_survey_question_responses wv_survey_question_responses_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wv_survey_question_responses"
    ADD CONSTRAINT "wv_survey_question_responses_pkey" PRIMARY KEY ("id");


--
-- Name: wv_survey_responses wv_survey_responses_pkey; Type: CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wv_survey_responses"
    ADD CONSTRAINT "wv_survey_responses_pkey" PRIMARY KEY ("id");


--
-- Name: idx_attendances_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_attendances_created_by_id" ON "pima"."attendances" USING "btree" ("created_by_id");


--
-- Name: idx_attendances_farmer_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_attendances_farmer_id" ON "pima"."attendances" USING "btree" ("farmer_id");


--
-- Name: idx_attendances_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_attendances_last_updated_by_id" ON "pima"."attendances" USING "btree" ("last_updated_by_id");


--
-- Name: idx_attendances_training_session_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_attendances_training_session_id" ON "pima"."attendances" USING "btree" ("training_session_id");


--
-- Name: idx_checks_checker_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_checks_checker_id" ON "pima"."checks" USING "btree" ("checker_id");


--
-- Name: idx_checks_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_checks_created_by_id" ON "pima"."checks" USING "btree" ("created_by_id");


--
-- Name: idx_checks_farm_visit_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_checks_farm_visit_id" ON "pima"."checks" USING "btree" ("farm_visit_id");


--
-- Name: idx_checks_farmer_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_checks_farmer_id" ON "pima"."checks" USING "btree" ("farmer_id");


--
-- Name: idx_checks_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_checks_last_updated_by_id" ON "pima"."checks" USING "btree" ("last_updated_by_id");


--
-- Name: idx_checks_observation_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_checks_observation_id" ON "pima"."checks" USING "btree" ("observation_id");


--
-- Name: idx_checks_training_session_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_checks_training_session_id" ON "pima"."checks" USING "btree" ("training_session_id");


--
-- Name: idx_coffee_varieties_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_coffee_varieties_created_by_id" ON "pima"."coffee_varieties" USING "btree" ("created_by_id");


--
-- Name: idx_coffee_varieties_farm_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_coffee_varieties_farm_id" ON "pima"."coffee_varieties" USING "btree" ("farm_id");


--
-- Name: idx_coffee_varieties_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_coffee_varieties_last_updated_by_id" ON "pima"."coffee_varieties" USING "btree" ("last_updated_by_id");


--
-- Name: idx_farm_visits_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farm_visits_created_by_id" ON "pima"."farm_visits" USING "btree" ("created_by_id");


--
-- Name: idx_farm_visits_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farm_visits_last_updated_by_id" ON "pima"."farm_visits" USING "btree" ("last_updated_by_id");


--
-- Name: idx_farm_visits_training_session_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farm_visits_training_session_id" ON "pima"."farm_visits" USING "btree" ("training_session_id");


--
-- Name: idx_farm_visits_visited_household_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farm_visits_visited_household_id" ON "pima"."farm_visits" USING "btree" ("visited_household_id");


--
-- Name: idx_farm_visits_visited_primary_farmer_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farm_visits_visited_primary_farmer_id" ON "pima"."farm_visits" USING "btree" ("visited_primary_farmer_id");


--
-- Name: idx_farm_visits_visited_secondary_farmer_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farm_visits_visited_secondary_farmer_id" ON "pima"."farm_visits" USING "btree" ("visited_secondary_farmer_id");


--
-- Name: idx_farm_visits_visiting_staff_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farm_visits_visiting_staff_id" ON "pima"."farm_visits" USING "btree" ("visiting_staff_id");


--
-- Name: idx_farmer_groups_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farmer_groups_created_by_id" ON "pima"."farmer_groups" USING "btree" ("created_by_id");


--
-- Name: idx_farmer_groups_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farmer_groups_last_updated_by_id" ON "pima"."farmer_groups" USING "btree" ("last_updated_by_id");


--
-- Name: idx_farmer_groups_project_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farmer_groups_project_id" ON "pima"."farmer_groups" USING "btree" ("project_id");


--
-- Name: idx_farmer_groups_responsible_staff_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farmer_groups_responsible_staff_id" ON "pima"."farmer_groups" USING "btree" ("responsible_staff_id");


--
-- Name: idx_farmers_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farmers_created_by_id" ON "pima"."farmers" USING "btree" ("created_by_id");


--
-- Name: idx_farmers_farmer_group_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farmers_farmer_group_id" ON "pima"."farmers" USING "btree" ("farmer_group_id");


--
-- Name: idx_farmers_household_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farmers_household_id" ON "pima"."farmers" USING "btree" ("household_id");


--
-- Name: idx_farmers_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farmers_last_updated_by_id" ON "pima"."farmers" USING "btree" ("last_updated_by_id");


--
-- Name: idx_farms_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farms_created_by_id" ON "pima"."farms" USING "btree" ("created_by_id");


--
-- Name: idx_farms_farm_visit_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farms_farm_visit_id" ON "pima"."farms" USING "btree" ("farm_visit_id");


--
-- Name: idx_farms_household_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farms_household_id" ON "pima"."farms" USING "btree" ("household_id");


--
-- Name: idx_farms_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_farms_last_updated_by_id" ON "pima"."farms" USING "btree" ("last_updated_by_id");


--
-- Name: idx_fv_best_practice_answers_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_fv_best_practice_answers_created_by_id" ON "pima"."fv_best_practice_answers" USING "btree" ("created_by_id");


--
-- Name: idx_fv_best_practice_answers_fv_best_practice_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_fv_best_practice_answers_fv_best_practice_id" ON "pima"."fv_best_practice_answers" USING "btree" ("fv_best_practice_id");


--
-- Name: idx_fv_best_practice_answers_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_fv_best_practice_answers_last_updated_by_id" ON "pima"."fv_best_practice_answers" USING "btree" ("last_updated_by_id");


--
-- Name: idx_fv_best_practices_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_fv_best_practices_created_by_id" ON "pima"."fv_best_practices" USING "btree" ("created_by_id");


--
-- Name: idx_fv_best_practices_farm_visit_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_fv_best_practices_farm_visit_id" ON "pima"."fv_best_practices" USING "btree" ("farm_visit_id");


--
-- Name: idx_fv_best_practices_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_fv_best_practices_last_updated_by_id" ON "pima"."fv_best_practices" USING "btree" ("last_updated_by_id");


--
-- Name: idx_households_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_households_created_by_id" ON "pima"."households" USING "btree" ("created_by_id");


--
-- Name: idx_households_farmer_group_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_households_farmer_group_id" ON "pima"."households" USING "btree" ("farmer_group_id");


--
-- Name: idx_households_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_households_last_updated_by_id" ON "pima"."households" USING "btree" ("last_updated_by_id");


--
-- Name: idx_images_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_images_created_by_id" ON "pima"."images" USING "btree" ("created_by_id");


--
-- Name: idx_images_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_images_last_updated_by_id" ON "pima"."images" USING "btree" ("last_updated_by_id");


--
-- Name: idx_locations_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_locations_created_by_id" ON "pima"."locations" USING "btree" ("created_by_id");


--
-- Name: idx_locations_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_locations_last_updated_by_id" ON "pima"."locations" USING "btree" ("last_updated_by_id");


--
-- Name: idx_locations_parent_location_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_locations_parent_location_id" ON "pima"."locations" USING "btree" ("parent_location_id");


--
-- Name: idx_observation_results_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_observation_results_created_by_id" ON "pima"."observation_results" USING "btree" ("created_by_id");


--
-- Name: idx_observation_results_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_observation_results_last_updated_by_id" ON "pima"."observation_results" USING "btree" ("last_updated_by_id");


--
-- Name: idx_observation_results_observation_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_observation_results_observation_id" ON "pima"."observation_results" USING "btree" ("observation_id");


--
-- Name: idx_observations_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_observations_created_by_id" ON "pima"."observations" USING "btree" ("created_by_id");


--
-- Name: idx_observations_farmer_group_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_observations_farmer_group_id" ON "pima"."observations" USING "btree" ("farmer_group_id");


--
-- Name: idx_observations_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_observations_last_updated_by_id" ON "pima"."observations" USING "btree" ("last_updated_by_id");


--
-- Name: idx_observations_observer_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_observations_observer_id" ON "pima"."observations" USING "btree" ("observer_id");


--
-- Name: idx_observations_trainer_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_observations_trainer_id" ON "pima"."observations" USING "btree" ("trainer_id");


--
-- Name: idx_observations_training_session_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_observations_training_session_id" ON "pima"."observations" USING "btree" ("training_session_id");


--
-- Name: idx_programs_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_programs_created_by_id" ON "pima"."programs" USING "btree" ("created_by_id");


--
-- Name: idx_programs_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_programs_last_updated_by_id" ON "pima"."programs" USING "btree" ("last_updated_by_id");


--
-- Name: idx_project_staff_roles_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_project_staff_roles_created_by_id" ON "pima"."project_staff_roles" USING "btree" ("created_by_id");


--
-- Name: idx_project_staff_roles_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_project_staff_roles_last_updated_by_id" ON "pima"."project_staff_roles" USING "btree" ("last_updated_by_id");


--
-- Name: idx_project_staff_roles_project_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_project_staff_roles_project_id" ON "pima"."project_staff_roles" USING "btree" ("project_id");


--
-- Name: idx_project_staff_roles_staff_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_project_staff_roles_staff_id" ON "pima"."project_staff_roles" USING "btree" ("staff_id");


--
-- Name: idx_projects_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_projects_created_by_id" ON "pima"."projects" USING "btree" ("created_by_id");


--
-- Name: idx_projects_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_projects_last_updated_by_id" ON "pima"."projects" USING "btree" ("last_updated_by_id");


--
-- Name: idx_projects_location_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_projects_location_id" ON "pima"."projects" USING "btree" ("location_id");


--
-- Name: idx_projects_program_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_projects_program_id" ON "pima"."projects" USING "btree" ("program_id");


--
-- Name: idx_survey_question_responses_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_survey_question_responses_created_by_id" ON "pima"."wv_survey_question_responses" USING "btree" ("created_by_id");


--
-- Name: idx_survey_question_responses_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_survey_question_responses_last_updated_by_id" ON "pima"."wv_survey_question_responses" USING "btree" ("last_updated_by_id");


--
-- Name: idx_survey_question_responses_survey_response_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_survey_question_responses_survey_response_id" ON "pima"."wv_survey_question_responses" USING "btree" ("survey_response_id");


--
-- Name: idx_survey_responses_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_survey_responses_created_by_id" ON "pima"."wv_survey_responses" USING "btree" ("created_by_id");


--
-- Name: idx_survey_responses_form_visit_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_survey_responses_form_visit_id" ON "pima"."wv_survey_responses" USING "btree" ("form_visit_id");


--
-- Name: idx_survey_responses_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_survey_responses_last_updated_by_id" ON "pima"."wv_survey_responses" USING "btree" ("last_updated_by_id");


--
-- Name: idx_training_modules_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_training_modules_created_by_id" ON "pima"."training_modules" USING "btree" ("created_by_id");


--
-- Name: idx_training_modules_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_training_modules_last_updated_by_id" ON "pima"."training_modules" USING "btree" ("last_updated_by_id");


--
-- Name: idx_training_modules_project_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_training_modules_project_id" ON "pima"."training_modules" USING "btree" ("project_id");


--
-- Name: idx_training_sessions_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_training_sessions_created_by_id" ON "pima"."training_sessions" USING "btree" ("created_by_id");


--
-- Name: idx_training_sessions_farmer_group_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_training_sessions_farmer_group_id" ON "pima"."training_sessions" USING "btree" ("farmer_group_id");


--
-- Name: idx_training_sessions_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_training_sessions_last_updated_by_id" ON "pima"."training_sessions" USING "btree" ("last_updated_by_id");


--
-- Name: idx_training_sessions_module_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_training_sessions_module_id" ON "pima"."training_sessions" USING "btree" ("module_id");


--
-- Name: idx_training_sessions_trainer_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_training_sessions_trainer_id" ON "pima"."training_sessions" USING "btree" ("trainer_id");


--
-- Name: idx_users_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_users_created_by_id" ON "pima"."users" USING "btree" ("created_by_id");


--
-- Name: idx_users_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_users_last_updated_by_id" ON "pima"."users" USING "btree" ("last_updated_by_id");


--
-- Name: idx_users_manager_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_users_manager_id" ON "pima"."users" USING "btree" ("manager_id");


--
-- Name: idx_wetmill_visits_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_wetmill_visits_created_by_id" ON "pima"."wetmill_visits" USING "btree" ("created_by_id");


--
-- Name: idx_wetmill_visits_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_wetmill_visits_last_updated_by_id" ON "pima"."wetmill_visits" USING "btree" ("last_updated_by_id");


--
-- Name: idx_wetmill_visits_user_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_wetmill_visits_user_id" ON "pima"."wetmill_visits" USING "btree" ("user_id");


--
-- Name: idx_wetmill_visits_wetmill_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_wetmill_visits_wetmill_id" ON "pima"."wetmill_visits" USING "btree" ("wetmill_id");


--
-- Name: idx_wetmills_created_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_wetmills_created_by_id" ON "pima"."wetmills" USING "btree" ("created_by_id");


--
-- Name: idx_wetmills_last_updated_by_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_wetmills_last_updated_by_id" ON "pima"."wetmills" USING "btree" ("last_updated_by_id");


--
-- Name: idx_wetmills_user_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "idx_wetmills_user_id" ON "pima"."wetmills" USING "btree" ("user_id");


--
-- Name: ix_upload_row_errors_run_farmer; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "ix_upload_row_errors_run_farmer" ON "pima"."upload_row_errors" USING "btree" ("upload_run_id", "farmer_id");


--
-- Name: ix_upload_row_errors_run_row; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "ix_upload_row_errors_run_row" ON "pima"."upload_row_errors" USING "btree" ("upload_run_id", "row_number");


--
-- Name: ix_upload_runs_parent_upload_id; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "ix_upload_runs_parent_upload_id" ON "pima"."upload_runs" USING "btree" ("parent_upload_id");


--
-- Name: ix_upload_runs_project_status_uploaded_at; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "ix_upload_runs_project_status_uploaded_at" ON "pima"."upload_runs" USING "btree" ("project_id", "status", "uploaded_at" DESC);


--
-- Name: ix_upload_runs_project_uploaded_at; Type: INDEX; Schema: pima; Owner: -
--

CREATE INDEX "ix_upload_runs_project_uploaded_at" ON "pima"."upload_runs" USING "btree" ("project_id", "uploaded_at" DESC);


--
-- Name: etl_tasks etl_tasks_run_id_fkey; Type: FK CONSTRAINT; Schema: ops; Owner: -
--

ALTER TABLE ONLY "ops"."etl_tasks"
    ADD CONSTRAINT "etl_tasks_run_id_fkey" FOREIGN KEY ("run_id") REFERENCES "ops"."etl_runs"("run_id");


--
-- Name: attendances attendances_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."attendances"
    ADD CONSTRAINT "attendances_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: attendances attendances_farmer_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."attendances"
    ADD CONSTRAINT "attendances_farmer_id_fkey" FOREIGN KEY ("farmer_id") REFERENCES "pima"."farmers"("id");


--
-- Name: attendances attendances_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."attendances"
    ADD CONSTRAINT "attendances_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: attendances attendances_training_session_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."attendances"
    ADD CONSTRAINT "attendances_training_session_id_fkey" FOREIGN KEY ("training_session_id") REFERENCES "pima"."training_sessions"("id");


--
-- Name: checks checks_checker_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."checks"
    ADD CONSTRAINT "checks_checker_id_fkey" FOREIGN KEY ("checker_id") REFERENCES "pima"."users"("id");


--
-- Name: checks checks_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."checks"
    ADD CONSTRAINT "checks_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: checks checks_farm_visit_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."checks"
    ADD CONSTRAINT "checks_farm_visit_id_fkey" FOREIGN KEY ("farm_visit_id") REFERENCES "pima"."farm_visits"("id");


--
-- Name: checks checks_farmer_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."checks"
    ADD CONSTRAINT "checks_farmer_id_fkey" FOREIGN KEY ("farmer_id") REFERENCES "pima"."farmers"("id");


--
-- Name: checks checks_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."checks"
    ADD CONSTRAINT "checks_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: checks checks_observation_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."checks"
    ADD CONSTRAINT "checks_observation_id_fkey" FOREIGN KEY ("observation_id") REFERENCES "pima"."observations"("id");


--
-- Name: checks checks_training_session_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."checks"
    ADD CONSTRAINT "checks_training_session_id_fkey" FOREIGN KEY ("training_session_id") REFERENCES "pima"."training_sessions"("id");


--
-- Name: coffee_varieties coffee_varieties_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."coffee_varieties"
    ADD CONSTRAINT "coffee_varieties_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: coffee_varieties coffee_varieties_farm_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."coffee_varieties"
    ADD CONSTRAINT "coffee_varieties_farm_id_fkey" FOREIGN KEY ("farm_id") REFERENCES "pima"."farms"("id");


--
-- Name: coffee_varieties coffee_varieties_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."coffee_varieties"
    ADD CONSTRAINT "coffee_varieties_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: farm_visits farm_visits_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farm_visits"
    ADD CONSTRAINT "farm_visits_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: farm_visits farm_visits_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farm_visits"
    ADD CONSTRAINT "farm_visits_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: farm_visits farm_visits_training_session_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farm_visits"
    ADD CONSTRAINT "farm_visits_training_session_id_fkey" FOREIGN KEY ("training_session_id") REFERENCES "pima"."training_sessions"("id");


--
-- Name: farm_visits farm_visits_visited_household_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farm_visits"
    ADD CONSTRAINT "farm_visits_visited_household_id_fkey" FOREIGN KEY ("visited_household_id") REFERENCES "pima"."households"("id");


--
-- Name: farm_visits farm_visits_visited_primary_farmer_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farm_visits"
    ADD CONSTRAINT "farm_visits_visited_primary_farmer_id_fkey" FOREIGN KEY ("visited_primary_farmer_id") REFERENCES "pima"."farmers"("id");


--
-- Name: farm_visits farm_visits_visited_secondary_farmer_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farm_visits"
    ADD CONSTRAINT "farm_visits_visited_secondary_farmer_id_fkey" FOREIGN KEY ("visited_secondary_farmer_id") REFERENCES "pima"."farmers"("id");


--
-- Name: farm_visits farm_visits_visiting_staff_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farm_visits"
    ADD CONSTRAINT "farm_visits_visiting_staff_id_fkey" FOREIGN KEY ("visiting_staff_id") REFERENCES "pima"."users"("id");


--
-- Name: farmer_groups farmer_groups_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmer_groups"
    ADD CONSTRAINT "farmer_groups_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: farmer_groups farmer_groups_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmer_groups"
    ADD CONSTRAINT "farmer_groups_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: farmer_groups farmer_groups_location_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmer_groups"
    ADD CONSTRAINT "farmer_groups_location_id_fkey" FOREIGN KEY ("location_id") REFERENCES "pima"."locations"("id");


--
-- Name: farmer_groups farmer_groups_project_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmer_groups"
    ADD CONSTRAINT "farmer_groups_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "pima"."projects"("id");


--
-- Name: farmer_groups farmer_groups_responsible_staff_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmer_groups"
    ADD CONSTRAINT "farmer_groups_responsible_staff_id_fkey" FOREIGN KEY ("responsible_staff_id") REFERENCES "pima"."users"("id");


--
-- Name: farmers farmers_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmers"
    ADD CONSTRAINT "farmers_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: farmers farmers_farmer_group_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmers"
    ADD CONSTRAINT "farmers_farmer_group_id_fkey" FOREIGN KEY ("farmer_group_id") REFERENCES "pima"."farmer_groups"("id");


--
-- Name: farmers farmers_household_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmers"
    ADD CONSTRAINT "farmers_household_id_fkey" FOREIGN KEY ("household_id") REFERENCES "pima"."households"("id");


--
-- Name: farmers farmers_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farmers"
    ADD CONSTRAINT "farmers_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: farms farms_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farms"
    ADD CONSTRAINT "farms_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: farms farms_farm_visit_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farms"
    ADD CONSTRAINT "farms_farm_visit_id_fkey" FOREIGN KEY ("farm_visit_id") REFERENCES "pima"."farm_visits"("id");


--
-- Name: farms farms_household_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farms"
    ADD CONSTRAINT "farms_household_id_fkey" FOREIGN KEY ("household_id") REFERENCES "pima"."households"("id");


--
-- Name: farms farms_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."farms"
    ADD CONSTRAINT "farms_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: fv_best_practice_answers fv_best_practice_answers_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."fv_best_practice_answers"
    ADD CONSTRAINT "fv_best_practice_answers_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: fv_best_practice_answers fv_best_practice_answers_fv_best_practice_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."fv_best_practice_answers"
    ADD CONSTRAINT "fv_best_practice_answers_fv_best_practice_id_fkey" FOREIGN KEY ("fv_best_practice_id") REFERENCES "pima"."fv_best_practices"("id");


--
-- Name: fv_best_practice_answers fv_best_practice_answers_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."fv_best_practice_answers"
    ADD CONSTRAINT "fv_best_practice_answers_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: fv_best_practices fv_best_practices_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."fv_best_practices"
    ADD CONSTRAINT "fv_best_practices_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: fv_best_practices fv_best_practices_farm_visit_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."fv_best_practices"
    ADD CONSTRAINT "fv_best_practices_farm_visit_id_fkey" FOREIGN KEY ("farm_visit_id") REFERENCES "pima"."farm_visits"("id");


--
-- Name: fv_best_practices fv_best_practices_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."fv_best_practices"
    ADD CONSTRAINT "fv_best_practices_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: households households_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."households"
    ADD CONSTRAINT "households_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: households households_farmer_group_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."households"
    ADD CONSTRAINT "households_farmer_group_id_fkey" FOREIGN KEY ("farmer_group_id") REFERENCES "pima"."farmer_groups"("id");


--
-- Name: households households_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."households"
    ADD CONSTRAINT "households_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: images images_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."images"
    ADD CONSTRAINT "images_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: images images_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."images"
    ADD CONSTRAINT "images_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: locations locations_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."locations"
    ADD CONSTRAINT "locations_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: locations locations_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."locations"
    ADD CONSTRAINT "locations_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: locations locations_parent_location_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."locations"
    ADD CONSTRAINT "locations_parent_location_id_fkey" FOREIGN KEY ("parent_location_id") REFERENCES "pima"."locations"("id");


--
-- Name: observation_results observation_results_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."observation_results"
    ADD CONSTRAINT "observation_results_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: observation_results observation_results_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."observation_results"
    ADD CONSTRAINT "observation_results_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: observation_results observation_results_observation_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."observation_results"
    ADD CONSTRAINT "observation_results_observation_id_fkey" FOREIGN KEY ("observation_id") REFERENCES "pima"."observations"("id");


--
-- Name: observations observations_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."observations"
    ADD CONSTRAINT "observations_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: observations observations_farmer_group_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."observations"
    ADD CONSTRAINT "observations_farmer_group_id_fkey" FOREIGN KEY ("farmer_group_id") REFERENCES "pima"."farmer_groups"("id");


--
-- Name: observations observations_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."observations"
    ADD CONSTRAINT "observations_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: observations observations_observer_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."observations"
    ADD CONSTRAINT "observations_observer_id_fkey" FOREIGN KEY ("observer_id") REFERENCES "pima"."users"("id");


--
-- Name: observations observations_trainer_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."observations"
    ADD CONSTRAINT "observations_trainer_id_fkey" FOREIGN KEY ("trainer_id") REFERENCES "pima"."users"("id");


--
-- Name: observations observations_training_session_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."observations"
    ADD CONSTRAINT "observations_training_session_id_fkey" FOREIGN KEY ("training_session_id") REFERENCES "pima"."training_sessions"("id");


--
-- Name: programs programs_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."programs"
    ADD CONSTRAINT "programs_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: programs programs_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."programs"
    ADD CONSTRAINT "programs_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: project_staff_roles project_staff_roles_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."project_staff_roles"
    ADD CONSTRAINT "project_staff_roles_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: project_staff_roles project_staff_roles_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."project_staff_roles"
    ADD CONSTRAINT "project_staff_roles_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: project_staff_roles project_staff_roles_project_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."project_staff_roles"
    ADD CONSTRAINT "project_staff_roles_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "pima"."projects"("id");


--
-- Name: project_staff_roles project_staff_roles_staff_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."project_staff_roles"
    ADD CONSTRAINT "project_staff_roles_staff_id_fkey" FOREIGN KEY ("staff_id") REFERENCES "pima"."users"("id");


--
-- Name: projects projects_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."projects"
    ADD CONSTRAINT "projects_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: projects projects_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."projects"
    ADD CONSTRAINT "projects_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: projects projects_location_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."projects"
    ADD CONSTRAINT "projects_location_id_fkey" FOREIGN KEY ("location_id") REFERENCES "pima"."locations"("id");


--
-- Name: projects projects_program_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."projects"
    ADD CONSTRAINT "projects_program_id_fkey" FOREIGN KEY ("program_id") REFERENCES "pima"."programs"("id");


--
-- Name: training_modules training_modules_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."training_modules"
    ADD CONSTRAINT "training_modules_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: training_modules training_modules_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."training_modules"
    ADD CONSTRAINT "training_modules_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: training_modules training_modules_project_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."training_modules"
    ADD CONSTRAINT "training_modules_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "pima"."projects"("id");


--
-- Name: training_sessions training_sessions_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."training_sessions"
    ADD CONSTRAINT "training_sessions_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: training_sessions training_sessions_farmer_group_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."training_sessions"
    ADD CONSTRAINT "training_sessions_farmer_group_id_fkey" FOREIGN KEY ("farmer_group_id") REFERENCES "pima"."farmer_groups"("id");


--
-- Name: training_sessions training_sessions_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."training_sessions"
    ADD CONSTRAINT "training_sessions_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: training_sessions training_sessions_module_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."training_sessions"
    ADD CONSTRAINT "training_sessions_module_id_fkey" FOREIGN KEY ("module_id") REFERENCES "pima"."training_modules"("id");


--
-- Name: training_sessions training_sessions_trainer_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."training_sessions"
    ADD CONSTRAINT "training_sessions_trainer_id_fkey" FOREIGN KEY ("trainer_id") REFERENCES "pima"."users"("id");


--
-- Name: upload_row_errors upload_row_errors_upload_run_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."upload_row_errors"
    ADD CONSTRAINT "upload_row_errors_upload_run_id_fkey" FOREIGN KEY ("upload_run_id") REFERENCES "pima"."upload_runs"("id") ON DELETE CASCADE;


--
-- Name: upload_runs upload_runs_parent_upload_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."upload_runs"
    ADD CONSTRAINT "upload_runs_parent_upload_id_fkey" FOREIGN KEY ("parent_upload_id") REFERENCES "pima"."upload_runs"("id");


--
-- Name: upload_runs upload_runs_uploaded_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."upload_runs"
    ADD CONSTRAINT "upload_runs_uploaded_by_id_fkey" FOREIGN KEY ("uploaded_by_id") REFERENCES "pima"."users"("id");


--
-- Name: users users_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."users"
    ADD CONSTRAINT "users_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: users users_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."users"
    ADD CONSTRAINT "users_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: users users_manager_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."users"
    ADD CONSTRAINT "users_manager_id_fkey" FOREIGN KEY ("manager_id") REFERENCES "pima"."users"("id");


--
-- Name: wetmill_visits wetmill_visits_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wetmill_visits"
    ADD CONSTRAINT "wetmill_visits_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: wetmill_visits wetmill_visits_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wetmill_visits"
    ADD CONSTRAINT "wetmill_visits_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: wetmill_visits wetmill_visits_user_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wetmill_visits"
    ADD CONSTRAINT "wetmill_visits_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "pima"."users"("id") NOT VALID;


--
-- Name: wetmill_visits wetmill_visits_wetmill_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wetmill_visits"
    ADD CONSTRAINT "wetmill_visits_wetmill_id_fkey" FOREIGN KEY ("wetmill_id") REFERENCES "pima"."wetmills"("id");


--
-- Name: wetmills wetmills_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wetmills"
    ADD CONSTRAINT "wetmills_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: wetmills wetmills_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wetmills"
    ADD CONSTRAINT "wetmills_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: wetmills wetmills_user_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wetmills"
    ADD CONSTRAINT "wetmills_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "pima"."users"("id");


--
-- Name: wv_survey_question_responses wv_survey_question_responses_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wv_survey_question_responses"
    ADD CONSTRAINT "wv_survey_question_responses_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: wv_survey_question_responses wv_survey_question_responses_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wv_survey_question_responses"
    ADD CONSTRAINT "wv_survey_question_responses_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- Name: wv_survey_question_responses wv_survey_question_responses_survey_response_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wv_survey_question_responses"
    ADD CONSTRAINT "wv_survey_question_responses_survey_response_id_fkey" FOREIGN KEY ("survey_response_id") REFERENCES "pima"."wv_survey_responses"("id");


--
-- Name: wv_survey_responses wv_survey_responses_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wv_survey_responses"
    ADD CONSTRAINT "wv_survey_responses_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "pima"."users"("id");


--
-- Name: wv_survey_responses wv_survey_responses_form_visit_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wv_survey_responses"
    ADD CONSTRAINT "wv_survey_responses_form_visit_id_fkey" FOREIGN KEY ("form_visit_id") REFERENCES "pima"."wetmill_visits"("id");


--
-- Name: wv_survey_responses wv_survey_responses_last_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: pima; Owner: -
--

ALTER TABLE ONLY "pima"."wv_survey_responses"
    ADD CONSTRAINT "wv_survey_responses_last_updated_by_id_fkey" FOREIGN KEY ("last_updated_by_id") REFERENCES "pima"."users"("id");


--
-- PostgreSQL database dump complete
--

\unrestrict pJytBU8e19sKymeJ7NDlEkyj15l4qlExguBSgmvPVsEe4h2TFJKm82KAZ5CaEP4

