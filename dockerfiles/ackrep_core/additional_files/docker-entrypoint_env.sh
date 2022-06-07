#!/bin/bash
set -e

# create an empty database
python manage.py migrate --noinput --run-syncdb >/dev/null

if [[ $ACKREP_DATABASE_PATH == *"unittest"* ]]
then
    python -c "from ackrep_core import core; core.load_repo_to_db('/code/ackrep_data_for_unittests')" >/dev/null
else
    python -c "from ackrep_core import core; core.load_repo_to_db('/code/ackrep_data')" >/dev/null
fi

exec "$@"
