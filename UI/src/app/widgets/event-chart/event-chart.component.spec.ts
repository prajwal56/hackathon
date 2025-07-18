import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EventChartComponent } from './event-chart.component';

describe('EventChartComponent', () => {
  let component: EventChartComponent;
  let fixture: ComponentFixture<EventChartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EventChartComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EventChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
