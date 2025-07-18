import { Component, Input, OnInit } from '@angular/core';
import { EventService } from '../../services/event.service';

@Component({
  selector: 'app-widget-renderer',
  templateUrl: './widget-renderer.component.html',
  styleUrls: ['./widget-renderer.component.scss'],
})
export class WidgetRendererComponent implements OnInit {
  @Input() widgetType!: string;
  selectedEvent: any;
  eventSummaryData: any[] = [];
  rules = [
  { name: 'Critical', count: 10 },
  { name: 'High', count: 5 },
  { name: 'Medium', count: 3 },
  { name: 'Low', count: 1 }
];

  constructor(private eventService: EventService) {}

  ngOnInit(): void {
    this.getEventData();
    this.get_rule_donut_chart_data();
  }

  getEventData(): void {
    this.eventService.get_event_rca_list().subscribe((data: any[]) => {
      console.log(data);
      this.eventSummaryData = data.map(event => ({
      ...event,
      timestamp: event.timestamp.replace('+00:00Z', 'Z') // or '' if you prefer
    }));
    });
  }

  get_rule_donut_chart_data() {
    this.eventService.get_rule_donut_chart().subscribe((data: any[]) => {
      console.log(data);
      this.rules= data;
    });
  }

  showEventDetail(event: any): void {
    this.selectedEvent = event.details;
  }

}
