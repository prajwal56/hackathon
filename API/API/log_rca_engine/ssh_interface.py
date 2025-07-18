import subprocess
import tempfile
import os
import paramiko


class SSHInterface:
    def __init__(self):
        self.key = ""


    def run_ssh_command(self, host, user, password, commands):
        try:
            import html  # for escaping special HTML characters

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, username=user, password=password)

            full_output = ""
            for command in commands.split("\n"):
                if not command.strip():
                    continue
                stdin, stdout, stderr = client.exec_command(command)
                command_html = f'<span class="ssh-command">$ {html.escape(command)}</span>'
                stdout_html = f'<span class="ssh-stdout">{html.escape(stdout.read().decode())}</span>'
                stderr_html = f'<span class="ssh-stderr">{html.escape(stderr.read().decode())}</span>'
                full_output += f"{command_html}<br>{stdout_html}{stderr_html}<br>"

            return f'<div class="ssh-terminal">{full_output}</div>'
        except Exception as e:
            return f'<div class="ssh-error">❌ SSH Error: {html.escape(str(e))}</div>'

