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
  hostname = '';
  username = '';
  password = '';
  selectedIp = '';
  currentServiceName = '';
  currentEvent = '';
  services: any[] = [];

  constructor(private eventGenerateService: EventService) { }

  ngOnInit(): void {
    this.services = [
      { name: 'nginx', events: ['unknown directive','invalid nginx port','nginx failure','permission denied'] },
      { name: 'postgresql', events: ['max connection','pgsql config error'] },
      { name: 'redis', events: ['simulate redis permission error','redis corrupt config test','redis port conflict']}
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
      case 'foreign key violation test':
        return 'This button triggers a foreign key violation error in Postgres, which happens when you try to insert or update a value that does not exist in the referenced table.';
      case 'generate pg errors':
        return 'This button generates general Postgres errors for testing purposes, to check how the system handles database exceptions.';
      case 'max connection':
        return 'This button simulates reaching the maximum number of allowed connections in Postgres, resulting in connection refusal for new clients.';
      case 'simulate deadlock':
        return 'This button creates a deadlock situation in Postgres, where two transactions wait for each other to release locks, causing both to block.';
      case 'unique violation test':
        return 'This button triggers a unique constraint violation error in Postgres, which happens when you insert duplicate values into a column with a unique constraint.';
      case 'simulate redis permission error':
        return 'This button triggers a Redis permission error to test how your system handles access denial or insufficient privilege scenarios.';
      default:
        return 'No description available.';
    }
  }

  openCredentialDialog(serviceName: string, event: string) {
    this.currentServiceName = serviceName;
    this.currentEvent = event;
    this.showCredentialPopup = true;
  }

  selectIp(ip: string) {
    this.hostname = ip;
    this.selectedIp = ip;
  }

 submitCredentials() {
  const payload = {
    service: this.currentServiceName,
    event: this.currentEvent,
    hostname: this.hostname,
    username: 'root',          // hardcoded
    password: 'hanTZ123'       // hardcoded
  };

  this.eventGenerateService.generateEvent(payload).subscribe(
    (res: any) => {
      console.log('Event generated:', res);
      this.showCredentialPopup = false;
      alert(`Event '${this.currentEvent}' generated for ${this.currentServiceName}`);
      // Clear only hostname since username/password are hardcoded
      this.hostname = '';
    },
    (err: any) => {
      console.error('Error generating event:', err);
      alert('Failed to generate event.');
    }
  );
}

}