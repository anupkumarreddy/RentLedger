# RentLedger server layout

RentLedger runs as the `rentledger` system user with its own virtual environment,
SQLite database, media directory, Gunicorn socket, systemd service, and Nginx
virtual host.

- Code: `/srv/apps/rentledger/current`
- Virtual environment: `/srv/apps/rentledger/venv`
- Database: `/srv/apps/rentledger/data/db.sqlite3`
- Media: `/srv/apps/rentledger/media`
- Environment: `/etc/rentledger/rentledger.env`

Run `sudo deploy/update-server.sh` from the repository to pull and deploy the
latest `main` branch after the initial server setup.
