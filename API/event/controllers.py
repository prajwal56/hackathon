from .serializers import EventSerializer
from .models import Event
from API.log_rca_engine.ai_engine import AIEngine
from API.log_rca_engine.ssh_interface import SSHInterface
from datetime import datetime
from zoneinfo import ZoneInfo 
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
from collections import Counter
import paramiko
import uuid

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
        data = request.data.copy()  # Ensure mutable
        data['event_id'] = str(uuid.uuid4())

        serializer = EventSerializer(data=data)
        if serializer.is_valid():
            event = serializer.save()
            return {"message": "Event created successfully", "event_id": event.event_id}
        else:
            return {"error": serializer.errors}
            
        
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
        RCA_data = EventController.ai_engine.analyze_error(str(data))
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
        elif event == 'invalid nginx port':
            script_path = '/data/scripts/nginx/invalid_nginx_unchange.sh'
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
    
    
    def get_5min_bucket(dt_str):
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))  # Ensure UTC parsing
        # Round down to nearest 5 minutes
        minute = (dt.minute // 5) * 5
        bucket = dt.replace(minute=minute, second=0, microsecond=0)
        return bucket.isoformat() + 'Z'

    def transform_events_to_5min_summary(events):
        
        events = Event.objects.all()
        events = list(EventSerializer(events, many=True).data)
        grouped = defaultdict(lambda: {"count": 0, "titles": set()})

        for event in events:
            severity = event.get('severity', 'Unknown').capitalize()
            created_at = event.get('created_at', {})
            if not created_at:
                continue

            time_bucket = EventController.get_5min_bucket(created_at)
            title = event.get('rule_name') or event.get('title', 'No Title')

            key = (severity, time_bucket)
            grouped[key]["count"] += 1
            grouped[key]["titles"].add(title)

        # Build final summary list
        summary_data = []
        for (severity, timestamp), info in grouped.items():
            title_sample = next(iter(info["titles"]))
            hash_code = hashlib.md5(title_sample.encode()).hexdigest()[:6].upper()
            summary_data.append({
                "severity": severity,
                "count": info["count"],
                "timestamp": timestamp,
                "details": {
                    "code": f"{severity.upper()}_{hash_code}",
                    "desc": title_sample
                }
            })

        return summary_data
    
    def get_rule_donut_chart(request):
        """
        Returns count of each unique rule_name from Event documents.
        """
        events = Event.objects.filter(resolved=True).only("rule_name")
        event_data = EventSerializer(events, many=True).data

        # Count occurrences of each rule_name
        rule_counts = Counter(event["rule_name"] for event in event_data if event.get("rule_name"))

        # Format as list of dicts for frontend
        result = [{"name": rule, "count": count} for rule, count in rule_counts.items()]

        return result
    
    def clear_ai_memory():
         EventController.ai_engine.clear_session()

    def mark_resolved(request, event_id):
        """
        Marks an event as resolved.
        """
        try:
            event = Event.objects.get(event_id=event_id)
            event.resolved = True
            event.save()
            return {"message": "Event marked as resolved."}
        except Event.DoesNotExist:
            return {"error": "Event not found."}


        
        