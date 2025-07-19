import { Component, OnInit } from '@angular/core';
import { EventService } from '../services/event.service';

@Component({
  selector: 'app-event-generate',
  templateUrl: './event-generate.component.html',
  styleUrls: ['./event-generate.component.scss']
})
export class EventGenerateComponent implements OnInit {
  showCredentialPopup = false;
  shownDescription: string | null = null;
  currentServiceName = '';
  currentEvent = '';
  services: any[] = [];

  constructor(private eventGenerateService: EventService) { }

  ngOnInit(): void {
    this.services = [
      {
        name: 'nginx',
        events: ['unknown directive', 'invalid nginx port', 'nginx failure', 'permission denied'],
        color: '#e3f2fd'
      },
      {
        name: 'postgresql',
        events: ['max connection', 'pgsql config error'],
        color: '#f3e5f5'
      },
      {
        name: 'redis',
        events: ['simulate redis permission error', 'redis corrupt config test', 'redis port conflict'],
        color: '#e8f5e8'
      }
    ];
  }

  toggleDescription(event: string) {
    if (this.shownDescription === event) {
      this.shownDescription = null;
    } else {
      this.shownDescription = event;
    }
  }

  getDescriptionForEvent(event: string): string {
    switch (event) {
      case 'unknown directive':
        return 'This button triggers an issue where nginx configuration has an unknown or unsupported directive, usually due to syntax errors or missing modules.';
      case 'invalid nginx port':
        return 'This button triggers an issue where nginx is configured with an invalid port number, causing the service to fail starting or be inaccessible.';
      case 'nginx failure':
        return 'This button simulates a general nginx service failure scenario.';
      case 'permission denied':
        return 'This button simulates a permission denied error for nginx operations.';
      case 'max connection':
        return 'This button simulates reaching the maximum number of allowed connections in Postgres, resulting in connection refusal for new clients.';
      case 'pgsql config error':
        return 'This button triggers PostgreSQL configuration errors for testing purposes.';
      case 'simulate redis permission error':
        return 'This button triggers a Redis permission error to test how your system handles access denial or insufficient privilege scenarios.';
      case 'redis corrupt config test':
        return 'This button simulates Redis configuration corruption scenarios.';
      case 'redis port conflict':
        return 'This button triggers a Redis port conflict error for testing purposes.';
      default:
        return 'No description available.';
    }
  }

  openCredentialDialog(serviceName: string, event: string) {
    this.currentServiceName = serviceName;
    this.currentEvent = event;
    this.showCredentialPopup = true;
  }

  selectAndSubmit(ip: string) {
    const payload = {
      service: this.currentServiceName,
      event: this.currentEvent,
      hostname: ip,
      username: 'root',          // hardcoded
      password: 'hanTZ123'       // hardcoded
    };

    console.log('Submitting credentials:', payload);

    this.eventGenerateService.generateEvent(payload).subscribe(
      (res: any) => {
        console.log('Event generated:', res);
        this.closePopup();
        alert(`Event '${this.currentEvent}' generated successfully for ${this.currentServiceName} on ${ip}`);
      },
      (err: any) => {
        console.error('Error generating event:', err);
        alert('Failed to generate event. Please try again.');
        this.closePopup();
      }
    );
  }

  closePopup() {
    this.showCredentialPopup = false;
    this.currentServiceName = '';
    this.currentEvent = '';
  }

  isPostgresService(serviceName: string) {
    return serviceName && serviceName.toLowerCase().includes('postgres');
  }

}
