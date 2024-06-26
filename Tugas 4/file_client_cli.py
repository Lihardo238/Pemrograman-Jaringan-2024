import socket
import json
import base64
import logging

# Server address
server_address = ('127.0.0.1', 3000)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"Connecting to {server_address}")
    try:
        logging.warning("Sending message")
        sock.sendall((command_str + "\r\n\r\n").encode())
        data_received = ""
        while True:
            data = sock.recv(1024)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        logging.warning(f"Raw data received: {data_received}")
        result = json.loads(data_received.strip())
        logging.warning("Data received from server:")
        return result
    except json.JSONDecodeError as e:
        logging.warning(f"Error during JSON decoding: {e}")
        logging.warning(f"Raw data received: {data_received}")
        return None
    except Exception as e:
        logging.warning(f"Error during data receiving: {e}")
        return None
    finally:
        sock.close()

def list_files():
    command_str = "LIST"
    result = send_command(command_str)
    if result and result['status'] == 'OK':
        print("File list:")
        for filename in result['data']:
            print(f"- {filename}")
        return True
    else:
        print("Failed to retrieve file list")
        return False

def get_file(filename=""):
    command_str = f"GET {filename}"
    result = send_command(command_str)
    if result and result['status'] == 'OK':
        file_name = result['data_namafile']
        file_content = base64.b64decode(result['data_file'])
        with open(file_name, 'wb+') as fp:
            fp.write(file_content)
        print(f"File {filename} retrieved successfully.")
        return True
    else:
        print("Failed to retrieve file")
        return False

def upload_file(filepath=""):
    try:
        with open(filepath, 'rb') as fp:
            file_data = base64.b64encode(fp.read()).decode()
        filename = filepath.split('/')[-1]
        command_str = f"UPLOAD {filename} {file_data}"
        logging.warning(f"Command to be sent: {command_str[:100]}...")  # Log only first 100 characters for brevity
        result = send_command(command_str)
        if result and result['status'] == 'OK':
            print(f"File {filename} uploaded successfully.")
            return True
        else:
            print("Failed to upload file")
            return False
    except FileNotFoundError:
        print("File not found")
        return False

def delete_file(filename=""):
    command_str = f"DELETE {filename}"
    result = send_command(command_str)
    if result and result['status'] == 'OK':
        print(f"File {filename} deleted successfully.")
        return True
    else:
        print("Failed to delete file")
        return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    server_address = ('127.0.0.1', 3000)

    while True:
        print("\nOptions:")
        print("1. List files")
        print("2. Get file")
        print("3. Upload file")
        print("4. Delete file")
        print("5. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            list_files()
        elif choice == '2':
            filename = input("Enter the filename to retrieve: ")
            get_file(filename)
        elif choice == '3':
            filepath = input("Enter the full path of the file to upload: ")
            upload_file(filepath)
        elif choice == '4':
            filename = input("Enter the filename to delete: ")
            delete_file(filename)
        elif choice == '5':
            break
        else:
            print("Invalid choice, please try again.")
