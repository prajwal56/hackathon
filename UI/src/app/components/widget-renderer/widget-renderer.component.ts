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
  public successRate:any = null;
  constructor(private eventService: EventService) {}

  ngOnInit(): void {
    this.getEventData();
    this.get_rule_donut_chart_data();
    this.getSuccessRate();
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

  getSuccessRate() {
    this.eventService.get_success_rate().subscribe((count: any) => {
      console.log(count);
      this.successRate = +(Math.round(count?.success_rate * 100) / 100).toFixed(2);
      // const totalCount = this.getTotalRules();
      // const successRate = ((successCount / totalCount) * 100).toFixed(1);
    });
  }

}
