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
    alert: {
      severity: null,
      type: ''
    }
  };

  ruleId: string | null = null;
  isLoading = false;
  indexOptions = [];
  fieldOptions = [];
  operatorOptions = [];
  severityOptions = [];
  typeOptions = [];
  readonly separatorKeysCodes: number[] = [ENTER, COMMA];
  service_list = []
  rule_list = []
  resource_list = []
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
    const payload = {
      name: this.ruleFormModel.name,
      index: this.ruleFormModel.index,
      description: this.ruleFormModel.description,
      condition: this.generateESQuery(),
      alert: {
        severity: this.ruleFormModel.alert.severity,
      },
      business_service_details : this.ruleFormModel.business_service_details
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
    this.ruleFormModel.alert = {
      severity: rule.alert?.severity || '',
      type: rule.alert?.type || ''
    };
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
        return { wildcard: { [fieldForText]: { value: `*${rawValue}*`, case_insensitive: true } } };

      case 'starts with':
        return { wildcard: { [fieldForText]: { value: `${rawValue}*`, case_insensitive: true } } };

      case 'ends with':
        return { wildcard: { [fieldForText]: { value: `*${rawValue}`, case_insensitive: true } } };

      default:
        return { match: { [fieldForText]: { query: rawValue, case_insensitive: true } } };
    }
  }
}
