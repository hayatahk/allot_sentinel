import os
import sys
import paramiko
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def block_url(url):
    # Retrieve and validate environment variables
    ip = os.getenv('IP')
    port = int(os.getenv('PORT', 22))
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    cli_path = os.getenv('CLI_PATH')
    
    if not all([ip, port, username, password, cli_path]):
        logging.error("Error: One or more environment variables are missing.")
        sys.exit(1)

    # Check if URL argument is provided
    if not url:
        logging.error("Error: The URL argument is empty.")
        sys.exit(1)

    # Sanitize URL to prevent command injection
    url = url.replace(';', '').replace('&', '').strip()

    # Establish an SSH client
    client = paramiko.SSHClient()
    # Automatically add host keys from the local HostKeys object
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the host
        logging.info(f"Connecting to {ip}:{port} as {username}...")
        client.connect(hostname=ip, port=port, username=username, password=password)
        logging.info("Connection established successfully.")

        # Construct the command
        command = f'echo {url} > /tmp/addnewurl.tmp && cd {cli_path} && ./ConfigurationCLI.sh ' \
                  f'-loadWebSafeImportFile -filename /tmp/addnewurl.tmp ' \
                  f'-isSaveWS true -listType BLACK_LIST -filter Default -saveMode "append"'

        # Execute the command
        logging.info("Executing command...")
        stdin, stdout, stderr = client.exec_command(command)

        # Print the command's output
        output = stdout.read().decode()
        logging.info(f"Output: {output}")

        # Print any errors
        error = stderr.read().decode()
        if error:
            logging.error(f"Error: {error}")
    except paramiko.AuthenticationException:
        logging.error("Error: Authentication failed.")
    except paramiko.SSHException as ssh_exception:
        logging.error(f"Error: SSH connection failed: {ssh_exception}")
    except Exception as e:
        logging.error(f"Error: An unexpected error occurred: {e}")
    finally:
        # Close the SSH connection
        client.close()
        logging.info("SSH connection closed.")

def get_url(url):
    # Retrieve and validate environment variables
    ip = os.getenv('IP')
    port = int(os.getenv('PORT', 22))
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    
    if not all([ip, port, username, password]):
        logging.error("Error: One or more environment variables are missing.")
        sys.exit(1)

    # Check if URL argument is provided
    if not url:
        logging.error("Error: The URL argument is empty.")
        sys.exit(1)

    # Sanitize URL to prevent command injection
    url = url.replace(';', '').replace('&', '').strip()

    # Establish an SSH client
    client = paramiko.SSHClient()
    # Automatically add host keys from the local HostKeys object
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the host
        logging.info(f"Connecting to {ip}:{port} as {username}...")
        client.connect(hostname=ip, port=port, username=username, password=password)
        logging.info("Connection established successfully.")

        # Construct the command to search for the URL
        command = f'cat /opt/sybase/data/nx/webSafe/Default/operator_bl.url | grep {url}'

        # Execute the command
        logging.info("Executing search command...")
        stdin, stdout, stderr = client.exec_command(command)

        # Print the search result
        output = stdout.read().decode()
        if output:
            logging.info(f"Search Result: {output}")
        else:
            logging.info(f"No matches found for URL: {url}")

        # Print any errors
        error = stderr.read().decode()
        if error:
            logging.error(f"Error: {error}")
    except paramiko.AuthenticationException:
        logging.error("Error: Authentication failed.")
    except paramiko.SSHException as ssh_exception:
        logging.error(f"Error: SSH connection failed: {ssh_exception}")
    except Exception as e:
        logging.error(f"Error: An unexpected error occurred: {e}")
    finally:
        # Close the SSH connection
        client.close()
        logging.info("SSH connection closed.")

if __name__ == "__main__":
    # Check if the required arguments are passed
    if len(sys.argv) < 3:
        logging.error("Usage: python script.py <action> <URL>")
        sys.exit(1)

    # Get the action and URL from the command-line arguments
    action = sys.argv[1].lower()
    url = sys.argv[2]

    # Perform the appropriate action
    if action == '-block':
        block_url(url)
    elif action == '-get':
        get_url(url)
    else:
        logging.error("Invalid action specified. Use '-block' to block a URL or '-get' to search for a URL.")
        sys.exit(1)
