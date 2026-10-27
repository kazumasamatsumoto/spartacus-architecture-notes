import { AsyncPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { CmsComponentData } from '../cms/cms-component-data';
import { CmsComponent } from '../cms/model';
import { ProbePipe } from '../debug/probe.pipe';
import { Traced } from './traced';

interface CmsParagraph extends CmsComponent {
  content: string;
}

/** typeCode: CMSParagraphComponent。本家 paragraph.component.ts とほぼ同じ */
@Component({
  selector: 'app-paragraph',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [AsyncPipe, ProbePipe],
  template: `{{ 'Paragraph(' + uid + ')' | probe }}<div class="paragraph" [innerHTML]="(data$ | async)?.content"></div>`,
})
export class ParagraphComponent extends Traced {
  private cmsData = inject(CmsComponentData<CmsParagraph>);
  readonly uid = this.cmsData.uid;
  readonly data$ = this.cmsData.data$;
  constructor() {
    super('Paragraph');
  }
}
