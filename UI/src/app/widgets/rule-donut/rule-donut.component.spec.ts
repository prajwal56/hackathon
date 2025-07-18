import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RuleDonutComponent } from './rule-donut.component';

describe('RuleDonutComponent', () => {
  let component: RuleDonutComponent;
  let fixture: ComponentFixture<RuleDonutComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RuleDonutComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RuleDonutComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
