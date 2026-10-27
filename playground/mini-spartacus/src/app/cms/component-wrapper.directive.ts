import {
  ChangeDetectorRef,
  ComponentRef,
  Directive,
  Injector,
  Input,
  OnDestroy,
  OnInit,
  ViewContainerRef,
  inject,
} from '@angular/core';
import { DebugLogService } from '../debug/debug-log.service';
import { CmsComponentData } from './cms-component-data';
import { cmsComponents } from './cms-config';
import { CmsService } from './cms.service';
import { ContentSlotComponentData } from './model';

/**
 * スロット内の 1 要素 {uid, flexType} を Angular コンポーネントに変える場所。
 * 本家 component-wrapper.directive.ts:81-117 + default-component.handler.ts:56-70
 * やっていることは 3 つ:
 *  1. flexType で表④(cmsComponents)を引いてクラスを得る
 *  2. CmsComponentData を provide した子 Injector を作る(= @Input の代わり)
 *  3. ViewContainerRef.createComponent で、この ng-container の位置に生成する
 */
@Directive({ selector: '[appComponentWrapper]' })
export class ComponentWrapperDirective implements OnInit, OnDestroy {
  @Input({ required: true, alias: 'appComponentWrapper' }) component!: ContentSlotComponentData;

  private vcr = inject(ViewContainerRef);
  private injector = inject(Injector);
  private cd = inject(ChangeDetectorRef); // = ホストである PageSlot の view
  private cms = inject(CmsService);
  private log = inject(DebugLogService);
  private ref?: ComponentRef<unknown>;

  ngOnInit(): void {
    const { uid, flexType } = this.component;
    const type = cmsComponents[flexType];
    if (!type) {
      this.log.life(`× ${uid}: flexType "${flexType}" は cmsComponents に無い → 何も描かない(エラーにもならない)`);
      return;
    }
    const injector = Injector.create({
      providers: [
        { provide: CmsComponentData, useValue: new CmsComponentData(uid, this.cms.getComponentData(uid)) },
      ],
      parent: this.injector,
    });
    this.ref = this.vcr.createComponent(type, { injector });
    (this.ref.location.nativeElement as HTMLElement).setAttribute('data-cms-uid', uid);
    this.cd.markForCheck(); // 本家 :112
  }

  ngOnDestroy(): void {
    this.ref?.destroy();
  }
}
