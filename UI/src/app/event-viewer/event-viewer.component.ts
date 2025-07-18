// Updated eventviewer-component.ts
import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { EventService } from './../services/event.service';

@Component({
  selector: 'app-event-viewer',
  templateUrl: './event-viewer.component.html',
  styleUrls: ['./event-viewer.component.scss']
})


export class EventViewerComponent {
  selectedLogsMap: { [key: string]: boolean } = {};
  selectedLogs: string[] = [];
  parsedAnalysis =
    {
      rca: '',
      solution: '',
      commands: '',
      user_input: '',
    };

  showAnalysis = false;
  loading = false;
  analysisText = '';
  analysisQuery: string = '';
  customInputs = [{ text: '', selected: false }];
  selectedCommands: string[] = [];
  executionOutput = '';
  executing = false;

  ipAddress: string = '';
  username: string = '';
  password: string = '';
  showPassword = false;

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: any,
    private dialogRef: MatDialogRef<EventViewerComponent>,
    private event_service: EventService
  ) {}

  close(): void {
    this.dialogRef.close();
  }


  isAllSelected(groupIndex: number, ruleIndex: number): boolean {
    const messages = this.data.logs[groupIndex].rules[ruleIndex].msg;
    return messages.every((_: string, i: number) =>
      this.selectedLogsMap[`${groupIndex}-${ruleIndex}-${i}`]
    );
  }
  
  toggleSelectAll(event: any, groupIndex: number, ruleIndex: number): void {
    const isChecked = event.target.checked;
    const messages = this.data.logs[groupIndex].rules[ruleIndex].msg;
  
    messages.forEach((_: string, i: number) => {
      this.selectedLogsMap[`${groupIndex}-${ruleIndex}-${i}`] = isChecked;
    });
  
    this.updateSelectedLogs(groupIndex);
  }
  
  updateSelectedLogs(groupIndex: number): void {
    this.selectedLogs = [];
  
    this.data.logs[groupIndex].rules.forEach((rule:any, ruleIndex:any) => {
      rule.msg.forEach((msg: string, i: number) => {
        if (this.selectedLogsMap[`${groupIndex}-${ruleIndex}-${i}`]) {
          this.selectedLogs.push(msg);
        }
      });
    });
  }
  

  analyzeSelected(groupIndex: number, ip: string, analysisQuery:string,user_input=''): void {
    this.ipAddress = ip;
    this.showAnalysis = true;
    this.loading = true;
    const payload = {
      logs: this.selectedLogs,
      analysisQuery: analysisQuery,
      user_input: user_input

    };
    this.event_service.get_event_rca(payload).subscribe(
      (res: any) => {
        // console.log("res>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",res)
        this.analysisText = res;
        this.parsedAnalysis = {
          rca: res.rca,
          solution: res.solution,
          commands: res.commands || '',
          user_input: res?.user_input,
        };
        this.parseAndAddCommandsToCustomInputs(res.commands);
        this.loading = false;
      },
      (error) => {
        console.error('Error:', error);
        this.loading = false;
      }
    );
  }

  parseAndAddCommandsToCustomInputs(commands: string): void {
    if (!commands) return;

    // Remove any existing empty entries
    this.customInputs = this.customInputs.filter(cmd => cmd.text.trim().length > 0);

    const commandLines = commands
      .split(/[\r\n]+/)
      .map(cmd => cmd.trim())
      .filter(cmd => cmd.length > 0); // ensures no empty or whitespace-only commands

    commandLines.forEach(command => {
      if (!command.startsWith('#')) {
        this.customInputs.push({ text: command, selected: false });
      }

    });
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

  async executeCommands() {
    this.executing = true;
    this.executionOutput = '';

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
      this.executionOutput = response || '✅ Execution completed.';
    } catch (error: any) {
      this.executionOutput = '❌ Error: ' + (error?.message || 'Unknown error');
    } finally {
      this.executing = false;
    }
  }
}
