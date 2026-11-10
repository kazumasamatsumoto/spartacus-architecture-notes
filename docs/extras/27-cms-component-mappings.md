# 付録 27: Spartacus に登録されている CMS コンポーネントの対応表

> 27 章の付録。Spartacus `b7b028f`(2612.0.0)の全ソースから、`cmsComponents` に書かれた対応を [`tools/cms-mapping-keys.js`](../../tools/cms-mapping-keys.js) で抜き出した(テスト・e2e・schematics は除く)。**キー**は OCC の `typeCode`。ただし `CMSFlexComponent` は `flexType`、`JspIncludeComponent` は `uid` がキーになる(`core-libs/core/src/occ/adapters/cms/converters/occ-cms-page-normalizer.ts:151-158`)

- 対応の行数: 258(キーの種類は 229)
- 同じキーが 2 か所以上で登録されているもの: 23 種類(「重複」列)。B2B・OPF・CDC・My Account V2 などの機能ライブラリが、本体の対応を同じキーで上書きしている。27.2 の M6 と同じ仕組み
- 「他の設定」は、`component` 以外に書かれている項目(`guards`、`data`、`providers`、`childRoutes`、`deferLoading` など)。「(なし)」は `component` を持たず、ほかの設定だけを足している行

[27 章へ戻る](../27-frontend-component-customization-catalog.md)

## core-libs/storefront(46)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `AccountPaymentDetailsComponent` | `PaymentMethodsComponent` | guards | `core-libs/storefront/cms-components/myaccount/payment-methods/payment-methods.module.ts:34` | ×2 |
| `AnonymousConsentManagementBannerComponent` | `AnonymousConsentManagementBannerComponent` | deferLoading | `core-libs/storefront/cms-components/anonymous-consent-management/anonymous-consent-management.module.ts:34` |  |
| `AnonymousConsentOpenDialogComponent` | `AnonymousConsentOpenDialogComponent` |  | `core-libs/storefront/cms-components/anonymous-consent-management/anonymous-consent-management.module.ts:38` |  |
| `BannerComponent` | `BannerComponent` |  | `core-libs/storefront/cms-components/content/banner/banner.module.ts:36` |  |
| `BreadcrumbComponent` | `BreadcrumbComponent` |  | `core-libs/storefront/cms-components/navigation/breadcrumb/breadcrumb.module.ts:31` |  |
| `CMSLinkComponent` | `LinkComponent` |  | `core-libs/storefront/cms-components/content/link/link.module.ts:19` |  |
| `CMSParagraphComponent` | `ParagraphComponent` |  | `core-libs/storefront/cms-components/content/paragraph/paragraph.module.ts:24` |  |
| `CMSProductListComponent` | `ProductListComponent` | data | `core-libs/storefront/cms-components/product/product-list/product-list.module.ts:68` |  |
| `CMSSiteContextComponent` | `SiteContextSelectorComponent` | providers | `core-libs/storefront/cms-components/misc/site-context-selector/site-context-selector.module.ts:36` |  |
| `CMSTabParagraphComponent` | `ParagraphComponent` |  | `core-libs/storefront/cms-components/content/paragraph/paragraph.module.ts:27` |  |
| `CMSTabParagraphContainer` | `TabParagraphContainerComponent` |  | `core-libs/storefront/cms-components/content/tab-paragraph-container/tab-paragraph-container.module.ts:33` |  |
| `CategoryNavigationComponent` | `CategoryNavigationComponent` | data | `core-libs/storefront/cms-components/navigation/category-navigation/category-navigation.module.ts:23` |  |
| `ClaimDialogComponent` | `ClaimDialogComponent` | guards | `core-libs/storefront/cms-components/myaccount/my-coupons/my-coupons.module.ts:76` |  |
| `ConsentManagementComponent` | `MyAccountV2ConsentManagementComponent` |  | `core-libs/storefront/cms-components/myaccount/consent-management/consent-management.module.ts:28` | ×2 |
| `ConsentManagementComponent` | `ConsentManagementComponent` | guards | `core-libs/storefront/cms-components/myaccount/consent-management/consent-management.module.ts:51` | ×2 |
| `CouponClaimComponent` | `CouponClaimComponent` | guards | `core-libs/storefront/cms-components/myaccount/my-coupons/my-coupons.module.ts:72` |  |
| `FooterNavigationComponent` | `FooterNavigationComponent` |  | `core-libs/storefront/cms-components/navigation/footer-navigation/footer-navigation.module.ts:27` |  |
| `HamburgerMenuComponent` | `HamburgerMenuComponent` |  | `core-libs/storefront/layout/header/hamburger-menu/hamburger-menu.module.ts:17` |  |
| `LanguageCurrencyComponent` | `LanguageCurrencyComponent` |  | `core-libs/storefront/cms-components/misc/site-context-selector/site-context-selector.module.ts:46` |  |
| `MyAccountSideNavigationComponent` | `MyAccountV2NavigationComponent` | guards | `core-libs/storefront/cms-components/myaccount/my-account-v2/my-account-v2-navigation/my-account-v2-navigation.module.ts:22` |  |
| `MyCouponsComponent` | `MyCouponsComponent` | guards | `core-libs/storefront/cms-components/myaccount/my-coupons/my-coupons.module.ts:68` |  |
| `MyInterestsComponent` | `MyInterestsComponent` | guards | `core-libs/storefront/cms-components/myaccount/my-interests/my-interests.module.ts:51` |  |
| `NavigationComponent` | `NavigationComponent` |  | `core-libs/storefront/cms-components/navigation/navigation/navigation.module.ts:35` |  |
| `NotificationPreferenceComponent` | `MyAccountV2NotificationPreferenceComponent` |  | `core-libs/storefront/cms-components/myaccount/notification-preference/notification-preference.module.ts:27` | ×2 |
| `NotificationPreferenceComponent` | `NotificationPreferenceComponent` | guards | `core-libs/storefront/cms-components/myaccount/notification-preference/notification-preference.module.ts:53` | ×2 |
| `PDFDocumentComponent` | `PDFComponent` |  | `core-libs/storefront/cms-components/content/pdf/pdf.module.ts:18` |  |
| `PageTitleComponent` | `PageTitleComponent` |  | `core-libs/storefront/cms-components/navigation/page-header/page-title.module.ts:22` |  |
| `ProductCarouselComponent` | `ProductCarouselComponent` |  | `core-libs/storefront/cms-components/product/carousel/product-carousel/product-carousel.module.ts:45` |  |
| `ProductDetailsTabComponent` | `ProductDetailsTabComponent` |  | `core-libs/storefront/cms-components/product/product-tabs/product-details-tab/product-details-tab.module.ts:24` |  |
| `ProductGridComponent` | `ProductListComponent` | data | `core-libs/storefront/cms-components/product/product-list/product-list.module.ts:76` |  |
| `ProductImagesComponent` | `ProductImagesComponent` |  | `core-libs/storefront/cms-components/product/product-images/product-images.module.ts:32` | ×2 |
| `ProductIntroComponent` | `ProductIntroComponent` |  | `core-libs/storefront/cms-components/product/product-intro/product-intro.module.ts:29` |  |
| `ProductReferencesComponent` | `ProductReferencesComponent` |  | `core-libs/storefront/cms-components/product/carousel/product-references/product-references.module.ts:35` |  |
| `ProductRefinementComponent` | `ProductFacetNavigationComponent` |  | `core-libs/storefront/cms-components/product/product-list/product-facet-navigation/product-facet-navigation.module.ts:23` |  |
| `ProductReviewsTabComponent` | `ProductReviewsComponent` |  | `core-libs/storefront/cms-components/product/product-tabs/product-reviews/product-reviews.module.ts:43` |  |
| `ProductSpecsTabComponent` | `ProductAttributesComponent` |  | `core-libs/storefront/cms-components/product/product-tabs/product-attributes/product-attributes.module.ts:18` |  |
| `ProductSummaryComponent` | `ProductSummaryComponent` |  | `core-libs/storefront/cms-components/product/product-summary/product-summary.module.ts:23` |  |
| `RotatingImagesComponent` | `BannerCarouselComponent` |  | `core-libs/storefront/cms-components/content/banner-carousel/banner-carousel.module.ts:25` |  |
| `ScrollToTopComponent` | `ScrollToTopComponent` |  | `core-libs/storefront/cms-components/navigation/scroll-to-top/scroll-to-top.module.ts:18` |  |
| `SearchBoxComponent` | `SearchBoxComponent` |  | `core-libs/storefront/cms-components/navigation/search-box/search-box.module.ts:43` |  |
| `SearchResultsListComponent` | `ProductListComponent` | data | `core-libs/storefront/cms-components/product/product-list/product-list.module.ts:84` |  |
| `SimpleBannerComponent` | `BannerComponent` |  | `core-libs/storefront/cms-components/content/banner/banner.module.ts:39` |  |
| `SimpleResponsiveBannerComponent` | `BannerComponent` |  | `core-libs/storefront/cms-components/content/banner/banner.module.ts:33` |  |
| `SiteThemeSwitcherComponent` | `SiteThemeSwitcherComponent` |  | `core-libs/storefront/cms-components/misc/site-theme-switcher/site-theme-switcher.module.ts:31` |  |
| `StockNotificationComponent` | `StockNotificationComponent` |  | `core-libs/storefront/cms-components/product/stock-notification/stock-notification.module.ts:39` |  |
| `VideoComponent` | `VideoComponent` |  | `core-libs/storefront/cms-components/content/video/video.module.ts:29` |  |

