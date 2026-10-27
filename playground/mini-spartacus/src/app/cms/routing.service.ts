import { Injectable, inject } from '@angular/core';
import { ActivatedRouteSnapshot, NavigationEnd, Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';
import { distinctUntilChanged, filter } from 'rxjs/operators';
import { DebugLogService } from '../debug/debug-log.service';
import { PageContext, serializePageContext } from './model';

/**
 * URL → PageContext の変換規則。本家 router.reducer.ts:169-215。
 * クエリパラメータは見ない。だから ?sortCode=... が変わっても PageContext は変わらない。
 */
export function getPageContextFromRoute(route: ActivatedRouteSnapshot): PageContext {
  const code = route.params['code'];
  if (code) {
    return { type: 'ProductPage', id: code };
  }
  const segments = route.url.map((s) => s.path);
  if (segments.length === 0) {
    return { type: 'ContentPage', id: 'homepage' };
  }
  return { type: 'ContentPage', id: segments.join('/') };
}

/** 本家 RoutingService の getPageContext / getNextPageContext の最小版 */
@Injectable({ providedIn: 'root' })
export class RoutingService {
  private log = inject(DebugLogService);
  private current$ = new BehaviorSubject<PageContext | undefined>(undefined);
  private next?: PageContext;

  constructor(router: Router) {
    router.events.pipe(filter((e) => e instanceof NavigationEnd)).subscribe((e) => {
      this.log.nav(`NavigationEnd ${e.urlAfterRedirects}`);
      if (this.next) {
        this.current$.next(this.next);
      }
    });
  }

  /** Guard が「これから表示するページ」を先に登録する */
  setNextPageContext(ctx: PageContext): void {
    this.next = ctx;
  }

  /** 表示中ページの PageContext。同じ値なら流さない */
  getPageContext(): Observable<PageContext> {
    return this.current$.pipe(
      filter((c): c is PageContext => !!c),
      distinctUntilChanged((a, b) => serializePageContext(a) === serializePageContext(b))
    );
  }
}
