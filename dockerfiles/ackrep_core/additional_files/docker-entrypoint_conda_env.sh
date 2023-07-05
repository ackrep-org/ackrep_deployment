#!/bin/bash
set -e

if [[ -z "$HOST_UID" ]]; then
    echo "ERROR: please set HOST_UID" >&2
    exit 1
fi

# Update the UID
chown -R $HOST_UID:$HOST_UID /code
chown -R $HOST_UID:$HOST_UID /home


# see https://www.joyfulbikeshedding.com/blog/2021-03-15-docker-and-the-host-filesystem-owner-matching-problem.html
usermod --uid "$HOST_UID" appuser
groupmod --gid "$HOST_UID" appuser


# create an empty database
python manage.py migrate --noinput --run-syncdb >/dev/null
# echo $ACKREP_DATABASE_PATH
if [[ $ACKREP_DATABASE_PATH == *"unittest"* ]]
then
    echo "loading unittest repo"
    python -c "from ackrep_core import core; core.load_repo_to_db('/code/ackrep/ackrep_data_for_unittests')" #>/dev/null
    chown $HOST_UID:$HOST_UID /code/ackrep/ackrep_core/db_for_unittests.sqlite3
elif [[ $ACKREP_DATABASE_PATH == *"db"* ]]
then
    # echo "loading data repo"
    python -c "from ackrep_core import core; core.load_repo_to_db('/code/ackrep/ackrep_data')" >/dev/null
    chown $HOST_UID:$HOST_UID /code/ackrep/ackrep_core/db.sqlite3
else
    echo "no db path specified, no db loaded"
fi


# open a 'good' shell, see https://unix.stackexchange.com/a/307581
su -s /bin/bash appuser

exec "$@"
