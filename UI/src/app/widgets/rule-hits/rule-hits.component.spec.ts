import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RuleHitsComponent } from './rule-hits.component';

describe('RuleHitsComponent', () => {
  let component: RuleHitsComponent;
  let fixture: ComponentFixture<RuleHitsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RuleHitsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RuleHitsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
