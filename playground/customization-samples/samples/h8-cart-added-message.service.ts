// H8 イベント: カートに入ったことを EventService で受け取り、画面にメッセージを出す
// カートの機能は遅延ロードされるが、イベントの型は root(@spartacus/cart/base/root)にあるので購読できる
import { DestroyRef, inject, Injectable } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CartAddEntrySuccessEvent } from '@spartacus/cart/base/root';
import { EventService, GlobalMessageService, GlobalMessageType } from '@spartacus/core';

@Injectable({ providedIn: 'root' })
export class SampleCartAddedMessageService {
  private events = inject(EventService);
  private messages = inject(GlobalMessageService);
  private destroyRef = inject(DestroyRef);

  start(): void {
    this.events
      .get(CartAddEntrySuccessEvent)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((e) => {
        const text = `[H8 event] ${e.productCode} x${e.quantityAdded ?? e.quantity} added`;
        console.log(text);
        // 確認メッセージは数秒で消える(GlobalMessageConfig の timeout)
        this.messages.add(text, GlobalMessageType.MSG_TYPE_CONFIRMATION);
      });
  }
}
