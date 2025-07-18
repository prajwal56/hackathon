import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EventGenerateComponent } from './event-generate.component';

describe('EventGenerateComponent', () => {
  let component: EventGenerateComponent;
  let fixture: ComponentFixture<EventGenerateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EventGenerateComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EventGenerateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
