# 付録

## 付録 A. OCC エンドポイントとデモで観測した URL の対応

| 定義(`default-cms-config.ts:13-16`) | 観測 URL |
|---|---|
| `users/${userId}/cms/pages` | `users/anonymous/cms/pages?lang=en&curr=USD`(ホーム)、`...?pageType=ProductPage&code=300938` |
| `users/${userId}/cms/components` | `users/anonymous/cms/components?fields=DEFAULT&currentPage=0&pageSize=26&componentIds=...` |

`fields` は `OccCmsComponentAdapter.findComponentsByIds` の既定引数 `'DEFAULT'`(`occ-cms-component.adapter.ts:51-68`)。ページ側に `fields` は付かない。

---

## 付録 B. `cms/pages`(homepage)レスポンスの構造(curl, 2026-10-23)

```
top keys: uid, uuid, title, template(LandingPage2Template), typeCode(ContentPage), name, robotTag, contentSlots, label
slots: 19
  Section1          SimpleResponsiveBannerComponent ×2
  Section2A/2B      SimpleResponsiveBannerComponent ×2 ずつ
  Section2C         MerchandisingCarouselComponent
  Section3          ProductCarouselComponent ×2
  Section4          SimpleResponsiveBannerComponent ×4
  Section5          SimpleResponsiveBannerComponent
  BottomHeaderSlot  CMSFlexComponent(flexType=PageTitleComponent)
  NavigationBar     CategoryNavigationComponent
  MiniCart          MiniCartComponent
  SiteContext       CMSSiteContextComponent ×2, CMSFlexComponent(SiteThemeSwitcherComponent)
  SiteLogo          SimpleBannerComponent
  Footer            FooterNavigationComponent, CMSFlexComponent ×2, CMSParagraphComponent
  SiteLinks         CMSLinkComponent ×4
  SearchBox         SearchBoxComponent
  HomepageNavLink   CMSLinkComponent
  HeaderLinks / TopHeaderSlot / PlaceholderContentSlot  (空)
components inline: 33  (すべて typeCode・uid・各属性を含む完全なデータ)
```

---

## 付録 C. 参照したリポジトリ内ドキュメント

- `spartacus/core-libs/skills/skills/spartacus-developer/references/cms-component-wiring.md` — マッピング登録・上書き・`CmsComponentData` の使い方・アンチパターン(Angular ルートに置かない)
- `spartacus/core-libs/skills/skills/spartacus-developer/references/placement-mechanisms.md` — CMS 配置 / アウトレット / 静的 `cmsStructure` の使い分け
- `spartacus/core-libs/skills/skills/spartacus-developer/references/lazy-loading.md`, `configuration.md`, `outlets.md`

---

[目次](README.md) | ← [15. 業務データを扱うカスタムコンポーネント: Facade / Connector / Adapter の作り方](15-facade-connector-adapter.md)
