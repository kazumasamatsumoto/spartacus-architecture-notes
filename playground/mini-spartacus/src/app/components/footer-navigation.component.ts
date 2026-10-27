import { ChangeDetectionStrategy, Component } from '@angular/core';
import { ProbePipe } from '../debug/probe.pipe';
import { Traced } from './traced';

/** typeCode: FooterNavigationComponent */
@Component({
  selector: 'app-footer-navigation',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ProbePipe],
  template: `{{ 'FooterNav' | probe }}<small>© MiniStore. このフッターも cms/pages 応答の Footer スロットから来ている</small>`,
})
export class FooterNavigationComponent extends Traced {
  constructor() {
    super('FooterNav');
  }
}
