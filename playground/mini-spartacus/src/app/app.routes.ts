import { Routes } from '@angular/router';
import { cmsPageGuard } from './cms/cms-page.guard';
import { PageLayoutComponent } from './cms/page-layout.component';

/**
 * ルート表はこれだけ。どの URL でも出てくるのは PageLayoutComponent。
 *  - 商品ページ: パスのパターンだけフロント設定(本家 product-details-page.module.ts:17-23、パス文字列は RoutingConfig)
 *  - それ以外: ** 1 本(本家 add-cms-route.ts:12-16)。URL ごとの対応表は CMS 側にある
 */
export const routes: Routes = [
  { path: 'product/:code', canActivate: [cmsPageGuard], component: PageLayoutComponent },
  { path: '**', canActivate: [cmsPageGuard], component: PageLayoutComponent },
];
