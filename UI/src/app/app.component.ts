import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  constructor(private router: Router) {}

  goToRuleGrid() {
    this.router.navigate(['/rule-grid']);
  }

  goToEventViewer() {
    this.router.navigate(['/event-viewer']);
  }
   goToEventGenarator(){
    this.router.navigate(['/event-generate']);
  }
}
