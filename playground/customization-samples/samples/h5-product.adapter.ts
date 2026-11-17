// H5 DI の置き換え: 取得先(Adapter)を替える
// ここでは OCC の Adapter を継承し、呼ばれた scope を記録するだけにしている。
// 別の API から取るなら、この 2 つのメソッドの中身を書き換える
//
// 注意: 商品詳細ページは複数の scope をまとめて取るために loadMany() を呼ぶ。
// 本体の loadMany() は load() を経由しない(core/occ/adapters/product/occ-product.adapter.ts:29-57)。
// load() だけを替えても、商品詳細ページでは何も起きない
import { Injectable } from '@angular/core';
import { OccProductAdapter, Product, ScopedProductData } from '@spartacus/core';
import { Observable } from 'rxjs';

@Injectable()
export class SampleProductAdapter extends OccProductAdapter {
  override load(productCode: string, scope?: string): Observable<Product> {
    console.log(`[H5 adapter] load ${productCode} scope=${scope}`);
    return super.load(productCode, scope);
  }

  override loadMany(products: ScopedProductData[]): ScopedProductData[] {
    console.log(`[H5 adapter] loadMany ${products.map((p) => `${p.code}:${p.scope}`).join(', ')}`);
    return super.loadMany(products);
  }
}
