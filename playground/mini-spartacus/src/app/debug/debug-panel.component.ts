import { ChangeDetectionStrategy, Component, ElementRef, NgZone, OnInit, ViewChild, inject } from '@angular/core';
import { combineLatest } from 'rxjs';
import { CmsService } from '../cms/cms.service';
import { ProductSearchService, ProductService } from '../components/product.services';
import { DebugLogService, LogEntry } from './debug-log.service';

/**
 * 画面下の固定パネル。左: ログ、右: State(DevTools の代わり)。
 * 観測が観測対象を汚さないように、Angular の変更検知を使わず DOM を直接書く。
 * (zone 外で detectChanges しても v18 以降はアプリ全体の tick が予約されてしまうため)
 */
@Component({
  selector: 'app-debug-panel',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="bar">
      <strong>観測パネル</strong>
      <span>左: 何が起きたか(NAV 遷移 / HTTP / STATE / LIFE 生成破棄 / CD 変更検知)。右: State</span>
      <button (click)="clear()">ログを消す</button>
    </div>
    <div class="cols">
      <ol class="log" #log></ol>
      <pre class="state" #state></pre>
    </div>
  `,
})
export class DebugPanelComponent implements OnInit {
  @ViewChild('log', { static: true }) logEl!: ElementRef<HTMLOListElement>;
  @ViewChild('state', { static: true }) stateEl!: ElementRef<HTMLPreElement>;

  private log = inject(DebugLogService);
  private cms = inject(CmsService);
  private search = inject(ProductSearchService);
  private products = inject(ProductService);
  private zone = inject(NgZone);
  private rendered = 0;

  ngOnInit(): void {
    this.zone.runOutsideAngular(() => {
      this.log.entries$.subscribe((entries) => this.renderLog(entries));
      combineLatest([this.cms.state$, this.search.results$, this.products.state$]).subscribe(
        ([cms, results, products]) => {
          this.stateEl.nativeElement.textContent = JSON.stringify(
            {
              cms: {
                pageIndex: cms.pageIndex,
                pages: Object.fromEntries(
                  Object.values(cms.pages).map((p) => [
                    p.pageId,
                    {
                      template: p.template,
                      slots: Object.fromEntries(
                        Object.entries(p.slots).map(([pos, s]) => [pos, s.components.map((c) => c.uid)])
                      ),
                    },
                  ])
                ),
                components: Object.keys(cms.components),
              },
              productSearch: results ? { sortCode: results.sortCode, count: results.products.length } : null,
              products: Object.keys(products),
            },
            null,
            1
          );
        }
      );
    });
  }

  private renderLog(entries: LogEntry[]): void {
    const ol = this.logEl.nativeElement;
    if (entries.length === 0 || (entries[0]?.id ?? 0) > this.rendered + 1) {
      ol.replaceChildren();
      this.rendered = entries.length ? entries[0].id - 1 : 0;
    }
    for (const e of entries) {
      if (e.id <= this.rendered) {
        continue;
      }
      const li = document.createElement('li');
      li.className = e.kind;
      const badge = document.createElement('span');
      badge.className = 'badge';
      badge.textContent = e.kind;
      li.append(badge, e.text);
      ol.append(li);
      this.rendered = e.id;
    }
    ol.scrollTop = ol.scrollHeight;
  }

  clear() {
    this.log.clear();
    this.rendered = 0;
    this.logEl.nativeElement.replaceChildren();
  }
}
