import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ProbePipe } from '../debug/probe.pipe';
import { Traced } from './traced';

/** typeCode: SearchBoxComponent */
@Component({
  selector: 'app-search-box',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink, ProbePipe],
  template: `{{ 'SearchBox' | probe }}<a routerLink="/search" class="searchbox">🔍 商品を探す(/search へ)</a>`,
})
export class SearchBoxComponent extends Traced {
  constructor() {
    super('SearchBox');
  }
}