## feature-libs/cart(20)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `AccountSavedCartHistoryComponent` | `SavedCartListComponent` | guards | `feature-libs/cart/saved-cart/components/list/saved-cart-list.module.ts:35` |  |
| `AddToSavedCartsComponent` | `AddToSavedCartComponent` |  | `feature-libs/cart/saved-cart/components/add-to-saved-cart/add-to-saved-cart.module.ts:31` |  |
| `AddToWishListComponent` | `AddToWishListComponent` |  | `feature-libs/cart/wish-list/components/add-to-wishlist/add-to-wish-list.module.ts:39` |  |
| `CartApplyCouponComponent` | `CartCouponComponent` |  | `feature-libs/cart/base/components/cart-coupon/cart-coupon.module.ts:43` |  |
| `CartComponent` | `CartDetailsComponent` |  | `feature-libs/cart/base/components/cart-details/cart-details.module.ts:37` |  |
| `CartProceedToCheckoutComponent` | `CartProceedToCheckoutComponent` |  | `feature-libs/cart/base/components/cart-proceed-to-checkout/cart-proceed-to-checkout.module.ts:31` |  |
| `CartQuickOrderFormComponent` | `CartQuickOrderFormComponent` |  | `feature-libs/cart/quick-order/components/cart-quick-order-form/cart-quick-order-form.module.ts:37` |  |
| `CartTotalsComponent` | `CartTotalsComponent` |  | `feature-libs/cart/base/components/cart-totals/cart-totals.module.ts:18` |  |
| `ClearCartComponent` | `ClearCartComponent` |  | `feature-libs/cart/base/components/clear-cart/clear-cart-button/clear-cart.module.ts:25` |  |
| `ExportOrderEntriesComponent` | `ExportOrderEntriesComponent` |  | `feature-libs/cart/import-export/components/export-entries/export-order-entries.module.ts:26` |  |
| `ImportExportOrderEntriesComponent` | `ImportExportOrderEntriesComponent` |  | `feature-libs/cart/import-export/components/import-export/import-export-order-entries.module.ts:25` |  |
| `ImportOrderEntriesComponent` | `ImportOrderEntriesComponent` |  | `feature-libs/cart/import-export/components/import-to-cart/import-order-entries.module.ts:49` |  |
| `MiniCartComponent` | `MiniCartComponent` |  | `feature-libs/cart/base/components/mini-cart/mini-cart.module.ts:31` |  |
| `ProductAddToCartComponent` | `AddToCartComponent` | data | `feature-libs/cart/base/components/add-to-cart/add-to-cart.module.ts:37` |  |
| `QuickOrderComponent` | `QuickOrderComponent` | data | `feature-libs/cart/quick-order/components/quick-order/quick-order-list.module.ts:55` |  |
| `SaveForLaterComponent` | `SaveForLaterComponent` |  | `feature-libs/cart/base/components/save-for-later/save-for-later.module.ts:23` |  |
| `SavedCartDetailsActionComponent` | `SavedCartDetailsActionComponent` | guards | `feature-libs/cart/saved-cart/components/details/saved-cart-details.module.ts:52` |  |
| `SavedCartDetailsItemsComponent` | `SavedCartDetailsItemsComponent` | guards | `feature-libs/cart/saved-cart/components/details/saved-cart-details.module.ts:48` |  |
| `SavedCartDetailsOverviewComponent` | `SavedCartDetailsOverviewComponent` | guards | `feature-libs/cart/saved-cart/components/details/saved-cart-details.module.ts:44` |  |
| `WishListComponent` | `WishListComponent` | data,guards | `feature-libs/cart/wish-list/components/wish-list-components.module.ts:46` |  |

