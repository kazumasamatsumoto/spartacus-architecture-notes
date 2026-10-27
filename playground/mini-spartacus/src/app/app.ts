import { Component } from '@angular/core';
import { DebugPanelComponent } from './debug/debug-panel.component';
import { ProbePipe } from './debug/probe.pipe';
import { StorefrontComponent } from './storefront.component';

/** 本家の app.component.html も <cx-storefront></cx-storefront> の 1 行 */
@Component({
  selector: 'app-root',
  imports: [StorefrontComponent, DebugPanelComponent, ProbePipe],
  template: `{{ 'App' | probe }}<app-storefront /><app-debug-panel class="debug" />`,
})
export class App {}
