import { EventService } from './../services/event.service';
import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-event-viewer',
  templateUrl: './event-viewer.component.html',
  styleUrls: ['./event-viewer.component.scss']
})
export class EventViewerComponent {
  selectedLogsMap: { [index: number]: boolean } = {};
  selectedLogs: string[] = [];
  parsedAnalysis: any;
  showAnalysis = false;
  loading = false;
  analysisText = '';
  customInputs = [{ text: '', selected: false }];
  selectedCommands: string[] = [];
  executionOutput = '';
  executing = false;
  hostForm = {
    ipAddress: '',
    username: '',
    password: ''
  };

  ipAddress: string = '';
  username: string = '';
  password: string = '';

  touched = false;
  showPassword: boolean = false;

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: any,
    private dialogRef: MatDialogRef<EventViewerComponent>,
    private event_service: EventService
  ) { }

  close(): void {
    this.dialogRef.close();
  }

  isAllSelected(): boolean {
    return this.data.logs?.length > 0 &&
      this.data.logs.every((_: any, i: any) => this.selectedLogsMap[i]);
  }

  toggleSelectAll(event: any): void {
    const isChecked = event.target.checked;
    this.data.logs.forEach((_: any, i: any) => {
      this.selectedLogsMap[i] = isChecked;
    });
    this.updateSelectedLogs();
  }

  updateSelectedLogs(): void {
    this.selectedLogs = this.data.logs.filter((_: any, i: any) => this.selectedLogsMap[i]);
    console.log('✅ Selected Logs:', this.selectedLogs);
  }

  analyzeSelected(): void {
    this.showAnalysis = true;
    this.loading = true;
    this.event_service.get_event_rca(this.selectedLogs).subscribe(
      (res: any) => {
        console.log('✅ Analysis Result:', res);
        this.analysisText = res;
        this.parsedAnalysis = {
          "rca": res.rca,
          "solution": res.solution
        }
        this.loading = false;
      },
      (error) => {
        console.error('Error:', error);
        this.loading = false;
      }
    );
    // Simulate processing
  }

  addInput() {
    this.customInputs.push({ text: '', selected: false });
  }

  removeInput(index: number) {
    this.customInputs.splice(index, 1);
    this.updateSelectedCommands();
  }

  updateSelectedCommands() {
    this.selectedCommands = this.customInputs
      .filter(cmd => cmd.selected && cmd.text.trim() !== '')
      .map(cmd => cmd.text.trim());
  }

  async executeCommands() {
    this.executing = true;
    this.executionOutput = '';

    // Input validation
    if (!this.ipAddress || !this.username || !this.password) {
      this.executionOutput = '❌ Please provide IP address, username, and password.';
      this.executing = false;
      return;
    }

    if (!this.isValidIP(this.ipAddress)) {
      this.executionOutput = '❌ Invalid IP address format.';
      this.executing = false;
      return;
    }

    if (!this.selectedCommands || this.selectedCommands.length === 0) {
      this.executionOutput = '❌ Please select at least one command to execute.';
      this.executing = false;
      return;
    }

    const payload = {
      ip: this.ipAddress.trim(),
      username: this.username.trim(),
      password: this.password.trim(),
      commands: this.selectedCommands
    };

    try {
      const response = await this.event_service.executeCustomCommands(payload).toPromise();
      this.executionOutput = response.output || '✅ Execution completed.';
    } catch (error: any) {
      console.error('Error:', error?.message || 'Unknown error');
      this.executionOutput = '❌ Error: ' + (error?.message || 'Unknown error');
    } finally {
      this.executing = false;
    }
  }



  areAllCommandsSelected(): boolean {
    return this.customInputs.every(cmd => cmd.selected);
  }

  toggleSelectAllCommands(event: any): void {
    const checked = event.target.checked;
    this.customInputs.forEach(cmd => cmd.selected = checked);
    this.updateSelectedCommands();
  }


  isValidIP(ip: string): boolean {
    const ipRegex = /^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}$/;
    return ipRegex.test(ip.trim());
  }

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

}
