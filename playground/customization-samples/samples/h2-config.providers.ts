// H2 設定: provideConfig の断片は 1 つの Config に深くマージされる(29.3)
// K7 URL: 商品ページのリンクを /item/... で作る(受け付けるパスもこれに変わる)
// K6 文言: 「Add to cart」ボタンの文言だけを上書きする(他の翻訳はそのまま)
import { provideConfig, RoutingConfig, I18nConfig } from '@spartacus/core';

export const sampleConfigProviders = [
  provideConfig(<RoutingConfig>{
    routing: {
      routes: {
        product: { paths: ['item/:productCode/:name', 'item/:productCode'] },
      },
    },
  }),
  provideConfig(<I18nConfig>{
    i18n: {
      resources: {
        en: { product: { addToCart: { addToCart: 'Add to cart (sample)' } } },
      },
    },
  }),
];
