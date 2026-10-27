import { Directive, OnDestroy, inject } from '@angular/core';
import { DebugLogService } from '../debug/debug-log.service';

/** 生成・破棄をログに出すだけの土台。本家には無い(観測用) */
@Directive()
export abstract class Traced implements OnDestroy {
  protected log = inject(DebugLogService);
  protected constructor(public readonly traceName: string) {
    this.log.life(`created ${traceName}`);
  }
  ngOnDestroy(): void {
    this.log.life(`destroyed ${this.traceName}`);
  }
}
