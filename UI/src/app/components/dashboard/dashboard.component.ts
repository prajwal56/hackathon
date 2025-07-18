import { Component } from '@angular/core';
import { GridsterConfig, GridsterItem } from 'angular-gridster2';
import { GridType } from 'angular-gridster2';
@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent {
  options: GridsterConfig = {
  draggable: { enabled: true },
  resizable: { enabled: true },
  pushItems: true,
  displayGrid: 'none',
  minCols: 100,
  minRows: 100,
  gridType: GridType.ScrollVertical, // ⬅️ add this line
};
  dashboard: GridsterItem[] = [
    // { cols: 20, rows: 50, y: 0, x: 0, widgetType: 'error-summary' },
    // { cols: 20, rows: 50, y: 1, x: 0, widgetType: 'rule-hits' },
    // { cols: 20, rows: 40, y: 0, x: 1, widgetType: 'event-grid' },
    { cols: 40, rows: 40, y: 0, x: 0, widgetType: 'event-chart' },
    { cols: 20, rows: 20, y: 0, x: 0, widgetType: 'rule-donut' },
  ];


}
