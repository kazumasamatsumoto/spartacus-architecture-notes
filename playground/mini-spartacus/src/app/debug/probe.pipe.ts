import { Pipe, PipeTransform, inject } from '@angular/core';
import { DebugLogService } from './debug-log.service';

/**
 * 観測用。impure なので「このテンプレートが評価されたとき」に必ず呼ばれる。
 * OnPush で飛ばされた view では呼ばれない。何も描かない。
 */
@Pipe({ name: 'probe', pure: false })
export class ProbePipe implements PipeTransform {
  private log = inject(DebugLogService);
  transform(name: string): string {
    this.log.checked(name);
    return '';
  }
}
