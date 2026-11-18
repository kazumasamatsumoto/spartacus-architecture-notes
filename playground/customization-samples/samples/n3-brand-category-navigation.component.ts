// 29-2 C: 親の CategoryNavigationComponent を自作に差し替え、子のリンクを自分のテンプレートで描く
//
// 本物の <img>(alt を持つ、CMS の Media を使う)を出したいときはこの方法になる。
// cx-navigation-ui のテンプレートには outlet が無く、{{ node.title }} の文字しか出せないため
// (navigation-ui.component.html:34-60)。木の組み立てと一括取得は、本体の NavigationService をそのまま使う。
// 代わりに、cx-navigation-ui が持っていたフライアウトやキーボード操作は失われる
import { AsyncPipe, NgTemplateOutlet } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { CmsNavigationComponent, CmsService } from '@spartacus/core';
import { CmsComponentData, GenericLinkComponent, NavigationNode, NavigationService } from '@spartacus/storefront';
import { combineLatest } from 'rxjs';
import { filter, map, switchMap } from 'rxjs/operators';
import { sampleBrandLogo } from './n-brand-logos';

@Component({
  selector: 'app-sample-brand-category-navigation',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [AsyncPipe, NgTemplateOutlet, GenericLinkComponent],
  template: `
    @if (view$ | async; as v) {
      <nav class="sample-nav" aria-label="Category (29-2 C)">
        <ng-container *ngTemplateOutlet="tree; context: { $implicit: v.node.children, items: v.items }" />
      </nav>
    }
    <ng-template #tree let-nodes let-items="items">
      <ul>
        @for (n of nodes; track $index) {
          <li>
            @if (n.url) {
              <cx-generic-link [url]="n.url">
                @if (logoOf(n, items); as src) {
                  <img [src]="src" alt="" width="20" height="20" />
                }
                {{ n.title }}
              </cx-generic-link>
            } @else {
              <span>{{ n.title }}</span>
            }
            @if (n.children?.length) {
              <ng-container *ngTemplateOutlet="tree; context: { $implicit: n.children, items: items }" />
            }
          </li>
        }
      </ul>
    </ng-template>
  `,
  styles: `
    .sample-nav > ul { display: flex; flex-wrap: wrap; gap: 0 24px; padding: 8px 16px; margin: 0; }
    ul { list-style: none; padding-inline-start: 12px; }
    img { vertical-align: middle; margin-inline-end: 6px; }
  `,
})
export class SampleBrandCategoryNavigationComponent {
  private data$ = inject(CmsComponentData<CmsNavigationComponent>).data$;
  private cmsService = inject(CmsService);

  view$ = combineLatest([
    inject(NavigationService).getNavigationNode(this.data$),
    this.data$.pipe(
      filter(Boolean),
      switchMap((data) => this.cmsService.getNavigationEntryItems((data.navigationNode ?? data).uid ?? '')),
      filter(Boolean)
    ),
  ]).pipe(map(([node, items]) => ({ node, items: Object.values(items) as any[] })));

  logoOf(node: NavigationNode, items: any[]): string | undefined {
    const item = node.url ? items.find((it) => it.url && it.url === node.url) : undefined;
    return item?.logoUrl ?? sampleBrandLogo(item);
  }
}
