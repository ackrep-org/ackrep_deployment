#!/bin/bash
set -e









# create an empty database
python manage.py migrate --noinput --run-syncdb >/dev/null
# echo $ACKREP_DATABASE_PATH
if [[ $ACKREP_DATABASE_PATH == *"unittest"* ]]
then
    echo "loading unittest repo"
    python -c "from ackrep_core import core; core.load_repo_to_db('/code/ackrep_data_for_unittests')" #>/dev/null
    chown $HOST_UID:$HOST_UID /code/ackrep_core/db_for_unittests.sqlite3
elif [[ $ACKREP_DATABASE_PATH == *"db"* ]]
then
    # echo "loading data repo"
    python -c "from ackrep_core import core; core.load_repo_to_db('/code/ackrep_data')" >/dev/null
    chown $HOST_UID:$HOST_UID /code/ackrep_core/db.sqlite3
else
    echo "no db path specified, no db loaded"
fi


# open a 'good' shell, see https://unix.stackexchange.com/a/307581

exec "$@"
