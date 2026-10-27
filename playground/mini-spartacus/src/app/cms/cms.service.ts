import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { distinctUntilChanged, filter, first, map, switchMap } from 'rxjs/operators';
import { DebugLogService } from '../debug/debug-log.service';
import { CmsComponent, ContentSlotData, Page, PageContext, serializePageContext } from './model';
import { OccFakeBackend } from './occ-fake-backend';
import { normalizeCmsPage } from './occ-cms-page.normalizer';
import { RoutingService } from './routing.service';

/**
 * NgRx の cms ストア + CmsService(Facade)を 1 クラスに畳んだもの。
 * 形は本家の State と同じ: pageIndex(context → pageId)、pages(pageId → Page)、components(uid → 本体)。
 * 本家: core-libs/core/src/cms/store/cms-state.ts、cms/facade/cms.service.ts
 */
export interface CmsState {
  pageIndex: Record<string, string>;
  pages: Record<string, Page>;
  components: Record<string, CmsComponent>;
}

@Injectable({ providedIn: 'root' })
export class CmsService {
  private backend = inject(OccFakeBackend);
  private routing = inject(RoutingService);
  private log = inject(DebugLogService);

  readonly state$ = new BehaviorSubject<CmsState>({ pageIndex: {}, pages: {}, components: {} });

  /**
   * Guard から呼ばれる。index にあれば HTTP なしで返す(= 本家 hasPage → getPageState)。
   * 無ければ cms/pages を取りに行き、Normalizer を通して State に入れる。
   */
  getPage(ctx: PageContext): Observable<Page | null> {
    const key = serializePageContext(ctx);
    const s = this.state$.value;
    if (s.pageIndex[key]) {
      this.log.state(`hasPage(${key}) = true → HTTP なし`);
      return of(s.pages[s.pageIndex[key]]);
    }
    this.log.state(`hasPage(${key}) = false → cms/pages を取得`);
    return this.backend.loadPage(ctx).pipe(
      first(),
      map((occ) => {
        if (!occ) {
          return null;
        }
        const { page, components } = normalizeCmsPage(occ);
        const prev = this.state$.value;
        this.state$.next({
          pageIndex: { ...prev.pageIndex, [key]: page.pageId },
          pages: { ...prev.pages, [page.pageId]: page },
          components: {
            ...prev.components,
            ...Object.fromEntries(components.map((c) => [c.uid, c])),
          },
        });
        this.log.state(`State 更新: pageIndex[${key}] = ${page.pageId}, components +${components.length}`);
        return page;
      })
    );
  }

  /** 表示中ページ。PageContext が変わるたびに、その index → page を引き直す */
  getCurrentPage(): Observable<Page> {
    return this.routing.getPageContext().pipe(
      switchMap((ctx) =>
        this.state$.pipe(
          map((s) => s.pages[s.pageIndex[serializePageContext(ctx)]]),
          filter((p): p is Page => !!p),
          distinctUntilChanged()
        )
      )
    );
  }

  /** 表示中ページの、ある position のスロット。ヘッダーもフッターもこれで引く */
  getContentSlot(position: string): Observable<ContentSlotData> {
    return this.getCurrentPage().pipe(map((p) => p.slots[position] ?? { components: [] }));
  }

  /** コンポーネント本体。ページ応答に同梱されていたものは State に入っている */
  getComponentData<T extends CmsComponent>(uid: string): Observable<T> {
    return this.state$.pipe(
      map((s) => s.components[uid] as T | undefined),
      filter((c): c is T => !!c),
      distinctUntilChanged()
    );
  }
}
