import { Component } from '@angular/core';

@Component({
  selector: 'app-rule-hits',
  templateUrl: './rule-hits.component.html',
  styleUrls: ['./rule-hits.component.scss']
})
export class RuleHitsComponent {
  rules = [
    { name: 'Too Many 500 Errors', count: 12 },
    { name: 'Postgres Connection Fail', count: 7 }
  ];
}
