# Pima Migration (Salesforce ➜ Postgres)

Pipelines to fetch from Salesforce, transform, and load into the new **Pima** schema.
- Organized per new pima db objects (Programs, Locations etc).
- Additional ops audit tables (`ops.etl_runs`, `ops.etl_tasks`).
- Run through CLI via `runner.py`.

## Quick start

```bash
# Setup environment
python -m venv .venv && source .venv/bin/activate
# Install requirements
pip install -r requirements.txt

# setup .env
cp .env.example .env
# edit .env with Salesforce + Postgres credentials

# Example commands
python runner.py init           # create ops tables

# Commanda to load unique object data one by one
python runner.py programs       # load Programs
python runner.py locations      # load Locations (two-pass for parent linkage)
python runner.py projects       # load Projects

# Runs all objects in dependency order
python runner.py run-all        # run in dependency order
```

## Structure

```
pima_migrate/
  app/
    config.py        # env & settings
    db.py            # SQLAlchemy engine, helper executors
    sf.py            # Salesforce client + query helper
    audit.py         # etl_runs / etl_tasks
    utils.py         # helpers (chunked, lookups)
    sql/
      programs_upsert.sql
      locations_upsert.sql
      projects_upsert.sql
    objects/
      programs.py        
      locations.py       
      projects.py        
      farmers.py         
      households.py      
      farmer_groups.py   
      training_modules.py 
      training_sessions.py 
      attendances.py     # placeholder
      observations.py    # placeholder
      observation_results.py # placeholder
      farm_visits.py     # placeholder
      farms.py           # placeholder
      fv_best_practices.py # placeholder
      fv_best_practice_answers.py # placeholder
      coffee_varieties.py # placeholder
      checks.py          # placeholder
      images.py          # placeholder
      project_staff_roles.py # placeholder
  runner.py
  requirements.txt
  .env.example
```