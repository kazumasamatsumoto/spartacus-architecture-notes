import { AsyncPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input, OnInit, inject } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { distinctUntilChanged, map, switchMap } from 'rxjs/operators';
import { DebugLogService } from '../debug/debug-log.service';
import { ProbePipe } from '../debug/probe.pipe';
import { CmsService } from './cms.service';
import { layoutConfig } from './layout-config';
import { PageSlotComponent } from './page-slot.component';

/**
 * ルーターが唯一出すコンポーネント。かつ header / footer としても使う。
 * 本家 core-libs/storefront/cms-structure/page/page-layout/page-layout.component.ts
 *  - section が無ければ「表示中ページの template 名」で表②を引く
 *  - section があれば section 名で表②を引く(header / footer)
 *  - どちらも「表②の並び」と「ページが実際に持つスロット」の積集合(本家 page-layout.service.ts:106-127)
 */
@Component({
  selector: 'app-page-layout',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [AsyncPipe, PageSlotComponent, ProbePipe],
  host: { '[attr.section]': 'section ?? "main"' },
  template: `{{ 'PageLayout[' + (section ?? 'main') + ']' | probe }}
    @for (slot of slots$ | async; track slot) {
      <app-page-slot [position]="slot" />
    }`,
})
export class PageLayoutComponent implements OnInit {
  private section$ = new BehaviorSubject<string | undefined>(undefined);
  private cms = inject(CmsService);
  private log = inject(DebugLogService);

  @Input() set section(v: string | undefined) {
    this.section$.next(v);
  }
  get section(): string | undefined {
    return this.section$.value;
  }

  readonly slots$: Observable<string[]> = this.section$.pipe(
    switchMap((section) =>
      this.cms.getCurrentPage().pipe(
        map((page) => {
          const name = section ?? page.template;
          const slots = (layoutConfig[name] ?? []).filter((s) => s in page.slots);
          this.log.state(`PageLayout[${section ?? 'main'}]: layoutConfig[${name}] ∩ page.slots = [${slots.join(', ')}]`);
          return slots;
        })
      )
    ),
    distinctUntilChanged((a, b) => a.join() === b.join())
  );

  ngOnInit(): void {
    this.log.life(`created PageLayout[${this.section ?? 'main'}]`);
  }
}
