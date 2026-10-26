import html
def esc(t):
    return html.escape(html.escape(t,quote=True),quote=True).replace("\n","&lt;br&gt;")
class D:
    def __init__(s, name):
        s.name=name; s.cells=[]; s.n=1
    def nid(s):
        s.n+=1; return f"c{s.n}"
    def box(s, label, x, y, w=200, h=60, fill="#dae8fc", stroke="#6c8ebf", font=12, extra="", parent="1"):
        i=s.nid()
        style=f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontSize={font};align=center;verticalAlign=middle;{extra}"
        s.cells.append(f'<mxCell id="{i}" value="{esc(label)}" style="{style}" vertex="1" parent="{parent}"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i
    def group(s, label, x, y, w, h, fill="#f5f5f5", stroke="#666666", font=13):
        i=s.nid()
        style=f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontSize={font};fontStyle=1;align=left;verticalAlign=top;spacingLeft=8;spacingTop=4;dashed=0;"
        s.cells.append(f'<mxCell id="{i}" value="{esc(label)}" style="{style}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i
    def text(s, label, x, y, w=300, h=30, font=11, extra=""):
        i=s.nid()
        style=f"text;html=1;whiteSpace=wrap;align=left;verticalAlign=top;fontSize={font};{extra}"
        s.cells.append(f'<mxCell id="{i}" value="{esc(label)}" style="{style}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i
    def edge(s, a, b, label="", dashed=False, color="#333333", exit=None, entry=None, font=11, pts=None):
        i=s.nid()
        style=f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={color};fontSize={font};endArrow=block;endFill=1;jettySize=auto;orthogonalLoop=1;"
        if dashed: style+="dashed=1;"
        if exit: style+=f"exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;"
        if entry: style+=f"entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;"
        geo='<mxGeometry relative="1" as="geometry">'
        if pts:
            geo+='<Array as="points">'+''.join(f'<mxPoint x="{px}" y="{py}"/>' for px,py in pts)+'</Array>'
        geo+='</mxGeometry>'
        s.cells.append(f'<mxCell id="{i}" value="{esc(label)}" style="{style}" edge="1" parent="1" source="{a}" target="{b}">{geo}</mxCell>')
        return i
    def xml(s):
        body="".join(s.cells)
        return (f'<diagram name="{html.escape(s.name,quote=True)}" id="{s.name}">'
                f'<mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1654" pageHeight="1169" math="0" shadow="0">'
                f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{body}</root></mxGraphModel></diagram>')

BLUE=("#dae8fc","#6c8ebf"); GREEN=("#d5e8d4","#82b366"); ORANGE=("#ffe6cc","#d79b00"); YEL=("#fff2cc","#d6b656"); RED=("#f8cecc","#b85450"); PURP=("#e1d5e7","#9673a6"); GREY=("#f5f5f5","#666666")

# ---------- 1. overall flow ----------
d1=D("01 全体フロー URL→描画")
d1.text("Spartacus: URL から Angular コンポーネント描画までの流れ(spartacus develop b7b028f / v2612.0.0)", 40, 20, 900, 30, 16, "fontStyle=1;")
gB=d1.group("ブラウザ / Angular アプリ(@spartacus/storefront + @spartacus/core)", 40, 70, 980, 980)
gO=d1.group("SAP Commerce Cloud / OCC (REST)", 1100, 70, 420, 980, "#fff7e6", "#d79b00")
y=120
s1=d1.box("① Angular Router\nroute '**' (canActivate: CmsPageGuard, component: PageLayoutComponent)\nadd-cms-route.ts:12-22", 80, y, 420, 70, *BLUE)
s2=d1.box("② NgRx Router State (CustomSerializer)\nURL → PageContext {type, id}\nrouter.reducer.ts:186-214", 80, y+110, 420, 70, *PURP)
s3=d1.box("③ CmsPageGuard → CmsService.getPage() / hasPage()\n未取得なら LoadCmsPageData を dispatch\ncms.service.ts:247-257", 80, y+220, 420, 70, *BLUE)
s4=d1.box("④ PageEffects → CmsPageConnector → OccCmsPageAdapter\npage.effect.ts:58-79 / occ-cms-page.adapter.ts:48-64", 80, y+330, 420, 70, *PURP)
s5=d1.box("⑤ OccCmsPageNormalizer\npage{template, slots{position→[uid,typeCode,flexType]}}\n+ components[全データ] → CmsGetComponentFromPage\noccc-cms-page-normalizer.ts:26-35,151-190".replace("occc","occ"), 80, y+440, 420, 80, *GREEN)
s6=d1.box("⑥ PageLayoutComponent\npage.template → LayoutConfig.layoutSlots[template].slots\npage-layout.service.ts:111-122", 80, y+560, 420, 70, *BLUE)
s7=d1.box("⑦ <cx-page-slot position> × N\n[cxOutlet]=flexType → [cxComponentWrapper]\npage-slot.component.html:6-14", 80, y+670, 420, 70, *BLUE)
s8=d1.box("⑧ ComponentWrapperDirective\nCmsComponentsService.getMapping(flexType)\n→ cmsComponents[flexType].component\ncomponent-wrapper.directive.ts:81-101", 80, y+780, 420, 80, *YEL)
s9=d1.box("⑨ ComponentHandler → ViewContainerRef.createComponent(\n component, injector = CmsInjectorService.getInjector(flexType, uid))\ndefault-component.handler.ts:56-69 / cms-injector.service.ts:28-49", 560, y+780, 430, 80, *YEL)
s10=d1.box("⑩ 生成された Angular コンポーネント\ninject(CmsComponentData).data$\n= CmsService.getComponentData(uid)\ncms-component-data.ts:10-13", 560, y+560, 430, 80, *GREEN)
store=d1.box("NgRx Store (cms スライス)\npages / components / navigation\nEntity Loader: loading / success / error / value", 560, y+220, 430, 80, *PURP)
lazy=d1.box("featureModules に属す typeCode なら\n() => import() で機能チャンクを遅延ロード\ncms-features.service.ts:56-74", 560, y+890, 430, 60, *GREY)
for a,b in [(s1,s2),(s2,s3),(s3,s4),(s4,s5),(s5,s6),(s6,s7),(s7,s8)]:
    d1.edge(a,b)
d1.edge(s8,s9)
d1.edge(s9,s10, "data$ 購読", entry=(0.5,1), exit=(0.5,0))
d1.edge(s5,store,"CmsGetComponentFromPage\n(API 追加なし)", color="#009900", exit=(1,0.5), entry=(0,1))
d1.edge(s3,store,"select / dispatch", dashed=True)
d1.edge(s10,store,"ストアにあれば即値", dashed=True, color="#009900", exit=(0.5,0), entry=(0.5,1))
d1.edge(s8,lazy,"", dashed=True, exit=(0.5,1), entry=(0,0.5))
occ1=d1.box("GET /occ/v2/{site}/users/{userId}/cms/pages\n?pageType=ProductPage&code=300938\n(default-cms-config.ts:9-24)\n→ ページ構造 + 全コンポーネントデータ", 1130, y+320, 360, 90, *ORANGE)
occ2=d1.box("GET .../cms/components?fields=DEFAULT\n&componentIds=a,b,c&pageSize=50\n(不足分のみ・同一ティックでバッチ)\ncomponents.effect.ts:47-63", 1130, y+560, 360, 90, *ORANGE)
occ3=d1.box("GET .../products/search?filters=code:...\nGET .../products/{code}?fields=...\n(コンポーネントが追加で要求する業務データ)", 1130, y+780, 360, 80, *ORANGE)
d1.edge(s4,occ1,"HTTP", exit=(1,0.5), entry=(0,0.5))
d1.edge(s10,occ2,"無ければ", dashed=True, exit=(1,0.5), entry=(0,0.5))
d1.edge(s10,occ3,"Facade 経由", dashed=True, exit=(1,0.8), entry=(0,0.3))

# ---------- 2. layers ----------
d2=D("02 レイヤ構成")
d2.text("Spartacus のパッケージ / レイヤ構成と依存方向", 40, 20, 800, 30, 16, "fontStyle=1;")
L=[("利用者の Angular アプリ(ng add @spartacus/schematics が生成)\nmain.ts → bootstrapApplication(AppComponent) → importProvidersFrom(AppModule)\napp/spartacus/ spartacus.module.ts / spartacus-features.module.ts(機能モジュール列挙・カスタムコンポーネントを追加)/ spartacus-configuration.module.ts(provideConfig: OCC baseUrl, context, layoutSlots, cmsComponents 上書き)", BLUE),
   ("機能ライブラリ feature-libs/* (@spartacus/cart, user, checkout, order, storefinder …)\n各ライブラリは root(常時ロード・軽量: facade 抽象 + featureModules 宣言)/ core(facade 実装・connector・store)/ occ(adapter・endpoints)/ components(UI + cmsComponents マッピング)の 4 エントリ。本体は typeCode 出現時に遅延ロード", GREEN),
   ("@spartacus/storefront (core-libs/storefront)\nCMS エンジン: PageLayoutComponent / PageSlotComponent / ComponentWrapperDirective / ComponentHandler / CmsInjectorService / CmsComponentData / Outlet\nLayoutConfig(layoutSlots)・標準 CMS コンポーネント(Banner, Paragraph, Link, ProductCarousel, Navigation …)・BaseStorefrontModule", YEL),
   ("@spartacus/core (core-libs/core)\nモデル(CmsComponent 派生)・設定 DI(provideConfig / Config / deepMerge)・NgRx(StateModule, cms/product/site-context ストア, Entity Loader)・Facade(CmsService, ProductService)\nConnector / Adapter / Converter(Normalizer)・OccEndpointsService(baseUrl + prefix + ${baseSiteId})・Routing(ConfigurableRoutes, CmsPageGuard 用 PageContext)・i18n(i18next)・LazyLoading", PURP),
   ("OCC v2 REST API (/occ/v2/{baseSiteId}/...)\ncms/pages, cms/components, products, users/{userId}/carts, basesites, languages, currencies …  + カスタム拡張エンドポイント", ORANGE),
   ("SAP Commerce Cloud (Java / Spring)\ncommercewebservices(OCC Controller + WsDTO + DataMapper/fields)・cmsocc / cmsfacades(CMS ページ・コンポーネントのレンダリング)・facades / services / DAO・ItemType(*-items.xml)・Content Catalog(Staged/Online)", RED)]
ids=[]
y=70
for label,(f,s) in L:
    ids.append(d2.box(label, 60, y, 1000, 90, f, s, 12, "align=left;spacingLeft=10;"))
    y+=120
for a,b in zip(ids,ids[1:]):
    d2.edge(a,b,"依存 / 呼び出し")
d2.text("ポイント: cmsComponents マッピングの型 (CmsConfig) は core、動的生成とレイアウトは storefront。機能ライブラリの UI は typeCode 単位で遅延ロード。", 60, y+10, 1000, 30, 12)

# ---------- 3. custom component data paths ----------
d3=D("03 カスタムコンポーネントのデータ経路")
d3.text("カスタム CMS コンポーネントが受け取る 2 種類のデータ経路(A: CMS 属性 / B: 業務データ)", 40, 20, 1100, 30, 16, "fontStyle=1;")
gFE=d3.group("フロントエンド(Angular / Spartacus)", 40, 70, 1060, 900)
gBE=d3.group("バックエンド(SAP Commerce Cloud / Java)", 1160, 70, 560, 900, "#fff7e6", "#d79b00")
cmp=d3.box("MyPromoComponent (Angular, standalone, OnPush)\ncmsComponents: { MyPromoBannerComponent: { component: MyPromoComponent } }\ninject(CmsComponentData).data$   /   inject(MyPromoFacade).get(id)", 80, 110, 980, 80, *YEL)
# path A
pa=d3.text("経路 A: CMS 属性(バックオフィスで編集する内容)", 80, 220, 460, 24, 13, "fontStyle=1;fontColor=#009900;")
a1=d3.box("CmsComponentData<CmsMyPromoBannerComponent>\n{ uid, data$ }  (cms-injector.service.ts:28-49)", 80, 250, 460, 60, *GREEN)
a2=d3.box("CmsService.getComponentData(uid)\n→ NgRx cms.components[uid] (取得済みなら API なし)", 80, 340, 460, 60, *PURP)
a3=d3.box("OccCmsPageNormalizer / OccCmsComponentAdapter\ncms/pages 同梱 or cms/components?componentIds= バッチ", 80, 430, 460, 60, *BLUE)
d3.edge(cmp,a1,"", exit=(0.25,1), entry=(0.5,0)); d3.edge(a1,a2); d3.edge(a2,a3)
# path B
pb=d3.text("経路 B: 業務データ(動的・商品/ユーザー/在庫など)", 580, 220, 480, 24, 13, "fontStyle=1;fontColor=#b85450;")
b1=d3.box("Facade (抽象, root エントリ)  MyPromoFacade\nfacadeFactory で遅延実装へプロキシ", 580, 250, 480, 60, *GREEN)
b2=d3.box("Facade 実装 (core)  MyPromoService\nQuery / NgRx Store: loading・success・error をキャッシュ\n同一キーは再取得しない", 580, 340, 480, 70, *PURP)
b3=d3.box("Connector (core)  MyPromoConnector\n機能向け API。Adapter に委譲", 580, 440, 480, 60, *BLUE)
b4=d3.box("Adapter 抽象 (core) MyPromoAdapter  ←  OCC 実装 (occ) OccMyPromoAdapter\nOccEndpointsService.buildUrl('myPromo', {urlParams, queryParams})\nconverter.pipeable(MY_PROMO_NORMALIZER)", 580, 530, 480, 80, *BLUE)
b5=d3.box("Converter / Normalizer (occ)\nOcc DTO (JSON) → FE モデル MyPromo", 580, 640, 480, 60, *GREEN)
b6=d3.box("endpoints 設定(occ)\nprovideDefaultConfig({ backend: { occ: { endpoints: {\n  myPromo: 'users/${userId}/my-promos/${promoId}?fields=DEFAULT' }}}})", 80, 560, 460, 80, *GREY)
d3.edge(cmp,b1,"", exit=(0.75,1), entry=(0.5,0)); d3.edge(b1,b2); d3.edge(b2,b3); d3.edge(b3,b4); d3.edge(b4,b5,"レスポンス変換", dashed=True); d3.edge(b6,b4,"URL 組み立て", dashed=True, exit=(1,0.5), entry=(0,0.5))
# backend side
be1=d3.box("cmsocc + cmsfacades\nGET cms/pages / cms/components\nItemType の属性を自動でレンダリング(文字列化)\n→ コントローラ追加は不要", 1190, 770, 500, 90, *ORANGE)
be2=d3.box("*-items.xml\nMyPromoBannerComponent extends SimpleCMSComponent\n属性: headline, content, promoId(参照のみ)", 1190, 640, 500, 70, *RED)
be3=d3.box("カスタム OCC Controller (commercewebservices 拡張)\n@Controller @RequestMapping(\"/{baseSiteId}/users/{userId}/my-promos\")\n@GetMapping(\"/{promoId}\") → MyPromoWsDTO (fields 対応)\n単位 = リソース(コンポーネントではない)", 1190, 110, 500, 100, *ORANGE)
be4=d3.box("Facade → Service → DAO / 外部 API\nMyPromoFacade.getPromo(promoId) → MyPromoData → DataMapper → WsDTO", 1190, 240, 500, 70, *RED)
d3.edge(a3,be1,"HTTP GET (lang / curr はインターセプタが付与)", exit=(0,0.5), entry=(0.5,1), pts=[(62,460),(62,880),(1440,880)])
d3.edge(be2,be1,"属性を読む", dashed=True)
d3.edge(b4,be3,"HTTP GET\n(認証/lang/curr 自動付与)", exit=(1,0.5), entry=(0,0.5), pts=[(1125,570),(1125,160)])
d3.edge(be3,be4)
d3.text("設計ルール: CMS 属性には「参照(ID/コード)と表示設定」だけを持たせ、実体データは経路 B のリソース API で返す。\nリスト系は codes=a,b,c のような一括取得エンドポイントにして、FE 側で bufferDebounceTime によるバッチ化ができる形にする。", 80, 905, 980, 50, 12)

# ---------- 4. backend decision ----------
d4=D("04 バックエンド判断フロー")
d4.text("バックエンド担当者向け: カスタムコンポーネントで「何を・どの単位で」返すかの判断", 40, 20, 1000, 30, 16, "fontStyle=1;")
q1=d4.box("そのデータは CMS 管理者が\nバックオフィスで編集する内容か?", 400, 80, 320, 70, *YEL)
r1=d4.box("YES → ItemType の属性にする\n・*-items.xml に属性追加(文字列/HTML/メディア/参照コード)\n・cms/pages に自動同梱される(コントローラ不要)\n・FE は CmsComponentData.data$ で受け取る\n・依頼書: typeCode, 属性名/型/例, 配置先スロット", 60, 200, 420, 110, *GREEN)
q2=d4.box("NO(動的データ)→ 既存 OCC API で取れるか?\n(products, categories, users/{id}/carts, orders …)", 620, 200, 420, 70, *YEL)
r2=d4.box("YES → コントローラ追加不要\n・CMS 属性には code / ID だけ持たせる\n・FE が既存 Facade(ProductService 等)で取得\n(例: ProductCarouselComponent.productCodes → products/search?filters=code:...)", 620, 320, 420, 100, *GREEN)
q3=d4.box("NO → 既存リソースの拡張で足りるか?\n(Product/Order 等の DTO に属性追加)", 620, 460, 420, 70, *YEL)
r3=d4.box("YES → 既存 WsDTO / Populator を拡張\n・fields=... で返す属性を制御\n・FE は Occ モデル拡張 + Normalizer で受ける", 620, 570, 420, 90, *GREEN)
r4=d4.box("NO → 新しい OCC エンドポイント(リソース単位)\n・@Controller + @RequestMapping(\"/{baseSiteId}/...\")\n・URL はコンポーネント名ではなく資源名(名詞・複数形)\n・単件 GET /{id} と一括 GET ?ids=a,b,c の両方\n・WsDTO + DataMapper、fields パラメータ対応、lang/curr 前提\n・FE: Facade/Connector/Adapter/Normalizer/Store を新設", 620, 700, 420, 130, *ORANGE)
d4.edge(q1,r1,"YES", exit=(0.25,1), entry=(0.5,0)); d4.edge(q1,q2,"NO", exit=(0.75,1), entry=(0.5,0))
d4.edge(q2,r2,"YES"); d4.edge(r2,q3,"足りない", dashed=True); d4.edge(q3,r3,"YES"); d4.edge(r3,r4,"足りない", dashed=True)
d4.text("アンチパターン: コンポーネントごとに専用 API を作る(/myPromoBannerComponentData)。再利用できず、バッチ化もできない。\n単位は「ドメインのリソース」。CMS コンポーネントは「どのリソースを、どう見せるか」の設定だけを持つ。", 60, 860, 1000, 50, 12, "fontColor=#b85450;")

# ---------- 5. JSP -> headless ----------
d5=D("05 JSP→ヘッドレス 責務の移行")
d5.text("JSP(アクセラレータ)の CMS コンポーネントコントローラが持っていた責務は、ヘッドレスではどこへ行くか", 40, 20, 1200, 30, 16, "fontStyle=1;")
gJ=d5.group("JSP 時代: 1 コンポーネント = 1 コントローラ + 1 JSP", 40, 70, 420, 760, "#fff2cc", "#d6b656")
jc=d5.box("XxxComponentController extends AbstractCMSComponentController\nfillModel(request, model, component)\n→ return \"cms/xxxComponent.jsp\"", 60, 110, 380, 80, *YEL)
j=[]
labels=[("(a) component.getXxx() を Model へ",YEL),("(b) 派生データの計算\n(商品引き当て・ナビツリー展開・在庫・判定)",ORANGE),("(c) URL 生成 (c:url / 商品 URL / メディア URL)",YEL),("(d) HTML 描画 (JSP)",YEL),("(e) <cms:component> 子コンポーネント include",YEL),("(f) フォーム POST 処理",YEL)]
y=220
for lab,col in labels:
    j.append(d5.box(lab, 60, y, 380, 70, *col)); y+=95
gH=d5.group("ヘッドレス: JSON は cms/pages が一律に返し、描画は Angular", 540, 70, 1120, 760, "#f5f5f5", "#666666")
h_a=d5.box("自動: ItemType 属性が cms/pages / cms/components の JSON に出る\n(コントローラ不要)", 580, 220, 500, 70, *GREEN)
h_b1=d5.box("B-1 フロントが資源 API で再計算\n例: productCodes → products/search?filters=code:...", 580, 315, 500, 60, *GREEN)
h_b2=d5.box("B-2 バックエンドが構造化データを JSON に埋め込む\n例: navigationNode ツリー(葉は itemId の参照)\n→ 構造は埋め込み、実体は参照。全ユーザー共通・小さいものだけ", 1110, 290, 530, 80, *ORANGE)
h_b3=d5.box("B-3 新しい資源 API(12 章)\nユーザー固有 / 大きい / 他画面でも使う / 高頻度更新", 1110, 390, 530, 60, *ORANGE)
h_c=d5.box("フロントで生成: cxRoute + RoutingConfig、media.baseUrl 前置\nバックエンドは code / label / 相対メディアパスだけ返す", 580, 410, 500, 60, *GREEN)
h_d=d5.box("Angular コンポーネントのテンプレート\n(リッチテキストだけは HTML 文字列を属性で返し innerHTML 表示)", 580, 505, 500, 60, *GREEN)
h_e=d5.box("スロット構造 / composition.inner / entries 参照", 580, 600, 500, 60, *GREEN)
h_f=d5.box("REST POST エンドポイント + フロントの CommandService", 580, 695, 500, 60, *GREEN)
d5.edge(j[0],h_a); d5.edge(j[1],h_b1); d5.edge(j[1],h_b2,"",exit=(1,0.5),entry=(0,0.5),pts=[(520,255),(520,330),(1095,330)]); d5.edge(h_b1,h_b3,"足りない",dashed=True,exit=(1,0.5),entry=(0,0.5))
d5.edge(j[2],h_c); d5.edge(j[3],h_d); d5.edge(j[4],h_e); d5.edge(j[5],h_f)
d5.text("禁止: HTML 断片で済ませる / ストアフロント絶対 URL を返す / コンポーネント専用エンドポイント / ユーザー固有データを CMS JSON に埋め込む / Model 名のままの JSON キー", 60, 850, 1600, 30, 12, "fontColor=#b85450;")

# ---------- 6. Angular app skeleton & config DI ----------
d6=D("06 Angular アプリの骨格と設定 DI")
d6.text("利用者の Angular アプリの骨格(左)と、provideConfig が効く仕組み(右)", 40, 20, 1100, 30, 16, "fontStyle=1;")
gA=d6.group("Angular アプリ(ng add @spartacus/schematics が生成 / projects/storefrontapp と同形)", 40, 70, 760, 900)
m1=d6.box("main.ts\nbootstrapApplication(AppComponent, appConfig)   main.ts:17", 70, 110, 700, 50, *BLUE)
m2=d6.box("app.config.ts  (ApplicationConfig)\nprovideHttpClient(withFetch, withInterceptorsFromDi) / provideClientHydration(withNoHttpTransferCache)\nimportProvidersFrom(AppModule)   app.config.ts:26-35", 70, 185, 700, 70, *BLUE)
m3=d6.box("AppModule   app.module.ts:15-25\nBrowserModule / StoreModule.forRoot({}) / EffectsModule.forRoot([]) / AppRoutingModule / SpartacusModule", 70, 280, 700, 60, *BLUE)
m4=d6.box("AppComponent  template: <cx-storefront />   app.component.ts:14-19", 70, 365, 700, 40, *BLUE)
m5=d6.box("SpartacusModule   app/spartacus/spartacus.module.ts", 70, 430, 700, 40, *GREEN)
m6=d6.box("BaseStorefrontModule (@spartacus/storefront)\nPageLayoutModule / PageSlotModule / PageComponentModule / OutletModule / RoutingModule / BaseCoreModule\ncore-libs/storefront/base-storefront.module.ts:26-49", 70, 500, 340, 90, *YEL)
m7=d6.box("BaseCoreModule (@spartacus/core)\nStateModule / ConfigModule / CmsModule / BaseOccModule / I18nModule / SiteContextModule / LazyLoadingModule\ncore-libs/core/src/base-core.module.ts:26-46", 70, 620, 340, 90, *PURP)
m8=d6.box("SpartacusFeaturesModule\n使う機能モジュールを imports に列挙\n(CmsParagraphModule, BannerModule, *-feature.module …)\n★ カスタム CMS コンポーネントのモジュールを足す場所", 430, 500, 340, 90, *GREEN)
m9=d6.box("SpartacusConfigurationModule\nprovideConfig(...) の列挙: OCC baseUrl / context / layoutConfigFactory / i18n\n★ cmsComponents 上書き・layoutSlots 追加を書く場所", 430, 620, 340, 90, *GREEN)
m10=d6.box("機能ライブラリ(遅延チャンク)\nfeatureModules[name].module: () => import(...)\ntypeCode がページに現れたときだけロード", 70, 760, 700, 60, *GREY)
for a,b in [(m1,m2),(m2,m3),(m3,m4)]: d6.edge(a,b)
d6.edge(m3,m5,"imports",exit=(1,0.5),entry=(1,0.5),pts=[(788,310),(788,450)])
d6.edge(m5,m6,"",exit=(0.25,1),entry=(0.5,0)); d6.edge(m6,m7,"imports"); d6.edge(m5,m8,"",exit=(0.75,1),entry=(0.5,0)); d6.edge(m8,m9,"")
d6.edge(m9,m10,"featureModules 設定",dashed=True,exit=(0.5,1),entry=(0.7,0))
gC=d6.group("設定 DI: provideConfig / provideDefaultConfig → Config(deepMerge)", 860, 70, 760, 900, "#fff7e6", "#d79b00")
c1=d6.box("ライブラリ側  provideDefaultConfig(<CmsConfig>{ cmsComponents: { CMSParagraphComponent: {...} } })\n→ DefaultConfigChunk (InjectionToken, multi: true = 同じキーへの複数登録が配列で届く)\n→ DefaultConfig = deepMerge(配列...)   config-providers.ts:55-61 / config-tokens.ts:23-35", 890, 110, 700, 70, *YEL)
c2=d6.box("アプリ側  provideConfig({ cmsComponents: { MyPromoBannerComponent: {...} }, layoutSlots: {...} })\n→ ConfigChunk (InjectionToken, multi: true)\n→ RootConfig = deepMerge(配列...)   config-providers.ts:18-27 / config-tokens.ts:37-47", 890, 205, 700, 70, *GREEN)
c3=d6.box("遅延モジュール内の provideDefaultConfig / provideConfig\n→ ambientDefaultConfig / ambientConfig   configuration.service.ts:92-105", 890, 290, 700, 50, *GREY)
c4=d6.box("Config = deepMerge({}, DefaultConfig, ambientDefault, ambient, RootConfig)\nオブジェクトは再帰マージ・後勝ち、配列は丸ごと置換   config-tokens.ts:10-62 / deep-merge.ts:31-48", 890, 390, 700, 70, *ORANGE)
c5=d6.box("CmsConfig / LayoutConfig / OccConfig / RoutingConfig / StateConfig\n@Injectable({ providedIn: 'root', useExisting: Config })  = 同じ合成済み設定を型付きで覗く窓", 890, 500, 700, 60, *PURP)
c6=d6.box("利用側\nCmsComponentsService.getMapping(flexType) → cmsComponents[flexType]\nPageLayoutService → layoutSlots[template]\nOccEndpointsService.buildUrl → backend.occ.endpoints / baseUrl / prefix", 890, 600, 700, 90, *BLUE)
d6.edge(c1,c4,"",exit=(0,0.5),entry=(0.08,0),pts=[(872,145),(872,375),(946,375)]); d6.edge(c2,c4,"",exit=(1,0.5),entry=(0.92,0),pts=[(1608,240),(1608,375),(1534,375)]); d6.edge(c3,c4,"",exit=(0.5,1),entry=(0.5,0)); d6.edge(c4,c5); d6.edge(c5,c6)
d6.text("Spring で言えば: provideConfig = @Bean 登録、multi: true = List<Bean> 注入、Config = 全 properties を合成した 1 つの Environment。結果: アプリの provideConfig は、ライブラリ既定の同じキーだけを置き換える(他のキーは既定のまま)。typeCode のマッピング追加・上書き、スロット追加、エンドポイント追加はすべてこの 1 つの仕組みで行う。", 890, 720, 700, 60, 12)

# ---------- 7. API minimization ----------
d7=D("07 API 呼び出しを減らす仕組み")
d7.text("コンポーネントがデータを要求してから HTTP が飛ぶまでに通る「止め弁」(ホーム表示: cms/pages 1 本 + バッチ数本で済む理由)", 40, 20, 1300, 30, 16, "fontStyle=1;")
# page load column
gP=d7.group("A. ページ取得(CmsPageGuard)", 40, 70, 420, 820, "#f5f5f5", "#666666")
p1=d7.box("CmsService.getPage(ctx) → hasPage(ctx)", 60, 110, 380, 50, *BLUE)
p2=d7.box("弁①  loading / success / error のどれかが立っている?\n(Entity Loader)   cms.service.ts:247-257", 60, 185, 380, 60, *YEL)
p3=d7.box("dispatch LoadCmsPageData", 60, 270, 380, 40, *PURP)
p4=d7.box("弁②  groupBy(ctx) + switchMap\n同一ページの重複要求は 1 本に   page.effect.ts:58-66", 60, 335, 380, 60, *YEL)
p5=d7.box("弁③  cmsStructure.pages[ctx].ignoreBackend ?\n静的構成なら HTTP なし   cms-page.connector.ts:30-52", 60, 420, 380, 60, *YEL)
p6=d7.box("HTTP GET users/{userId}/cms/pages?...  (1 本)", 60, 505, 380, 50, *ORANGE)
p7=d7.box("Normalizer: 同梱された全コンポーネントを components[] へ\n→ CmsGetComponentFromPage でストアに格納\noccc-cms-page-normalizer.ts:160-190 / page.effect.ts:67-79".replace("occc","occ"), 60, 580, 380, 80, *GREEN)
p8=d7.box("NgRx Store: cms.pages[ctx], cms.components[uid]\n(言語変更 / ログイン / ログアウトで丸ごとクリア)", 60, 690, 380, 60, *PURP)
d7.edge(p1,p2); d7.edge(p2,p3,"いいえ"); d7.edge(p3,p4); d7.edge(p4,p5); d7.edge(p5,p6,"いいえ"); d7.edge(p6,p7); d7.edge(p7,p8)
d7.edge(p2,p8,"はい → 何もしない",dashed=True,color="#009900",exit=(1,0.5),entry=(1,0.5),pts=[(455,215),(455,720)])
# component column
gQ=d7.group("B. コンポーネントデータ(CmsComponentData.data$)", 520, 70, 460, 820, "#f5f5f5", "#666666")
q1=d7.box("CmsService.getComponentData(uid)", 540, 110, 420, 50, *BLUE)
q2=d7.box("弁④  uid × context の Observable キャッシュ(shareReplay)\ncms.service.ts:82-94, 142-145", 540, 185, 420, 60, *YEL)
q3=d7.box("弁⑤  attemptedLoad(loading/success/error) ?\n弁⑥  遷移先ページの応答に含まれる見込み(couldBeLoadedWithPageData)?\ncms.service.ts:112-133", 540, 270, 420, 70, *YEL)
q4=d7.box("dispatch LoadCmsComponent({uid, ctx})", 540, 365, 420, 40, *PURP)
q5=d7.box("弁⑦  bufferDebounceTime: 同一ティックの要求を 1 つに\ngroupBy(ctx)   components.effect.ts:47-63", 540, 430, 420, 60, *YEL)
q6=d7.box("弁⑧  静的 cmsStructure.components にある uid は除外\n弁⑨  残りを 50 件ずつに分割   cms-component.connector.ts:41-73", 540, 515, 420, 60, *YEL)
q7=d7.box("HTTP GET .../cms/components?fields=DEFAULT&componentIds=a,b,c&pageSize=N", 540, 600, 420, 50, *ORANGE)
q8=d7.box("弁⑩  コンテンツページ間でキャッシュ共有\nserializePageContext(ctx, true) → \"ContentPage\"   cms-utils.ts:21-34", 540, 680, 420, 60, *GREY)
q9=d7.box("弁⑪  cxOutletDefer: ビューポート外は描画も購読も遅延\npage-slot.component.html:11", 540, 765, 420, 60, *GREY)
d7.edge(q1,q2); d7.edge(q2,q3); d7.edge(q3,q4,"いいえ / いいえ"); d7.edge(q4,q5); d7.edge(q5,q6); d7.edge(q6,q7)
d7.edge(q3,p8,"はい → ストアの値を待つ / 使う",dashed=True,color="#009900",exit=(0,0.5),entry=(1,0.3),pts=[(500,305),(500,708)])
# product column
gR=d7.group("C. 業務データ(例: 商品カルーセル)", 1040, 70, 460, 820, "#f5f5f5", "#666666")
r1=d7.box("ProductSearchByCodeService.get({code, scope})\nproductCodes を split(' ') して 1 件ずつ呼ぶ", 1060, 110, 420, 60, *BLUE)
r2=d7.box("弁⑫  state.loading / success / error ?\nproduct-search-by-code.service.ts:46-53", 1060, 195, 420, 60, *YEL)
r3=d7.box("dispatch ProductSearchLoadByCode", 1060, 280, 420, 40, *PURP)
r4=d7.box("弁⑬  groupBy(scope) + bufferDebounceTime\n同時要求をスコープごとに 1 本へ   product-search-by-code.effect.ts:42-67", 1060, 345, 420, 60, *YEL)
r5=d7.box("弁⑭  100 件ずつに分割(OCC 上限)\noccc-product-search.adapter.ts:73-99".replace("occc","occ"), 1060, 430, 420, 50, *YEL)
r6=d7.box("HTTP GET products/search?filters=code:a,b,c&pageSize=100&fields=...", 1060, 505, 420, 50, *ORANGE)
r7=d7.box("弁⑮  同一商品の複数スコープは fields を結合して 1 URL に\n(products/{code})  occ-requests-optimizer.service.ts:34-75", 1060, 590, 420, 60, *GREY)
r8=d7.box("弁⑯  SSR 時: cms / product / siteContext / siteTheme を\nTransferState で転送し、ブラウザは再取得しない(デモは CSR)\ntransfer-state.reducer.ts:16-95", 1060, 680, 420, 70, *GREY)
d7.edge(r1,r2); d7.edge(r2,r3,"いいえ"); d7.edge(r3,r4); d7.edge(r4,r5); d7.edge(r5,r6)
d7.text("実測(2026-10-23 デモ, CSR): ホーム = cms/pages 1 + cms/components 2 + products/search 1 + サイト情報 4 + cart 1。PDP への SPA 遷移 = 6 本、サイト情報/カートは再取得なし。", 40, 905, 1460, 30, 12)


# ---------- shared helpers for the "paired + grid" style ----------
HEAD=("#666666","#666666")
def paired(d, x, y, rows, w1, w2, h, gap=12):
    for label,color,text in rows:
        d.box(label, x, y, w1, h, *color, 11, "fontStyle=1;")
        d.box(text, x+w1+10, y, w2, h, *YEL, 11)
        y+=h+gap
    return y
def grid(d, x, y, cols, rows, h=44, gap=6, hh=44):
    xs=[]; cx=x
    for name,w in cols:
        xs.append((cx,w)); d.box(name, cx, y, w, hh, *HEAD, 11, "fontColor=#ffffff;fontStyle=1;"); cx+=w+gap
    y+=hh+gap
    for cells in rows:
        for (t,c),(gx,gw) in zip(cells, xs):
            d.box(t, gx, y, gw, h, *c, 11)
        y+=h+gap
    return y
NA=("", ("#ffffff","#cccccc"))

# ---------- 8. per-resource call patterns (ch.11) ----------
d8=D("08 リソースごとの呼び出し方法の違い")
d8.text("フロント側の呼び出し: 通信層は共通、状態層は 2 方式、リソース固有なのは「文脈」と「捨てる条件」(10 章)", 40, 20, 1500, 30, 16, "fontStyle=1;")
gA=d8.group("A. 3 層に分けると、何が共通で何が違うか", 40, 70, 560, 760, "#f5f5f5", "#666666")
paired(d8, 60, 110, [
 ("通信層\nConnector → Adapter →\nConverter → HttpClient", GREEN, "全リソース共通。URL は buildUrl(OCC アダプタ 75 中 74)、変換は pipeable(59)、lang / curr と Bearer はインターセプタが自動付与。違うのは設定値(URL テンプレート、Normalizer)だけ"),
 ("状態層\nFacade の中身", PURP, "2 方式のどちらか(機能ライブラリごとに固定)。NgRx: CMS・商品・サイト・カート本体・注文履歴・ユーザー配下・店舗・B2B 組織。Query / Command: ユーザー本体・チェックアウト・注文確定・見積・チケット・カート検証・在庫。SAP ガイド「既存に合わせよ」"),
 ("文脈と捨てる条件\nFacade の設計", BLUE, "リソースごとに違う。必要な ID(userId / cartId / PageContext / scope)、前提条件、再読込・破棄のきっかけ、バッチ化。右の表がその一覧"),
 ("コンポーネントから見た形", GREY, "どのリソースでも facade.get() が Observable<T> を返す。違いは Facade の内側だけ。カスタムリソースで決めるのは「方式」「文脈」「捨てる条件」「更新系」の 4 問(10.5)"),
], 190, 330, 150)
d8.text("混在の例: 注文(履歴 = NgRx / 確定 = Command)、カート(本体 = NgRx / 検証 = Query)、商品(本体 = NgRx / 在庫 = Query)。境界はリソースではなく「機能ライブラリが書かれた時期」。", 60, 760, 520, 60, 11)
gB=d8.group("B. リソースごとの文脈 / 捨てる条件 / バッチ(色: 灰 = サイト共通、青 = ユーザー固有、橙 = カート配下)", 640, 70, 980, 760, "#fff7e6", "#d79b00")
NG=("NgRx",PURP); QC=("Query / Command",GREEN)
rows=[
 [("CMS(pages / components)",GREY), NG, ("PageContext + userId(anonymous / current)",BLUE), ("言語変更・ログイン・ログアウトで全破棄",YEL), ("componentIds 50 件ずつ",ORANGE)],
 [("商品",GREY), ("NgRx(在庫は Query)",YEL), ("productCode + scope",GREY), ("言語・通貨変更で全破棄。scope ごとに maxAge / reloadOn",YEL), ("コード検索 100 件 / fields 結合",ORANGE)],
 [("サイトコンテキスト",GREY), NG, ("なし(起動時)",GREY), ("なし(起動時 1 回)",YEL), ("SSR なら TransferState",ORANGE)],
 [("店舗(検索・受取)",GREY), NG, ("検索条件 / storeId",GREY), ("検索ごとに上書き",YEL), ("なし",GREY)],
 [("カート",GREY), ("NgRx(検証・ゲストは Query)",YEL), ("userId + cartId(current)+ 安定待ち",ORANGE), ("ログイン時 loadOrMerge。更新ごとに全体再取得。ID は localStorage",YEL), ("なし",GREY)],
 [("チェックアウト",GREY), QC, ("userId + cartId + 前提条件",ORANGE), ("更新 Command の成功イベント → 単一 Query を Reload / Reset",YEL), ("なし(1 Query に集約)",ORANGE)],
 [("注文",GREY), ("混在(履歴 NgRx / 確定 Command)",YEL), ("userId(履歴は loggedIn)",BLUE), ("履歴・詳細は明示 Clear。確定は CancelPrevious + OrderPlacedEvent",YEL), ("なし",GREY)],
 [("ユーザー本体・プロフィール",GREY), QC, ("userId(loggedIn、匿名なら例外)",BLUE), ("UserAccountChangedEvent で再読込 / Login・Logout で破棄 / 言語依存は LanguageSetEvent",YEL), ("なし",GREY)],
 [("ユーザー配下(住所・支払・同意・クーポン)",GREY), NG, ("userId",BLUE), ("ログアウトでユーザーストア破棄。更新後に再読込",YEL), ("なし",GREY)],
 [("問い合わせチケット / 見積",GREY), QC, ("userId + ticketId / quoteCode",BLUE), ("専用の Reload / Reset イベント",YEL), ("なし",GREY)],
 [("B2B 組織",GREY), NG, ("userId + 各 ID",BLUE), ("更新アクションで該当エンティティ再読込",YEL), ("なし",GREY)],
]
yend=grid(d8, 660, 110, [("リソース",170),("方式",150),("文脈(必要な ID)",190),("捨てる・再読込する条件",270),("バッチ",140)], rows, h=50)
d8.text("URL の階層(users/{userId}/carts/{cartId}/...)が、そのままフロントで必要な ID の数になる(9.4)。", 660, yend+4, 940, 30, 11)

# ---------- 9. application lifecycle (ch.12) ----------
d9=D("09 アプリケーションのライフサイクル")
d9.text("Spartacus アプリのライフサイクル: index.html 取得 → 起動 → 初期化 → ゲート → 描画 → 実行中イベント → SSR → 永続化(6 章)", 40, 20, 1500, 30, 16, "fontStyle=1;")
gA=d9.group("A. 9 フェーズ: 何が起きるか", 40, 70, 700, 900, "#f5f5f5", "#666666")
paired(d9, 60, 110, [
 ("0. HTML 取得", GREY, "index.html は <app-root> だけ(CSR)。meta occ-backend-base-url でビルド後に接続先を差し替え可能"),
 ("1. 起動と DI 構築\nmain.ts:17", BLUE, "bootstrapApplication(AppComponent, appConfig)→ importProvidersFrom(AppModule)→ Config を deepMerge で合成。イベントビルダー(Navigation / Login・Logout / LanguageSet)が登録される"),
 ("2. APP_INITIALIZER(23 個)", YEL, "並列に走る。順序保証が無いので各自が configInit.getStable(scope) を待つ。サイトコンテキストは URL > localStorage > config 既定。'**' ルート追加、i18next 初期化、MODULE_INITIALIZER(カート ID 復元)"),
 ("3. ゲート\nLOCATION_INITIALIZED", RED, "Promise.all(LOCATION_INITIALIZED_MULTI): ① Config が stable ② 認証(localStorage のトークン復元 → OAuth コールバック判定)→ userId = current / anonymous。通過後に Router の初回ナビゲーション"),
 ("4. ルーティング → 描画\n(3 章)", BLUE, "NavigationStart で URL(/site/lang/curr/...)からサイトコンテキスト確定 → CmsPageGuard → cms/pages → PageLayout → スロット → NavigationEnd(スクロール復元・SEO)"),
 ("5. コンポーネント", GREEN, "ComponentWrapperDirective.ngOnInit → 遅延ロード判定 → createComponent(Injector に CmsComponentData)→ ComponentCreateEvent → ngOnInit / data$ | async(OnPush)→ 遷移で ngOnDestroy → ComponentDestroyEvent"),
 ("6. 実行中のイベント", PURP, "ページ遷移 / 言語・通貨変更 / ログイン / ログアウト / 401 / HTTP エラー / 遅延ロード。それぞれ「何を捨てて何を取り直すか」が決まっている(右表)"),
 ("7. SSR の場合\n(デモは CSR)", GREY, "OptimizedSsrEngine: timeout 3 秒で CSR にフォールバック、concurrency 10、cache 既定 off。サーバで 1〜5 を実行し TransferState(cms / product / siteContext / siteTheme)を HTML へ。ブラウザは再取得なし + hydration"),
 ("8. 永続化と終了", GREY, "明示的な終了処理は無い。StatePersistenceService が実行中ずっと localStorage へ書き、次回起動の 2〜3 で復元(トークン / カート ID / 言語 / 通貨 / 同意 / テーマ)"),
], 170, 490, 78, 10)
gB=d9.group("B. フェーズごとの OCC 呼び出し / localStorage / ストアの破棄 / イベント", 780, 70, 840, 900, "#fff7e6", "#d79b00")
rows=[
 [("0",GREY), ("なし",GREY), ("—",GREY), ("—",GREY), ("—",GREY)],
 [("1",GREY), ("なし",GREY), ("—",GREY), ("—",GREY), ("ビルダー登録のみ",GREY)],
 [("2",GREY), ("GET languages / currencies / basesites",ORANGE), ("読む: 言語・通貨・カート ID・テーマ・同意",BLUE), ("—",GREY), ("—",GREY)],
 [("3",GREY), ("OAuth コールバック時のみ token 交換",ORANGE), ("読む: 認証トークン",BLUE), ("—",GREY), ("LoginEvent(新規トークン時)",PURP)],
 [("4",GREY), ("GET cms/pages / cms/components(不足分)/ carts/{id}(復元時)",ORANGE), ("—",GREY), ("—",GREY), ("NavigationEvent / PageEvent",PURP)],
 [("5",GREY), ("業務データ(products/... 等、Facade 経由・初回のみ)",ORANGE), ("—",GREY), ("—",GREY), ("ComponentCreateEvent / DestroyEvent",PURP)],
 [("6 遷移",GREY), ("GET cms/pages(既定で毎回)。他はストア済みなら無し",ORANGE), ("—",GREY), ("—",GREY), ("NavigationEvent",PURP)],
 [("6 言語変更",GREY), ("全部を lang=xx で再取得",ORANGE), ("書く: 言語",BLUE), ("CMS + 商品ストア全破棄",RED), ("LanguageSetEvent → Query 再読込",PURP)],
 [("6 ログイン",GREY), ("POST oauth/token、carts 併合、users/current、cms/pages",ORANGE), ("書く: トークン・カート ID",BLUE), ("CMS ストア破棄",RED), ("LoginEvent → Query resetOn",PURP)],
 [("6 ログアウト",GREY), ("POST revoke、cms/pages(匿名)",ORANGE), ("消す: トークン",BLUE), ("CMS + ユーザーストア破棄、カート index リセット",RED), ("LogoutEvent",PURP)],
 [("6 401 / エラー",GREY), ("POST oauth/token(refresh)または logout へ",ORANGE), ("—",GREY), ("—",GREY), ("GlobalMessage",PURP)],
 [("7",GREY), ("サーバ側で同じ呼び出し。ブラウザはゼロで開始",ORANGE), ("—",GREY), ("—",GREY), ("TransferState",PURP)],
 [("8",GREY), ("なし",GREY), ("書き続ける",BLUE), ("—",GREY), ("—",GREY)],
]
yend=grid(d9, 800, 110, [("フェーズ",90),("OCC 呼び出し",250),("localStorage",150),("ストアの破棄",150),("イベント",140)], rows, h=50)
d9.text("ゲート(3)を通るまで Router は動かないので、4 以降は「Config・userId・サイトコンテキストは確定済み」を前提にできる。", 800, yend+4, 800, 30, 11)

# ---------- 11. resource catalog (ch.10) ----------
d11=D("11 OCC リソースの 3 層とカスタムの置き場所")
d11.text("OCC リソースの 3 層(左)と、業務データ層の主なリソース・カスタムの置き場所(右)。9 章", 40, 20, 1500, 30, 16, "fontStyle=1;")
gA=d11.group("A. リソースの 3 層(+ 別 Web サービス)とカスタムの置き場所", 40, 70, 600, 760, "#f5f5f5", "#666666")
paired(d11, 60, 110, [
 ("A. サイト設定層\nbasesites / languages /\ncurrencies / countries / titles", GREY, "読み取り専用のマスタ。カスタムの対象になることはまれ(サイト固有の値は CMS 属性か別リソースへ)"),
 ("B. CMS 層\ncms/pages →\ncms/components/{uid}", BLUE, "AbstractCMSComponent の全サブタイプを返す汎用リソース。items.xml に型を足せば typeCode と属性が自動で返る。★ カスタム CMS コンポーネントはここに現れる。新しい URL は要らない"),
 ("C. 業務データ層\n商品 / ユーザー / カート /\n注文 / 店舗 / B2B 組織", GREEN, "コンポーネントが参照する「もの」(ItemType)。属性を足す = WsDTO + Populator 拡張 + fields。該当する型が無い概念だけが新リソース(12.3 の設計ルール)"),
 ("D. 別 Web サービス\nASM / punchout /\nsubscriptions", ORANGE, "OCC の prefix を持たない絶対パス。OCC とは別の独立 Web アプリを立てる場合の前例"),
], 200, 360, 130)
d11.box("決め方の順序:  ① B 層の属性で済むか(コントローラ不要) → ② C 層の既存リソースに参照 ID で済むか → ③ C 層の DTO 拡張で済むか → ④ C 層に新リソース(12.1 ①〜④)", 60, 680, 560, 60, *RED, 11, "fontStyle=1;")
gB=d11.group("B. 業務データ層の主なリソース(URL は {baseUrl}/occ/v2/{site}/ の後ろ)", 680, 70, 940, 760, "#fff7e6", "#d79b00")
rows=[
 [("商品",GREY), ("products/{code}?fields=... / products/search / .../reviews / .../stock",BLUE), ("Product, CustomerReview, StockLevel",GREY), ("ProductWsDTO 拡張 + fields レベル追加",YEL), ("productCodes(カルーセル)",GREEN)],
 [("ユーザー本体",GREY), ("users/{userId}",BLUE), ("Customer(User)",GREY), ("UserWsDTO 拡張",YEL), ("—",GREY)],
 [("ユーザー配下",GREY), ("users/{userId}/addresses / paymentdetails / consents / customercoupons / wishlists / tickets",BLUE), ("Address, PaymentInfo, Consent, CustomerCoupon, CsTicket",GREY), ("各 WsDTO 拡張",YEL), ("—",GREY)],
 [("カート",GREY), ("users/{userId}/carts/{cartId} / .../entries / .../vouchers",BLUE), ("Cart, CartEntry, Voucher",GREY), ("CartWsDTO / OrderEntryWsDTO 拡張 + fields",YEL), ("—",GREY)],
 [("チェックアウト",GREY), ("carts/{cartId}/addresses/delivery / deliverymodes / paymentdetails / costcenter",BLUE), ("Address, DeliveryMode, PaymentInfo",GREY), ("配送・支払の選択肢はデータ追加",YEL), ("—",GREY)],
 [("注文",GREY), ("users/{userId}/orders/{id} / .../cancellation / orderReturns / replenishmentOrders",BLUE), ("Order, Consignment, ReturnRequest",GREY), ("OrderWsDTO 拡張 + fields",YEL), ("orderCode(注文確認バナー)",GREEN)],
 [("店舗",GREY), ("stores?query=... / stores/{storeId}",BLUE), ("PointOfService",GREY), ("PointOfServiceWsDTO 拡張",YEL), ("storeCode(店舗バナー)",GREEN)],
 [("B2B 組織",GREY), ("users/{userId}/orgUnits / orgCustomers / budgets / costcenters / orderapprovals / quotes",BLUE), ("B2BUnit, B2BCustomer, B2BBudget, B2BCostCenter, Quote",GREY), ("各 WsDTO 拡張",YEL), ("—",GREY)],
 [("新しい概念",GREY), ("users/{userId}/campaignEntries/{code}(例)",RED), ("新 ItemType",RED), ("新コントローラ + WsDTO(12.4)",RED), ("campaignCode",GREEN)],
]
yend=grid(d11, 700, 110, [("分類",100),("URL パターン",280),("ItemType(要確認)",170),("属性を足すなら",170),("CMS 属性に持たせる参照 ID",160)], rows, h=60)
d11.text("ItemType 名は SAP Commerce 標準型システムの一般知識で、本リポジトリでは検証不能(Backoffice の型検索で確認)。URL パターンは Spartacus の default-occ-*-config.ts 45 ファイルから収集。", 700, yend+4, 900, 40, 11)

# ---------- 10. four tiers + measured timeline ----------
d10=D("10 呼び出しの 4 階層と毎回・初回")
d10.text("OCC 呼び出しの 4 階層(左)と、デモサイトで実測した「毎回」と「初回」の違い(右)。7 章", 40, 20, 1500, 30, 16, "fontStyle=1;")
gL=d10.group("A. 呼び出しの 4 階層: いつ飛ぶか / いつまで使い回すか", 40, 70, 640, 760, "#f5f5f5", "#666666")
tiers=[
 ("1. セッション単位\nbasesites / languages / currencies\nトークンがあれば users/current、カート ID があれば carts/{id}", "アプリ起動時に 1 回(6 章フェーズ 2〜4)\nタブを閉じるまで使い回す。ログイン / ログアウトでユーザーとカートだけ取り直し", GREY),
 ("2. ページ単位\ncms/pages(ページ構造 + 同梱コンポーネント)\n+ 同梱されなかった分の cms/components", "cms/pages は既定で毎回(routing.loadStrategy = ALWAYS)\ncms/components は初回のみ(同梱 or ストア済みなら飛ばない)\n言語変更 / ログイン / ログアウトで全部捨てる", BLUE),
 ("3. コンポーネント単位(追加リソース)\nページに置かれたコンポーネントの型で決まる\n商品カルーセル → products/search、商品詳細 → products/{code}", "コンポーネント生成時(ビューポート外なら遅延)\n初回のみ。捨てる条件はリソースごと(10 章): 商品は言語・通貨変更まで\n例外: コンポーネントが自分で捨てる設計(商品参照は毎回)", GREEN),
 ("4. アクション単位\nカート追加 POST carts/{id}/entries、配送先設定、注文確定、ログイン", "ユーザー操作のたび(更新系なので使い回しは無い)\n代わりに「成功後に何を取り直すか」が決まっている\n(カートは全体を再取得、チェックアウトは単一 Query を再読込)", ORANGE),
]
y=110
for a,b,c in tiers:
    d10.box(a, 60, y, 290, 160, *c, 11, "fontStyle=1;"); d10.box(b, 360, y, 300, 160, *YEL, 11); y+=180
gR=d10.group("B. 実測(2026-10-23, CSR, 匿名): 同じ画面に戻ったとき何が飛ぶか  GET/HEAD のみ(OPTIONS 除く)", 720, 70, 900, 760, "#fff7e6", "#d79b00")
cols=["リソース","① ホーム初回\n(ブラウザ起動)","② 商品詳細へ\nSPA 遷移(初回)","③ 戻るで\nホーム(再訪)","④ 進むで\n商品詳細(再訪)","階層"]
ws=[250,120,120,120,120,110]
x=740
xs=[]
for n,w in zip(cols,ws):
    xs.append((x,w)); d10.box(n, x, 110, w, 44, "#666666", "#666666", 11, "fontColor=#ffffff;fontStyle=1;"); x+=w+6
HIT=("GET",ORANGE); NO=("— ストア",GREY); NA=("",("#ffffff","#cccccc"))
rowsT=[
 ("basesites / languages / currencies", [("GET ×3",ORANGE), NA, NA, NA], "1"),
 ("carts/{cartId}(localStorage から復元)", [HIT, NA, NA, NA], "1"),
 ("consenttemplates(HEAD)", [("HEAD",ORANGE), NA, NA, NA], "1"),
 ("cms/pages(ホーム)", [HIT, NA, ("GET 再取得",RED), NA], "2"),
 ("cms/pages(ProductPage, code=300938)", [NA, HIT, NA, ("GET 再取得",RED)], "2"),
 ("cms/components(同梱されなかった分)", [("GET ×2",ORANGE), HIT, NO, NO], "2"),
 ("products/search?filters=code:…(カルーセル 17 件)", [HIT, NA, NO, NA], "3"),
 ("products/300938(details / classifications)", [NA, ("GET ×2",ORANGE), NA, NO], "3"),
 ("products/300938/reviews", [NA, HIT, NA, NO], "3"),
 ("products/300938/references", [NA, HIT, NA, ("GET 再取得",RED)], "3 例外"),
 ("合計(GET + HEAD)", [("9",ORANGE), ("6",ORANGE), ("1",RED), ("2",RED)], ""),
]
y=160
for name,cells,tier in rowsT:
    d10.box(name, xs[0][0], y, xs[0][1], 44, *GREY, 11)
    for (t,c),(cx,cw) in zip(cells, xs[1:5]):
        d10.box(t, cx, y, cw, 44, *c, 11)
    d10.box(tier, xs[5][0], y, xs[5][1], 44, *GREY, 11)
    y+=48
d10.text("読み方: 橙 = HTTP が飛んだ、灰 = ストアにあるので飛ばない、赤 = 再訪でも飛ぶ(cms/pages は loadStrategy の既定 ALWAYS、references はコンポーネントが初期化時に cleanReferences() する設計)。\n「毎回」なのは cms/pages だけで、同梱されたコンポーネントデータも一緒に毎回届く。業務データは初回のみ。", 740, y+6, 860, 60, 11)

d12=D("12 cms/pages 応答 → async パイプまでの 8 段階")
d12.text("cms/pages の応答が届いてから、コンポーネントの data$ | async が値を出すまでの 8 段階(左)と、段階ごとに何が起きるか・失敗したときの範囲(右)。4 章", 40, 20, 1700, 30, 16, "fontStyle=1;")
gL=d12.group("A. 8 段階: 何をするか(上から順に実行される)", 40, 70, 680, 1010, "#f5f5f5", "#666666")
steps=[
 ("1. 正規化\nOccCmsPageNormalizer", BLUE, "1 つの JSON から 2 つの形を作る\n・page.slots[位置].components = {uid, typeCode, flexType, properties}\n・components = コンポーネント本体(properties は捨てる)\nflexType = typeCode(CMSFlexComponent だけ flexType 属性)"),
 ("2. ストア格納\nPageEffects → reducer", BLUE, "CmsGetComponentFromPage(同梱全件)と LoadCmsPageDataSuccess を一度に dispatch\ncomponents[uid].pageContext['ContentPage'] = success\nページ index[pageId] = success → ガードが待っていた hasPage が通る"),
 ("3. ガード(まだ描画しない)\nCmsPageGuardService.canActivatePage", PURP, "ページ内の flexType 集合 → determineMappings(遅延モジュールの import())\n→ guards 実行 → i18n チャンク読込 → childRoutes があれば再ナビゲーション\n→ true で Router が PageLayoutComponent を生成、ROUTER_NAVIGATED"),
 ("4. レイアウト → スロット\nPageLayoutComponent / PageSlotComponent", GREEN, "LayoutConfig.layoutSlots[template].slots ∩ 応答の slots → <cx-page-slot> を並べる\n各スロットが getContentSlot(position) で components 配列を取る\npending = 件数 → cx-pending クラス"),
 ("5. 遅延判定とアウトレット\nOutletDirective + DeferLoaderService", GREEN, "cxOutletDefer: INSTANT なら即、DEFER なら IntersectionObserver で画面に入るまで\nラッパーすら作らない(既定は INSTANT)\ncxOutlet=flexType に差し替えテンプレートがあればそちらを描く(1.7)"),
 ("6. ラッパーが createComponent\nComponentWrapperDirective", GREEN, "getMapping(flexType) → 無ければ何もしない(dev 警告のみ)\n子 Injector に CmsComponentData{uid, data$} と mapping.providers を provide\n→ ViewContainerRef.createComponent → constructor で注入 → ComponentCreateEvent"),
 ("7. data$ を購読(ここで初めて動く)\nCmsService.getComponentData", ORANGE, "ストアに uid × context があれば同期で値 → HTTP なし\n無ければ LoadCmsComponent → 同一マクロタスク分をまとめて\nGET cms/components?componentIds=…(50 件/回、商品ページなら productCode=)\nナビゲーションの子項目も同じ getList を通る(別エフェクト)"),
 ("8. async パイプ → 変更検知 → 描画\nAngular AsyncPipe(pure: false)", GREY, "最初の transform で subscribe(= 7 が動く)。同期で来ればその場で値\n値が来るたび markForCheck → OnPush を次の変更検知で再描画\n無い間は null → *ngIf が描かない。(loaded) で pending-- → cx-pending 解除"),
]
paired(d12, 60, 164, steps, 250, 390, 96, 10)
gR=d12.group("B. 段階ごとに何が起きるか: 通信 / ストア / DOM / 失敗の範囲", 760, 70, 1070, 1010, "#fff7e6", "#d79b00")
cols=[("段階",110),("OCC への通信",160),("静的ファイル",120),("NgRx ストア",200),("DOM / 変更検知",190),("失敗したときの範囲",200)]
NONE=("なし",GREY); DASH=("—",GREY)
rows=[
 [("1 正規化",GREY), NONE, NONE, ("まだ触らない",GREY), NONE, ("応答が壊れていれば\nLoadCmsPageDataFail → 404 ページ",RED)],
 [("2 ストア格納",GREY), NONE, NONE, ("components[uid] と page.index に\nsuccess を書く",BLUE), NONE, DASH],
 [("3 ガード",GREY), ("なし\n(guards の実装次第)",GREY), ("遅延モジュールの JS\n翻訳 JSON",ORANGE), ("読むだけ\n(flexType の集合)",BLUE), ("なし\n(ルート設定の差し替えあり)",GREY), ("ページ全体: 遷移中止\n(guards false / import 失敗)",RED)],
 [("4 レイアウト→スロット",GREY), NONE, NONE, ("読むだけ\n(page.template, slots)",BLUE), ("<cx-page-slot> が並ぶ\ncx-pending 付き",GREEN), ("LayoutConfig に無いスロットは\n描かれない(dev 警告)",RED)],
 [("5 遅延判定",GREY), NONE, NONE, NONE, ("IntersectionObserver 登録\n画面内なら即ビルド",GREEN), DASH],
 [("6 createComponent",GREY), NONE, NONE, ("なし(data$ は未購読)",GREY), ("コンポーネントの DOM が生まれる\nComponentCreateEvent",GREEN), ("mapping 無し: そのコンポーネント\nだけ描かれない(本番は無言)",RED)],
 [("7 data$ 購読",GREY), ("同梱済みなら なし\n不足分だけ cms/components",ORANGE), NONE, ("loaderState を見て dispatch 判定\n応答を components[uid] に格納",BLUE), NONE, ("uid が無い: null → そのコンポーネント\nだけ空。言語変更/ログインで要求破棄",RED)],
 [("8 async → 描画",GREY), NONE, NONE, ("select で現在値を読む",BLUE), ("markForCheck → 次の変更検知で描画\npending-- → cx-pending 解除",GREEN), DASH],
]
grid(d12, 780, 110, cols, rows, 96, 10, 44)
d12.text("読み方: 橙 = 通信が起きる(OCC か静的ファイル)、青 = NgRx ストアを書く/読む、緑 = DOM が変わる、赤 = 失敗したときに影響する範囲。\ncms/pages の応答から最初の描画まで OCC への通信は 0 本。cms/components が飛ぶのは「購読した時点でストアに無い uid」とナビゲーションの子項目だけ。", 780, 1024, 1030, 44, 11)

d13=D("13 API の形 → State の形: 3 層の作り変え")
d13.text("cms/pages の JSON(入れ子の木)が Normalizer → Effect → Reducer の 3 層を通って cms ステート(3 テーブル)になるまで(左)と、State で見える違いごとに「どの層が作るか」「変えたいときの入口」(右)。5 章", 40, 20, 1760, 30, 16, "fontStyle=1;")
gL=d13.group("A. 3 層の作り変え(上から順に通る)", 40, 70, 720, 900, "#f5f5f5", "#666666")
steps=[
 ("入力: cms/pages の JSON\nOcc.CMSPage", GREY, "入れ子の木。スロットの中にコンポーネント本体が埋まっている\n{ uid, typeCode, label, template, ...,\n  contentSlots.contentSlot[ { position, properties,\n    components.component[ { uid, typeCode, name, properties, ...本体 } ] } ] }"),
 ("層 1 Normalizer\nOccCmsPageNormalizer.convert\n(DI: CMS_PAGE_NORMALIZER, multi)", BLUE, "ConverterService.pipeable がアダプタの中で適用。出力は {page, components} の 2 つ\n・normalizePageData: uid→pageId, typeCode→type, robotTag→robots[]\n・normalizePageSlotData: contentSlot[] → slots[position] の辞書\n・normalizePageComponentData: 各本体を {uid,typeCode,flexType,properties} に削って slots に\n・normalizeComponentData: 本体全体を components[] に。properties は undefined に"),
 ("層 2 Effect\nPageEffects.loadPageData$", PURP, "1 つの応答を 2〜3 個のアクションに分割して一度に dispatch\n・CmsGetComponentFromPage( components.map(c => {component: c, pageContext}) )\n・LoadCmsPageDataSuccess( pageContext, page )\n・(CmsSetPageSuccessIndex: label と id が違うときだけ)\npageContext は API に無い情報。ここで添えられる"),
 ("層 3 Reducer\nentityReducer / loaderReducer\n+ cms の各 reducer", ORANGE, "・entityReducer: entityId と payload が両方配列なら 1 件ずつ割って entities[id] に\n・loaderReducer: {loading, error, success, value} のフラグを包む\n・components.reducer: {component, pageContext[serializePageContext(ctx,true)]}\n・page-data.reducer: entities[pageId] = page(Normalizer 出力そのまま)\n・page-index.reducer: entities[label|code] = pageId(索引だけ)\n・navigation-entry-item.reducer: { uid + '_AbstractCMSComponent': 本体 } の辞書"),
 ("出力: cms ステート\n(Redux DevTools で見える形)", GREEN, "cms\n├ page.pageData.entities[pageId]   ← 配置(slots[pos].components = 4 項目)\n├ page.index.{content|product|category|catalog}.entities[id] = pageId\n├ components.entities[uid] = { component, pageContext: {\"ContentPage\": {...}} }\n└ navigation.entities[nodeId] = { uid_AbstractCMSComponent: {...} }"),
]
paired(d13, 60, 164, steps, 250, 440, 120, 10)
gR=d13.group("B. State で見える違い: どの層が作るか / 変えたいときの入口", 800, 70, 1100, 900, "#fff7e6", "#d79b00")
cols=[("State で見える違い",200),("API 側",160),("State 側",190),("作っている場所",250),("変えたいときの入口",250)]
rows=[
 [("ページとコンポーネントが\n別テーブル",GREY), ("スロットの中に本体が入れ子",GREY), ("page.pageData と components",GREEN), ("層 1 normalizePageComponentData\n+ normalizeComponentData",BLUE), ("CMS_PAGE_NORMALIZER に\n自作 converter を multi 追加",BLUE)],
 [("スロットが辞書 /\n中のコンポーネントが 4 項目",GREY), ("contentSlot[] 配列\n本体の全属性",GREY), ("slots[position]\n{uid,typeCode,flexType,properties}",GREEN), ("層 1 normalizePageSlotData\n:120-125",BLUE), ("同上",BLUE)],
 [("本体に properties が無い",GREY), ("有る",GREY), ("undefined",GREEN), ("層 1 normalizeComponentData:185\n(意図的: コメントあり)",BLUE), ("同上。ただし既定の後に動くので\n消された後。トップレベル属性を使う",RED)],
 [("flexType が全件に有る /\npageId・type・robots[] の名前",GREY), ("CMSFlexComponent だけ /\nuid・typeCode・robotTag",GREY), ("全コンポーネント /\npageId・type・robots[]",GREEN), ("層 1 getFlexTypeFromComponent\nnormalizePageData / normalizeRobots",BLUE), ("同上",BLUE)],
 [("pageContext が付いている",GREY), ("無い",GREY), ("pageContext[\"ContentPage\"]\npageContext[\"ProductPage-<code>\"]",GREEN), ("層 2 PageEffects で添付\n層 3 components.reducer で形に",PURP), ("変えない(キャッシュ共有の鍵)",GREY)],
 [("loading/success/error/value",GREY), ("無い",GREY), ("有る",GREEN), ("層 3 loaderReducer\n(value = componentExistsReducer)",ORANGE), ("変えない",GREY)],
 [("entities[uid] / entities[pageId]\nの辞書",GREY), ("配列",GREY), ("辞書",GREEN), ("層 3 entityReducer\n(配列 payload を 1 件ずつ分割)",ORANGE), ("変えない",GREY)],
 [("cms/components で取った本体",GREY), ("API の形のまま",GREY), ("API の形のまま + pageContext",GREEN), ("層 1 は無し(CMS_COMPONENT_NORMALIZER\nの既定登録 0 件)。層 2 ComponentsEffects",PURP), ("CMS_COMPONENT_NORMALIZER に\nmulti 追加(既定は空)",BLUE)],
]
grid(d13, 820, 110, cols, rows, 76, 8, 44)
d13.text("読み方: 青 = 層 1 Normalizer(アダプタ層、DI の multi provider で差し替え可)、紫 = 層 2 Effect、橙 = 層 3 Reducer、緑 = State 側の形、赤 = 注意点。\nAPI → State の変換はこの 3 層に分散している。State の形を変えたい場合の入口は CMS_PAGE_NORMALIZER / CMS_COMPONENT_NORMALIZER で、Effect と Reducer には手を入れない。", 820, 870, 1060, 44, 11)

out='<mxfile host="app.diagrams.net" modified="2026-10-23T00:00:00.000Z" agent="gen_drawio.py" version="24.0.0" type="device">'+d1.xml()+d2.xml()+d3.xml()+d4.xml()+d5.xml()+d6.xml()+d7.xml()+d8.xml()+d9.xml()+d10.xml()+d11.xml()+d12.xml()+d13.xml()+'</mxfile>'
import os,sys; out_path=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(__file__),'..','docs','diagrams','spartacus-architecture.drawio'); open(out_path,'w').write(out)
print("ok", len(out))
