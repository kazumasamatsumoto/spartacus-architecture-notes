import { Type } from '@angular/core';
import { BannerComponent } from '../components/banner.component';
import { FooterNavigationComponent } from '../components/footer-navigation.component';
import { LogoComponent } from '../components/logo.component';
import { ParagraphComponent } from '../components/paragraph.component';
import { ProductListComponent } from '../components/product-list.component';
import { ProductSummaryComponent } from '../components/product-summary.component';
import { SearchBoxComponent } from '../components/search-box.component';

/**
 * 表④: typeCode(flexType)→ Angular クラス。フロント側の設定。
 * 本家は各モジュールが provideDefaultConfig({ cmsComponents: {...} }) で分散登録し、
 * ConfigModule が 1 つに deepMerge する(core-libs/core/src/cms/config/cms-config.ts)。
 * バックエンドで新しい typeCode を作ったら、フロントに頼むのはこの表への 1 行追加。
 */
export const cmsComponents: Record<string, Type<unknown>> = {
  SiteLogoComponent: LogoComponent,
  SearchBoxComponent: SearchBoxComponent,
  SimpleBannerComponent: BannerComponent,
  CMSParagraphComponent: ParagraphComponent,
  CMSProductListComponent: ProductListComponent,
  ProductSummaryComponent: ProductSummaryComponent,
  FooterNavigationComponent: FooterNavigationComponent,
};
