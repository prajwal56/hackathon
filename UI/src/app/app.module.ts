import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { RuleGridComponent } from './rule-grid/rule-grid.component';
import { RuleConfigComponent } from './rule-config/rule-config.component';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { EventViewerComponent } from './event-viewer/event-viewer.component';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatTableModule } from '@angular/material/table';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatChipsModule } from '@angular/material/chips';
import { MatSelectModule } from '@angular/material/select';
import { HttpClientModule } from '@angular/common/http';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { NgSelectModule } from '@ng-select/ng-select';
import { EventGridComponent } from './event-grid/event-grid.component';
// import { FormsModule } from '@angular/forms'
// import { ReactiveFormsModule } from '@angular/forms';
// import { MatChipsModule } from '@angular/material/chips';
// import { MatIconModule } from '@angular/material/icon';
// import { MatInputModule } from '@angular/material/input';
import { MatDialogModule } from '@angular/material/dialog';
import { EventGenerateComponent } from './event-generate/event-generate.component';

import { DashboardComponent } from './components/dashboard/dashboard.component';
import { WidgetRendererComponent } from './components/widget-renderer/widget-renderer.component';
import { ErrorSummaryComponent } from './widgets/error-summary/error-summary.component';
import { RuleHitsComponent } from './widgets/rule-hits/rule-hits.component';
import { GridsterModule } from 'angular-gridster2';
import { EventChartComponent } from './widgets/event-chart/event-chart.component';
import { NgxEchartsModule } from 'ngx-echarts';
import { RuleDonutComponent } from './widgets/rule-donut/rule-donut.component';
import { SafeHtmlPipe } from './safe-html.pipe';
@NgModule({
  declarations: [
    AppComponent,
    RuleGridComponent,
    RuleConfigComponent,
    EventViewerComponent,
    EventGridComponent,
    DashboardComponent,
    WidgetRendererComponent,
    ErrorSummaryComponent,
    RuleHitsComponent,
    EventChartComponent,
    RuleDonutComponent,
    EventGenerateComponent,
    SafeHtmlPipe
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    MatToolbarModule,
    MatButtonModule,
    BrowserAnimationsModule,
    MatCardModule,
    MatIconModule,
    MatTooltipModule,
    MatPaginatorModule,
    MatTableModule,
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatExpansionModule,
    MatChipsModule,
    MatSelectModule,
    HttpClientModule,
    MatSnackBarModule,
    MatDividerModule,
    MatAutocompleteModule,
    NgSelectModule,
    MatDialogModule,
    GridsterModule,
     NgxEchartsModule.forRoot({
      echarts: () => import('echarts')
    })
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
