import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { RuleGridComponent } from './rule-grid/rule-grid.component';
import { EventGridComponent } from './event-grid/event-grid.component';
import { RuleConfigComponent } from './rule-config/rule-config.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';import { EventGenerateComponent } from './event-generate/event-generate.component';

const routes: Routes = [
  { path: 'rule-grid', component: RuleGridComponent },
  { path: 'event-viewer', component: EventGridComponent },
  { path: 'rule-config', component: RuleConfigComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'event-generate', component: EventGenerateComponent },
  { path: '', redirectTo: 'rule-grid', pathMatch: 'full' },
  { path: '**', redirectTo: 'rule-grid' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
