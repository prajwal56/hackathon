import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WidgetRendererComponent } from './widget-renderer.component';

describe('WidgetRendererComponent', () => {
  let component: WidgetRendererComponent;
  let fixture: ComponentFixture<WidgetRendererComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WidgetRendererComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(WidgetRendererComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
