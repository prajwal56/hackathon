import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { RuleGridComponent } from './rule-grid/rule-grid.component';
import { EventViewerComponent } from './event-viewer/event-viewer.component';
import { RuleConfigComponent } from './rule-config/rule-config.component';

const routes: Routes = [
  { path: 'rule-grid', component: RuleGridComponent },
  { path: 'event-viewer', component: EventViewerComponent },
  { path: 'rule-config', component: RuleConfigComponent },
  { path: '', redirectTo: 'rule-grid', pathMatch: 'full' },
  { path: '**', redirectTo: 'rule-grid' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
