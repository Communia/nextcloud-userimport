# Perform nextcloud provision tasks from a CSV file

Credit to [t-markmann](https://github.com/t-markmann/nc-userimporter) for inspiration.

It helps you provisioning users, groups from csv, or helping in some other provisioning tasks
such as dumping the current users, or showing the nextcloud mail app command to create mail 
accounts for mail client app.

Quick Usage:

```
python3 nextcloud_user_importer.py users -nc-url your-nextcloud-url.com --admin-name admin --admin-pass password --csv-file users.csv
```

For help:

```
python3 nextcloud_user_importer.py {command} --help
```

Where commands are users, groups, dump, and mail-app.

# Users

```
usage: nextcloud_user_importer.py users [-h] [--users-csv-file USERS_CSV_FILE] [--protocol {http,https}] --nc-url NC_URL --admin-name ADMIN_NAME --admin-pass ADMIN_PASS [--api-url API_URL] [--csv-delimiter CSV_DELIMITER] [--csv-delimiter-groups CSV_DELIMITER_GROUPS]
                                        [--generate-password] [--no-ssl-verify] [--language LANGUAGE] [--dry-run] [--password]

options:
  -h, --help            show this help message and exit
  --users-csv-file USERS_CSV_FILE
                        Path to CSV file
  --protocol {http,https}
                        Protocol (http or https)
  --nc-url NC_URL       Nextcloud URL
  --admin-name ADMIN_NAME
                        Admin username
  --admin-pass ADMIN_PASS
                        Admin password
  --api-url API_URL     API URL
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

If you want to add users, your CSV users file should look like this:

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
this may be useful as a template. (more information on dump section below).

`python3 nextcloud_user_importer.py dump --nc-url your-nextcloud-url.com --admin-name admin --admin-pass password --dump-users-csv`



**Note about passwords** : Take care that plain password cannot be
obtained so if importing new users using this dump, password field in csv must
be changed or use the `--generate-password` to generate a new one
automatically. Otherwise passwords will be set to `*CHANGEME*` value.


# Groups

```
usage: nextcloud_user_importer.py groups [-h] [--groups-csv-file GROUPS_CSV_FILE] [--protocol {http,https}] --nc-url NC_URL --admin-name ADMIN_NAME --admin-pass ADMIN_PASS [--api-url API_URL] [--csv-delimiter CSV_DELIMITER] [--no-ssl-verify] [--dry-run]

options:
  -h, --help            show this help message and exit
  --groups-csv-file GROUPS_CSV_FILE
                        Path to CSV file
  --protocol {http,https}
                        Protocol (http or https)
  --nc-url NC_URL       Nextcloud URL
  --admin-name ADMIN_NAME
                        Admin username
  --admin-pass ADMIN_PASS
                        Admin password
  --api-url API_URL     API URL
  --csv-delimiter CSV_DELIMITER
                        CSV delimiter
  --no-ssl-verify       Disable SSL verification
  --dry-run             Perform a dry run without creating groups
```


## Importing groups

If you wnat to add groups your CSV groups file should look like this:

```
groupid,display_name
users,Users
marketing,Marketing
engineering,Engineering
```

And groups can be imported running:

`python3 nextcloud_user_importer.py groups --nc-url your-nextcloud-url.com --admin-name admin --admin-pass password --groups-csv-file groups.csv`


# Dump

It is useful to obtain a list of current users, this csv could be used also as
a template to be used for importing users with the `users` command (check above
for notes).

```
usage: nextcloud_user_importer.py dump [-h] [--protocol {http,https}] --nc-url NC_URL --admin-name ADMIN_NAME --admin-pass ADMIN_PASS [--api-url API_URL] [--csv-delimiter CSV_DELIMITER] [--no-ssl-verify] [--dry-run]

options:
  -h, --help            show this help message and exit
  --protocol {http,https}
                        Protocol (http or https)
  --nc-url NC_URL       Nextcloud URL
  --admin-name ADMIN_NAME
                        Admin username
  --admin-pass ADMIN_PASS
                        Admin password
  --api-url API_URL     API URL
  --csv-delimiter CSV_DELIMITER
                        CSV delimiter
  --no-ssl-verify       Disable SSL verification
  --dry-run             Perform a dry run without creating dump
```


# Mail app

This action will not perform any action, isntead will show the command to be run
on the server, right now there's no api endpoint to create mail app accounts.

```
usage: nextcloud_user_importer.py mail-app [-h] --mail-csv-file MAIL_CSV_FILE [--generate-password] [--csv-delimiter CSV_DELIMITER] --imap-host IMAP_HOST --imap-port IMAP_PORT --imap-ssl-mode {ssl,tls,none} --smtp-host SMTP_HOST --smtp-port SMTP_PORT --smtp-ssl-mode
                                           {ssl,tls,none} [--auth-method {password,xoauth2}] [--occ-out] [--ldiff-out] [--ldiff-template LDIFF_TEMPLATE]

options:
  -h, --help            show this help message and exit
  --mail-csv-file MAIL_CSV_FILE
                        Path to CSV file as in users csv to out occ script to be run in server
  --generate-password   Generate random passwords
  --csv-delimiter CSV_DELIMITER
                        CSV delimiter
  --imap-host IMAP_HOST
  --imap-port IMAP_PORT
  --imap-ssl-mode {ssl,tls,none}
  --smtp-host SMTP_HOST
  --smtp-port SMTP_PORT
  --smtp-ssl-mode {ssl,tls,none}
  --auth-method {password,xoauth2}
  --occ-out             Output the occ command for each user
  --ldiff-out           Output the ldiff out for each user (Needs --ldiff-template argument)
  --ldiff-template LDIFF_TEMPLATE
                        Path to the file to be used as ldiff template (Needs --ldiff-out flag)

```

## Creating mail accounts

Based on the same csv structure as users command, an example could be this users.csv:

```
username,display_name,password,email,groups,quota
bob,Robert Wang,,bob@example.com,devs,5 GB
```

run suited to your needs

```
$ python nextcloud_user_importer.py mail-app --mail-csv-file users.csv --imap-host mails.example.com --imap-port 993  --imap-ssl-mode ssl --smtp-host mails.example.com --smtp-port 465 --smtp-ssl-mode ssl --occ-out
occ mail:account:create bob bob bob@example.com mails.example.com 993 ssl bob@example.com  mails.example.com 465 ssl bob@example.com  password
```

Copy the output (`occ mail:account:create ...` ). Login to your server, go to nextcloud directory. and paste the
the commands.

Optionally it could also output the ldiff file for openldap needed scenarios. Then the options
`--ldiff-out` together with `--ldiff-template {file.tpl}` must be added. You can take the ldiff_template.tpl
as starting example. The template may use these variables: 

```
${username}
${email}
${imap_host}
${imap_port}
${imap_ssl_mode} :  ssl,tls or none.
${password} : raw password.
${smtp_host}
${smtp_port}
${smtp_ssl_mode} : ssl,tls or none.
${auth_method} : auth method used by nextcloud mail app.
${password_hash} : password hash
```
