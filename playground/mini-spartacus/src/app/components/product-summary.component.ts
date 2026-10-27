import { AsyncPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { map, switchMap } from 'rxjs/operators';
import { ProbePipe } from '../debug/probe.pipe';
import { ProductService } from './product.services';
import { Traced } from './traced';

/**
 * typeCode: ProductSummaryComponent。CMS データは使わず、URL の :code から商品を引く。
 * 商品 A → 商品 B の遷移では、このコンポーネントは作り直されず、product$ の値だけ変わる。
 */
@Component({
  selector: 'app-product-summary',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [AsyncPipe, RouterLink, ProbePipe],
  template: `{{ 'ProductSummary' | probe }}
    @if (product$ | async; as p) {
      <div class="summary">
        <h2>{{ p.name }}</h2>
        <p>code: {{ p.code }} / \${{ p.price }}</p>
        <a routerLink="/search">← 一覧へ</a>
        <p class="others">
          他の商品へ(同じルート、:code だけ変わる):
          @for (code of codes; track code) {
            <a [routerLink]="['/product', code]">{{ code }}</a>
          }
        </p>
      </div>
    } @else {
      <p>商品を読み込み中…</p>
    }`,
})
export class ProductSummaryComponent extends Traced {
  private route = inject(ActivatedRoute);
  private products = inject(ProductService);

  readonly codes = ['1934793', '300938', '3557133', '816802', '1382080'];

  readonly product$ = this.route.paramMap.pipe(
    map((p) => p.get('code')!),
    switchMap((code) => this.products.get(code))
  );

  constructor() {
    super('ProductSummary');
  }
}
