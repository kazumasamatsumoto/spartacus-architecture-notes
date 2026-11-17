// H6 DI の追加(全部を順に使う): PRODUCT_NORMALIZER に 1 つ足す
// 本体の変換(OCC の JSON → Product)は残ったまま、自作が後ろに加わる
import { Injectable } from '@angular/core';
import { Converter, Product } from '@spartacus/core';

declare module '@spartacus/core' {
  interface Product {
    sampleBadge?: string;
  }
}

@Injectable()
export class SampleProductNormalizer implements Converter<any, Product> {
  convert(source: any, target: Product = {}): Product {
    // 価格を含む scope の応答のときだけ付ける(他の scope で上書きしないため)
    const price = source?.price?.value;
    if (typeof price === 'number') {
      target.sampleBadge = price >= 500 ? 'Premium' : 'Value';
    }
    return target;
  }
}
