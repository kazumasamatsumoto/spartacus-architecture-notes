/**
 * 本家 RoutingConfig.routing.loadStrategy(core/src/routing/configurable-routes/config/routing-config.ts:11-44)。
 * 既定は ALWAYS: 一度取ったページでも、ページ遷移のたびに cms/pages を取り直す
 * (routing-config.service.ts:45-47、cms-page.guard.ts:89-91)。
 * CMS の編集やログイン状態による出し分けを次の遷移で反映するための設計。
 * ★ 実験: 'ONCE' にすると、再訪で cms/pages が飛ばなくなる。
 */
export const routingConfig: { loadStrategy: 'ALWAYS' | 'ONCE' } = {
  loadStrategy: 'ALWAYS',
};
