import subprocess
import time


def wait_postgres(host: str, max_retries: int = 5, delay: int = 5) -> bool:
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                ["pg_isready", "-h", host],
                check=True,
                capture_output=True,
                text=True
            )
            if "accepting connections" in result.stdout:
                print("Successfully connected to PostgreSQL")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error on connecting to PostgreSQL: {e}")
            retries+=1
            time.sleep(delay)
    return False


if not wait_postgres('source_postgres'): exit(1)

source_config = {
    'dbname': 'source_db',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'source_postgres'
}

destination_config = {
    'dbname': 'destination_db',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'destination_postgres'
}

dump_command = [
    'pg_dump', 
    '-h', source_config['host'],
    '-U', source_config['user'],
    '-d', source_config['dbname'],
    '-f', 'data_dump.sql',
    '-w'
]

load_command = [
    'psql', 
    '-h', destination_config['host'],
    '-U', destination_config['user'],
    '-d', destination_config['dbname'],
    '-a', '-f', 'data_dump.sql'
]

subprocess_env = dict(PGPASSWORD=source_config['password'])
subprocess.run(dump_command, env=subprocess_env, check=True)

subprocess_env = dict(PGPASSWORD=destination_config['password'])
subprocess.run(load_command, env=subprocess_env, check=True)