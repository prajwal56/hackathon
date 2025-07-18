from .serializers import EventSerializer
from .models import Event
from API.log_rca_engine.ai_engine import AIEngine
from API.log_rca_engine.ssh_interface import SSHInterface
from datetime import datetime
from zoneinfo import ZoneInfo 
class EventController:
    """
    Handles business logic for Event operations.
    """
    ai_engine = AIEngine()
    ssh_interface = SSHInterface()
    @staticmethod
    def create_event(request):
        """
        Validates and creates a new Event document.
        """
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            event = serializer.save()
            return EventSerializer(event).data
        
    @staticmethod
    def get_event_list(request):
        """
        Retrieves a list of all Event documents with created_at converted to IST and formatted.
        """
        events = Event.objects.all()
        data = EventSerializer(events, many=True).data

        for i in data:
            time = i.get("created_at")
            if time:
                # Parse string in UTC
                dt = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')
                dt = dt.replace(tzinfo=ZoneInfo('UTC'))

                # Convert to IST
                ist_time = dt.astimezone(ZoneInfo('Asia/Kolkata'))

                # Format
                formatted = ist_time.strftime('%d-%m-%Y %I:%M:%S %p')
                i['created_at'] = formatted

        return data

    @staticmethod
    def get_event_rca(request):
        """
        Retrieves a list of all Event documents.
        """ 
        data = request.data
        RCA_data = EventController.ai_engine.generate_prompt(str(data))
        return RCA_data
    
    
    def executeCommands(request):
        """
        Executes the commands from the request data.
        """
        try:
            data = request.data
            commands = data.get("commands", [])
            single_string_command = "\n".join(commands)
            host = data.get("ip", "")
            username = data.get("username", "")
            password = data.get("password", "")
            res_data = EventController.ssh_interface.run_ssh_command(host,username,password,single_string_command)
            if res_data:
                return res_data
        except Exception as e:
                return {"error": str(e)}
            
            
    @staticmethod
    def generate_event(request):
        service = request.data.get('service')
        event = request.data.get('event')

        if not service or not event:
            raise Exception('Service and event are required.')

        # SSH connection details
        hostname = request.data.get('hostname')
        username = request.data.get('username')
        password = request.data.get('password')


        # Select script path based on event
        if event == 'unknown directive':
            script_path = '/data/scripts/nginx/unknown_directive.sh'
        elif event == 'invalid nginx_port':
            script_path = '/data/scripts/nginx/invalid_nginx_port.sh'
        elif event == 'foreign key violation_test':
            script_path = '/data/scripts/postgresql/foreign_key_violation_test.sh'
        elif event == 'generate pg errors':
            script_path = '/data/scripts/postgresql/generate_pg_errors.sh'
        elif event == 'max connection':
            script_path = '/data/scripts/postgresql/max_connection.sh'
        elif event == 'simulate deadlock':
            script_path = '/data/scripts/postgresql/simulate_deadlock.sh'
        elif event == 'unique violation test':
            script_path = '/data/scripts/postgresql/unique_violation_test.sh'
        elif event == 'simulate redis permission error':
            script_path = '/data/scripts/redis/simulate_redis_permission_error.sh'
        else:
            return {'message': f"No script defined for event: {event}"}

        # Connect via SSH and execute
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname, username=username, password=password)

            stdin, stdout, stderr = ssh.exec_command(f'bash {script_path}')
            output = stdout.read().decode()
            error = stderr.read().decode()

            ssh.close()

            # if error:
            #     raise Exception(f"Script Error: {error}")

            return {'message': output}

        except Exception as e:
            raise Exception(f"SSH Connection or Execution Failed: {str(e)}")
    
    
        
        