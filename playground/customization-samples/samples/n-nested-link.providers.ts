// 29-2 のサンプルの切り替え。3 つは同じリンクを別の方法で変えるので、1 つずつ有効にする
//   'css'     … A: n1-brand-logo.scss だけ(providers は無し)
//   'service' … B: NavigationService を差し替える
//   'parent'  … C: CategoryNavigationComponent を差し替える
import { Provider } from '@angular/core';
import { CmsConfig, provideConfig } from '@spartacus/core';
import { NavigationService } from '@spartacus/storefront';
import { SampleBrandLogoNavigationService } from './n2-brand-logo-navigation.service';
import { SampleBrandCategoryNavigationComponent } from './n3-brand-category-navigation.component';

export const NESTED_LINK_SAMPLE: 'css' | 'service' | 'parent' = 'css';

export function nestedLinkProviders(mode: 'css' | 'service' | 'parent'): Provider[] {
  switch (mode) {
    case 'service':
      // NavigationService は providedIn: 'root'(navigation.service.ts:19)。ルートで差し替えると、
      // ヘッダー・フッターなど、このサービスを使う全部のナビゲーションに効く
      return [{ provide: NavigationService, useExisting: SampleBrandLogoNavigationService }];
    case 'parent':
      return [
        provideConfig(<CmsConfig>{
          cmsComponents: { CategoryNavigationComponent: { component: SampleBrandCategoryNavigationComponent } },
        }),
      ];
    default:
      return [];
  }
}
