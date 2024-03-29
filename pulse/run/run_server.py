import subprocess

def server(file_name: str) -> int:
    try:
        if '.pods' in file_name:
            print(f"Running the open.mp server with pods!")
        else:
            print(f"Running the open.mp server with pulse!")

        server_arguments = ['-c', 'config.json']
        server_command = [file_name] + server_arguments
        
        subprocess.run(server_command)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")