## feature-libs/checkout(20)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `CheckoutCostCenterComponent` | `CheckoutCostCenterComponent` | guards | `feature-libs/checkout/b2b/components/checkout-cost-center/checkout-cost-center.module.ts:23` |  |
| `CheckoutDeliveryAddress` | `B2BCheckoutDeliveryAddressComponent` | guards | `feature-libs/checkout/b2b/components/checkout-delivery-address/checkout-delivery-address.module.ts:39` | ×2 |
| `CheckoutDeliveryAddress` | `CheckoutDeliveryAddressComponent` | guards | `feature-libs/checkout/base/components/checkout-delivery-address/checkout-delivery-address.module.ts:37` | ×2 |
| `CheckoutDeliveryMode` | `CheckoutDeliveryModeComponent` | data,guards | `feature-libs/checkout/base/components/checkout-delivery-mode/checkout-delivery-mode.module.ts:39` | ×2 |
| `CheckoutOrchestrator` | `CheckoutOrchestratorComponent` | guards | `feature-libs/checkout/base/components/checkout-orchestrator/checkout-orchestrator.module.ts:20` |  |
| `CheckoutOrderSummary` | `CheckoutOrderSummaryComponent` |  | `feature-libs/checkout/base/components/checkout-order-summary/checkout-order-summary.module.ts:18` | ×2 |
| `CheckoutPaymentDetails` | `CheckoutPaymentMethodComponent` | guards | `feature-libs/checkout/base/components/checkout-payment-method/checkout-payment-method.module.ts:36` | ×3 |
| `CheckoutPaymentType` | `CheckoutPaymentTypeComponent` | guards | `feature-libs/checkout/b2b/components/checkout-payment-type/checkout-payment-type.module.ts:30` |  |
| `CheckoutPlaceOrder` | `CheckoutPlaceOrderComponent` | guards | `feature-libs/checkout/base/components/checkout-place-order/checkout-place-order.module.ts:47` | ×2 |
| `CheckoutPlaceOrder` | `CheckoutScheduledReplenishmentPlaceOrderComponent` | guards | `feature-libs/checkout/scheduled-replenishment/components/checkout-place-order/checkout-place-order.module.ts:37` | ×2 |
| `CheckoutProgress` | `CheckoutProgressComponent` | guards | `feature-libs/checkout/base/components/checkout-progress/checkout-progress.module.ts:35` |  |
| `CheckoutProgressMobileBottom` | `CheckoutProgressMobileBottomComponent` | guards | `feature-libs/checkout/base/components/checkout-progress/checkout-progress-mobile-bottom/checkout-progress-mobile-bottom.module.ts:32` |  |
| `CheckoutProgressMobileTop` | `CheckoutProgressMobileTopComponent` | guards | `feature-libs/checkout/base/components/checkout-progress/checkout-progress-mobile-top/checkout-progress-mobile-top.module.ts:32` |  |
| `CheckoutReviewOrder` | `B2BCheckoutReviewSubmitComponent` | guards | `feature-libs/checkout/b2b/components/checkout-review-submit/checkout-review-submit.module.ts:43` | ×3 |
| `CheckoutReviewOrder` | `CheckoutReviewSubmitComponent` | guards | `feature-libs/checkout/base/components/checkout-review-submit/checkout-review-submit.module.ts:41` | ×3 |
| `CheckoutReviewOverview` | `CheckoutReviewOverviewComponent` | guards | `feature-libs/checkout/base/components/checkout-review/checkout-review-overview/checkout-review-overview.module.ts:25` |  |
| `CheckoutReviewPayment` | `CheckoutReviewPaymentComponent` | guards | `feature-libs/checkout/base/components/checkout-review/checkout-review-payment/checkout-review-payment.module.ts:35` |  |
| `CheckoutReviewShipping` | `CheckoutReviewShippingComponent` | guards | `feature-libs/checkout/base/components/checkout-review/checkout-review-shipping/checkout-review-shipping.module.ts:36` |  |
| `CheckoutScheduleReplenishmentOrder` | `CheckoutScheduleReplenishmentOrderComponent` | guards | `feature-libs/checkout/scheduled-replenishment/components/checkout-schedule-replenishment-order/checkout-schedule-replenishment-order.module.ts:29` |  |
| `GuestCheckoutLoginComponent` | `CheckoutLoginComponent` | guards | `feature-libs/checkout/base/components/checkout-login/checkout-login.module.ts:39` |  |

## feature-libs/customer-ticketing(6)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `MyAccountViewRequestsComponent` | `MyAccountV2CustomerTicketingComponent` | guards | `feature-libs/customer-ticketing/components/my-account-v2/my-account-v2-customer-ticketing.module.ts:25` |  |
| `SupportTicketCloseComponent` | `CustomerTicketingCloseComponent` | guards | `feature-libs/customer-ticketing/components/details/customer-ticketing-close/customer-ticketing-close.module.ts:48` |  |
| `SupportTicketDetailsComponent` | `CustomerTicketingDetailsComponent` | guards | `feature-libs/customer-ticketing/components/details/customer-ticketing-details/customer-ticketing-details.module.ts:31` |  |
| `SupportTicketHistoryComponent` | `CustomerTicketingListComponent` | guards | `feature-libs/customer-ticketing/components/list/customer-ticketing-list/customer-ticketing-list.module.ts:42` |  |
| `SupportTicketReopenComponent` | `CustomerTicketingReopenComponent` | guards | `feature-libs/customer-ticketing/components/details/customer-ticketing-reopen/customer-ticketing-reopen.module.ts:44` |  |
| `SupportTicketUpdateComponent` | `CustomerTicketingMessagesComponent` | guards | `feature-libs/customer-ticketing/components/details/customer-ticketing-messages/customer-ticketing-messages.module.ts:35` |  |

