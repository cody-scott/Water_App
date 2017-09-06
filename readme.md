# Water App

New QC App for reviewing the water data


## Create virtualenv

Create an isolated virtual environment

    mkvirtualenv water_app

activate global site packages for using the arcpy module

    toggleglobalsitepackages -q

## Install With pip

    pip install -r requirements.txt

## Running

Activate workspace

    workon water_app

Load New data

    python manage.py load_data

Push reviewed data to DB once reviewed

    python manage.py push_changes

Load Base data (if needed)

    python manage.py fill_base_data
