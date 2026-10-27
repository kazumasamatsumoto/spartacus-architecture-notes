import { AsyncPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CmsComponentData } from '../cms/cms-component-data';
import { CmsComponent } from '../cms/model';
import { ProbePipe } from '../debug/probe.pipe';
import { Traced } from './traced';

interface CmsBanner extends CmsComponent {
  headline: string;
  content: string;
  productCode: string;
}

/** typeCode: SimpleBannerComponent。CMS のプロパティは @Input ではなく CmsComponentData から */
@Component({
  selector: 'app-banner',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [AsyncPipe, RouterLink, ProbePipe],
  template: `{{ 'Banner' | probe }}
    @if (data$ | async; as d) {
      <a class="banner" [routerLink]="['/product', d.productCode]">
        <strong>{{ d.headline }}</strong>
        <span>{{ d.content }}</span>
      </a>
    }`,
})
export class BannerComponent extends Traced {
  readonly data$ = inject(CmsComponentData<CmsBanner>).data$;
  constructor() {
    super('Banner');
  }
}
