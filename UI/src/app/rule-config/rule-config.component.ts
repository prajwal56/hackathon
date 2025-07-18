import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatChipInputEvent } from '@angular/material/chips';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { RuleService } from '../services/rule.service';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-rule-config',
  templateUrl: './rule-config.component.html',
  styleUrls: ['./rule-config.component.scss']
})
export class RuleConfigComponent implements OnInit {
  ruleFormModel: any = {
    name: '',
    index: null,
    description: '',
    condition: [
      {
        logic: 'AND',
        filters: [
          {
            field: null,
            operator: null,
            value: null,
            logicWithNext: 'AND'
          }
        ]
      }
    ],
    business_service_details:
    {
      service_id: null,
      service_rules: [
        {
          rule_id: null,
          process_details: null
        }
      ]
    },
    duration: {
      value: null,
      unit: 'seconds'  // or 'minutes', 'hours', 'days'
    },
    ssh_commands: [''],
    alert: {
      severity: null,
      type: ''
    },
    linked_rules: []
  };

  ruleId: string | null = null;
  isLoading = false;
  indexOptions = [];
  availableRules = [];
  fieldOptions = [];
  operatorOptions = ['is', 'is not', 'is one of', 'is not one of', 'exists', 'does not exist', 'contains'];
  severityOptions = ["CRITICAL", "MAJOR", "MINOR", "WARNING"];
  typeOptions = [];
  readonly separatorKeysCodes: number[] = [ENTER, COMMA];
  service_list = []
  rule_list = []
  resource_list = []
  ssh_commands: [''] = ['']

  constructor(
    private ruleService: RuleService,
    private route: ActivatedRoute,
    private router: Router,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.ruleId = this.route.snapshot.queryParamMap.get('ruleId');
    if (this.ruleId) {
      this.fetchRule(this.ruleId);
    }
    this.getOptions();
  }

