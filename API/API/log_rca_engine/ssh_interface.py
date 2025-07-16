import subprocess
import tempfile
import os

class SSHInterface:
    def __init__(self):
        self.key = ""


    def run_ansible_commands_dynamic(self, commands: str, host: str, user: str, password: str):
        try:
            # Create dynamic inventory
            inventory_content = f"""
    [all]
    {host} ansible_user={user} ansible_ssh_pass={password} ansible_become_pass={password}

    [all:vars]
    ansible_python_interpreter=/usr/bin/python3
    """

            with tempfile.NamedTemporaryFile("w", delete=False) as temp_inventory:
                temp_inventory.write(inventory_content)
                inventory_path = temp_inventory.name

            # Create playbook
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yml") as temp_playbook:
                playbook_content = f"""
    - name: Run remote shell commands
    hosts: all
    become: yes
    tasks:
        - name: Run shell commands
        shell: |
            {commands}
        args:
            executable: /bin/bash
    """
                temp_playbook.write(playbook_content)
                playbook_path = temp_playbook.name

            # Execute playbook
            result = subprocess.run(
                ["ansible-playbook", "-i", inventory_path, playbook_path],
                capture_output=True, text=True
            )

            # Clean up
            os.remove(playbook_path)
            os.remove(inventory_path)

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "status": "success" if result.returncode == 0 else "error",
                "returncode": result.returncode
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}
