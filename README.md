# Import Nextcloud users from a CSV file

Credit to [t-markmann](https://github.com/t-markmann/nc-userimporter) for inspiration.

Quick Usage:

```
python3 nextcloud_user_importer.py --nc-url your-nextcloud-url.com --admin-name admin --admin-pass password --csv-file users.csv
```

For help:

```
python3 nextcloud_user_importer.py --help
```

```
usage: nextcloud_user_importer.py [-h] [--protocol PROTOCOL] --nc-url NC_URL --admin-name ADMIN_NAME --admin-pass ADMIN_PASS [--api-url API_URL] (--users-csv-file USERS_CSV_FILE | --groups-csv-file GROUPS_CSV_FILE | --dump-users-csv) [--csv-delimiter CSV_DELIMITER] [--csv-delimiter-groups CSV_DELIMITER_GROUPS] [--generate-password] [--no-ssl-verify] [--language LANGUAGE] [--dry-run] [--password]

Nextcloud User Importer

options:
  -h, --help            show this help message and exit
  --protocol PROTOCOL   Protocol (http or https)
  --nc-url NC_URL       Nextcloud URL
  --admin-name ADMIN_NAME
                        Admin username
  --admin-pass ADMIN_PASS
                        Admin password
  --api-url API_URL     API URL
  --users-csv-file USERS_CSV_FILE
                        Path to CSV file
  --groups-csv-file GROUPS_CSV_FILE
                        Path to CSV file
  --dump-users-csv      Dump current users
  --csv-delimiter CSV_DELIMITER
                        CSV delimiter
  --csv-delimiter-groups CSV_DELIMITER_GROUPS
                        CSV delimiter for groups
  --generate-password   Generate random passwords
  --no-ssl-verify       Disable SSL verification
  --language LANGUAGE   User language
  --dry-run             Perform a dry run without creating users
  --password            Update password processing when updating user
```


## Importing Users

If adding users your CSV users file should look like this:

```
username,display_name,password,email,groups,quota
jdoe,John Doe,password123,jdoe@example.com,Users;Marketing,5 GB
asmith,Alice Smith,securepass,asmith@example.com,Users;Engineering,10 GB
```
And can be imported running:

`python3 nextcloud_user_importer.py --nc-url your-nextcloud-url.com --admin-name admin --admin-pass password --users-csv-file users.csv`

If any username in csv exists in nextcloud instance it will be updated 
with the values of the row, with the exception of the password value. 
If you want to update also the password add the argument `--password`.


You can obtain the current users list with the argument `--dump-users-csv`,
this may be useful as a template.

`python3 nextcloud_user_importer.py --nc-url your-nextcloud-url.com --admin-name admin --admin-pass password --dump-users-csv`

**Note about passwords** : Take care that plain password cannot be 
obtained so if importing new users using this dump, password field must be 
changed or use the `--generate-password` to generate a new one automatically.
Otherwise passwords will be set to `*CHANGEME*` value.



## Groups

If adding groups your CSV groups file should look like this:

```
groupid,display_name
users,Users
marketing,Marketing
engineering,Engineering
```

And groups can be imported running:

`python3 nextcloud_user_importer.py --nc-url your-nextcloud-url.com --admin-name admin --admin-pass password --groups-csv-file groups.csv`

