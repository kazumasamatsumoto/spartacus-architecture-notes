import { inject } from '@angular/core';
import { CanActivateFn } from '@angular/router';
import { of } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { DebugLogService } from '../debug/debug-log.service';
import { CmsService } from './cms.service';
import { PageContext, serializePageContext } from './model';
import { routingConfig } from './routing-config';
import { RoutingService, getPageContextFromRoute } from './routing.service';

/**
 * 本家 CmsPageGuard(core-libs/storefront/cms-structure/guards/cms-page.guard.ts)の最小版。
 * 1. URL から PageContext を作る
 * 2. CMS にそのページがあるか聞く。既定(loadStrategy=ALWAYS)では State にあっても取り直す
 * 3. あれば通す。無ければ notFound ページを読み込んで、URL はそのままで通す
 * Angular 標準では Guard は「通す/通さない」だけ。ここでは「ページの中身を先に取る」仕事も兼ねている。
 */
export const cmsPageGuard: CanActivateFn = (route, state) => {
  const routing = inject(RoutingService);
  const cms = inject(CmsService);
  const log = inject(DebugLogService);

  const ctx = getPageContextFromRoute(route);
  log.nav(`CmsPageGuard: ${state.url} → PageContext ${serializePageContext(ctx)}`);
  routing.setNextPageContext(ctx);

  const shouldReload = routingConfig.loadStrategy !== 'ONCE'; // 本家 cms-page.guard.ts:89-91
  return cms.getPage(ctx, shouldReload).pipe(
    switchMap((page) => {
      if (page) {
        return of(true);
      }
      const notFound: PageContext = { type: 'ContentPage', id: 'notFound' };
      log.nav(`ページ無し → notFound ページを表示(URL は変えない)`);
      routing.setNextPageContext(notFound);
      return cms.getPage(notFound, shouldReload).pipe(map(() => true));
    })
  );
};
