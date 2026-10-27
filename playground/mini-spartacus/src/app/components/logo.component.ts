import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ProbePipe } from '../debug/probe.pipe';
import { Traced } from './traced';

/** typeCode: SiteLogoComponent。CMS データは使わないが、置き場所は CMS が決める */
@Component({
  selector: 'app-logo',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink, ProbePipe],
  template: `{{ 'Logo' | probe }}<a routerLink="/" class="logo">MiniStore</a>`,
})
export class LogoComponent extends Traced {
  constructor() {
    super('Logo');
  }
}