## feature-libs/order(37)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `AccountOrderAttachmentsComponent` | `OrderAttachmentsComponent` | guards | `feature-libs/order/components/order-details/order-details.module.ts:168` |  |
| `AccountOrderDetailsActionsComponent` | `MyAccountV2OrderDetailsActionsComponent` |  | `feature-libs/order/components/order-details/order-details.module.ts:82` | ×3 |
| `AccountOrderDetailsActionsComponent` | `OrderDetailActionsComponent` | guards | `feature-libs/order/components/order-details/order-details.module.ts:130` | ×3 |
| `AccountOrderDetailsGroupedItemsComponent` | `OrderDetailItemsComponent` | guards,data | `feature-libs/order/components/order-details/order-details.module.ts:141` |  |
| `AccountOrderDetailsItemsComponent` | `OrderDetailItemsComponent` | guards,data | `feature-libs/order/components/order-details/order-details.module.ts:134` |  |
| `AccountOrderDetailsOverviewComponent` | `OrderOverviewComponent` | guards | `feature-libs/order/components/order-details/order-details.module.ts:153` |  |
| `AccountOrderDetailsReorderComponent` | `OrderDetailReorderComponent` | guards | `feature-libs/order/components/order-details/order-details.module.ts:164` |  |
| `AccountOrderDetailsSimpleOverviewComponent` | `OrderOverviewComponent` | guards,data | `feature-libs/order/components/order-details/order-details.module.ts:157` |  |
| `AccountOrderDetailsTotalsComponent` | `OrderDetailTotalsComponent` | guards | `feature-libs/order/components/order-details/order-details.module.ts:149` | ×2 |
| `AccountOrderDocumentFlowComponent` | `OrderDocumentFlowComponent` | guards | `feature-libs/order/document-flow/components/order-document-flow-components.module.ts:51` |  |
| `AccountOrderHistoryComponent` | `MyAccountV2OrderHistoryComponent` |  | `feature-libs/order/components/order-history/order-history.module.ts:36` | ×2 |
| `AccountOrderHistoryComponent` | `OrderHistoryComponent` | guards | `feature-libs/order/components/order-history/order-history.module.ts:68` | ×2 |
| `AccountReplenishmentHistoryComponent` | `ReplenishmentOrderHistoryComponent` | guards | `feature-libs/order/components/replenishment-order-history/replenishment-order-history.module.ts:37` |  |
| `CancelOrderComponent` | `CancelOrderComponent` | guards,providers | `feature-libs/order/components/amend-order/cancellations/cancel-order/cancel-order.module.ts:40` |  |
| `CancelOrderConfirmationComponent` | `CancelOrderConfirmationComponent` | guards,providers | `feature-libs/order/components/amend-order/cancellations/cancel-order-confirmation/cancel-order-confirmation.module.ts:29` |  |
| `MyAccountViewOrderComponent` | `MyAccountV2OrdersComponent` | guards | `feature-libs/order/components/my-account-v2/my-account-v2-orders.module.ts:36` |  |
| `OrderConfirmationBillingComponent` | `OrderDetailBillingComponent` | providers,guards | `feature-libs/order/components/order-confirmation/order-confirmation.module.ts:120` |  |
| `OrderConfirmationItemsComponent` | `OrderConfirmationItemsComponent` | guards | `feature-libs/order/components/order-confirmation/order-confirmation.module.ts:80` |  |
| `OrderConfirmationOverviewComponent` | `OrderOverviewComponent` | providers,guards | `feature-libs/order/components/order-confirmation/order-confirmation.module.ts:96` |  |
| `OrderConfirmationShippingComponent` | `OrderConfirmationShippingComponent` | guards | `feature-libs/order/components/order-confirmation/order-confirmation.module.ts:116` |  |
| `OrderConfirmationThankMessageComponent` | `OrderConfirmationThankYouMessageComponent` | guards | `feature-libs/order/components/order-confirmation/order-confirmation.module.ts:72` |  |
| `OrderConfirmationTotalsComponent` | `OrderConfirmationTotalsComponent` | guards | `feature-libs/order/components/order-confirmation/order-confirmation.module.ts:88` | ×2 |
| `OrderReturnRequestListComponent` | `OrderReturnRequestListComponent` | guards | `feature-libs/order/components/return-request-list/order-return-request-list.module.ts:34` |  |
| `ReplenishmentConfirmationItemsComponent` | `OrderConfirmationItemsComponent` | guards | `feature-libs/order/components/order-confirmation/order-confirmation.module.ts:84` |  |
| `ReplenishmentConfirmationMessageComponent` | `OrderConfirmationThankYouMessageComponent` | guards | `feature-libs/order/components/order-confirmation/order-confirmation.module.ts:76` |  |
| `ReplenishmentConfirmationOverviewComponent` | `OrderOverviewComponent` | providers,guards | `feature-libs/order/components/order-confirmation/order-confirmation.module.ts:106` |  |
| `ReplenishmentConfirmationTotalsComponent` | `OrderConfirmationTotalsComponent` | guards | `feature-libs/order/components/order-confirmation/order-confirmation.module.ts:92` |  |
| `ReplenishmentDetailActionsComponent` | `ReplenishmentOrderCancellationComponent` |  | `feature-libs/order/components/replenishment-order-details/replenishment-order-details.module.ts:80` |  |
| `ReplenishmentDetailItemsComponent` | `OrderDetailItemsComponent` | providers | `feature-libs/order/components/replenishment-order-details/replenishment-order-details.module.ts:53` |  |
| `ReplenishmentDetailOrderHistoryComponent` | `OrderHistoryComponent` |  | `feature-libs/order/components/replenishment-order-details/replenishment-order-details.module.ts:83` |  |
| `ReplenishmentDetailShippingComponent` | `OrderOverviewComponent` | providers | `feature-libs/order/components/replenishment-order-details/replenishment-order-details.module.ts:71` |  |
| `ReplenishmentDetailTotalsComponent` | `OrderDetailTotalsComponent` | providers | `feature-libs/order/components/replenishment-order-details/replenishment-order-details.module.ts:62` |  |
| `ReturnOrderComponent` | `ReturnOrderComponent` | guards,providers | `feature-libs/order/components/amend-order/returns/return-order/return-order.module.ts:28` |  |
| `ReturnOrderConfirmationComponent` | `ReturnOrderConfirmationComponent` | guards,providers | `feature-libs/order/components/amend-order/returns/return-order-confirmation/return-order-confirmation.module.ts:35` |  |
| `ReturnRequestItemsComponent` | `ReturnRequestItemsComponent` |  | `feature-libs/order/components/return-request-detail/return-request-detail.module.ts:42` |  |
| `ReturnRequestOverviewComponent` | `ReturnRequestOverviewComponent` |  | `feature-libs/order/components/return-request-detail/return-request-detail.module.ts:39` |  |
| `ReturnRequestTotalsComponent` | `ReturnRequestTotalsComponent` |  | `feature-libs/order/components/return-request-detail/return-request-detail.module.ts:45` |  |

