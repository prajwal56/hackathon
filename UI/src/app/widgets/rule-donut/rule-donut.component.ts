import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';

@Component({
  selector: 'app-rule-donut',
  templateUrl: './rule-donut.component.html',
  styleUrls: ['./rule-donut.component.scss']
})
export class RuleDonutComponent implements OnChanges {
  @Input() rulesData: any[] = [];
  @Input() isLoading: boolean = false;

  chartOptions: any;
  colorMap = new Map<string, string>();
  selectedRule: string | null = null;

  // Sidebar properties
  isSidebarOpen: boolean = false;
  sidebarData: any = null;
  isLoadingDetails: boolean = false;

  // Professional color palette
  private colorPalette = [
    '#667eea', '#764ba2', '#f093fb', '#f5576c',
    '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
    '#ffecd2', '#fcb69f', '#a8edea', '#fed6e3',
    '#ffd89b', '#19547b', '#f12711', '#f5af19'
  ];

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['rulesData'] && this.rulesData?.length > 0) {
      this.assignColorsToRules();
      this.generateChartOptions();
    }
  }

  assignColorsToRules(): void {
    this.colorMap.clear();
    this.rulesData.forEach((rule, index) => {
      const color = this.colorPalette[index % this.colorPalette.length];
      this.colorMap.set(rule.name, color);
    });
  }

  generateChartOptions(): void {
    const chartData = this.rulesData.map(item => ({
      value: item.count,
      name: item.name,
      itemStyle: {
        color: this.colorMap.get(item.name),
        borderRadius: 4,
        borderColor: '#fff',
        borderWidth: 2
      }
    }));

    this.chartOptions = {
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          const percentage = ((params.value / this.getTotalRules()) * 100).toFixed(1);
          return `
          <div style="padding: 8px 12px; background: #fff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            <div style="font-weight: 600; color: #1f2937; margin-bottom: 4px;">${params.name}</div>
            <div style="color: #6b7280; font-size: 14px;">
              <span style="display: inline-block; width: 8px; height: 8px; background: ${params.color}; border-radius: 50%; margin-right: 6px;"></span>
              ${params.value} rules (${percentage}%)
            </div>
          </div>
        `;
        },
        backgroundColor: 'transparent',
        borderWidth: 0,
        textStyle: {
          color: '#1f2937'
        }
      },
      legend: {
        show: false
      },
      // IMPORTANT: Add grid to ensure proper centering
      grid: {
        left: 0,
        right: 0,
        top: 0,
        bottom: 0,
        containLabel: false
      },
      series: [
        {
          name: 'Rules',
          type: 'pie',
          radius: ['55%', '85%'],
          center: ['50%', '50%'], // This ensures the donut is centered
          avoidLabelOverlap: false,
          label: {
            show: false
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '16',
              fontWeight: 'bold',
              color: '#1f2937'
            },
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          labelLine: {
            show: false
          },
          data: chartData,
          animationType: 'scale',
          animationEasing: 'elasticOut',
          animationDelay: (idx: number) => idx * 100
        }
      ]
    };
  }


  // Helper methods
  getTotalRules(): number {
    return this.rulesData.reduce((total, rule) => total + rule.count, 0);
  }

  getPercentage(count: number): string {
    const total = this.getTotalRules();
    return total > 0 ? ((count / total) * 100).toFixed(1) : '0';
  }

  getMostActiveRule(): string {
    if (!this.rulesData || this.rulesData.length === 0) return 'N/A';
    const mostActive = this.rulesData.reduce((max, rule) =>
      rule.count > max.count ? rule : max
    );
    return mostActive.name;
  }

  getSuccessRate(): string {
    return '94.5';
  }

  getLastUpdated(): string {
    return new Date().toLocaleTimeString();
  }

  selectRule(ruleName: string): void {
    this.selectedRule = this.selectedRule === ruleName ? null : ruleName;
  }

  // ADD THESE HELPER METHODS FOR TEMPLATE
  getTotalLogEntries(): number {
    if (!this.sidebarData || !this.sidebarData.logs) return 0;
    return this.sidebarData.logs.length;
  }

  getTotalMessages(): number {
    if (!this.sidebarData || !this.sidebarData.logs) return 0;
    return this.sidebarData.logs.reduce((total: number, log: any) => {
      return total + (log.msg ? log.msg.length : 0);
    }, 0);
  }

  getUniqueIPs(): number {
    if (!this.sidebarData || !this.sidebarData.logs) return 0;
    const uniqueIPs = new Set(this.sidebarData.logs.map((log: any) => log.ip_address));
    return uniqueIPs.size;
  }

  // Sidebar methods
  viewRuleDetails(rule: any): void {
    this.isLoadingDetails = true;
    this.isSidebarOpen = true;

    // Simulate API call
    setTimeout(() => {
      this.sidebarData = {
        "_id": {
          "$oid": "6878a317cd8a3a74c4541303"
        },
        "title": `Rule triggered: ${rule.name}`,
        "description": "1 unique messages found.\n\nRCA: Unknown directive \"invalid_directive\" in nginx.conf\n\nSolution: Check the nginx.conf file for any typos or incorrect directives",
        "logs": [
          {
            "ip_address": "10.0.5.78",
            "msg": [
              [
                "2025/07/17 12:43:56 [emerg] 62018#62018: unknown directive \"invalid_directive\" in /etc/nginx/nginx.conf:18",
                "[emerg] 62018#62018: unknown directive \"invalid_directive\" in /etc/nginx/nginx.conf:18"
              ]
            ]
          },
          {
            "ip_address": "10.0.5.79",
            "msg": [
              [
                "2025/07/17 12:44:12 [emerg] 62019#62019: unknown directive \"test_directive\" in /etc/nginx/nginx.conf:22",
                "[emerg] 62019#62019: configuration file /etc/nginx/nginx.conf test failed"
              ]
            ]
          }
        ],
        "created_at": {
          "$date": "2025-07-17T07:15:35.433Z"
        },
        "rule_name": rule.name,
        "severity": "MAJOR"
      };
      this.isLoadingDetails = false;
    }, 800);
  }

  closeSidebar(): void {
    this.isSidebarOpen = false;
    this.sidebarData = null;
  }

  getSeverityColor(severity: string): string {
    const colors = {
      'CRITICAL': '#ef4444',
      'MAJOR': '#f59e0b',
      'MINOR': '#10b981',
      'WARNING': '#f97316'
    };
    return colors[severity as keyof typeof colors] || '#6b7280';
  }

  getSeverityIcon(severity: string): string {
    const icons = {
      'CRITICAL': '🚨',
      'MAJOR': '⚠️',
      'MINOR': '💡',
      'WARNING': '⚡'
    };
    return icons[severity as keyof typeof icons] || '📋';
  }

  formatDate(dateObj: any): string {
    const date = new Date(dateObj.$date);
    return date.toLocaleString();
  }

  // Action methods
  refreshData(): void {
    this.isLoading = true;
    setTimeout(() => {
      this.isLoading = false;
    }, 1000);
  }

  exportData(): void {
    console.log('Exporting data...');
  }

  createRule(): void {
    console.log('Creating new rule...');
  }

  viewAllRules(): void {
    console.log('Viewing all rules...');
  }
}
