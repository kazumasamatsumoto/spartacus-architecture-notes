import { Injectable, NgZone, afterEveryRender, inject } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type LogKind = 'NAV' | 'HTTP' | 'STATE' | 'LIFE' | 'CD';
export interface LogEntry {
  id: number;
  kind: LogKind;
  text: string;
}

/**
 * 画面下のパネルに出すログ。アプリの本体とは無関係。
 * CD(変更検知)の行は「その tick でテンプレートが実際に評価された view」の一覧。
 * パネル自身の更新は Angular の zone の外で行い、tick を起こさない(観測が観測対象を汚さないため)。
 */
@Injectable({ providedIn: 'root' })
export class DebugLogService {
  readonly entries$ = new BehaviorSubject<LogEntry[]>([]);

  private zone = inject(NgZone);
  private buffer: LogEntry[] = [];
  private checkedInThisTick: string[] = [];
  private tickNo = 0;
  private seq = 0;
  private scheduled = false;

  constructor() {
    // 1 回の変更検知(tick)が終わるたびに、評価された view をまとめて 1 行にする
    afterEveryRender(() => this.closeTick());
  }

  nav(text: string) { this.push('NAV', text); }
  http(text: string) { this.push('HTTP', text); }
  state(text: string) { this.push('STATE', text); }
  life(text: string) { this.push('LIFE', text); }

  /** ProbePipe から、テンプレート評価中に呼ばれる */
  checked(name: string) {
    if (!this.checkedInThisTick.includes(name)) {
      this.checkedInThisTick.push(name);
    }
  }

  clear() {
    this.entries$.next([]);
  }

  private closeTick() {
    if (this.checkedInThisTick.length === 0) {
      return;
    }
    this.tickNo++;
    this.push('CD', `tick #${this.tickNo} で評価された view: ${this.checkedInThisTick.join(' › ')}`);
    this.checkedInThisTick = [];
  }

  private push(kind: LogKind, text: string) {
    this.buffer.push({ id: ++this.seq, kind, text });
    if (!this.scheduled) {
      this.scheduled = true;
      this.zone.runOutsideAngular(() => setTimeout(() => this.flush(), 0));
    }
  }

  private flush() {
    this.scheduled = false;
    const batch = this.buffer;
    this.buffer = [];
    this.entries$.next([...this.entries$.value, ...batch].slice(-200));
  }
}