## feature-libs/organization(23)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `AccountOrderDetailsApprovalDetailsComponent` | `OrderDetailPermissionResultsComponent` |  | `feature-libs/organization/order-approval/components/details/order-approval-details.module.ts:67` |  |
| `AccountSummaryDocumentComponent` | `AccountSummaryDocumentComponent` | guards | `feature-libs/organization/account-summary/components/details/document/account-summary-document.module.ts:27` |  |
| `AccountSummaryHeaderComponent` | `AccountSummaryHeaderComponent` | guards | `feature-libs/organization/account-summary/components/details/header/account-summary-header.module.ts:21` |  |
| `ManageAccountSummaryListComponent` | `AccountSummaryListComponent` | providers,childRoutes,guards | `feature-libs/organization/account-summary/components/list/account-summary-list.config.ts:49` |  |
| `ManageBudgetsListComponent` | `ListComponent` | providers,childRoutes,guards | `feature-libs/organization/administration/components/budget/budget.config.ts:31` |  |
| `ManageCostCentersListComponent` | `ListComponent` | providers,childRoutes,guards | `feature-libs/organization/administration/components/cost-center/cost-center.config.ts:32` |  |
| `ManagePermissionsListComponent` | `ListComponent` | providers,childRoutes,guards | `feature-libs/organization/administration/components/permission/permission.config.ts:27` |  |
| `ManageUnitsListComponent` | `UnitListComponent` | providers,childRoutes,guards | `feature-libs/organization/administration/components/unit/units.config.ts:53` | ×2 |
| `ManageUserGroupsListComponent` | `ListComponent` | providers,childRoutes,guards | `feature-libs/organization/administration/components/user-group/user-group.config.ts:34` |  |
| `ManageUsersListComponent` | `ListComponent` | providers,childRoutes,guards | `feature-libs/organization/administration/components/user/user.config.ts:43` | ×2 |
| `OrderApprovalDetailApprovalDetailsComponent` | `OrderDetailPermissionResultsComponent` | providers,guards | `feature-libs/organization/order-approval/components/details/order-approval-details.module.ts:57` |  |
| `OrderApprovalDetailFormComponent` | `OrderApprovalDetailFormComponent` | guards | `feature-libs/organization/order-approval/components/details/order-approval-details.module.ts:90` |  |
| `OrderApprovalDetailItemsComponent` | `OrderDetailItemsComponent` | providers,guards | `feature-libs/organization/order-approval/components/details/order-approval-details.module.ts:80` |  |
| `OrderApprovalDetailShippingComponent` | `OrderOverviewComponent` | providers,guards | `feature-libs/organization/order-approval/components/details/order-approval-details.module.ts:70` |  |
| `OrderApprovalDetailTotalsComponent` | `OrderDetailTotalsComponent` | providers,guards | `feature-libs/organization/order-approval/components/details/order-approval-details.module.ts:47` |  |
| `OrderApprovalListComponent` | `OrderApprovalListComponent` | guards | `feature-libs/organization/order-approval/components/list/order-approval-list.module.ts:27` |  |
| `OrganizationUserRegistrationComponent` | `UserRegistrationFormComponent` | guards | `feature-libs/organization/user-registration/components/form/user-registration-form.module.ts:45` |  |
| `RegisterB2BCustomerWithOTPComponent` | `UserRegistrationOTPFormComponent` | guards | `feature-libs/organization/user-registration/components/registration-otp-form/user-registration-otp-form.module.ts:41` |  |
| `UnitLevelOrderDetailsItemsComponent` | `OrderDetailItemsComponent` | guards,providers | `feature-libs/organization/unit-order/components/unit-level-order-detail/unit-level-order-detail.module.ts:31` |  |
| `UnitLevelOrderDetailsOverviewComponent` | `UnitLevelOrderOverviewComponent` | guards | `feature-libs/organization/unit-order/components/unit-level-order-detail/unit-level-order-detail.module.ts:27` |  |
| `UnitLevelOrderDetailsTotalsComponent` | `OrderDetailTotalsComponent` | guards,providers | `feature-libs/organization/unit-order/components/unit-level-order-detail/unit-level-order-detail.module.ts:41` |  |
| `UnitLevelOrderHistoryComponent` | `UnitLevelOrderHistoryComponent` | guards | `feature-libs/organization/unit-order/components/unit-level-order-history/unit-level-order-history.module.ts:43` |  |
| `VerifyOTPForB2BRegistrationComponent` | `RegisterVerificationTokenFormComponent` | guards,providers | `feature-libs/organization/user-registration/components/verification-token-form/verification-token-form.module.ts:53` |  |

## feature-libs/pdf-invoices(1)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `AccountOrderDetailsPDFInvoicesComponent` | `InvoicesListComponent` | guards | `feature-libs/pdf-invoices/components/pdf-invoices-components.module.ts:45` |  |

## feature-libs/pickup-in-store(4)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `CheckoutReviewPickup` | `PickUpItemsDetailsComponent` | data | `feature-libs/pickup-in-store/components/container/pickup-items-details/pickup-items-details.module.ts:42` |  |
| `MyPreferredStoreComponent` | `MyPreferredStoreComponent` |  | `feature-libs/pickup-in-store/components/container/my-preferred-store/my-preferred-store.module.ts:22` |  |
| `OrderConfirmationPickUpComponent` | `PickUpItemsDetailsComponent` | data | `feature-libs/pickup-in-store/components/container/pickup-items-details/pickup-items-details.module.ts:35` |  |
| `PickupInStoreDeliveryModeComponent` | `PickUpItemsDetailsComponent` | data | `feature-libs/pickup-in-store/components/container/pickup-items-details/pickup-items-details.module.ts:49` |  |

## feature-libs/product(4)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `BulkPricingTableComponent` | `BulkPricingTableComponent` |  | `feature-libs/product/bulk-pricing/components/bulk-pricing-table/bulk-pricing-table.module.ts:21` |  |
| `FutureStockComponent` | `FutureStockAccordionComponent` |  | `feature-libs/product/future-stock/components/future-stock-accordion/future-stock-accordion.module.ts:23` |  |
| `ProductImagesComponent` | `ProductImageZoomProductImagesComponent` |  | `feature-libs/product/image-zoom/components/product-image-zoom/product-image-zoom.module.ts:55` | ×2 |
| `ProductVariantSelectorComponent` | `ProductVariantsContainerComponent` | guards | `feature-libs/product/variants/components/product-variants-components.module.ts:26` |  |

