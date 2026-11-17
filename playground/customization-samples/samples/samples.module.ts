// 29 章のサンプルをまとめて登録するモジュール。AppModule の imports に 1 行足すだけで全部が効く
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { inject, NgModule, provideAppInitializer } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CmsConfig, ProductAdapter, ProductPageMetaResolver, PRODUCT_NORMALIZER, provideConfig } from '@spartacus/core';
import { provideOutlet, OutletPosition } from '@spartacus/storefront';
import { sampleConfigProviders } from './h2-config.providers';
import { SampleShippingNoteComponent } from './h4-shipping-note.component';
import { SampleProductAdapter } from './h5-product.adapter';
import { SampleProductPageMetaResolver } from './h5-product-page-meta.resolver';
import { SampleProductNormalizer } from './h6-product.normalizer';
import { SampleHelloPageComponent } from './h7-hello-page.component';
import { SampleTimingInterceptor } from './h7-timing.interceptor';
import { SampleCartAddedMessageService } from './h8-cart-added-message.service';
import { SampleProductIntroComponent } from './k3-product-intro.component';

@NgModule({
  imports: [
    // H7: CMS に無いページ
    RouterModule.forChild([{ path: 'sample/hello', component: SampleHelloPageComponent }]),
  ],
  providers: [
    // H2: 設定(URL・文言)
    ...sampleConfigProviders,
    // H2 の cmsComponents: 部品の差し替え(K3)
    provideConfig(<CmsConfig>{
      cmsComponents: { ProductIntroComponent: { component: SampleProductIntroComponent } },
    }),
    // H4: 差し込み
    provideOutlet({
      id: 'ProductAddToCartComponent',
      position: OutletPosition.BEFORE,
      component: SampleShippingNoteComponent,
    }),
    // H5: 置き換え(Adapter、PageMetaResolver)
    { provide: ProductAdapter, useClass: SampleProductAdapter },
    { provide: ProductPageMetaResolver, useExisting: SampleProductPageMetaResolver },
    // H6: 追加(Normalizer)
    { provide: PRODUCT_NORMALIZER, useClass: SampleProductNormalizer, multi: true },
    // H7: HTTP インターセプター
    { provide: HTTP_INTERCEPTORS, useClass: SampleTimingInterceptor, multi: true },
    // H8: イベントの購読を起動時に始める
    provideAppInitializer(() => inject(SampleCartAddedMessageService).start()),
  ],
})
export class SamplesModule {}
