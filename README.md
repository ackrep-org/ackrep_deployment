# ACKREP Deployment Utils

**Note:** The full documentation is available online at <https://ackrep-doc.readthedocs.io/en/latest/index.html>.

## General Information

This repository contains code used to run instances <demo.ackrep.org>, <testing.ackrep.org>, etc. It should also provide a starting point to deploy an own instance.

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
- *[pyerk-core](https://github.com/ackrep-org/pyerk-core)*
    - (experimental) tool for symbolic knowledge representation
- *[ocse](https://github.com/ackrep-org/ocse)*
    - ontology of control engineering

**Auxiliary Components**

- *ackrep_deployment*
    - code for simple deployment of the functional components on a virtual server
- *ackrep_deployment_config*
    - data used for customization and maintainance. For privacy and security reasons this repo is not published.

<a name="directory-layout"></a>
These components are represented in the following **directory layout**:

```

    <common-root>                 ← desired context directory
    │
    ├── ackrep              
    │   ├── ackrep_data/...
    │   ├── ackrep_data_for_unittests/    ← expected to be a clone/copy of ackrep_data
    │   │                                   (must be created manually)
    │   │                                   <ackrep_project_dir>/config.ini cannot be found.
    │   ├── ackrep_core/...
    │   │   ├── config-example.ini        ← example config file which will be used as fallback if
    │   │   └── ...                         <ackrep_project_dir>/config.ini cannot be found.
    │   ├── ackrep_deployment/            ← assumed working directory
    │   │   ├── README.md                 ← the currently displayed file (README.md)
    │   │   ├── deploy.py                 ← deployment script
    │   │   └── ...                       
    │   ├── ackrep_deployment_config/     ← repo with deployment code for the ackrep project
    │   │   ├── config_demo.ini           ← settings for public demo instance
    │   │   ├── config_testing2.ini       ← settings for testing instance (for development)
    │   │   └── ...                       
    │   │                                 
    │   ├── config.ini                    ← config file which will be used by settings.py
    │   │                                   On the remote server: This file is created during deployment.
    │   │                                   On local testing machine: This might be absent, then the
    │   │                                   example from ackrep-core will be used.
    │   └── ...
    └── erk
        ├── pyerk-core/
        ├── erk-data/
        │   ├── ocse                      ← repo of the ontology of control systems engineering
        │   │   ├── erkpackage.toml           
        │   │   └── ...
        │   └──...                       
        └── ...
```

For the deployment to work it is expected to clone all repos separately and manually establish the above directory structure.

### Deployment and Testing:


#### Without Docker

**Setup:**

- create a new python environment (optional)
- establish the directory structure above via appropriate `mkdir ..` and `git clone ...` commands
- in *ackrep_core* directory, run the following commands from there.
- `pip install -r requirements.txt`
    - if building uwsgi fails → no problem (not needed for local testing)
- `pip install -e .`
- `python3 manage.py makemigrations`
- `python manage.py migrate --noinput --run-syncdb`
- `python -c "from ackrep_core import core; core.load_repo_to_db('../ackrep_data')"`
- `python3 manage.py runserver`


### With Docker


**steps for local testing deployment**
- install docker (e.g. via `apt install docker-ce docker-ce-cli docker-ce-rootless-extras`)
- install docker-compose (e.g. via `pip install docker-compose`)
- create a directory structure like above
- `cd ackrep_deployment`
- build the main container: `docker-compose up -d --remove-orphans --build ackrep-django`
- run the main container: `docker-compose up ackrep-django`



### Basic Test

- visit <http://localhost:8000/> with your browser and check if the ackrep landing page is shown
- visit <http://localhost:8000/entities>, search for key (UKJZI), click on "check this solution"; this should load some curves after about 3s.


