import socket
import datetime

def send_request(server_ip, server_port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        
        command = input("Enter 'TIME' to request current time, or 'QUIT' to exit: ").strip().upper()
        
        if command not in ["TIME", "QUIT"]:
            print("Invalid command. Please enter 'TIME' or 'QUIT'.")
            return
        
        client_socket.sendall(f"{command}\r\n".encode('utf-8'))
        
        response = client_socket.recv(1024).decode('utf-8').strip()
        
        if command == "TIME":
            print(f"Server response (TIME): {response}")
        elif command == "QUIT":
            print("Quit request sent to server.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()
        print("Connection closed.")

def main():
    SERVER_IP = '172.16.16.102'
    SERVER_PORT = 45000
    
    while True:
        send_request(SERVER_IP, SERVER_PORT)
        if input("Do you want to send another request? (y/n): ").strip().lower() != 'y':
            break

if __name__ == "__main__":
    main()

