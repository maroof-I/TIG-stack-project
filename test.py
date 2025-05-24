import subprocess
import csv
import os
import re
import argparse
from dotenv import load_dotenv

load_dotenv()


path_to_file = "data.txt"
telegraf_path = "telegraf.conf"

parser = argparse.ArgumentParser(description="Configure worlkflow for this script")

parser.add_argument("--list", action="store_true", dest="list", default=False, help="list all tokens - True or False(default)")
parser.add_argument("--delete-id", action="store", dest="delete", help="provide token id to delete")
parser.add_argument("--create", action="store_true", dest="create", default=False, help="create new scoped token for org(.env) - True or False(default)")
parser.add_argument("--update-telegraf", action="store_true", dest="update_telegraf", default=False, help="update telegraf config - True or False(default)")

args = parser.parse_args()

def save_result():
    with open(path_to_file, "w") as output_file:
        proce = subprocess.run(["docker", "exec", "-it", "influxdb", "influx", "auth", "list"], text=True, stdout=output_file)

def read_tsv_data():
    with open(path_to_file, 'r') as output_file:
        reader = csv.reader(output_file, delimiter="\t")
        table = list(reader)
    return table

def list_tokens():
    subprocess.run(["docker", "exec", "-it", "influxdb", "influx", "auth", "list"], text=True)

def get_token_id(token_index=1):
    table_data = read_tsv_data(path_to_file)
    token_id = table_data[token_index][0]
    return token_id

def get_token(token_index):
    table_data = read_tsv_data()
    token = table_data[token_index][3]
    return token

def add_to_env_file(key, value):
    with open(".env", "a") as env_file:
        env_file.write(f"{key}={value}\n")

def updating_telegraf_conf(scoped_token):
    print("updating telegraf config...\n")
    with open(telegraf_path, "r+") as telegraf_conf_file:
        config = telegraf_conf_file.read()
        telegraf_conf_file.seek(0)
        config = re.sub(r'token\s*=\s*"(.*)"', r'token = "{}"'.format(scoped_token), config)
        config = re.sub(r'organization\s=\s"(.*)"', r'organization = "{}"'.format(os.getenv("TEST_ORG")), config)
        config = re.sub(r'bucket\s*=\s*"(.*)"', r'bucket = "{}"'.format(os.getenv("TEST_BUCKET")), config)
        telegraf_conf_file.write(config)

def delete_token(token_id):
    try:
        print(f"deleting token id {token_id}...\n")
        subprocess.run(["docker", "exec", "-it", "influxdb", "influx", "auth", "delete","-i", token_id], capture_output=True, text=True)
        print(f"saving result to {path_to_file}...")
        save_result()
        
    except (IndexError) as e:
        print("no token found...")

def create_token():
    print("creating organaization...\n")
    org_name = os.getenv("TEST_ORG")
    token_name = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")
    subprocess.run(["docker", "exec", "-it", "influxdb", "influx", "org", "create", "--name", org_name, "-t", token_name], capture_output=True, text=True)
    
    print("creating bucket...\n")
    bucket_name = os.getenv("TEST_BUCKET")
    subprocess.run(["docker", "exec", "-it", "influxdb", "influx", "bucket", "create", "--name", bucket_name, "--org", org_name], capture_output=True, text=True)
    
    print("creating new scoped token...\n")
    subprocess.run(["docker", "exec", "-it", "influxdb", "influx", "auth", "create", "--org", org_name, "--all-access"], capture_output=True, text=True)
    
    print(f"saving result to {path_to_file}...\n")
    save_result()

    print("copying scoped token [second token in your list] to .env file...\n")
    token = get_token(token_index=2)
    add_to_env_file(key="SCOPED_TOKEN", value=token)


if __name__ == "__main__":
    if args.list:
        list_tokens()
        
    if args.delete != None:
        token_id = args.delete
        delete_token(token_id)
        
    if args.create:
        create_token()
        
    if args.update_telegraf:
        scoped_token = os.getenv("SCOPED_TOKEN")
        updating_telegraf_conf(scoped_token)


# print("configuring terminal credentials...\n")
# org_name = os.getenv("ORG_NAME")
# admin = os.getenv("ADMIN")
# password = os.getenv("PASSWORD")
# proce_config = subprocess.run(["docker", "exec", "-it", "influxdb", "influx", "config", "create", "-n", "my-config", "-u", "http://localhost:8086","-o", org_name, "-p", f"{admin}:{password}"], capture_output=True, text=True)
