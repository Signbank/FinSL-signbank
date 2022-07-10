# NZSL Signbank

## Purpose

NZSL-signbank is a web based database for sign language lexicons and
corpora. The original Signbank (for Auslan) was developed by Steve Cassidy [https://github.com/Signbank/Auslan-signbank][auslan-signbank] and subsequently built upon by other projects, now gathered at [https://github.com/Signbank].

NZSL-Signbank is most closely based on[FinSL-Signbank](https://github.com/Signbank/FinSL-signbank). The main differences between FinSL-Signbank and NZSL-Signbank are documented in this ReadMe.

Unlike other Signbanks, NZSL-Signbank is not intended as a public lexicon or dictionary. Instead, the application is used to enable the Deaf Studies Research Unit (DSRU) of Victoria University of Wellington, NZ to manage NZSL language data for use in the [NZSL Dictionary](https://nzsl.nz), NZSL Dictionary apps, NZSL learning resources, and for research purposes.

The application is primarily intended for managed access usage. Precedence is given to research and editorial features over performance.

## Overview

Main features:

- Manage and organize sign language lexicons and corpora.
- Store multiple lexicons.
- Use your Glosses in [ELAN][elan-link] with ECV (externally controlled dictionary).
  - ECV's are available for all lexicons automatically.
- Upload images and videos and connect them to glosses.
- Organise videos and images based on their purpose.
- Add comments on glosses and tag them.
- Store relationships between glosses.
- Control access to lexicons per user/group.
- Publish lexicons and their glosses.
- Detailed interface for researchers/annotators.
- add detailed information to glosses including translation equivalents, word class, phonology, morphology, semantics, usage and variation

## Operations:

### Branching naming conventions:

All deployments should be performed by CI unless there are specific deployment processes which prevent this.

| **Git branch name** | **Deploys to environment** | **Typically deployed by** |
| ------------------- | -------------------------- | ------------------------- |
| master              | UAT                        | CI                        |
| production          | Production                 | CI                        |

#### master

> Note: Convention is to use `main` as the primary branch name. This project has stuck with `master`
> to match the FinSL upstream primary branch name for now.

- The default branch features are merged into.
- master should always have a green build.
- Should always deploy to UAT environment if one exists.
- feature/ and bugfix/ work will be branched from, and merged back into, main.

#### production

- This will point to the production environment.
- Only the master branch will be merged.
- Merges should be squash merges so the release can be tagged if necessary from the commit.
- Merges should be via pull request from `master` to `production` for review and signoff.

#### feature/xxx-yyy

Development on new features happens in feature branches. Branch names should contain the story or ticket number and a brief description of the feature. For example feature/753-widget-show-page.

#### bugfix/xxx-yyy

Bug fixes should happen in branches. Branch names should contain the ticket or issue number and a brief description of the bug. For example bugfix/23-correct-pluralisation-of-radius.

##### support/xxx-yyy

Support ticket related changes or fixes should happen in support branches. Branch names should contain the ticket number and a brief description of the change. For example support/294-timestamp-error.

### Environments

| **Environment** | **URL**                      | **Hosting Platform** | **Git Branch** | **Exception monitoring URL** | **Logs available at**              | **Asset storage**                                             |
| --------------- | ---------------------------- | -------------------- | -------------- | ---------------------------- | ---------------------------------- | ------------------------------------------------------------- |
| UAT             | https://signbank-uat.nzsl.nz | Heroku (free tier)   | master         | Sentry                       | `heroku logs -a nzsl-signbank-uat` | S3 (nzsl-signbank-media-uat) owned by NZSL AWS account        |
| Production      | https://signbank.nzsl.nz     | Heroku (paid tier)   | production     | Sentry                       | `heroku logs -a nzsl-signbank`     | S3 (nzsl-signbank-media-production) owned by NZSL AWS account |

Both environments are managed by Terraform. The Terraform configurations are also open-sourced and [available on Github](https://github.com/ODNZSL/nzsl-infrastructure).

### Shell access

| **Environment** | **Shell access available** |
| --------------- | -------------------------- |
| UAT             | YES                        |
| Production      | YES                        |

Shell access is via Heroku:

- UAT: `heroku run bash -a nzsl-signbank-uat`
- Production: `heroku run bash -a nzsl-signbank`

### Browser Support

| **Browser**        | **Supported Versions** |
| ------------------ | ---------------------- |
| Edge               | Latest -2              |
| Safari             | Latest -2              |
| Chrome             | Latest -2              |
| Firefox            | Latest -2              |
| iOS Safari         | Latest -2              |
| Chrome for Android | Latest -2              |

> Note: Browser support for this project is best-effort and is primary focused on browsers used by actual users,
> primarily DSRU.

This project uses a lot of 'historical' Javascript, the style of which we've tried to follow when we have modified the
scripts from upstream. There is _no_ transpile or polyfilling set up for this project, so care must be used if using ES6+
features that browser support is adequate.

### AWS

This application uses an AWS S3 bucket to store glossvideo files. This is primarily because it means we decouple the application runtime from the external storage needs - both uploaded files and database. This is _required_ for running on Heroku, which offers no peristent storage, but is also useful for a range of other hosting providers that support containerisation, such as Fargate, ECS, Fly.io, etc.

The bucket is owned by the NZSL account that also stores files for [NZSL Share](https://nzslshare.nz).

By default, the normal filesystem-based file storage engine will be used. This is the default when running in development or test. To test that something in particular works with AWS, the following environment variables must be provided:

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_STORAGE_BUCKET_NAME

See [example.env](example.env) for more information about these variables. If you have set up infrastructure using the [Terraform config](https://github.com/odnzsl/nzsl-infrastructure), the output of applying a Terraform plan includes the bucket name and AWS keypair that are created by this configuration.

At this stage, S3 is the only AWS service used by this application.

## Secrets

All credentials and the `.env` file for this project are stored in Ackama 1Password vault for this project.
An example.env is available in the project root to give an idea of the configuration that the application expects.

## Healthchecks

This project doesn't have a healthcheck endpoint set up, but it _does_ utilise Django's internal checks framework.
Checks can be run via `bin/develop.py check`. Custom checks can be [added](https://docs.djangoproject.com/en/4.0/topics/checks/).

In the future, we may incorporate a healthcheck command into our Dockerfile. This would prevent the container from starting
up until all check warnings are satisfied.

## Project Resources:

| **Resource** | **URL**                                                                                                                                                                  |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Backlog URL  | Internal Jira backlog owned by Ackama. For external users, we welcome [issue reports](https://github.com/odnzsl/nzsl-signbank/issues/new) for prioritisation in our Jira |
| CI URL       | https://github.com/ODNZSL/NZSL-signbank/actions                                                                                                                          |

## Comms:

Internal project comms occur in #ackama-nzsl on Ackama's Slack. The #public-nzsl
channel is available for communication with DSRU and the product owner. For
external users, the best communication method is via [Github
issues](https://github.com/odnzsl/nzsl-signbank/issues/new), or by emailing
dsru@vuw.ac.nz.

During active development of this project, we work with the SCRUM methodology:

1. Features are added to the project backlog in Jira. We refine the backlog
   weekly, adding more information to stories, exploring approaches and
   preparing stories to be worked on.
2. We plan the next sprint weekly, adding stories from the top of our backlog to
   the sprint, sizing the sprint based on the previous sprints' velocity.
3. We review each sprint at the end of the sprint, moving any incomplete stories
   into the next sprint.
4. We have retrospectives regularly to analyse how we can improve our delivery
   process.

When this project is not in active development, we work off support tickets as
they are received and prioritised. Support tickets that represent new features
will be recorded on the project backlog to estimate for the next phase of work.

## Developers

### Dependencies

Running the app in Docker using docker-compose is recommended, but not
mandatory.

Local setup is unsupported. Docker receives good support since our CI, UAT and
Production pipelines all use our Docker containers as defined here.

To run the application locally you will need:

- Python 3 (3.6+ recommended)
- NodeJS (v16 is used at time of writing, but we aim to track LTS releases)
- Build tooling for compiling Pip dependencies with native extensions.
- Either PostgreSQL client libraries or SQLite (we use Postgres, but
  Global-signbank uses SQLite and this should continue to be supported)
- A postgres database that is reachable by the application. A database URI can
  be provided to the application using the `DATABASE_URL` environment variable.
- The configuration in example.env or .env sourced into the shell session that
  will run the app.
- Dependencies can be found in [requirements.txt][requirements.txt] and they can be installed using pip: `pip install -r requirements.txt`.

### Running the app

1. Clone the project: `git clone git@bitbucket.org:rabidtech/THIS_REPO.git`
2. Create `.env` file by copying data from 1Password.

To start the application using docker-compose, simply run:

`docker-compose up`

And the service will start bound to port 8000 on your host, with a companion Postgres database
running in its own container, and an SMTP mailcatcher that will receive outbound mail from the application bound to port 1025 on your host.

You may wish to run `docker-compose run backend ./bin/develop.py createsuperuser` to set up an admin user.

If Docker is not being used, you can run `./bin/develop.py createsuperuser` to set up an admin user and an initial dataset. You can start a server using `./bin/develop.py runserver '127.0.0.1:8000'` that is bound to localhost, port 8000. It's up to you to ensure that an SMTP and Postgres server are available to the application if not using docker.

### Running the tests

The test suite for this project is largely smoketest based, consisting of light coverage
of a selection of view and model tests using the Django testing framework.

```bash
# run all specs using docker
docker-compose run backend bin/runtests.py

# run all specs locally, or in a docker bash session
./bin/runtests.py
```

### Useful commands

- Enter a bash session in the backend container: `docker-compose run backend bash`
- Enter a Python REPL: `docker-compose run backend bin/develop.py shell`
- Enter a psql session: `docker-compose run backend bin/develop.py dbshell`
- Start a server in an interactive session that can be used with [pdb](https://docs.python.org/3/library/pdb.html): `docker-compose stop backend; docker-compose run --service-ports backend runserver '0.0.0.0:8000'`
- Reset the database: `docker-compose down; docker-compose up`

Note: Most of these commands can be used with `heroku run` replacing `docker-compose run backend`

## Documentation:

### FinSL-signbank documentation

**Technical documentation** for developers can be found at https://finsl-signbank.readthedocs.io/

**User documentation** is available at [https://github.com/Signbank/FinSL-signbank/wiki][https://github.com/signbank/finsl-signbank/wiki]

**Changelog** is available at [https://github.com/Signbank/FinSL-signbank/blob/master/CHANGELOG.rst](https://github.com/Signbank/FinSL-signbank/blob/master/CHANGELOG.rst)

**FinSL contribution information** is in their [README](https://github.com/Signbank/FinSL-signbank#contribution).

### Freelex data migration scripts

Are available to Ackama staff at
https://github.com/ackama/nzsl-freelex-signbank-data-migration. These scripts
were written to transfer data from Freelex, the legacy editorial tool, into
Signbank.

If you wish to run them against this application, you need to reset the Signbank
database: `docker-compose down && docker-compose up`, and then in another shell,
`cd` into the migration repository and run `docker-compose run migration`. There
are some assets you need to have in place for this, see the README of the
migration scripts repository for details.

Note that the migration does not create a superuser account, this needs to be
done manually after the migration finishes (it takes 15-20 minutes). The django
site is also reset to example.com, and needs to be changed for some links (like
those in emails) to have the correct hostname.

### Assets

This project has a mixture of assets that are built into the source tree (things
like Bootstrap 3, and a range of older jQuery plugins), and dependencies from
package.json (like jQuery and recordrtc). This is useful to know, since
depending on the feature, a developer might be referencing either or both of
these sources.

We have not yet developed an architecture approach for the frontend of this
project. It's likely to live on in its current form for some time, since
refactoring frontend dependencies into package.json gains us security auditing
and proper version pinning, but otherwise doesn't have much value.

### Gotchas/known issues

- Parts of the application functionality rely on `FieldChoice` records existing in the database.
  The Freelex migration scripts create these fieldchoice records, but if you set up this project
  from scratch, they won't be included by default.
- The application configuration has been refactored to use environment variables
  for configuration, rather than `settings_secret.py`. You'll see a warning
  about this file being missing each time a Django command is run - it can be
  disregarded.
- There are three ways glosses are presented - the 'basic' (public) view, the
  'advanced' view, and the admin view. Generally, the basic view is a
  low-priority for us, and we may remove it entirely in time, since the main
  public interface for Signbank is through the NZSL Dictionary applications.
- If a repository is forked, Github _always_ assumes you are opening a pull
  request to the upstream, not to a branch in your fork. When opening a PR,
  ensure you choose 'odnzsl/NZSL-signbank' as the base repository so that the
  diff is correct (_and so that FinSL doesn't get a giant PR with all of our
  changes, ever_). Remember that pull requests cannot be deleted, only closed,
  so making this mistake will live in the history of NZSL-signbank and FinSL
  forevermore. Ask me how I know.

### Differences between NZSL Signbank and FinSL Signbank

- We refactored how glossvideos are handled to use the Django File storage APIs.
  This allowed us to add django-storages and introduce an adapter pattern for
  file storage so that S3 OR local file storage can be used. FinSL works with
  local file storage, but not S3, since it was utilising a lot of local `os`
  commands to move or rename files.
- We refactored the configuration files to load a lot of settings from
  environment variables. This allows us to use `.env` files locally, and
  Heroku's config framework in deployments, to configure the application.
- Global signbank uses FieldChoices heavily for establishing connections between
  records. FinSL has walked some of this back to use Tags, and introduced
  AllowedTags, which enables tags to be 'permitted' for a particular record
  type. We use a mixture, using tags for editorial purposes, but FieldChoices
  for gloss data fields where a choice or multiple choices are made from a list.
- We added support for choosing fieldchoices from checkboxes or a multiselect to
  enable some many-many relationships added.
- We added several new datafields to the gloss model to hold data from Freelex
  (the old editorial tool).
- We set up Github CI, automated deployments, infrastructure config, and support
  for running the application in Docker. This was mostly for dev/support
  convenience since we don't have a lot of in-house Python capability.

The above is a summary of differences between FinSL and NZSL Signbank. For a more up-to-date
and comprehensive view, Github provides a diff between the two repositories at https://github.com/Signbank/FinSL-signbank/compare/master...ODNZSL:master.

## Running in production

### security.txt

- `/.well-known/security.txt` exists with instructions which security researchers can use to contact us if they find an issue in this application.

### Logging

The application runs in Heroku's Docker runtime, which logs all messages emitted by the application to STDOUT, available via the Heroku web UI or CLI.
To configure the log level, you may set the `DJANGO_LOG_LEVEL` environment variable to one of the following levels:

- DEBUG: Low level system information for debugging purposes (`heroku config:set DJANGO_LOG_LEVEL=DEBUG`)
- INFO: General system information (`heroku config:set DJANGO_LOG_LEVEL=INFO`) (default)
- WARNING: Information describing a minor problem that has occurred (`heroku config:set DJANGO_LOG_LEVEL=WARNING`)
- ERROR: Information describing a major problem that has occurred (`heroku config:set DJANGO_LOG_LEVEL=ERROR`)
- CRITICAL: Information describing a critical problem that has occurred (`heroku config:set DJANGO_LOG_LEVEL=CRITICAL`)

### Running in UAT mode locally

```sh
# get UAT secrets
$ heroku config --shell -a nzsl-signbank-uat > .env
```

```sh
# precompile assets
$ docker-compose run backend bin/develop.py collectstatic
```

```sh
# run server (note you need **all** these flags to run staging locally)
$ docker-compose up
```

### Running in production mode locally

```sh
# get production secrets
$ heroku config --shell -a nzsl-signbank > .env
```

```sh
# precompile assets
$ docker-compose run backend bin/develop.py collectstatic
```

```sh
# run server (note you need **all** these flags to run staging locally)
$ docker-compose up
```
