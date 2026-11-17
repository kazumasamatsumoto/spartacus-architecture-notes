// H5 DI の置き換え: 本体は PageMetaResolver の multi に `useExisting: ProductPageMetaResolver`
// で登録している(core/product/product.module.ts:17-21)。
// クラスのトークン ProductPageMetaResolver を置き換えれば、その multi の中身も自作になる
import { Injectable } from '@angular/core';
import { ProductPageMetaResolver } from '@spartacus/core';
import { Observable, map } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class SampleProductPageMetaResolver extends ProductPageMetaResolver {
  override resolveTitle(): Observable<string> {
    return super.resolveTitle().pipe(map((title) => `[H5 meta] ${title}`));
  }
}
