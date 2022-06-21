#!/bin/bash
set -e
# Update the UID
echo newid $HOST_UID
echo uid $UID
# id 
# ls -n ../
chown -R $HOST_UID:$HOST_UID /code
# ls -n ../

# create an empty database
python manage.py migrate --noinput --run-syncdb >/dev/null
# echo $ACKREP_DATABASE_PATH
if [[ $ACKREP_DATABASE_PATH == *"unittest"* ]]
then
    echo "loading unittest repo"
    python -c "from ackrep_core import core; core.load_repo_to_db('/code/ackrep_data_for_unittests')" #>/dev/null
elif [[ $ACKREP_DATABASE_PATH == *"db"* ]]
then
    # echo "loading data repo"
    python -c "from ackrep_core import core; core.load_repo_to_db('/code/ackrep_data')" >/dev/null
else
    echo "no db path specified, no db loaded"
fi

useradd --uid $HOST_UID $HOST_NAME
su $HOST_NAME
id

exec "$@"
