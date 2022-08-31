# ACKRep Deployment Utils

**Note:** The full documentation is available online at <https://ackrep-doc.readthedocs.io/en/latest/index.html>.

## General Information

This repository contains the code that runs on <demo.ackrep.org>. It should also provide a starting point to deploy an own instance.

## Deployment concept

The ackrep project consists of several components which are maintained each in their own repository.


**Functional Components**

- *[ackrep_core](https://github.com/cknoll/ackrep_core)*
    - main code of the ackrep engine and command-line-interface (cli)
- *[ackrep_data](https://github.com/cknoll/ackrep_data)*
    - actual data for the repository
- (*[ackrep_web](https://github.com/cknoll/ackrep_core/tree/main/ackrep_web)*)
    - code for the web front-end
    - currently still part of ackrep_core

**Auxiliary Components**

- *ackrep_deployment*
    - code for simple deployment of the functional components on a virtual server
- *ackrep_deployment_config*
    - data used for customization and maintainance. For privacy and security reasons this repo is not published.

<a name="directory-layout"></a>
These components are represented by the following **directory layout**:

    <ackrep_project_dir>/
    ├── ackrep_deployment/                ← repo with deployment code for the ackrep project
    │  ├── .git/
    │  ├── README.md                      ← the currently displayed file (README.md)
    │  ├── deploy.py                      ← deployment script
    │  └── ...
    │
    ├── ackrep_deployment_config/         ← non-public repo; deployment config data for ackrep.org;
    │  │                                    (paths and domains but no secret keys etc.)
    │  ├── README.md
    │  ├── config_demo.ini                ← settings for public demo instance
    │  ├── config_testing2.ini            ← settings for testing instance (for development)
    │  └── ...
    │
    ├── config.ini                        ← config file which will be used by settings.py
    │                                       On the remote server: This file is created during deployment.
    │                                       On local testing machine: This might be absent, then the
    │                                       example from ackrep-core will be used.
    │
    │
    ├── ackrep_data/                      ← separate repository for ackrep_data
    │  ├── .git/
    │  └── ...
    │
    ├── ackrep_data_for_unittests/        ← expected to be a clone/copy of ackrep_data
    │  ├── .git/                            (must be created manually)
    │  └── ...
    └── ackrep_core/                      ← separate repository for ackrep_core
       ├── .git/
       ├── config-example.ini             ← example config file which will be used as fallback if
       │                                     <ackrep_project_dir>/config.ini cannot be found.
       └── ...

The components *ackrep_core* and *ackrep_data* are maintained in separate repositories.
For the deployment to work it is expected to clone them separately one level up in the directory structure.

### Deployment and Testing:


#### Without Docker

**Setup:**

- create a new empty directory
- clone *ackrep_data*
- clone *ackrep_core*, enter the repo directory, run the following commands from there.
- `pip install -r requirements.txt`
    - if building uwsgi fails → no problem (not needed for local testing)
- `python3 manage.py makemigrations`
- `python manage.py migrate --noinput --run-syncdb`
- `python -c "from ackrep_core import core; core.load_repo_to_db('../ackrep_data')"`
- `python3 manage.py runserver`

**Test:**
- visit <http://localhost:8000/> with your browser and check if the ackrep landing page is shown
- visit <http://localhost:8000/entities>, search for key (UKJZI), click on "check this solution"; this should load some curves after about 3s.


### With Docker


**steps for local testing deployment**
- install docker (e.g. via `apt install docker-ce docker-ce-cli docker-ce-rootless-extras`)
- install docker-compose (e.g. via `pip install docker-compose`)
- create a directory structure like above
- `cd ackrep_deployment`
- build the main container: `docker-compose up -d --remove-orphans --build ackrep-django`
- run the main container: `docker-compose up ackrep-django`
- visit <http://localhost:8000/> with your browser and check if the ackrep landing page is shown