  getOptions() {
    let payload = {
      index: this.ruleFormModel.index
    };
    this.ruleService.getOptions(payload).subscribe({
      next: (rule: any) => {
        this.fieldOptions = rule.fields;
        this.indexOptions = rule.indexOptions;
        this.service_list = rule.service_list;
        this.rule_list = rule.rule_list;
        this.resource_list = rule.resource_list;
      },
      error: () => {
        this.snackBar.open('Failed to load rule', 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    });
  }

  getResourceOptions(serviceId: string) {
    let payload = {
      service_id: serviceId
    };
    this.ruleService.getResource_list(payload).subscribe({
      next: (rule: any) => {
        this.resource_list = rule;
      },
      error: () => {
        this.snackBar.open('Failed to load rule', 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    });
  }
  getValueArray(groupIndex: number, filterIndex: number): string[] {
    const val = this.ruleFormModel.condition[groupIndex].filters[filterIndex].value;
    return Array.isArray(val) ? val : (val ? val.split(',').map((v: string) => v.trim()) : []);
  }

  addChip(event: MatChipInputEvent, groupIndex: number, filterIndex: number): void {
    const input = event.input;
    const value = event.value.trim();
    const currentValues = this.getValueArray(groupIndex, filterIndex);

    if (value && !currentValues.includes(value)) {
      currentValues.push(value);
      const operator = this.ruleFormModel.condition[groupIndex].filters[filterIndex].operator;
      if (['is one of', 'is not one of'].includes(operator)) {
        this.ruleFormModel.condition[groupIndex].filters[filterIndex].value = currentValues;
      } else {
        this.ruleFormModel.condition[groupIndex].filters[filterIndex].value = currentValues.join(', ');
      }
    }

    if (input) {
      input.value = '';
    }
  }

  removeChip(groupIndex: number, filterIndex: number, chipValue: string): void {
    let currentValues = this.getValueArray(groupIndex, filterIndex).filter((v: string) => v !== chipValue);
    const operator = this.ruleFormModel.condition[groupIndex].filters[filterIndex].operator;
    if (['is one of', 'is not one of'].includes(operator)) {
      this.ruleFormModel.condition[groupIndex].filters[filterIndex].value = currentValues;
    } else {
      this.ruleFormModel.condition[groupIndex].filters[filterIndex].value = currentValues.join(', ');
    }
  }

  addConditionGroup() {
    this.ruleFormModel.condition.push({
      logic: 'AND',
      filters: [
        {
          field: '',
          operator: '',
          value: '',
          logicWithNext: 'AND'
        }
      ]
    });
  }
  addServiceGroup() {
    this.ruleFormModel.business_service_details.service_rules.push({
      rule_id: '',
      process_details: ''
    });
  }

  removeConditionGroup(index: number) {
    this.ruleFormModel.condition.splice(index, 1);
  }

  addFilter(groupIndex: number) {
    this.ruleFormModel.condition[groupIndex].filters.push({
      field: '',
      operator: '',
      value: '',
      logicWithNext: 'AND'
    });
  }

  removeFilter(groupIndex: number, filterIndex: number) {
    this.ruleFormModel.condition[groupIndex].filters.splice(filterIndex, 1);
  }

  submit() {
    const durationInSeconds = this.convertToSeconds(
      this.ruleFormModel.duration.value,
      this.ruleFormModel.duration.unit
    );


    const payload = {
      name: this.ruleFormModel.name,
      index: this.ruleFormModel.index,
      description: this.ruleFormModel.description,
      duration: durationInSeconds,
      condition: this.generateESQuery(),
      alert: {
        severity: this.ruleFormModel.alert.severity,
      },
      ssh_commands: this.ruleFormModel.ssh_commands.filter((cmd: string) => cmd.trim() !== ''),
      business_service_details: this.ruleFormModel.business_service_details,
      linked_rules : this.ruleFormModel.linked_rules
    };
    if (!this.ruleFormModel.name || !this.ruleFormModel.index || !this.ruleFormModel.alert.severity) {
      this.snackBar.open('Please fill all required fields.', 'Close', { duration: 3000 });
      return;
    }

    if (this.ruleId) {
      this.ruleService.updateRule(this.ruleId, payload).subscribe({
        next: () => {
          this.snackBar.open('Rule updated successfully', 'Close', { duration: 3000 });
          this.router.navigate(['/rule-grid']);
        },
        error: () => {
          this.snackBar.open('Failed to update rule', 'Close', { duration: 3000 });
        }
      });
    } else {
      this.ruleService.createRule(payload).subscribe({
        next: () => {
          this.snackBar.open('Rule created successfully', 'Close', { duration: 3000 });
          this.router.navigate(['/rule-grid']);
        },
        error: () => {
          this.snackBar.open('Failed to create rule', 'Close', { duration: 3000 });
        }
      });
    }
  }

  fetchRule(id: string) {
    this.isLoading = true;
    this.ruleService.getRule(id).subscribe({
      next: (rule: any) => {
        this.patchForm(rule);
        const durationInfo = this.convertFromSeconds(rule.duration || 0);
        this.ruleFormModel.duration = {
          value: durationInfo.value,
          unit: durationInfo.unit
        };

        this.isLoading = false;
      },
      error: () => {
        this.snackBar.open('Failed to load rule', 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    });
  }

  patchForm(rule: any) {
    this.ruleFormModel.name = rule.name || '';
    this.ruleFormModel.index = rule.index || '';
    this.ruleFormModel.description = rule.description || '';
    this.ruleFormModel.linked_rules = rule.linked_rules || [];
    this.ruleFormModel.alert = {
      severity: rule.alert?.severity || '',
      type: rule.alert?.type || ''
    };

    // Patch SSH commands (load existing or fallback to one empty input)
    this.ruleFormModel.ssh_commands = (rule.ssh_commands && rule.ssh_commands.length)
  ? rule.ssh_commands
  : [''];


    // Patch conditions
    this.ruleFormModel.condition = (rule.condition || []).map((group: any) => {
      return {
        logic: group.logic || 'AND',
        filters: (group.filters || []).map((f: any) => ({
          field: f.field || '',
          operator: f.operator || '',
          value: f.value || '',
          logicWithNext: f.logicWithNext || 'AND'
        }))
      };
    });
  }


  generateESQuery(): any {
    const groupQueries = this.ruleFormModel.condition.map((group: any) => {
      const logic = group.logic?.toLowerCase() === 'or' ? 'should' : 'must';
      const filters = group.filters || [];

      const filterQueries = filters.map((filter: any) => this.convertFilterToDSL(filter));

      return {
        bool: {
          [logic]: filterQueries
        }
      };
    });

    return {
      query: {
        bool: {
          must: groupQueries
        }
      }
    };
  }

  private convertFilterToDSL(filter: any): any {
    const field = filter.field;
    const operator = filter.operator;
    const rawValue = filter.value;

    const values: string[] = Array.isArray(rawValue)
      ? rawValue
      : (rawValue || '').split(',').map((v: string) => v.trim());

    const keywordFields = [
      'host.name',
      'host.ip',
      'host.ip.keyword',
      'event.code',
      'user.name',
      'file.path',
      'process.name',
      'process.executable',
      'source.ip',
      'destination.ip',
      'winlog.event_id',
      'winlog.provider_name',
      'agent.name'
    ];

    const textFields = [
      'message',
      'process.command_line',
      'file.extension',
      'url.full',
      'http.request.body.content',
      'user_agent.original',
      'event.action'
    ];

    const useKeyword = keywordFields.includes(field) && !field.endsWith('.keyword');
    const fieldForTerm = useKeyword ? `${field}.keyword` : field;
    const fieldForText = textFields.includes(field) ? field : fieldForTerm;

    switch (operator) {
      case 'exists':
        return { exists: { field } };

      case 'does not exist':
        return { bool: { must_not: { exists: { field } } } };

      case 'is':
        return { term: { [fieldForTerm]: rawValue } };

      case 'is not':
        return { bool: { must_not: { term: { [fieldForTerm]: rawValue } } } };

      case 'is one of':
        return { terms: { [fieldForTerm]: values } };

      case 'is not one of':
        return { bool: { must_not: { terms: { [fieldForTerm]: values } } } };

      case 'contains':
        return { match_phrase: { [fieldForText]: `*${rawValue}*` } };

      // case 'starts with':
      //   return { match_phrase: { [fieldForText]: `${rawValue}*`} };

      // case 'ends with':
      //   return { match_phrase: { [fieldForText]: `*${rawValue}`} };

      default:
        return { match: { [fieldForText]: { query: rawValue, case_insensitive: true } } };
    }
  }

  convertToSeconds(value: number, unit: string): number {
    switch (unit) {
      case 'minutes': return value * 60;
      case 'hours': return value * 3600;
      case 'days': return value * 86400;
      default: return value;
    }
  }

  convertFromSeconds(seconds: number): { value: number; unit: string } {
    if (seconds % 86400 === 0) {
      return { value: seconds / 86400, unit: 'days' };
    } else if (seconds % 3600 === 0) {
      return { value: seconds / 3600, unit: 'hours' };
    } else if (seconds % 60 === 0) {
      return { value: seconds / 60, unit: 'minutes' };
    } else {
      return { value: seconds, unit: 'seconds' };
    }
  }

  addSSHCommand() {
    this.ruleFormModel.ssh_commands.push('');
  }

  removeSSHCommand(index: number) {
    if (this.ruleFormModel.ssh_commands.length > 1) {
      this.ruleFormModel.ssh_commands.splice(index, 1);
    }
  }

  trackByIndex(index: number, obj: any): any {
  return index;
}

// Add linked rule function
addLinkedRule(): void {
  // Add an empty string to the linkedRules array
  this.ruleFormModel.linkedRules.push('');
}

// Remove linked rule function
removeLinkedRule(index: number): void {
  // Check if the index is valid and array has items
  if (index >= 0 && index < this.ruleFormModel.linkedRules.length) {
    this.ruleFormModel.linkedRules.splice(index, 1);
  }
}

// Optional: Clear all linked rules
clearAllLinkedRules(): void {
  this.ruleFormModel.linkedRules = [];
}

// Optional: Check if a rule is already linked (to prevent duplicates)
isRuleAlreadyLinked(ruleId: string): boolean {
  return this.ruleFormModel.linkedRules.includes(ruleId);
}

// Optional: Get linked rule names for display
// getLinkedRuleNames(): string[] {
//   return this.ruleFormModel.linkedRules
//     .map(ruleId => {
//       const rule = this.availableRules.find(r => r.rule_id === ruleId);
//       return rule ? rule.name : 'Unknown Rule';
//     })
//     .filter(name => name !== 'Unknown Rule');
// }

}
