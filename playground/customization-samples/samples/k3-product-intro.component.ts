// H2 の cmsComponents で部品を差し替える(K3)
// キーは CMS の応答の flexType "ProductIntroComponent"(デモの PDP の Summary スロット)
// H6 の Normalizer が足した sampleBadge をここで表示する
import { AsyncPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { CurrentProductService } from '@spartacus/storefront';

@Component({
  selector: 'app-sample-product-intro',
  standalone: true,
  imports: [AsyncPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (product$ | async; as product) {
      <h1 class="sample-title">{{ product.name }}</h1>
      <p>
        [K3 component] code {{ product.code }}
        @if (product.sampleBadge) {
          <span class="sample-badge">[H6 normalizer] {{ product.sampleBadge }}</span>
        }
      </p>
    }
  `,
  styles: [`.sample-badge { margin-left: 8px; padding: 2px 6px; color: #fff; background: var(--cx-color-primary); border-radius: 4px; }`],
})
export class SampleProductIntroComponent {
  product$ = inject(CurrentProductService).getProduct();
}
