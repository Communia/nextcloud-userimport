#!/usr/bin/env python3
import os
import sys
import csv
import html
import random
import string
import requests
import argparse
from tabulate import tabulate
from string import Template
import base64
import hashlib

def generate_password():
    return ''.join(random.choices(string.digits, k=10))

def create_user(config, user_data):
    config.api_url = '/ocs/v1.php/cloud/users'
    url = f"{config.protocol}://{config.admin_name}:{config.admin_pass}@{config.nc_url}{config.api_url}"
    data = {
        'userid': user_data['username'],
        'displayName': user_data['display_name'],
        'password': user_data['password'],
        'email': user_data['email'],
        'quota': user_data['quota'],
        'language': config.language
    }
    for group in user_data['groups']:
        data[f'groups[]'] = group

    response = requests.post(url, headers={'OCS-APIRequest': 'true', 'Accept': 'application/json'}, data=data, verify=config.ssl_verify)
    return response

def update_user(config, user_data):
    config.api_url = '/ocs/v1.php/cloud/users/' + user_data['username']
    url = f"{config.protocol}://{config.admin_name}:{config.admin_pass}@{config.nc_url}{config.api_url}"
    data = {    
        'displayname': user_data['display_name'],
        'password': user_data['password'],
        'email': user_data['email'],
        'quota': user_data['quota'],
    }
    responses = []
    for key in data:
        if (key == 'password' and not config.password ):
            print("Password not updated")
            continue
        print("Updating:" + key)
        response =requests.put(url, headers={'OCS-APIRequest': 'true', 'Accept': 'application/json'}, data={'key' : key, 'value' : data[key]}, verify=config.ssl_verify)
        print(f"User update {user_data['username']}: {response.status_code} - {response.text}")
    
    current_groups = user_get_groups(config,user_data['username'])
    print("  Reassigning groups, first deleting current ones")
    user_clear_groups(config, user_data['username'],current_groups)
    print("  Adding new groups")
    user_add_groups(config, user_data['username'], user_data['groups'])

    return responses


# @todo use this when nextcloud 34
def update_bad_user(config, user_data):
    config.api_url = '/ocs/v2.php/cloud/users/' + user_data['username'] + '/additional_email'
    url = f"{config.protocol}://{config.admin_name}:{config.admin_pass}@{config.nc_url}{config.api_url}"
    data = {
        'displayName': user_data['display_name'],
        'password': user_data['password'],
        'email': user_data['email'],
        'quota': user_data['quota'],
        'language': config.language
    }
    for group in user_data['groups']:
        data[f'groups[]'] = group

    print('updating')
    print(url)
    print(data)
    response = requests.put(url, headers={'XDEBUG_SESSION': 'local_ide' ,'OCS-APIRequest': 'true', 'Accept': 'application/json'}, data=data, verify=config.ssl_verify)
    print(response.content)
    return response



def create_group(config, group_data):
    #config.api_url = '/ocs/v1.php/cloud/groups'
    url = f"{config.protocol}://{config.admin_name}:{config.admin_pass}@{config.nc_url}{config.api_url}"
    data = {
        'groupid': group_data['groupid'],
        'displayName': group_data['display_name']
    }

    response = requests.post(url, headers={'OCS-APIRequest': 'true'}, data=data, verify=config.ssl_verify)
    return response

def user_get_groups(config, username):
    config.api_url = '/ocs/v1.php/cloud/users/' + username + '/groups'
    url = f"{config.protocol}://{config.admin_name}:{config.admin_pass}@{config.nc_url}{config.api_url}"
    response = requests.get(url, headers={'OCS-APIRequest': 'true', 'Accept': 'application/json'}, verify=config.ssl_verify)
    if response.json()['ocs']['data'] and response.json()['ocs']['data']['groups']:
        return response.json()['ocs']['data']['groups']
    else:
        return []

def user_clear_groups(config, username, groups):
    config.api_url = '/ocs/v1.php/cloud/users/' + username + '/groups'
    url = f"{config.protocol}://{config.admin_name}:{config.admin_pass}@{config.nc_url}{config.api_url}"
    responses = []
    for group in groups:
        response = requests.delete(url, headers={'OCS-APIRequest': 'true', 'Accept': 'application/json'}, data={'groupid': group }, verify=config.ssl_verify)
        print(f"  User clear group {group} {username}: {response.status_code} - {response.text}")
        responses.append(response)
    return responses

def user_add_groups(config, username, groups):
    config.api_url = '/ocs/v1.php/cloud/users/' + username + '/groups'
    url = f"{config.protocol}://{config.admin_name}:{config.admin_pass}@{config.nc_url}{config.api_url}"
    responses = []
    for group in groups:
        print(f"  Add {username} to {group}")
        response = requests.post(url, headers={'OCS-APIRequest': 'true', 'Accept': 'application/json'}, data={'groupid': group }, verify=config.ssl_verify)
        print(f"  User add group {group} {username}: {response.status_code} - {response.text}")
        responses.append(response)
    return responses