## feature-libs/product-configurator(19)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `ConfiguratorAddToCartButton` | `ConfiguratorAddToCartButtonComponent` |  | `feature-libs/product-configurator/rulebased/components/add-to-cart-button/configurator-add-to-cart-button.module.ts:24` |  |
| `ConfiguratorExitButton` | `ConfiguratorExitButtonComponent` |  | `feature-libs/product-configurator/rulebased/components/exit-button/configurator-exit-button.module.ts:22` |  |
| `ConfiguratorForm` | `ConfiguratorFormComponent` |  | `feature-libs/product-configurator/rulebased/components/form/configurator-form.module.ts:25` | ×2 |
| `ConfiguratorForm` | `ConfiguratorGroupComponent` |  | `feature-libs/product-configurator/rulebased/components/group/configurator-group.module.ts:62` | ×2 |
| `ConfiguratorGroupTitle` | `ConfiguratorGroupTitleComponent` |  | `feature-libs/product-configurator/rulebased/components/group-title/configurator-group-title.module.ts:18` |  |
| `ConfiguratorMenu` | `ConfiguratorGroupMenuComponent` |  | `feature-libs/product-configurator/rulebased/components/group-menu/configurator-group-menu.module.ts:24` |  |
| `ConfiguratorOverviewBanner` | `ConfiguratorOverviewNotificationBannerComponent` |  | `feature-libs/product-configurator/rulebased/components/overview-notification-banner/configurator-overview-notification-banner.module.ts:31` |  |
| `ConfiguratorOverviewFilterButton` | `ConfiguratorOverviewFilterButtonComponent` |  | `feature-libs/product-configurator/rulebased/components/overview-filter-button/configurator-overview-filter-button.module.ts:23` |  |
| `ConfiguratorOverviewForm` | `ConfiguratorOverviewFormComponent` |  | `feature-libs/product-configurator/rulebased/components/overview-form/configurator-overview-form.module.ts:31` |  |
| `ConfiguratorOverviewSidebar` | `ConfiguratorOverviewSidebarComponent` |  | `feature-libs/product-configurator/rulebased/components/overview-sidebar/configurator-overview-sidebar.module.ts:25` |  |
| `ConfiguratorPrevNext` | `ConfiguratorPreviousNextButtonsComponent` |  | `feature-libs/product-configurator/rulebased/components/previous-next-buttons/configurator-previous-next-buttons.module.ts:23` |  |
| `ConfiguratorPriceSummary` | `ConfiguratorPriceSummaryComponent` |  | `feature-libs/product-configurator/rulebased/components/price-summary/configurator-price-summary.module.ts:24` |  |
| `ConfiguratorProductTitle` | `ConfiguratorProductTitleComponent` |  | `feature-libs/product-configurator/rulebased/components/product-title/configurator-product-title.module.ts:31` |  |
| `ConfiguratorTabBar` | `ConfiguratorTabBarComponent` |  | `feature-libs/product-configurator/rulebased/components/tab-bar/configurator-tab-bar.module.ts:36` |  |
| `ConfiguratorUpdateMessage` | `ConfiguratorUpdateMessageComponent` |  | `feature-libs/product-configurator/rulebased/components/update-message/configurator-update-message.module.ts:25` |  |
| `ConfiguratorVariantCarousel` | `ConfiguratorVariantCarouselComponent` |  | `feature-libs/product-configurator/rulebased/components/variant-carousel/configurator-variant-carousel.module.ts:27` |  |
| `ConfigureProductComponent` | `ConfigureProductComponent` |  | `feature-libs/product-configurator/common/components/configure-product/configure-product.module.ts:31` |  |
| `CpqConfiguratorConflictAndErrorMessagesComponent` | `ConfiguratorConflictAndErrorMessagesComponent` |  | `feature-libs/product-configurator/rulebased/components/configurator-conflict-and-error-messages/configurator-conflict-and-error-messages.module.ts:31` |  |
| `TextfieldConfigurationForm` | `ConfiguratorTextfieldFormComponent` |  | `feature-libs/product-configurator/textfield/components/textfield-configurator-components.module.ts:40` |  |

## feature-libs/product-multi-dimensional(1)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `ProductMultiDimensionalSelectorComponent` | `ProductMultiDimensionalSelectorComponent` | guards | `feature-libs/product-multi-dimensional/selector/components/selector/product-multi-dimensional-selector-component.module.ts:43` |  |

## feature-libs/qualtrics(2)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `QualtricsComponent` | `QualtricsComponent` |  | `feature-libs/qualtrics/components/qualtrics-components.module.ts:26` |  |
| `QualtricsEmbeddedFeedbackComponent` | `QualtricsEmbeddedFeedbackComponent` |  | `feature-libs/qualtrics/components/qualtrics-components.module.ts:23` |  |

## feature-libs/quote(8)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `AccountMyQuotesComponent` | `QuoteListComponent` | guards | `feature-libs/quote/components/list/quote-list.module.ts:43` |  |
| `QuoteCartGuardComponent` | `QuoteCartGuardComponent` | guards | `feature-libs/quote/components/cart-guard/quote-cart-guard.component.module.ts:18` |  |
| `QuoteCommentsComponent` | `QuoteCommentsComponent` | guards | `feature-libs/quote/components/comments/quote-comments.module.ts:29` |  |
| `QuoteHeaderOverviewComponent` | `QuoteHeaderOverviewComponent` | guards | `feature-libs/quote/components/header/overview/quote-header-overview.module.ts:36` |  |
| `QuoteItemsComponent` | `QuoteItemsComponent` | guards | `feature-libs/quote/components/items/quote-items.module.ts:31` |  |
| `QuoteLinksComponent` | `QuoteLinksComponent` | guards | `feature-libs/quote/components/links/quote-links.module.ts:32` |  |
| `QuoteRequestComponent` | `QuoteRequestButtonComponent` |  | `feature-libs/quote/components/request-button/quote-request-button.module.ts:18` |  |
| `QuoteSummaryComponent` | `QuoteSummaryComponent` | guards | `feature-libs/quote/components/summary/quote-summary.module.ts:32` |  |

## feature-libs/storefinder(1)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `StoreFinderComponent` | `StoreFinderComponent` | childRoutes | `feature-libs/storefinder/components/store-finder-components.module.ts:69` |  |

## feature-libs/subscription-billing(5)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `SubscriptionBillDetailsComponent` | `SubscriptionBillingDetailsComponent` | guards | `feature-libs/subscription-billing/components/billing-details/subscription-billing-details.module.ts:33` |  |
| `SubscriptionBillsHistoryComponent` | `SubscriptionBillingListComponent` | guards | `feature-libs/subscription-billing/components/list/billing/subscription-billing-list.module.ts:47` |  |
| `SubscriptionDetailsComponent` | `SubscriptionDetailsComponent` | guards | `feature-libs/subscription-billing/components/details/subscription-details.module.ts:33` |  |
| `SubscriptionHistoryComponent` | `SubscriptionListComponent` | guards | `feature-libs/subscription-billing/components/list/subscription-list.module.ts:34` |  |
| `SubscriptionProductPriceComponent` | `SubscriptionProductPriceComponent` |  | `feature-libs/subscription-billing/components/product/price/subscription-product-price.module.ts:24` |  |

