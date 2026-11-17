// H7 Angular の標準: CMS に無いページをルートで足す
// URL はサイトの接頭辞の後ろ(/electronics-spa/en/USD/sample/hello)
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { UrlModule } from '@spartacus/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-sample-hello-page',
  standalone: true,
  imports: [RouterLink, UrlModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section class="container">
      <h1>[H7 route] Hello from a non-CMS page</h1>
      <!-- H2 で変えた routing.routes.product.paths が、作るリンクに効く -->
      <a [routerLink]="{ cxRoute: 'product', params: { code: '358639', name: 'DSC-N1' } } | cxUrl">
        Product link built from routing config
      </a>
    </section>
  `,
})
export class SampleHelloPageComponent {}
