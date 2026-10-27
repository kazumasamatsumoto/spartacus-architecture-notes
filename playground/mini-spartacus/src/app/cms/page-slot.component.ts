import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  Input,
  OnDestroy,
  OnInit,
  inject,
} from '@angular/core';
import { Subscription } from 'rxjs';
import { distinctUntilChanged } from 'rxjs/operators';
import { DebugLogService } from '../debug/debug-log.service';
import { ProbePipe } from '../debug/probe.pipe';
import { ComponentWrapperDirective } from './component-wrapper.directive';
import { CmsService } from './cms.service';
import { ContentSlotComponentData, ContentSlotData } from './model';

/**
 * 表③: position → そのページのスロット内コンポーネント配列。
 * 本家 core-libs/storefront/cms-structure/page/slot/page-slot.component.ts
 *  - 手動購読して components を差し替え、markForCheck(本家 :124-130)
 *  - uid の並びが同じなら流さない(本家 isDistinct :201-213)。ヘッダーが作り直されない理由
 *  - *ngFor(ここでは @for)が ComponentWrapperDirective を 1 要素ずつ生やす
 */
@Component({
  selector: 'app-page-slot',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ComponentWrapperDirective, ProbePipe],
  host: { '[attr.position]': 'position', class: 'slot' },
  template: `{{ 'PageSlot[' + position + ']' | probe }}
    @for (c of components; track c) {
      <ng-container [appComponentWrapper]="c" />
    }`,
})
export class PageSlotComponent implements OnInit, OnDestroy {
  @Input({ required: true }) position!: string;

  components: ContentSlotComponentData[] = [];

  private cms = inject(CmsService);
  private cd = inject(ChangeDetectorRef);
  private log = inject(DebugLogService);
  private sub?: Subscription;

  ngOnInit(): void {
    this.sub = this.cms
      .getContentSlot(this.position)
      .pipe(distinctUntilChanged(isDistinct))
      .subscribe((slot) => {
        this.components = slot.components;
        this.log.state(`PageSlot[${this.position}] ← [${slot.components.map((c) => c.uid).join(', ')}]`);
        this.cd.markForCheck();
      });
  }

  ngOnDestroy(): void {
    this.sub?.unsubscribe();
  }
}

/** 本家 isDistinct: 長さと uid の並びが同じなら「同じ」とみなす */
function isDistinct(old: ContentSlotData, cur: ContentSlotData): boolean {
  return (
    old.components.length === cur.components.length &&
    old.components.every((c, i) => c.uid === cur.components[i]?.uid)
  );
}