def get_users(config):
    config.api_url = '/ocs/v1.php/cloud/users/details'
    url = f"{config.protocol}://{config.admin_name}:{config.admin_pass}@{config.nc_url}{config.api_url}"
    response = requests.get(url, headers={'OCS-APIRequest': 'true', 'Accept': 'application/json'}, verify=config.ssl_verify)
    writer = csv.writer(sys.stdout, lineterminator=os.linesep)
    writer.writerow(['username', 'display_name', 'password', 'email', 'groups', 'quota'])

    if response.json()['ocs']['data'] and response.json()['ocs']['data']['users']:
        users = response.json()['ocs']['data']['users']
        writer.writerows([[u, users[u]['displayname'], '*CHANGEME*', users[u]['email'], ",".join(users[u]['groups']), users[u]['quota']['total']] for u in users])

def generate_ssha(password: str) -> str:
    salt = os.urandom(4)
    sha1 = hashlib.sha1(password.encode("utf-8"))
    sha1.update(salt)
    digest = sha1.digest()
    encoded = base64.b64encode(digest + salt).decode("utf-8")
    return f"{{SSHA}}{encoded}=="

def main(args):
    if hasattr(args, 'users_csv_file'):
        users = []
        with open(args.users_csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=args.csv_delimiter)
            for row in reader:
                user = {
                    'username': html.escape(row['username']),
                    'display_name': html.escape(row['display_name']),
                    'password': generate_password() if args.generate_password else html.escape(row['password']),
                    'email': html.escape(row['email']),
                    'groups': html.escape(row['groups']).split(args.csv_delimiter_groups),
                    'quota': html.escape(row['quota'])
                }
                users.append(user)

        print(tabulate([[u['username'], u['display_name'], '*' * len(u['password']), u['email'], u['groups'], u['quota']] for u in users],
                       headers=['Username', 'Display Name', 'Password', 'Email', 'Groups', 'Quota']))

        if not args.dry_run:
            input("\nPress Enter to continue with user creation or Ctrl+C to abort...")

            for user in users:
                response = create_user(args, user)
                print(response.json()['ocs']['meta']['statuscode'])
                print(f"User {user['username']}: {response.status_code} - {response.text}")
                #Already exists:
                if response.json()['ocs']['meta']['statuscode'] == 102:
                    print("Already there, updating")
                    update_user(args,user)

        else:
            print("\nDry run completed. No users were created.")
    if hasattr(args, 'groups_csv_file'):
        groups = []
        with open(args.groups_csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=args.csv_delimiter)
            for row in reader:
                group = {
                    'groupid': html.escape(row['username']),
                    'display_name': html.escape(row['display_name'])
                }
                groups.append(group)

        print(tabulate([[u['groupid'], u['display_name']] for g in groups],
                       headers=['Group id', 'Display Name']))

        if not args.dry_run:
            input("\nPress Enter to continue with group creation or Ctrl+C to abort...")

            for group in groups:
                response = create_group(args, group)
                print(f"Group {group['groupid']}: {response.status_code} - {response.text}")
        else:
            print("\nDry run completed. No users were created.")
    if hasattr(args, 'dump_users_csv'):
        get_users(args)
    if hasattr(args, 'mail_csv_file'):
        users = []
        with open(args.mail_csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=args.csv_delimiter)
            for row in reader:
                user = {
                    'username': html.escape(row['username']),
                    'display_name': html.escape(row['display_name']),
                    'password': generate_password() if args.generate_password else html.escape(row['password']),
                    'email': html.escape(row['email'])
                }
                users.append(user)
        if (args.occ_out):
            for user in users:
                print('occ mail:account:create {user_id} {name} {email} {imap_host} {imap_port} {imap_ssl_mode} {imap_user} {imap_password} {smtp_host} {smtp_port} {smtp_ssl_mode} {smtp_user} {smtp_password} {auth_method}'.format(
                    user_id = user['username'],
                    name = user['username'],
                    email = user['email'],
                    imap_host = args.imap_host,
                    imap_port = args.imap_port,
                    imap_ssl_mode = args.imap_ssl_mode,
                    imap_user = user['email'],
                    imap_password = user['password'],
                    smtp_host = args.smtp_host,
                    smtp_port = args.smtp_port,
                    smtp_ssl_mode = args.smtp_ssl_mode,
                    smtp_user = user['email'],
                    smtp_password = user['password'],
                    auth_method = args.auth_method
                ))
        if (args.ldiff_out and args.ldiff_template):
            with open(args.ldiff_template, 'r') as file:
                template_string = file.read()
            template = Template(template_string)
            for user in users:
                password_hash = generate_ssha(user['password'])
                result = template.substitute(
                    username = user['username'],
                    display_name = user['display_name'],
                    email = user['email'],
                    imap_host = args.imap_host,
                    imap_port = args.imap_port,
                    imap_ssl_mode = args.imap_ssl_mode,
                    password = user['password'],
                    smtp_host = args.smtp_host,
                    smtp_port = args.smtp_port,
                    smtp_ssl_mode = args.smtp_ssl_mode,
                    auth_method = args.auth_method,
                    password_hash = password_hash
                )

                print(result)

 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nextcloud User Importer")
    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands', help='additional subcommands')
    mail_app_parser = subparsers.add_parser('mail-app')
    mail_app_parser.add_argument('--mail-csv-file', required=True, help="Path to CSV file as in users csv to out occ script to be run in server")
    mail_app_parser.add_argument("--generate-password", action="store_true", help="Generate random passwords")
    mail_app_parser.add_argument("--csv-delimiter", default=",", help="CSV delimiter")
    mail_app_parser.add_argument('--imap-host', required=True)
    mail_app_parser.add_argument('--imap-port', required=True)
    mail_app_parser.add_argument('--imap-ssl-mode', required=True, choices=["ssl", "tls", "none"])
    mail_app_parser.add_argument('--smtp-host', required=True)
    mail_app_parser.add_argument('--smtp-port', required=True)
    mail_app_parser.add_argument('--smtp-ssl-mode', required=True, choices=["ssl", "tls", "none"])
    mail_app_parser.add_argument('--auth-method', default="password", choices=["password", "xoauth2"])
    mail_app_parser.add_argument('--occ-out', action='store_true', help="Output the occ command for each user")
    mail_app_parser.add_argument('--ldiff-out', action='store_true', help="Output the ldiff out for each user (Needs --ldiff-template argument)")
    mail_app_parser.add_argument('--ldiff-template', help="Path to the file to be used as ldiff template (Needs --ldiff-out flag)")


    users_parser = subparsers.add_parser('users')
    users_parser.add_argument("--users-csv-file", help="Path to CSV file")
    users_parser.add_argument("--protocol", default="https", help="Protocol (http or https)", choices=["http", "https"])
    users_parser.add_argument("--nc-url", required=True, help="Nextcloud URL")
    users_parser.add_argument("--admin-name", required=True, help="Admin username")
    users_parser.add_argument("--admin-pass", required=True, help="Admin password")
    users_parser.add_argument("--api-url", default="/ocs/v1.php/cloud/users", help="API URL")
    users_parser.add_argument("--csv-delimiter", default=",", help="CSV delimiter")
    users_parser.add_argument("--csv-delimiter-groups", default=";", help="CSV delimiter for groups")
    users_parser.add_argument("--generate-password", action="store_true", help="Generate random passwords")
    users_parser.add_argument("--no-ssl-verify", action="store_false", dest="ssl_verify", help="Disable SSL verification")
    users_parser.add_argument("--language", default="en", help="User language")
    users_parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without creating users")
    users_parser.add_argument("--password", action="store_true", help="Update password processing when updating user")

    groups_parser = subparsers.add_parser('groups')
    groups_parser.add_argument("--groups-csv-file", help="Path to CSV file")
    groups_parser.add_argument("--protocol", default="https", help="Protocol (http or https)", choices=["http", "https"])
    groups_parser.add_argument("--nc-url", required=True, help="Nextcloud URL")
    groups_parser.add_argument("--admin-name", required=True, help="Admin username")
    groups_parser.add_argument("--admin-pass", required=True, help="Admin password")
    groups_parser.add_argument("--api-url", default="/ocs/v1.php/cloud/groups", help="API URL")
    groups_parser.add_argument("--csv-delimiter", default=",", help="CSV delimiter")
    groups_parser.add_argument("--no-ssl-verify", action="store_false", dest="ssl_verify", help="Disable SSL verification")
    groups_parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without creating groups")


    dump_parser = subparsers.add_parser('dump')
    dump_parser.add_argument("--protocol", default="https", help="Protocol (http or https)", choices=["http", "https"])
    dump_parser.add_argument("--nc-url", required=True, help="Nextcloud URL")
    dump_parser.add_argument("--admin-name", required=True, help="Admin username")
    dump_parser.add_argument("--admin-pass", required=True, help="Admin password")
    dump_parser.add_argument("--api-url", default="/ocs/v1.php/cloud/users/details", help="API URL")
    dump_parser.add_argument("--csv-delimiter", default=",", help="CSV delimiter")
    dump_parser.add_argument("--no-ssl-verify", action="store_false", dest="ssl_verify", help="Disable SSL verification")
    dump_parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without creating dump")




    args = parser.parse_args()
    
    main(args)

