import { AsyncPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input, OnDestroy, OnInit, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';
import { distinctUntilChanged, map } from 'rxjs/operators';
import { Product } from '../cms/model';
import { ProbePipe } from '../debug/probe.pipe';
import { ProductSearchService } from './product.services';
import { Traced } from './traced';

/** 一覧の 1 行。track が同一性なので、ソートで新しい配列が来ると全部作り直される(LIFE ログで見える) */
@Component({
  selector: 'app-product-tile',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink, ProbePipe],
  template: `{{ 'Tile(' + product.code + ')' | probe }}
    <a class="tile" [routerLink]="['/product', product.code]">
      <span>{{ product.name }}</span><b>\${{ product.price }}</b>
    </a>`,
})
export class ProductTileComponent extends Traced {
  @Input({ required: true }) product!: Product;
  constructor() {
    super('Tile');
  }
}

/**
 * typeCode: CMSProductListComponent。本家 ProductListComponent は Default 戦略なのでここも Default。
 *  - URL の ?sortCode を購読し、変わったら products/search(本家 searchByRouting$)
 *  - ソートの select は router.navigate([], { queryParams }) を呼ぶだけ(本家 :280-284)
 *    → URL は変わるが path は同じ → PageContext 同じ → Guard も cms/pages も走らない
 */
@Component({
  selector: 'app-product-list',
  changeDetection: ChangeDetectionStrategy.Default,
  imports: [AsyncPipe, ProductTileComponent, ProbePipe],
  template: `{{ 'ProductList' | probe }}
    @if (model$ | async; as model) {
      <div class="sort">
        並び替え:
        <select [value]="model.sortCode" (change)="sort($any($event.target).value)">
          <option value="relevance">関連度</option>
          <option value="name-asc">名前順</option>
          <option value="price-asc">価格が安い順</option>
          <option value="price-desc">価格が高い順</option>
        </select>
        <small>(URL の ?sortCode= が変わる。cms/pages は呼ばれない)</small>
      </div>
      @for (p of model.products; track p) {
        <app-product-tile [product]="p" />
      }
    } @else {
      <p>読み込み中…</p>
    }`,
})
export class ProductListComponent extends Traced implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private search = inject(ProductSearchService);
  private sub?: Subscription;

  readonly model$ = this.search.results$;

  constructor() {
    super('ProductList');
  }

  ngOnInit(): void {
    this.sub = this.route.queryParamMap
      .pipe(
        map((q) => q.get('sortCode') ?? 'relevance'),
        distinctUntilChanged()
      )
      .subscribe((sortCode) => this.search.search(sortCode));
  }

  sort(sortCode: string): void {
    this.log.nav(`router.navigate([], { queryParams: { sortCode: '${sortCode}' } })`);
    this.router.navigate([], { queryParams: { sortCode }, queryParamsHandling: 'merge', relativeTo: this.route });
  }

  override ngOnDestroy(): void {
    this.sub?.unsubscribe();
    super.ngOnDestroy();
  }
}
