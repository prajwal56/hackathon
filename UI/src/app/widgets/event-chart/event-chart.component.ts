import { Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';

@Component({
  selector: 'app-event-chart',
  templateUrl: './event-chart.component.html',
  styleUrls: ['./event-chart.component.scss']
})
export class EventChartComponent implements OnInit, OnChanges {
  @Input() eventData: any[] = [];

  selectedEvent: any;
  chartOption: any;
  isLoading: boolean = false;
  isSidebarOpen: boolean = false;

  // Chart view options
  chartViewMode: 'line' | 'bar' | 'area' = 'line';
  timeRange: 'all' | '1h' | '6h' | '24h' = 'all';

  // Summary statistics
  totalEvents: number = 0;
  criticalEvents: number = 0;
  averageEventsPerHour: number = 0;
  mostActiveSeverity: string = '';

  ngOnInit(): void {
    this.calculateSummaryStats();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['eventData'] && this.eventData && this.eventData.length) {
      console.log('✅ eventData changed:', this.eventData);
      this.calculateSummaryStats();
      this.generateChart();
    }
  }

  calculateSummaryStats(): void {
    if (!this.eventData || this.eventData.length === 0) return;

    this.totalEvents = this.eventData.reduce((sum, event) => sum + event.count, 0);
    this.criticalEvents = this.eventData
      .filter(event => event.severity.toLowerCase() === 'critical')
      .reduce((sum, event) => sum + event.count, 0);

    // Calculate average events per hour
    const timeSpan = this.getTimeSpanHours();
    this.averageEventsPerHour = timeSpan > 0 ? Math.round(this.totalEvents / timeSpan) : 0;

    // Find most active severity
    const severityCount = this.eventData.reduce((acc, event) => {
      acc[event.severity] = (acc[event.severity] || 0) + event.count;
      return acc;
    }, {} as { [key: string]: number });

    this.mostActiveSeverity = Object.entries(severityCount)
      .sort(([,a]:any, [,b]:any) => b - a)[0]?.[0] || 'N/A';
  }

  getTimeSpanHours(): number {
    if (!this.eventData || this.eventData.length === 0) return 0;

    const timestamps = this.eventData.map(e => new Date(e.timestamp).getTime());
    const minTime = Math.min(...timestamps);
    const maxTime = Math.max(...timestamps);

    return Math.max(1, Math.ceil((maxTime - minTime) / (1000 * 60 * 60)));
  }

  generateChart(): void {
    const grouped: { [severity: string]: any[] } = {};
    this.eventData.forEach(event => {
      const key = event.severity;
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(event);
    });

    const allTimestamps = Array.from(new Set(this.eventData.map(e => e.timestamp)))
      .sort((a, b) => new Date(a).getTime() - new Date(b).getTime());

    const series = Object.keys(grouped).map(severity => {
      const dataMap = new Map(grouped[severity].map(e => [e.timestamp, e]));
      return {
        name: severity,
        type: this.chartViewMode,
        smooth: true,
        data: allTimestamps.map(ts => {
          const e = dataMap.get(ts);
          return {
            value: e ? e.count : 0,
            details: e?.details || null,
            severity,
            timestamp: ts
          };
        }),
        lineStyle: {
          color: this.getColor(severity),
          width: 3
        },
        itemStyle: {
          color: this.getColor(severity),
          borderWidth: 2,
          borderColor: '#fff'
        },
        areaStyle: this.chartViewMode === 'area' ? {
          opacity: 0.3,
          color: this.getColor(severity)
        } : undefined
      };
    });

    this.chartOption = {
      tooltip: {
        trigger: 'item',
        backgroundColor: '#fff',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        borderRadius: 8,
        padding: 12,
        textStyle: {
          color: '#1f2937',
          fontSize: 14
        },
        formatter: (params: any) => {
          const d = params.data;
          return `
            <div style="font-weight: 600; color: ${this.getColor(d.severity)}; margin-bottom: 8px;">
              ${d.severity.toUpperCase()}
            </div>
            <div style="margin-bottom: 4px;">
              <span style="color: #6b7280;">Time:</span> ${new Date(d.timestamp).toLocaleString()}
            </div>
            <div style="margin-bottom: 4px;">
              <span style="color: #6b7280;">Count:</span> <strong>${d.value}</strong>
            </div>
            <div style="font-size: 12px; color: #9ca3af; margin-top: 8px;">
              Click to view details
            </div>
          `;
        }
      },
      legend: {
        data: Object.keys(grouped),
        top: 20,
        itemWidth: 14,
        itemHeight: 14,
        textStyle: {
          color: '#374151',
          fontSize: 13
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '8%',
        top: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: allTimestamps.map(ts => new Date(ts).toLocaleTimeString()),
        boundaryGap: false,
        axisLine: {
          lineStyle: {
            color: '#e5e7eb'
          }
        },
        axisTick: {
          lineStyle: {
            color: '#e5e7eb'
          }
        },
        axisLabel: {
          color: '#6b7280',
          fontSize: 12
        }
      },
      yAxis: {
        type: 'value',
        name: 'Event Count',
        nameTextStyle: {
          color: '#6b7280',
          fontSize: 12
        },
        axisLine: {
          lineStyle: {
            color: '#e5e7eb'
          }
        },
        axisTick: {
          lineStyle: {
            color: '#e5e7eb'
          }
        },
        axisLabel: {
          color: '#6b7280',
          fontSize: 12
        },
        splitLine: {
          lineStyle: {
            color: '#f3f4f6'
          }
        }
      },
      series
    };
  }

  getColor(severity: string): string {
    switch (severity.toLowerCase()) {
      case 'critical': return '#ef4444';  // Red
      case 'major': return '#f59e0b';     // Orange
      case 'minor': return '#10b981';     // Green
      case 'warning': return '#3b82f6';   // Blue
      default: return '#6b7280';          // Grey
    }
  }

  getSeverityIcon(severity: string): string {
    switch (severity.toLowerCase()) {
      case 'critical': return '🚨';
      case 'major': return '⚠️';
      case 'minor': return '💡';
      case 'warning': return '⚡';
      default: return '📋';
    }
  }

  // Event handlers
  onChartClick(event: any): void {
    if (event.data && event.data.details) {
      this.selectedEvent = {
        ...event.data.details,
        severity: event.data.severity,
        timestamp: event.data.timestamp,
        count: event.data.value
      };
      this.isSidebarOpen = true;
    }
  }

  closeSidebar(): void {
    this.isSidebarOpen = false;
    this.selectedEvent = null;
  }

  changeChartView(mode: 'line' | 'bar' | 'area'): void {
    this.chartViewMode = mode;
    this.generateChart();
  }

  exportData(): void {
    // Export functionality
    console.log('Exporting event data...');
  }

  refreshData(): void {
    this.isLoading = true;
    setTimeout(() => {
      this.isLoading = false;
      this.generateChart();
    }, 1000);
  }

  formatDate(timestamp: string): string {
    return new Date(timestamp).toLocaleString();
  }

  getStatusBadgeClass(severity: string): string {
    switch (severity.toLowerCase()) {
      case 'critical': return 'critical';
      case 'major': return 'major';
      case 'minor': return 'minor';
      case 'warning': return 'warning';
      default: return 'default';
    }
  }
}
