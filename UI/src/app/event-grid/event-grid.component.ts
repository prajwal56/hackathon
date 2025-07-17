import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';

import { EventViewerComponent } from '../event-viewer/event-viewer.component';
import { EventService } from '../services/event.service';

@Component({
  selector: 'app-event-grid',
  templateUrl: './event-grid.component.html',
  styleUrls: ['./event-grid.component.scss']
})
export class EventGridComponent implements OnInit {
  columns = ['name', 'description',"severity", 'log_count', 'actions'];
  dataSource = new MatTableDataSource<any>();

  @ViewChild(MatPaginator) paginator!: MatPaginator;

  startX!: number;
  startWidth!: number;
  resizingColIndex!: number;



  constructor(
    private dialog: MatDialog,
    private event_service: EventService
  ) { }

  ngOnInit(): void {
    this.getData();
  }

  getData(): void {
    this.event_service.getEvent_list().subscribe((res: any[]) => {
      this.dataSource.data = res;
      this.dataSource.paginator = this.paginator;
    });
  }

  openEvent(data: any = {}): void {
    const config: MatDialogConfig = {
      width: '70vw',
      height: '100vh',
      position: { right: '0', top: '0' },
      panelClass: 'side-panel',
      data: data,
      disableClose: false,
      autoFocus: false
    };

    this.dialog.open(EventViewerComponent, config);
  }

  startResize(event: MouseEvent, colIndex: number): void {
    this.startX = event.pageX;
    const th = document.querySelectorAll('th')[colIndex] as HTMLElement;
    this.startWidth = th.offsetWidth;
    this.resizingColIndex = colIndex;

    document.addEventListener('mousemove', this.resizeColumn);
    document.addEventListener('mouseup', this.stopResize);
  }

  resizeColumn = (event: MouseEvent): void => {
    const dx = event.pageX - this.startX;
    const th = document.querySelectorAll('th')[this.resizingColIndex] as HTMLElement;
    if (th) {
      th.style.width = `${this.startWidth + dx}px`;
    }
  };

  stopResize = (): void => {
    document.removeEventListener('mousemove', this.resizeColumn);
    document.removeEventListener('mouseup', this.stopResize);
  };

  getStatusClass(desc: string): string {
    return desc.toLowerCase().replace(/\s+/g, '-');
  }

  // Optional pagination helpers (for UI display purposes)
  getPageIndex(): number {
    return this.paginator?.pageIndex ?? 0;
  }

  getTotalItems(): number {
    return this.dataSource?.data?.length ?? 0;
  }

  getPageSize(): number {
    return this.paginator?.pageSize ?? 10;
  }

  getTotalPages(): number {
    return Math.ceil(this.getTotalItems() / this.getPageSize());
  }


  getSeverityClass(severity: string): string {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL': return 'severity-badge severity-critical';
      case 'MAJOR': return 'severity-badge severity-major';
      case 'MINOR': return 'severity-badge severity-minor';
      case 'WARNING': return 'severity-badge severity-warning';
      default: return 'severity-badge';
    }
  }



}
