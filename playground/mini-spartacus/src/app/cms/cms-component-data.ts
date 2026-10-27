import { Observable } from 'rxjs';
import { CmsComponent } from './model';

/**
 * 動的に作られたコンポーネントが CMS データを受け取る唯一の入口。
 * @Input ではなく DI で渡す。本家 core-libs/storefront/cms-structure/page/model/cms-component-data.ts
 */
export class CmsComponentData<T extends CmsComponent = CmsComponent> {
  constructor(
    public readonly uid: string,
    public readonly data$: Observable<T>
  ) {}
}