## feature-libs/user(21)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `AccountAddressBookComponent` | `AddressBookComponent` | guards | `feature-libs/user/profile/components/address-book/address-book.module.ts:36` |  |
| `CloseAccountComponent` | `CloseAccountComponent` | guards | `feature-libs/user/profile/components/close-account/close-account.module.ts:43` |  |
| `ForgotPasswordComponent` | `ForgotPasswordComponent` | guards,providers | `feature-libs/user/profile/components/forgot-password/forgot-password.module.ts:51` | ×2 |
| `LoginComponent` | `LoginComponent` |  | `feature-libs/user/account/components/login/login.module.ts:32` |  |
| `MyAccountViewUserComponent` | `MyAccountV2UserComponent` | guards | `feature-libs/user/account/components/my-account-v2-user/my-account-v2-user.module.ts:23` |  |
| `OAuthCallbackComponent` | `SpinnerComponent` | guards | `feature-libs/user/account/components/oauth-callback/oauth-callback.module.ts:31` |  |
| `RegisterCustomerComponent` | `RegisterComponent` | guards,providers | `feature-libs/user/profile/components/register/register.module.ts:55` | ×2 |
| `RegisterCustomerWithOTPComponent` | `OneTimePasswordRegisterComponent` | guards,providers | `feature-libs/user/profile/components/otp-login-register/otp-login-register.module.ts:54` |  |
| `ResetPasswordComponent` | `ResetPasswordComponent` | guards,providers | `feature-libs/user/profile/components/reset-password/reset-password.module.ts:49` |  |
| `ReturningCustomerLoginComponent` | `LoginFormComponent` | guards,providers | `feature-libs/user/account/components/login-form/login-form.module.ts:52` | ×2 |
| `ReturningCustomerOTPLoginComponent` | `OneTimePasswordLoginFormComponent` | guards | `feature-libs/user/account/components/otp-login-form/otp-login-form.module.ts:47` |  |
| `ReturningCustomerRegisterComponent` | `LoginRegisterComponent` | guards | `feature-libs/user/account/components/login-register/login-register.module.ts:35` |  |
| `ReturningOrganizationUserRegisterComponent` | `LoginRegisterB2BComponent` | guards | `feature-libs/user/account/components/login-register/login-register.module.ts:43` |  |
| `UpdateEmailComponent` | `MyAccountV2EmailComponent` |  | `feature-libs/user/profile/components/update-email/update-email.module.ts:42` | ×3 |
| `UpdateEmailComponent` | `UpdateEmailComponent` | guards,providers | `feature-libs/user/profile/components/update-email/update-email.module.ts:71` | ×3 |
| `UpdatePasswordComponent` | `MyAccountV2PasswordComponent` |  | `feature-libs/user/profile/components/update-password/update-password.module.ts:42` | ×3 |
| `UpdatePasswordComponent` | `UpdatePasswordComponent` | guards,providers | `feature-libs/user/profile/components/update-password/update-password.module.ts:70` | ×3 |
| `UpdateProfileComponent` | `MyAccountV2ProfileComponent` |  | `feature-libs/user/profile/components/update-profile/update-profile.module.ts:38` | ×3 |
| `UpdateProfileComponent` | `UpdateProfileComponent` | guards,providers | `feature-libs/user/profile/components/update-profile/update-profile.module.ts:67` | ×3 |
| `VerifyOTPForRegistrationComponent` | `RegistrationVerificationTokenFormComponent` | guards,providers | `feature-libs/user/profile/components/registration-verification-token-form/verify-register-verification-token-form.module.ts:50` |  |
| `VerifyOTPTokenComponent` | `VerificationTokenFormComponent` | guards,providers | `feature-libs/user/account/components/verification-token-form/verification-token-form.module.ts:59` |  |

## integration-libs/cdc(9)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `ForgotPasswordComponent` | `ForgotPasswordComponent` | providers | `integration-libs/cdc/user-profile/forgot-password/cdc-forgot-password.module.ts:37` | ×2 |
| `GigyaRaasComponent` | `GigyaRaasComponent` | guards | `integration-libs/cdc/components/gigya-raas/gigya-raas.module.ts:20` |  |
| `ManageUnitsListComponent` | (なし) | providers | `integration-libs/cdc/organization/administration/cdc-administration.module.ts:46` | ×2 |
| `ManageUsersListComponent` | (なし) | providers | `integration-libs/cdc/organization/administration/cdc-administration.module.ts:28` | ×2 |
| `RegisterCustomerComponent` | (なし) | providers | `integration-libs/cdc/user-profile/register/cdc-register.module.ts:41` | ×2 |
| `ReturningCustomerLoginComponent` | `LoginFormComponent` | guards,providers | `integration-libs/cdc/user-account/login-form/cdc-login-form.module.ts:51` | ×2 |
| `UpdateEmailComponent` | (なし) | providers | `integration-libs/cdc/user-profile/update-email/cdc-update-email.module.ts:40` | ×3 |
| `UpdatePasswordComponent` | (なし) | providers | `integration-libs/cdc/user-profile/update-password/cdc-update-password.module.ts:40` | ×3 |
| `UpdateProfileComponent` | (なし) | providers | `integration-libs/cdc/user-profile/update-profile/cdc-update-profile.module.ts:42` | ×3 |

## integration-libs/cds(2)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `MerchandisingCarouselComponent` | `MerchandisingCarouselComponent` |  | `integration-libs/cds/src/merchandising/cms-components/merchandising-carousel-cms.module.ts:28` |  |
| `ProfileTagComponent` | `ProfileTagComponent` | deferLoading | `integration-libs/cds/src/profiletag/cms-components/profile-tag-cms.module.ts:21` |  |

## integration-libs/digital-payments(1)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `CheckoutPaymentDetails` | `DpPaymentMethodComponent` |  | `integration-libs/digital-payments/src/checkout/cms-components/dp-payment-method/dp-payment-method.module.ts:34` | ×3 |

## integration-libs/epd-visualization(1)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `VisualPickingTabComponent` | `VisualPickingTabComponent` |  | `integration-libs/epd-visualization/components/visual-picking/visual-picking-tab/visual-picking-tab.module.ts:32` |  |

