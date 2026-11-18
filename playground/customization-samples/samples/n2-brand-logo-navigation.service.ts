// 29-2 B: NavigationService を差し替え、組み立て済みの node に「アイコンの印」を書き足す
//
// 子のリンクの属性は、本体の populateLink が 5 項目(linkName・url・target・styleClasses・styleAttributes)
// だけを node に書き写し、残りは捨てる(navigation.service.ts:166-193)。populateLink は private で上書きできない。
// そこで public の getNavigationNode を上書きし、本体が作った node と、書き写される前の取得結果(items)を
// 突き合わせて、アイコンを styleClasses と styleAttributes(CSS 変数)に入れ直す
import { Injectable } from '@angular/core';
import { CmsNavigationComponent } from '@spartacus/core';
import { NavigationNode, NavigationService } from '@spartacus/storefront';
import { combineLatest, Observable } from 'rxjs';
import { filter, map, switchMap } from 'rxjs/operators';
import { sampleBrandLogo } from './n-brand-logos';

@Injectable({ providedIn: 'root' })
export class SampleBrandLogoNavigationService extends NavigationService {
  override getNavigationNode(data$: Observable<CmsNavigationComponent>): Observable<NavigationNode> {
    const node$ = super.getNavigationNode(data$);
    if (!data$) {
      return node$;
    }
    // 本体と同じキーで、書き写される前の取得結果を読む(navigation.service.ts:54-56)
    const items$ = data$.pipe(
      filter(Boolean),
      switchMap((data) =>
        this.cmsService.getNavigationEntryItems((data.navigationNode ?? data).uid ?? '')
      ),
      filter(Boolean)
    );
    return combineLatest([node$, items$]).pipe(
      map(([node, items]) => this.withLogos(node, Object.values(items)))
    );
  }

  private withLogos(node: NavigationNode, items: any[]): NavigationNode {
    // node には uid が残らないので、url で元の item を探す
    const item = node.url ? items.find((it) => it.url && it.url === node.url) : undefined;
    // 本番ではバックエンドが足した属性を使う。デモの OCC には無いので仮のアイコンを作る
    const logo: string | undefined = item?.logoUrl ?? sampleBrandLogo(item);
    const result: NavigationNode = { ...node };
    if (logo) {
      result.styleClasses = [node.styleClasses, 'sample-brand-logo'].filter(Boolean).join(' ');
      result.styleAttributes = [node.styleAttributes, `--sample-brand-logo: url("${logo}")`]
        .filter(Boolean)
        .join('; ');
    }
    if (node.children) {
      result.children = node.children.map((child) => this.withLogos(child, items));
    }
    return result;
  }
}
