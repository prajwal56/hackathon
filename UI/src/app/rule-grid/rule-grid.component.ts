import { Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { Router } from '@angular/router';
import { RuleService } from '../services/rule.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-rule-grid',
  templateUrl: './rule-grid.component.html',
  styleUrls: ['./rule-grid.component.scss']
})
export class RuleGridComponent implements OnInit, AfterViewInit {
  columns: string[] = ['name', 'index', 'description', 'actions'];
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;

  dataSource = new MatTableDataSource<any>();

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private router: Router,
    private ruleService: RuleService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.fetchRules();
  }

  ngAfterViewInit() {
    this.paginator.page.subscribe(() => {
      const page = this.paginator.pageIndex + 1;
      const limit = this.paginator.pageSize;
      this.fetchRules(page, limit);
    });
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  fetchRules(page = 1, limit = 10) {
    this.ruleService.getRules(page, limit).subscribe({
      next: (response: any) => {
        const rules = response.data || [];
        this.totalItems = response.pagination?.total || 0;
        this.currentPage = response.pagination?.page || 1;
        this.pageSize = response.pagination?.limit || 10;

        this.dataSource = new MatTableDataSource<any>(rules);
        this.dataSource.paginator = this.paginator;
        this.dataSource.sort = this.sort;
      },
      error: () => {
        this.snackBar.open('Failed to load rules', 'Close', { duration: 3000 });
      }
    });
  }

  openDialog(rule: any) {
    this.router.navigate(['/rule-config'], {
      queryParams: { ruleId: rule?.id ?? '' }
    });
  }

  deleteRule(rule: any) {
    if (confirm(`Are you sure you want to delete rule "${rule.name}"?`)) {
      this.ruleService.deleteRule(rule.id).subscribe({
        next: () => {
          this.snackBar.open('Rule deleted successfully', 'Close', { duration: 3000 });
          this.fetchRules();
        },
        error: () => {
          this.snackBar.open('Failed to delete rule', 'Close', { duration: 3000 });
        }
      });
    }
  }

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
    return Math.ceil(this.totalItems / this.pageSize);
  }

  getStatusClass(desc: string): string {
    return desc.toLowerCase().replace(/\s+/g, '-');
  }
  toggleRuleStatus(row: any): void {
    const newStatus = !row.is_active;
    const action = newStatus ? 'enable' : 'disable';
    
    // Call your service to update the rule status
    this.ruleService.updateRuleStatus(row.rule_id, newStatus).subscribe({
      next: (response) => {
        // Update the local data
        row.is_active = newStatus;
        console.log(`Rule ${action}d successfully`);
        
        // Optional: Show success message
        // this.snackBar.open(`Rule ${action}d successfully`, 'Close', { duration: 3000 });
      },
      error: (error: any) => {
        console.error(`Error ${action}ing rule:`, error);
        
        // Optional: Show error message
        // this.snackBar.open(`Failed to ${action} rule`, 'Close', { duration: 3000 });
      }
    });
  }
}
