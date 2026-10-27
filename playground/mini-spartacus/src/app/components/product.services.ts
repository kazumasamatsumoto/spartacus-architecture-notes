import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { distinctUntilChanged, filter, map } from 'rxjs/operators';
import { OccFakeBackend } from '../cms/occ-fake-backend';
import { Product, SearchResults } from '../cms/model';
import { DebugLogService } from '../debug/debug-log.service';

/** 本家 ProductSearchService + product-search ストア。条件が前回と同じなら呼ばない(本家 searchIfCriteriaHasChanged) */
@Injectable({ providedIn: 'root' })
export class ProductSearchService {
  readonly results$ = new BehaviorSubject<SearchResults | null>(null);
  private backend = inject(OccFakeBackend);
  private log = inject(DebugLogService);

  search(sortCode: string): void {
    if (this.results$.value?.sortCode === sortCode) {
      this.log.state(`products/search: 前回と同じ sort=${sortCode} → 呼ばない`);
      return;
    }
    this.backend.searchProducts(sortCode).subscribe((r) => this.results$.next(r));
  }
}

/** 本家 ProductService + product ストア。code ごとに 1 回だけ取る(Entity Loader の最小版) */
@Injectable({ providedIn: 'root' })
export class ProductService {
  readonly state$ = new BehaviorSubject<Record<string, Product>>({});
  private loading = new Set<string>();
  private backend = inject(OccFakeBackend);
  private log = inject(DebugLogService);

  get(code: string): Observable<Product> {
    if (!this.state$.value[code] && !this.loading.has(code)) {
      this.loading.add(code);
      this.backend.getProduct(code).subscribe((p) => {
        this.loading.delete(code);
        if (p) {
          this.state$.next({ ...this.state$.value, [code]: p });
        }
      });
    } else if (this.state$.value[code]) {
      this.log.state(`products/${code}: State にある → 呼ばない`);
    }
    return this.state$.pipe(
      map((s) => s[code]),
      filter((p): p is Product => !!p),
      distinctUntilChanged()
    );
  }
}