## integration-libs/opf(14)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `AccountOrderDetailsTotalsComponent` | `OpfGiftCardOrderDetailTotalsComponent` | guards | `integration-libs/opf/gift-card/root/components/opf-gift-card-order-details/opf-gift-card-order-details.module.ts:25` | ×2 |
| `AccountPaymentDetailsComponent` | `OpfTokenisationAccountPaymentMethodsComponent` | guards | `integration-libs/opf/tokenisation/root/components/opf-tokenisation-account-payment-methods/opf-tokenisation-account-payment-methods.module.ts:36` | ×2 |
| `CheckoutOrderSummary` | `OpfGiftCardCheckoutOrderSummaryComponent` |  | `integration-libs/opf/gift-card/root/components/opf-gift-card-checkout/opf-gift-card-checkout.module.ts:37` | ×2 |
| `CheckoutPaymentDetails` | `OpfTokenisationPaymentMethodComponent` | guards | `integration-libs/opf/tokenisation/root/components/opf-tokenisation-payment-method/opf-tokenisation-payment-method.module.ts:40` | ×3 |
| `OpfB2bCheckoutPaymentAndReview` | `OpfB2bCheckoutPaymentAndReviewComponent` | guards | `integration-libs/opf/b2b-checkout/components/opf-b2b-checkout-payment-and-review/opf-b2b-checkout-payment-and-review.module.ts:61` |  |
| `OpfCheckoutDeliveryAddress` | `OpfB2bCheckoutDeliveryAddressComponent` |  | `integration-libs/opf/b2b-checkout/components/opf-b2b-checkout-delivery-address/opf-b2b-checkout-delivery-address.module.ts:35` |  |
| `OpfCheckoutEmailUpdateComponent` | `OpfCheckoutEmailUpdateComponent` |  | `integration-libs/opf/checkout/components/opf-checkout-email-update/opf-checkout-email-update.module.ts:26` |  |
| `OpfCheckoutPaymentAndReview` | `OpfCheckoutPaymentAndReviewComponent` | guards | `integration-libs/opf/checkout/components/opf-checkout-payment-and-review/opf-checkout-payment-and-review.module.ts:60` |  |
| `OpfCheckoutPaymentType` | `OpfB2bCheckoutPaymentTypeComponent` | guards | `integration-libs/opf/b2b-checkout/components/opf-b2b-checkout-payment-type/opf-b2b-checkout-payment-type.module.ts:38` |  |
| `OpfCheckoutReview` | `OpfB2bCheckoutReviewComponent` |  | `integration-libs/opf/b2b-checkout/components/opf-b2b-checkout-review/opf-b2b-checkout-review.module.ts:49` |  |
| `OpfCtaQuickBuyButtons` | `OpfCtaQuickBuyButtonsComponent` |  | `integration-libs/opf/cta/components/opf-cta-quick-buy-buttons/opf-cta-quick-buy-buttons.module.ts:25` |  |
| `OpfCtaScriptsComponent` | `OpfCtaScriptsComponent` |  | `integration-libs/opf/cta/components/opf-cta-scripts/opf-cta-scripts.module.ts:26` |  |
| `OpfQuickBuyButtonsComponent` | `OpfQuickBuyButtonsComponent` |  | `integration-libs/opf/quick-buy/components/opf-quick-buy-buttons/opf-quick-buy-buttons.module.ts:20` |  |
| `OrderConfirmationTotalsComponent` | `OpfGiftCardOrderConfirmationTotalsComponent` | guards | `integration-libs/opf/gift-card/root/components/opf-gift-card-order-confirmation/opf-gift-card-order-confirmation.module.ts:17` | ×2 |

## integration-libs/punchout(6)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `PunchoutButtonsComponent` | `PunchoutButtonsComponent` |  | `integration-libs/punchout/components/punchout-components.module.ts:51` |  |
| `PunchoutCloseSessionComponent` | `PunchoutCloseSessionComponent` |  | `integration-libs/punchout/components/punchout-components.module.ts:57` |  |
| `PunchoutErrorComponent` | `PunchoutErrorComponent` |  | `integration-libs/punchout/components/punchout-components.module.ts:48` |  |
| `PunchoutInspectCartComponent` | `PunchoutInspectCartComponent` |  | `integration-libs/punchout/components/punchout-components.module.ts:60` |  |
| `PunchoutRequisitionComponent` | `PunchoutRequisitionComponent` |  | `integration-libs/punchout/components/punchout-components.module.ts:54` |  |
| `PunchoutSessionComponent` | `PunchoutSessionComponent` |  | `integration-libs/punchout/components/punchout-components.module.ts:45` |  |

## integration-libs/s4-service(7)

| キー | Angular コンポーネント | 他の設定 | 場所 | 重複 |
|---|---|---|---|---|
| `AccountOrderDetailsActionsComponent` | `S4ServiceOrderDetailActionsComponent` |  | `integration-libs/s4-service/order/components/s4-service-order-detail-actions/s4-service-order-detail-actions.module.ts:31` | ×3 |
| `CancelServiceOrder` | `CancelServiceOrderComponent` | guards | `integration-libs/s4-service/order/components/cancel-service-order/cancel-service-order.module.ts:36` |  |
| `CancelServiceOrderHeadline` | `CancelServiceOrderHeadlineComponent` | guards | `integration-libs/s4-service/order/components/cancel-service-order-headline/cancel-service-order-headline.module.ts:40` |  |
| `CheckoutDeliveryMode` | `ServiceCheckoutDeliveryModeComponent` |  | `integration-libs/s4-service/checkout/components/checkout-delivery-mode/service-checkout-delivery-mode.module.ts:37` | ×2 |
| `CheckoutReviewOrder` | `ServiceCheckoutReviewSubmitComponent` | guards | `integration-libs/s4-service/checkout/components/checkout-review-submit/service-checkout-review-submit.module.ts:43` | ×3 |
| `CheckoutServiceDetails` | `CheckoutServiceDetailsComponent` | guards | `integration-libs/s4-service/checkout/components/checkout-service-details/checkout-service-details.module.ts:35` |  |
| `RescheduleServiceOrder` | `RescheduleServiceOrderComponent` | guards | `integration-libs/s4-service/order/components/reschedule-service-order/reschedule-service-order.module.ts:47` |  |

## 遅延ロードの一覧に名前はあるが、`cmsComponents` の対応が見つからないもの

`featureModules.*.cmsComponents` は「このキーが来たらこの機能を読み込む」という一覧で、描画する部品の対応ではない。下の 5 件は一覧にあるが、対応はこの抽出では見つからなかった。CMS にこのキーが来ると、機能は読み込まれても部品は描画されず、開発モードでは警告が出る(`core-libs/storefront/cms-structure/services/cms-components.service.ts:165-180`)

| キー | 一覧の場所 |
|---|---|
| `AccountOrderDetailsBillingComponent` | `feature-libs/order/root/order-root.module.ts:37` |
| `DeliveryModeDatePickerComponent` | `feature-libs/requested-delivery-date/root/requested-delivery-date-root.module.ts:23` |
| `OrderConfirmationContinueButtonComponent` | `feature-libs/order/root/order-root.module.ts:58` |
| `OrderOverviewDeliveryDateComponent` | `feature-libs/requested-delivery-date/root/requested-delivery-date-root.module.ts:24` |
| `PersonalizationScriptComponent` | `feature-libs/tracking/personalization/root/personalization-root.module.ts:22` |
