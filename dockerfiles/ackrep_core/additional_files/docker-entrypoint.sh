#!/bin/sh
set -e


if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then

    # create an empty database
    python manage.py migrate --noinput --run-syncdb #>/dev/null
    python -c "from ackrep_core import core; core.load_repo_to_db('/code/ackrep/ackrep_data')" #>/dev/null

    # this is the place where fixtures could be loaded

fi

exec "$@"
