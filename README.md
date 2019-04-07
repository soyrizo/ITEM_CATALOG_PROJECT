SPORTS ITEM CATALOG
===================
Creates a sports item catalog. The catalog contains various sports and lists specific items for each sport. Both sports and sport iems can be created, updated, or deleted.

## Requirements
- Python 2.7
- Vagrant & VirtualBox
- Google Account for OAuth2.0 Setup

## Setup
1. Install [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) and [Vagrant](https://www.vagrantup.com/downloads.html).
2. Clone this repo
```git clone git@github.com:soyrizo/ITEM_CATALOG_PROJECT.git```
3. `cd ITEM_CATALOG_PROJECT` and start up Vagrant
```vagrant up```
4. Once Vagrant is up, drop into the VM
```vagrant ssh```
5. The contents of this git repo will be under `/vagrant`
6. Create the database
```python database_setup.py```
7. Populate the database with some values (optional)
```python populate_sports_db.py```
8. Launch the sports item catalog application
```python item_catalog.py```
9. The application can be accessed in a browser via http://localhost:5000

*_NOTE_* Google OAuth2.0 will need to be setup. To do this, you must have a Google account. You can setup the Project [here](https://console.developers.google.com/apis) and populate the client_secrets.json with the following:
- CLIENT_ID
- CLIENT_SECRET
- PROJECT_ID

## API
The item catalog has a list of API endpoints available for use which return JSON.
### Examples
To access the list of Sports:
```localhost:5000/sports/JSON```

To access all items of a specific sport:
```http://localhost:5000/sport/<sport_id>/items/JSON```

To access a specific sports item of a sport:
```http://localhost:5000/sport/<sport_id>/item/<sport_item_id>/JSON```
