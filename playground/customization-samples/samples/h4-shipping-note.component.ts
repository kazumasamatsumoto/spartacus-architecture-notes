// H4 差し込み: PDP の「カートに追加」部品の前に、1 行足す
// 部品の flexType(通常の部品は typeCode と同じ)がアウトレットの名前になる
// (sf/cms-structure/page/slot/page-slot.component.html:9)
import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-sample-shipping-note',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<p class="sample-note">[H4 outlet] Free shipping over $100</p>`,
  styles: [`.sample-note { margin: 0 0 8px; padding: 4px 8px; border-left: 4px solid var(--cx-color-primary); }`],
})
export class SampleShippingNoteComponent {}
