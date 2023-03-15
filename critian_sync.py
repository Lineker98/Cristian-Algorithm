import time
import socket
import subprocess

# Define the IP addresses and port number for the time server and the clients
TIME_SERVER = ('time.nist.gov', 13)
CLIENTS = ['192.168.1.100', '192.168.1.101', '192.168.1.102']

# Define the maximum time difference allowed in seconds
MAX_TIME_DIFFERENCE = 5

def get_time_from_server(server_address):
    """Connects to a time server and returns the current time."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(server_address)
        data = s.recv(1024).decode('utf-8')
        timestamp = int(data[7:17])
        return timestamp - 2208988800

def get_time_from_client(client_address):
    """Connects to a client and returns the current time."""
    cmd = f"ssh {client_address} date +%s"
    output = subprocess.check_output(cmd, shell=True)
    return int(output)

def synchronize_time():
    """Synchronizes the time with the time server and the clients."""
    # Get the time from the time server
    server_time = get_time_from_server(TIME_SERVER)
    local_time = time.time()
    offset = server_time - local_time
    time_diff = abs(offset)
    
    if time_diff > MAX_TIME_DIFFERENCE:
        # If the time difference is too large, don't update the time
        print(f"Time difference between local and server time is too large: {time_diff} seconds")
        return
    
    # Adjust the local time in small increments
    increment = 0.1 if offset > 0 else -0.1
    while abs(offset) > 0.1:
        time.sleep(0.1)
        offset -= increment
    
    # Set the local time to the synchronized time
    new_time = server_time + increment
    print(f"Setting local time to: {time.ctime(new_time)}")
    subprocess.run(f"sudo date -u {new_time}", shell=True)  # Update the system time
    
    # Synchronize the time on the clients
    for client in CLIENTS:
        client_time = get_time_from_client(client)
        client_offset = server_time - client_time
        client_diff = abs(client_offset)
        
        if client_diff > MAX_TIME_DIFFERENCE:
            # If the time difference is too large, don't update the time
            print(f"Time difference between local and client time is too large: {client_diff} seconds")
            continue
        
        # Adjust the client time in small increments
        increment = 0.1 if client_offset > 0 else -0.1
        while abs(client_offset) > 0.1:
            time.sleep(0.1)
            client_offset -= increment
        
        # Set the client time to the synchronized time
        new_time = server_time + increment
        print(f"Setting client time on {client} to: {time.ctime(new_time)}")
        subprocess.run(f"ssh {client} 'sudo date -u {new_time}'", shell=True)  # Update the client time

if __name__ == '__main__':
    synchronize_time()
