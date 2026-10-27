import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { PageLayoutComponent } from './cms/page-layout.component';
import { ProbePipe } from './debug/probe.pipe';

/**
 * 固定の外枠。本家 core-libs/storefront/layout/main/storefront.component.html
 * プロジェクトのフロント担当が書くのは app.html の <app-storefront /> 1 行だけで、この外枠はライブラリ側。
 * header / footer は静的 HTML ではなく、section 付きの PageLayout = 表示中ページの cms/pages 応答から引く。
 * 本家と同じく Default 戦略(指定なし)。
 */
@Component({
  selector: 'app-storefront',
  imports: [RouterOutlet, PageLayoutComponent, ProbePipe],
  template: `{{ 'Storefront' | probe }}
    <header><app-page-layout section="header" /></header>
    <main><router-outlet /></main>
    <footer><app-page-layout section="footer" /></footer>`,
})
export class StorefrontComponent {}
