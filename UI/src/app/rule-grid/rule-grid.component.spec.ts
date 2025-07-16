import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RuleGridComponent } from './rule-grid.component';

describe('RuleGridComponent', () => {
  let component: RuleGridComponent;
  let fixture: ComponentFixture<RuleGridComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RuleGridComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RuleGridComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
