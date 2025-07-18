import subprocess
import tempfile
import os
import paramiko


class SSHInterface:
    def __init__(self):
        self.key = ""


    def run_ssh_command(self, host, user, password, commands):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, username=user, password=password)

            full_output = ""
            for command in commands.split("\n"):
                if not command.strip():
                    continue
                stdin, stdout, stderr = client.exec_command(command)
                full_output += f"$ {command}\n{stdout.read().decode()}{stderr.read().decode()}\n"

            client.close()
            return full_output
        except Exception as e:
            return f"❌ SSH Error: {e}"
