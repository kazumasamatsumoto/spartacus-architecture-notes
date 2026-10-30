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

d14=D("14 ルーティングと配置: 普通の Angular との違い")
d14.text("普通の Angular では自分で書く「URL → コンポーネントの表」と「どこに何を置くかのテンプレート」を、Spartacus は誰がどう持っているか。左: ルーティング。右: 配置は「文字列をキーに 4 つの表を引く」の繰り返し。3 章", 40, 20, 1740, 30, 16, "fontStyle=1;")
# ---- A. routing
gA=d14.group("A. ルーティング: URL とページの対応表は誰が持つか", 40, 70, 720, 900, "#f5f5f5", "#666666")
d14.text("普通の Angular", 60, 100, 300, 24, 12, "fontStyle=1;")
a1=d14.box("routes 表(自分で書く)\n/products/:id → ProductComponent\n/cart → CartComponent", 60, 128, 230, 80, *GREY, 11)
a2=d14.box("Angular Router\nパスを表で引く", 330, 128, 170, 80, *GREY, 11)
a3=d14.box("URL ごとに違う\nコンポーネントが出る", 540, 128, 200, 80, *GREY, 11)
d14.edge(a1,a2); d14.edge(a2,a3)
d14.text("Spartacus", 60, 232, 300, 24, 12, "fontStyle=1;")
s1=d14.box("URL\n/electronics-spa/en/USD/faq", 60, 260, 320, 56, *GREY, 11)
s2=d14.box("'**' ルートが 1 本だけ(起動時に追加)\ncanActivate: CmsPageGuard\ncomponent: PageLayoutComponent\n→ どの URL でも同じ 1 つのルートに当たる", 60, 340, 320, 90, *BLUE, 11)
s3=d14.box("URL → ページの問い合わせキー(PageContext)\nproductCode あり → {ProductPage, '300938'}\ncategoryCode あり → {CategoryPage, code}\nどれでもない → {ContentPage, '/faq'}(URL の残りがラベル)", 60, 454, 320, 100, *BLUE, 11)
s4=d14.box("CmsPageGuard\nGET cms/pages?pageType=ContentPage&pageLabelOrId=/faq", 60, 578, 320, 64, *ORANGE, 11)
s5=d14.box("CMS のページ表(Backoffice が持つ)\nラベル /faq → ContentPage1Template + スロット構成\nラベル /campaign を作れば、フロント無変更で開く", 60, 666, 320, 86, *ORANGE, 11)
s6=d14.box("あれば PageLayoutComponent を出す\n無ければ 404 ページ(notFound ラベル)へ", 60, 776, 320, 64, *GREEN, 11)
for a,b in [(s1,s2),(s2,s3),(s3,s4),(s4,s5),(s5,s6)]: d14.edge(a,b)
d14.box("例外: パスの「パターン」だけはフロント設定\n商品: path: null + data.cxRoute='product'\n→ 起動時に routing.routes.product.paths\n  ['product/:productCode/:name', …] で埋まる\nカテゴリ・検索・マイアカウント系も同じ方式\n\nただし component はやはり PageLayoutComponent。\nパターンは productCode を取り出すための入口で、\n画面の中身は CMS が返すスロット構成で決まる", 410, 340, 330, 214, *RED, 11)
d14.box("結論\nURL とページの対応表はフロントの routes ではなく、\nCMS のページラベルが持っている。\nフロントが持つのは「URL をキーに変える規則」と\n「商品・カテゴリなどのパスのパターン」だけ。", 410, 578, 330, 130, *YEL, 11)
d14.text("根拠: add-cms-route.ts:12-16 / router.reducer.ts:169-215 / cms-page.guard.ts:51-84 / product-details-page.module.ts:17-23 / configurable-routes.service.ts:48-100", 60, 860, 680, 40, 10)
# ---- B. placement
gB=d14.group("B. 配置: 「文字列をキーに表を引く」を 4 回繰り返す(橙 = CMS / Backoffice が持つ表、青 = フロント設定の表、緑 = 画面に起きること)", 800, 70, 980, 900, "#fff7e6", "#d79b00")
b0=d14.box("外枠 storefront.component.html(普通の Angular と同じ直書き)\n[ ヘッダ枠(固定スロット) ]  [ <router-outlet> ← PageLayoutComponent ]  [ フッタ枠 ]", 820, 110, 940, 56, *GREY, 11)
T=820; TW=400; AX=1260; AW=500; Y=190; H=104; STEP=132
t1=d14.box("表① cms/pages の応答(CMS が持つ)\ntemplate: 'LandingPage2Template'\nslots: { Section1:{…}, Section2A:{…}, … }   ← 辞書。順番は無い", T, Y, TW, H, *ORANGE, 11)
r1=d14.box("PageLayoutComponent\n応答の template 名を取り出し、その名前で表②を引く", AX, Y, AW, H, *GREEN, 11)
t2=d14.box("表② LayoutConfig.layoutSlots[template].slots(フロント設定)\nLandingPage2Template: ['Section1','Section2A','Section2B','Section2C',\n'Section3','Section4','Section5']   ← 縦に並べる順番はここ", T, Y+STEP, TW, H, *BLUE, 11)
r2=d14.box("*ngFor 1 回目: 表② にあって表① にもあるスロットだけ、順に\n<cx-page-slot position='Section1'> <cx-page-slot position='Section2A'> …\n空の箱が並ぶ。表② に無いスロットは描かれない(dev 警告)", AX, Y+STEP, AW, H, *GREEN, 11)
t3=d14.box("表③ 応答の slots[position].components(CMS が持つ)\n[ {uid, typeCode:'CMSParagraphComponent', flexType, properties}, … ]\n並び順 = Backoffice でスロットに並べた順", T, Y+2*STEP, TW, H, *ORANGE, 11)
r3=d14.box("*ngFor 2 回目: 各 <cx-page-slot> が自分の position で表③を引き、\n1 件ごとに <ng-container cxComponentWrapper> を置く", AX, Y+2*STEP, AW, H, *GREEN, 11)
t4=d14.box("表④ CmsConfig.cmsComponents[flexType](フロント設定)\nprovideConfig({ cmsComponents: {\n  CMSParagraphComponent: { component: ParagraphComponent } } })", T, Y+3*STEP, TW, H, *BLUE, 11)
r4=d14.box("cxComponentWrapper: flexType で表④を引き、\nViewContainerRef.createComponent(クラス, injector) で「その場に」生やす\n子 Injector に CmsComponentData{uid, data$} を入れておく\n表④に無い typeCode → 何も生えず空(本番は無言、dev 警告)", AX, Y+3*STEP, AW, H+20, *GREEN, 11)
for t,r in [(t1,r1),(t2,r2),(t3,r3),(t4,r4)]: d14.edge(t,r)
for a,b in [(b0,r1),(r1,r2),(r2,r3),(r3,r4)]: d14.edge(a,b, exit=(0.5,1), entry=(0.5,0))
d14.box("バックエンドが触るもの: template 名・スロット名・typeCode・並び順(表①③)。\nフロントに頼むのは 2 つだけ: 新しいテンプレート / スロット → 表②に追加。新しい typeCode → 表④に追加。\n「配置」は普通の Angular のテンプレートではなく、この 4 つの表の組み合わせで決まる。", 820, Y+4*STEP+30, 940, 80, *YEL, 11)
d14.text("根拠: storefront.component.html / page-layout.component.html / page-layout.service.ts:106-127 / recipes/config/layout-config.ts:55-64 / page-slot.component.html / component-wrapper.directive.ts:81-117 / default-component.handler.ts:56-70", 820, 920, 940, 40, 10)


d15=D("15 変更検知の 3 段階と dirty の経路")
d15.text("API の応答が State に入ったあと、Angular はどの view を評価し、どの DOM を触るのか。左: 3 段階(A いつ / B どの view / C どのバインディング)。右: ソート 1 回とホーム再訪 1 回を view の木で見る。16 章", 40, 20, 1740, 30, 16, "fontStyle=1;")
gL=d15.group("A → B → C: 応答が届いてから DOM が変わるまでの 3 段階", 40, 70, 720, 900, "#f5f5f5", "#666666")
l0=d15.box("きっかけ\nクリック / OCC 応答(XHR 完了) / タイマー完了", 70, 110, 660, 50, *GREY, 11)
l1=d15.box("A. tick の予約(いつ走るか)\nzone.js がマクロタスクの終わりに ApplicationRef.tick() を予約。eventCoalescing で 1 回にまとめる\nmarkForCheck() 自身も予約する(markViewDirty → changeDetectionScheduler.notify)\n→ OCC 応答のたびに最低 1 回、クリックのたびに 1 回", 70, 185, 660, 90, *BLUE, 11)
l2=d15.box("B-1. 印を付ける(markViewDirty)\n自分から根元まで親を辿って全部に付ける。兄弟には付けない\n入口 1: AsyncPipe が新しい値を受け取る → markForCheck()   ← API 応答はここから入る\n入口 2: テンプレート内の DOM イベント(wrapListener)\n入口 3: OnPush コンポーネントの @Input が変わった", 70, 300, 660, 104, *ORANGE, 11)
l3=d15.box("B-2. tick: view ごとに評価するか決める(detectChangesInView)\n評価する: Default(CheckAlways) / dirty / RefreshView / signal が変化\n評価しない: OnPush で印なし。子孫に印があれば「通過」するだけでテンプレートは一切評価しない\nSpartacus: storefront 98 コンポーネント中 67 が OnPush(PageSlot / PageLayout / Banner / Paragraph …)\nDefault は StorefrontComponent と ProductListComponent", 70, 428, 660, 104, *ORANGE, 11)
l4=d15.box("C の前段: Observable の中で止める\nPageSlot: uid の並びが同じなら流さない(isDistinct) → components 配列が差し替わらず *ngFor が動かない\nPageLayoutService.getSlots: スロット名を 1 つずつ比較 → 同じなら <cx-page-slot> を残す\n→ ヘッダー・フッターのコンポーネントは破棄も生成もされない", 70, 556, 660, 90, *YEL, 11)
l5=d15.box("C. 評価した view の中で、変わったバインディングだけ DOM に書く\n値: Object.is で比較。innerHTML の文字列が同じなら書かない\n*ngFor(trackBy なし): 新しい配列 → 行を全部破棄して作り直す(商品一覧)\n*ngFor(文字列配列): 値で比較 → 同じ名前なら残す(スロットの並び)", 70, 670, 660, 90, *GREEN, 11)
for a,b in [(l0,l1),(l1,l2),(l2,l3),(l3,l4),(l4,l5)]: d15.edge(a,b)
d15.box("結論: どの DOM が変わるかは「誰が何を | async しているか」という購読の配線と、Angular の規則で機械的に決まる。\nフロントが「ヘッダーは除外」と書いているのではない。API の本数と DOM の書き換え量は別の軸。", 70, 790, 660, 70, *RED, 11)
d15.text("根拠: app.config.ts:30 / @angular/core 21.2.25 _debug_node-chunk.mjs:5900-5915(detectChangesInView), 5967-5977(markViewDirty), 6142-6144(markForCheck), 8225-8232(wrapListener) / @angular/common _common_module-chunk.mjs:2601-2605(AsyncPipe) / page-slot.component.ts:51, 97-101, 124-130, 201-213 / page-layout.service.ts:68-78 / product-list.component.html:54, 64", 70, 870, 660, 80, 10)
gR=d15.group("view の木で見る 2 つの実例(橙 = 印が付いて評価される、灰 = 印なしで飛ばされる、緑 = Default なので評価されるが DOM は不変、赤枠 = DOM を触る)", 800, 70, 980, 900, "#fff7e6", "#d79b00")
# ---- tree 1: sort
d15.text("実例 1 ソート: クリック → products/search 1 本 → 応答 → ProductList の model$ | async が印 → 経路だけ評価。Guard も cms/pages も走らない(3.0, 16.5)", 820, 104, 940, 40, 12, "fontStyle=1;")
BW=190; BH=56; F=10
r1=d15.box("App(Default)\n評価、DOM 不変", 1195, 150, BW, BH, *GREEN, F)
r2=d15.box("StorefrontComponent(Default)\n評価、DOM 不変", 1195, 230, BW, BH, *GREEN, F)
r3=d15.box("PageLayout[header](OnPush)\n印なし → 飛ばされる", 830, 320, BW+30, BH, *GREY, F)
r3b=d15.box("header の PageSlot / Logo /\nSearchBox / Navigation\n評価されない", 830, 410, BW+30, BH+8, *GREY, F)
r4=d15.box("PageLayout[main](OnPush)\n印あり → 評価、DOM 不変", 1195, 320, BW, BH, *ORANGE, F)
r5=d15.box("PageSlot[ProductListSlot](OnPush)\n印あり → 評価、DOM 不変", 1195, 410, BW+20, BH, *ORANGE, F)
r6=d15.box("ProductListComponent(Default)\n印の起点: model$ | async が markForCheck\nDOM: 商品行を全部作り直し(trackBy なし)", 1150, 500, BW+110, BH+14, ORANGE[0], "#b85450", F, "strokeWidth=3;")
r7=d15.box("PageLayout[footer](OnPush)\n印なし → 飛ばされる", 1560, 320, BW+10, BH, *GREY, F)
for a,b in [(r1,r2),(r2,r3),(r2,r4),(r2,r7),(r3,r3b),(r4,r5),(r5,r6)]: d15.edge(a,b)
# ---- tree 2: home revisit
d15.text("実例 2 ホーム再訪(商品詳細 → ホーム): cms/pages 1 本 → State を同じ値で上書き → data$ を持つ全 view に印 → 評価されるが、値が同じなので DOM は 1 箇所も変わらない(16.6)", 820, 600, 940, 40, 12, "fontStyle=1;")
s1=d15.box("App / StorefrontComponent(Default)\n評価、DOM 不変", 1195, 646, BW+20, BH, *GREEN, F)
s2=d15.box("PageLayout[header](OnPush)\n子孫に印 → 通過・評価", 830, 730, BW+30, BH, *ORANGE, F)
s3=d15.box("PageLayout[main](OnPush)\n再利用(同じ ** ルート)、評価", 1195, 730, BW+20, BH, *ORANGE, F)
s4=d15.box("PageLayout[footer](OnPush)\n子孫に印 → 通過・評価", 1560, 730, BW+10, BH, *ORANGE, F)
s5=d15.box("各 PageSlot: isDistinct で止まる\n(uid の並びが同じ) → *ngFor 動かず\n破棄も生成も無し", 830, 815, BW+30, BH+14, *YEL, F)
s6=d15.box("Banner / Paragraph / Logo …\ndata$ が新オブジェクト → 印 → 評価\ninnerHTML の文字列が同じ → DOM 不変", 1130, 815, BW+150, BH+14, *ORANGE, F)
s7=d15.box("ナビゲーション\n同上。子項目は State 済み\n→ cms/components も飛ばない", 1560, 815, BW+10, BH+14, *ORANGE, F)
for a,b in [(s1,s2),(s1,s3),(s1,s4),(s2,s5),(s3,s6),(s4,s7)]: d15.edge(a,b)
d15.text("ソートと再訪の違い: ソートは API 1 本で商品行を全部作り直す。再訪は API 1 本で DOM を 1 箇所も触らない。API の本数と描画コストは別の軸(16.7)。", 820, 905, 940, 40, 11)

d16=D("16 zone.js の見張りと dirty の 2 つの時刻")
d16.text("zone.js は何を見張っていて、いつ tick を起こすのか。印が付く時刻と見つかる時刻はなぜ分かれるのか。左: zone.js → NgZone → tick。右: クリック 1 回と OCC 応答 1 回を時間軸で。17 章", 40, 20, 1740, 30, 16, "fontStyle=1;")
gL=d16.group("zone.js → NgZone → tick: 歩く人はいつ来るか", 40, 70, 760, 900, "#f5f5f5", "#666666")
z0=d16.box("zone.js がブラウザ API を差し替える(読み込み時)\nsetTimeout / addEventListener / XHR / Promise.then / fetch / queueMicrotask → すべて「タスク」になる(zone.js:1680-2327)", 70, 110, 700, 56, *GREY, 11)
z1=d16.box("タスクを数える\nscheduleTask で +1、runTask の finally で -1(zone.js:187-214, 144-186)。0 ↔ 1 の瞬間だけ onHasTask(:403-418)\nPromise の続きは自前のキューに積み、タスクの終わりにまとめて流す(:452-468, 538-566)", 70, 186, 700, 72, *BLUE, 11)
z2=d16.box("NgZone の 'angular' zone のフック(_effect-chunk2.mjs:2529-2585)\nonInvokeTask / onInvoke: 入るとき onEnter(isStable=false)、出るとき onLeave → checkStable\nonHasTask(microTask の増減): hasPendingMicrotasks を更新 → checkStable", 70, 278, 700, 72, *BLUE, 11)
z3=d16.box("checkStable の 3 条件(:2487-2502)\n① 実行中のタスクが無い(_nesting == 0) ② Angular zone のマイクロタスクが 0 ③ 前回 stable 以降に何か動いた\nマクロタスク(HTTP や setTimeout の残り)は見ない → 「全部返ってきたら」ではなく「今の仕事が終わったら」", 70, 370, 700, 76, *ORANGE, 11)
z3b=d16.box("eventCoalescing: true(app.config.ts:30)\nDOM イベントの直後だけ ② をわざと偽にして止め、rAF / setTimeout(0) の早い方で checkStable(:2504-2527)。マイクロタスクには効かない", 70, 466, 700, 56, *YEL, 11)
z4=d16.box("onMicrotaskEmpty → NgZoneChangeDetectionScheduler(core.mjs:299-325)\nappRef.dirtyFlags |= 1(Global)→ ApplicationRef._tick()", 70, 542, 700, 50, *GREEN, 11)
z5=d16.box("tick(_debug_node-chunk.mjs:12396-12498)\nsynchronize → synchronizeOnce → 各 root view を detectChangesInternal(mode 0 Global)\n→ detectChangesInView(:5900-5933)が view ごとにフラグを読む・決める・消す(1024|8192 は判定直後 :5913、64 は評価後 :5848)", 70, 612, 700, 76, *GREEN, 11)
for a,b in [(z0,z1),(z1,z2),(z2,z3),(z3,z3b),(z3b,z4),(z4,z5)]: d16.edge(a,b)
d16.box("結論: 印を付ける人と印を見つける人は別。付けるのは値が変わったコードの中(同期)、見つけるのは tick の中だけ。\ntick は「Angular zone のマイクロタスクが 0 になった瞬間」に走る。HTTP の本数ではなく、仕事の区切りの数だけ走る。", 70, 712, 700, 70, *RED, 11)
d16.box("印の 3 つの入口と時刻: ① async パイプ = 値が流れた瞬間(応答処理の中) ② DOM イベント = ハンドラの前(wrapListener :8232) ③ @Input = 親の tick の最中(同じ tick の数十行あとで見つかる)\ntick の中で付いた 64 は、その tick では見つからない(requiresRefreshOrTraversal は 1024 / 8192 / consumer.dirty しか見ない)→ 次の tick へ", 70, 798, 700, 72, *YEL, 10)
d16.text("根拠: zone.js 0.16.3 / @angular/core 21.2.25 / @angular/common _module-chunk.mjs:761-850(FetchBackend は fetch と body 読み取りを zone の外で行う)/ @angular/build utils.js:160-167, 366-373(zone.js ありなら async/await を then に落とす)/ projects/storefrontapp/project.json:23, app.config.ts:28, 30", 70, 884, 700, 70, 10)
gR=d16.group("時間軸(橙 = 印を付ける、緑 = tick で印を見つけて消す、灰 = zone の外や印に関係ない処理)", 840, 70, 940, 900, "#fff7e6", "#d79b00")
CW=440
d16.text("実例 1 ソートのクリック(16.5)", 860, 104, CW, 24, 12, "fontStyle=1;")
c1=d16.box("t1 click → zone.js globalCallback → invokeTask → onEnter(isStable = false)", 860, 134, CW, 44, *GREY, 10)
c2=d16.box("t1 wrapListener がハンドラの前に markViewDirty(ProductList, 5)\nProductList → PageSlot → PageLayout[main] → Storefront → App → root に 64|1024", 860, 192, CW, 56, *ORANGE, 10)
c3=d16.box("t1 ハンドラ: アクション → Effect → HttpClient → fetch 開始(zone の外)\nハンドラ終了 → eventTask + eventCoalescing → checkStable を保留", 860, 262, CW, 56, *GREY, 10)
c4=d16.box("t2 次フレーム(rAF / setTimeout 0)→ checkStable → onMicrotaskEmpty → tick #1\n印の道筋だけ評価。header / footer は飛ばす。印を消す", 860, 332, CW, 56, *GREEN, 10)
c5=d16.box("t3 応答ヘッダ → fetch の Promise 解決。ボディ読み取りは zone の外(tick なし)", 860, 402, CW, 44, *GREY, 10)
c6=d16.box("t4 await の続きが Angular zone のマイクロタスクで走る\nobserver.next → reducer → selector → async パイプ markForCheck\nProductList → root に 64|1024", 860, 460, CW, 64, *ORANGE, 10)
c7=d16.box("t4 マイクロタスク終了 → 数が 0 → onHasTask → checkStable → tick #2 その場で\nProductList を評価、行を作り直し(16.4)。印を消す。coalescing は効かない", 860, 538, CW, 56, *GREEN, 10)
for a,b in [(c1,c2),(c2,c3),(c3,c4),(c4,c5),(c5,c6),(c6,c7)]: d16.edge(a,b)
X2=1320
d16.text("実例 2 ホーム再訪: Router + cms/pages(16.6)", X2, 104, CW, 24, 12, "fontStyle=1;")
e1=d16.box("t1 リンクの click → wrapListener で印 → Router が遷移を開始", X2, 134, CW, 44, *ORANGE, 10)
e2=d16.box("t1' 次フレームで tick #1(リンクの view の道筋だけ)", X2, 192, CW, 44, *GREEN, 10)
e3=d16.box("t2… Router の各段(Guard / cms/pages の fetch / NavigationEnd)は Promise の連鎖\n= マイクロタスク。段が終わるたびに checkStable → tick", X2, 250, CW, 56, *GREY, 10)
e4=d16.box("応答 → State を同じ値で上書き → data$ | async を持つ全 view が markForCheck\n(Banner / Paragraph / Logo / Navigation …)→ それぞれ root まで 64|1024", X2, 320, CW, 56, *ORANGE, 10)
e5=d16.box("tick #2…#n 印の付いた view を全部評価\nbindingUpdated が全部 false → DOM は 1 箇所も変わらない(16.6)", X2, 390, CW, 56, *GREEN, 10)
e6=d16.box("遷移 1 回で tick は複数回。tick の回数と DOM を触った回数は別の軸。\ntick 1 回の費用 = 印の道筋 + Default の view(App / Storefront / ProductList)", X2, 460, CW, 56, *YEL, 10)
for a,b in [(e1,e2),(e2,e3),(e3,e4),(e4,e5),(e5,e6)]: d16.edge(a,b)
d16.box("本家の OCC 応答が Angular zone に戻る経路(17.3)\nFetchBackend は fetch とボディ読み取りを runOutsideAngular で行う(_module-chunk.mjs:793, 834)。\nしかし doRequest は Observable の購読時 = Angular zone の中で始まるので、runOutsideAngular の外側の await の続き(observer.next)は Angular zone に戻る。\nこれは CLI が zone.js ありのアプリで async/await を Promise.then に落とすから(@angular/build utils.js:160-167, 366-373)。", 860, 630, 900, 96, *BLUE, 10)
d16.box("きっかけ別の tick の時刻\nクリック: リスナ終了 → 次フレーム(coalescing) / setTimeout 完了(ミニアプリの擬似 OCC): その場 / Promise・await の続き: その場 / OCC 応答(fetch): 応答処理の続きが終わった瞬間 / Router 遷移: 段ごとに複数回 / zone の外からの markForCheck・signal.set: scheduler が rAF / setTimeout で予約(hybrid)", 860, 744, 900, 90, *GREY, 10)
d16.text("ミニアプリの観測パネル(playground/mini-spartacus)の CD 行は afterEveryRender で tick の終わりを検出する(debug-log.service.ts:29)。ソートで CD 行が 2 行(t2 と t4)出て、どちらにも PageLayout[header] が無いのはこの時間軸のとおり。", 860, 850, 900, 50, 10)

d17=D("17 Signal の反応グラフと async パイプとの違い")
d17.text("Signal は Observable + async パイプと何が違うのか。印はどこに付き、誰が tick を予約するのか。左: 値が変わってから DOM が変わるまでの 2 つの経路。右: producer / consumer のリンクと set() の経路。18 章", 40, 20, 1740, 30, 16, "fontStyle=1;")
gL=d17.group("値が変わってから DOM が変わるまで: 2 つの経路を並べる", 40, 70, 900, 900, "#f5f5f5", "#666666")
AX=70; BX=510; W=410
d17.text("Observable + async パイプ(Spartacus の主経路)", AX, 104, W, 24, 12, "fontStyle=1;")
d17.text("signal をテンプレートで読む", BX, 104, W, 24, 12, "fontStyle=1;")
rows=[
 (GREY, 56, "値が変わる: reducer が State を書き換え、selector が新しい値を流す", "値が変わる: s.set(v)。equal(既定は Object.is 相当)で同じなら何もしない。印も付かない(_effect-chunk.mjs:365-372)"),
 (ORANGE, 72, "印: AsyncPipe._updateLatestValue → markForCheck → markViewDirty\n自分〜根元に 64|1024(「購読している view」単位、_common_module-chunk.mjs:2601-2607)", "印: signalValueChanged → producerNotifyConsumers → consumerMarkDirty → consumerMarkedDirty\n読んだ view に consumer.dirty、先祖に 8192 だけ(markAncestorsForTraversal、_debug_node-chunk.mjs:5645-5647)"),
 (BLUE, 60, "tick の予約: 自分ではしない。zone が起こす tick を待つ(17 章)。zone の外なら notify(4)", "tick の予約: notify(0) → dirtyFlags |= 2。zone の中なら zone に任せ、外なら rAF / setTimeout で自前(18.4)。zone が無くても動く"),
 (ORANGE, 72, "評価判定: detectChangesInView の flags & 64 / flags & 1024\nOnPush でないと Global の tick で毎回評価される", "評価判定: 同じ関数の consumer.dirty && consumerPollProducersForChange(version 比較、:5908)\nOnPush かどうかに依らず「読んだ view」だけ"),
 (GREEN, 56, "DOM: bindingUpdated の Object.is で変わったバインディングだけ(16.4)", "DOM: 同じ。その前に equal と computed の version 比較で評価そのものが止まる"),
 (YEL, 72, "購読の開始: async パイプが初めて評価されたとき(遅延)\n= 8.0 規則 3「購読した瞬間に取りに行く」", "購読の開始: toSignal は作った瞬間(rxjs-interop.mjs:126-141)\n= コンポーネント生成時に API が飛ぶ。*ngIf で隠れていても"),
]
y=134
for col,h,a,b in rows:
    d17.box(a, AX, y, W, h, *col, 10); d17.box(b, BX, y, W, h, *col, 10); y+=h+14
d17.box("結論: signal が変えるのは「どの view に印が付くか」と「誰が tick を予約するか」だけ。API の本数・応答の形・State の形は変わらない。\nバックエンド側で signal の有無によって変えることは無い。変わるのは購読の開始時刻(toSignal は生成時)。", AX, y+6, 850, 72, *RED, 11)
d17.text("根拠: _effect-chunk.mjs:26-41(REACTIVE_NODE), 43-87(producerAccessed), 91-103(producerUpdateValueVersion), 105-129, 163-178, 340-396 / _debug_node-chunk.mjs:5641-5677(テンプレートの consumer), 5758-5770, 5908-5912, 18262-18266 / _effect-chunk2.mjs:1781-1805, 2884-3011(effect) / rxjs-interop.mjs:74-158 / core.mjs:25-57(input)", AX, y+92, 850, 70, 10)
gR=d17.group("反応グラフ: 誰が誰を読んだか(producer → consumer)と、set() が印を付ける経路", 980, 70, 800, 900, "#fff7e6", "#d79b00")
p1=d17.box("signal: storeCode\nversion = 3, value = '0001'\nconsumers → [computed hours]", 1010, 120, 230, 70, *BLUE, 10)
p2=d17.box("input(): productCode\n親テンプレートの [productCode] が親の tick の中で set() する(18.7)", 1300, 120, 230, 70, *BLUE, 10)
q1=d17.box("computed: hours\nproducers → [storeCode @ v3]\n読まれたときに version を比べ、違えば再計算(18.2)", 1010, 240, 230, 80, *PURP, 10)
t1=d17.box("テンプレートの consumer(lView)\nhours() を読んだ瞬間にリンクが張られる\nREACTIVE_TEMPLATE_CONSUMER(:5648-5650)", 1300, 240, 230, 80, *ORANGE, 10)
f1=d17.box("effect(view): フォーカス制御など\nrefreshView の中、テンプレートの後で実行(:5795)", 1010, 370, 230, 64, *PURP, 10)
f2=d17.box("effect(root) / toObservable\nsynchronizeOnce の先頭で flush(:12454-12457)", 1300, 370, 230, 64, *PURP, 10)
d17.edge(p1,q1,"読む"); d17.edge(q1,t1,"読む"); d17.edge(p2,t1,"読む"); d17.edge(q1,f1,"読む"); d17.edge(p1,f2,"読む", pts=[(1125,105),(1415,105)])
s1=d17.box("storeCode.set('0002') の経路(同期、値は渡さない)\n① version++、epoch++(_effect-chunk.mjs:391-396) ② consumers を辿って consumerMarkDirty(computed → テンプレートの consumer → effect)\n③ テンプレート consumer の consumerMarkedDirty → markAncestorsForTraversal: 先祖に 8192、changeDetectionScheduler.notify(0)\n④ effect は scheduler に予約(root)/ view に 8192(view)。実行は次の tick", 1010, 470, 740, 96, *RED, 10)
s2=d17.box("次の tick で: detectChangesInView が consumer.dirty を見つけ、version 比較で本当に変わっていれば評価(:5908)\n先祖(8192)は通過するだけ。兄弟は触らない。評価の中で bindingUpdated が変わった箇所だけ DOM へ", 1010, 586, 740, 60, *GREEN, 10)
d17.edge(s1,s2)
d17.box("Spartacus 2612 の実態: signal 系 API は 24 箇所 / 12 ファイル(spec 除く)。State → view の主経路(data$ / ProductService / Facade)は Observable + async のまま\n・consent-management.component.ts:72: isLoading = signal(false)(コード内で読む状態の入れ物)\n・subscription-product-price.component.ts:33-50: toSignal + computed × 3 → テンプレートで oneTimeCharges()\n・order-attachments-dialog.component.ts:42, 86-90: OnPush + signal + toSignal(initialValue: 0)\n・store-finder-list.component.ts:68, 79-81: viewChild signal + effect でフォーカス\n・http-error-handler.interceptor.ts:46: toSignal(userId)(サービス内で購読なしに最新値を読む)\n・NgRx の selectSignal は本体で 0 件", 1010, 666, 740, 130, *YEL, 10)
d17.box("カスタム実装で signal を選ぶとき(18.8): Facade(15 章)はそのまま。コンポーネントで toSignal(component.data$) → computed → toObservable → switchMap(facade.getHours) → toSignal。\n変わるのは購読の開始時刻だけ。/stores/{code}/hours が 1 本飛ぶ事実と応答の形は同じ。", 1010, 812, 740, 72, *BLUE, 10)

d18=D("18 Query の状態機械と Command の戦略")
d18.text("Facade の中身が Query / Command のとき、API はいつ飛び、いつ取り直され、いつ捨てられるのか。左: Query の 1 つの状態と遷移。中: Command の 4 strategy。右: EventService が結ぶ「書く → イベント → 取り直す」。19 章", 40, 20, 1740, 30, 16, "fontStyle=1;")
gL=d18.group("Query: BehaviorSubject 1 つ { loading, error, data } と 3 本の配線(query.service.ts:52-142)。橙 = API が飛ぶ遷移、灰 = 飛ばない", 40, 70, 640, 900, "#f5f5f5", "#666666")
q0=d18.box("初期状態 { loading: true, error: false, data: undefined }(:61-67)\nQuery を作っただけでは何も起きない(spec: should not load if not subscribed)", 70, 110, 580, 56, *GREY, 11)
q1=d18.box("1 人目が購読(using :131-134)→ onSubscribeLoad$ が「ロードせよ」(:71-75)\n→ loader 実行 → { loading: false, data }(:94-97)", 70, 186, 580, 56, *ORANGE, 11)
q2=d18.box("2 人目の購読 / 全員が去ったあとの再購読\n→ state$ の最新値が流れるだけ。loading: false なので onSubscribeLoad$ は EMPTY = 取得済みなら取らない", 70, 262, 580, 56, *GREY, 11)
q3=d18.box("ロード中に全員が購読解除 → load$ の購読解除で loader 中断。loading: true のまま残る(:69-70)\n→ 次の購読で onSubscribeLoad$ が再び発火して取り直す", 70, 338, 580, 56, *ORANGE, 11)
q4=d18.box("reloadOn のイベント(:106-114)→ { ...前の値, loading: true }: data は保持して裏で取り直す(ちらつかない)\n購読者がいなければ印だけ付け、次の購読で取る", 70, 414, 580, 56, *ORANGE, 11)
q5=d18.box("resetOn のイベント(:117-129)→ 即 initialState(data: undefined)。進行中の loader は takeUntil で中断(:86)\n購読者がいれば直ちに再ロード。loading を見ている画面はスピナーに戻る", 70, 490, 580, 56, *ORANGE, 11)
q6=d18.box("loader がエラー → { loading: false, error, data: undefined }(:98-101)\nload$ は sourceStream$ を返して生き続ける → 次のトリガーで再試行。成功で error は消える", 70, 566, 580, 56, *YEL, 11)
for a,b in [(q0,q1),(q1,q2),(q2,q3),(q3,q4),(q4,q5),(q5,q6)]: d18.edge(a,b)
d18.box("get() = state$ → data → distinctUntilChanged(:136-139)。getState() = { loading, error, data } そのもの。\nasync パイプが購読 → 値が来るたびに markForCheck → 印 → tick(16〜17 章)。state$ は NgRx ストアの外: DevTools に出ず、SSR の TransferState の対象でもない", 70, 646, 580, 70, *GREEN, 10)
d18.box("API が飛ぶ瞬間は 4 つだけ: 初回購読 / 中断後の再購読 / reloadOn / resetOn。\nパラメータは Query に無い → 前提条件ヘルパで take(1)(チケット 1 件)、呼ぶたびに create(チケット一覧)、loader 内で switchMap(見積一覧)の 3 通り", 70, 732, 580, 70, *RED, 10)
d18.text("根拠: query.service.ts:31-42, 52-142, 144-155 / query.service.spec.ts:56-364 / customer-ticketing.service.ts:191-227, 254-270 / quote.service.ts:446-447 / checkout-delivery-address.component.ts:351-352", 70, 816, 580, 60, 10)
gM=d18.group("Command(command.service.ts:50-135): execute() ごとに ReplaySubject を 1 つ返す", 720, 70, 480, 900, "#f5f5f5", "#666666")
m0=d18.box("execute(params): results$ に ReplaySubject、commands$ に params(:126-131)\nprocess$ は create 時に購読済み(:120)→ 戻り値を購読しなくても走る", 740, 110, 440, 60, *BLUE, 10)
m1=d18.box("Queue(既定): concatMap(:109-116)\n前が終わるまで待つ。全部実行\n例: プロフィール更新、チケット作成・返信", 740, 190, 440, 60, *GREEN, 10)
m2=d18.box("CancelPrevious: switchMap + finalize で complete(:75-93)\n前の購読を切る。前の fetch は abort。サーバーに届いていれば処理は進む\n例: 配送先設定、注文確定、カート検証、リアルタイム在庫", 740, 270, 440, 72, *ORANGE, 10)
m3=d18.box("ErrorPrevious: switchMap + 前の呼び出し元に Error('Canceled by next command')(:84-85)\n本体では未使用", 740, 362, 440, 56, *GREY, 10)
m4=d18.box("Parallel: mergeMap(:97-104)。全部同時\n本体では未使用", 740, 438, 440, 48, *GREY, 10)
m5=d18.box("エラー: tap(notify) が呼び出し元の ReplaySubject に error を転送(:62-68)\ncatchError(() => EMPTY) で process$ は生き続ける → 次の execute は普通に動く", 740, 506, 440, 60, *YEL, 10)
for a,b in [(m0,m1),(m1,m2),(m2,m3),(m3,m4),(m4,m5)]: d18.edge(a,b)
d18.box("Command は State に書かない。成功の tap でイベントを dispatch するだけ。\nState への反映は「更新 API の応答を merge」ではなく「Query がもう一度 GET」= 8.0 規則 2 の Query / Command 版", 740, 590, 440, 72, *RED, 10)
d18.box("strategy はクライアント側の順序だけを守る。冪等性はバックエンドの責任。\n注文確定の CancelPrevious は「2 回目が来たら 1 回目の応答を捨てる」。二重注文はサーバーでカートが消費されることで防がれる(place-order listener が OrderPlacedEvent でカートを捨てる)", 740, 676, 440, 90, *YEL, 10)
d18.text("根拠: command.service.ts:27-38, 50-135 / user-profile.service.ts:31-48 / checkout-delivery-address.service.ts:34-119 / order.service.ts:26-54 / cart-validation.service.ts:27-44 / product-availability.service.ts:33-42 / checkout-place-order-event.listener.ts:24-41 / 利用規模: Query 20、Command 65、CancelPrevious 24、Queue 8(明示)", 740, 780, 440, 110, 10)
gR=d18.group("EventService が結ぶ「書く → イベント → 読む側が取り直す」(event.service.ts:68-113, 144-159)", 1240, 70, 540, 900, "#fff7e6", "#d79b00")
d18.text("実例 1 プロフィール更新(直接配線、reload)", 1260, 104, 500, 24, 12, "fontStyle=1;")
r1=d18.box("フォーム送信 → UserProfileFacade.update(details)\n→ updateCommand.execute (Queue)", 1260, 134, 500, 48, *BLUE, 10)
r2=d18.box("takeUserId(true) → PATCH users/current\n成功の tap: dispatch(UserAccountChangedEvent)(user-profile.service.ts:36-41)", 1260, 196, 500, 48, *ORANGE, 10)
r3=d18.box("userQuery の reloadOn: [UserAccountChangedEvent](user-account.service.ts:32)\n→ loading: true(名前は古いまま)→ GET users/current → data 差し替え → async パイプ → 印 → tick", 1260, 258, 500, 56, *ORANGE, 10)
for a,b in [(r1,r2),(r2,r3)]: d18.edge(a,b)
d18.text("実例 2 配送先設定(リスナ経由、reset)", 1260, 334, 500, 24, 12, "fontStyle=1;")
s1=d18.box("住所カード選択 → setDeliveryAddress(address)\n→ setDeliveryAddressCommand.execute (CancelPrevious)", 1260, 364, 500, 48, *BLUE, 10)
s2=d18.box("checkoutPreconditions()(userId / cartId / ゲスト判定を take(1))→ PUT carts/{id}/addresses/delivery\n成功の tap: dispatch(CheckoutDeliveryAddressSetEvent)", 1260, 426, 500, 56, *ORANGE, 10)
s3=d18.box("リスナが翻訳(checkout-delivery-address-event.listener.ts:109-122)\n→ CheckoutSupportedDeliveryModesQueryResetEvent + CheckoutQueryResetEvent", 1260, 496, 500, 48, *YEL, 10)
s4=d18.box("checkoutQuery$ は 2 種類のイベントしか知らない(checkout-query.service.ts:32-54)\n→ initialState → 購読者がいるので即 GET carts/{id}?fields=deliveryAddress,deliveryMode,paymentInfo\n→ 各コンポーネントは loading でスピナー → data で描画", 1260, 558, 500, 64, *ORANGE, 10)
for a,b in [(s1,s2),(s2,s3),(s3,s4)]: d18.edge(a,b)
d18.box("イベントの供給源は 3 つ: ① Command の成功(tap で dispatch) ② NgRx のアクション(StateEventService: LoginEvent ← AuthActions.LOGIN、LanguageSetEvent ← SET_ACTIVE_LANGUAGE) ③ 任意の Observable(LogoutEvent ← isUserLoggedIn の true → false)\n→ NgRx の世界の出来事を Query が reloadOn / resetOn の 1 行で受けられる", 1260, 642, 500, 90, *GREEN, 10)
d18.box("バックエンドへの意味: 更新のあとは必ず GET が来る(PATCH の本文は画面に使われない)→ read-after-write 一貫性が前提。\n「いつ古くなるか」はイベントの一覧として依頼書に書く。書かれていなければフロントは初回購読の 1 回しか取りに来ない。", 1260, 746, 500, 80, *RED, 10)
d18.text("根拠: state-event.service.ts:36-55 / user-auth-event.builder.ts:40-63 / site-context-event.builder.ts:41-72 / checkout-query-event.listener.ts:38-62 / checkout.events.ts:12-31", 1260, 840, 500, 50, 10)

d19=D("19 zone モードと zoneless の経路の差")
d19.text("zone.js を外すと何が変わり、何が変わらないか。左: zone モードで tick が起きる 2 本の経路。中: zoneless に残る 1 本と Targeted。右: 差分と Spartacus 2612 の現状。20 章", 40, 20, 1740, 30, 16, "fontStyle=1;")
gL=d19.group("zone モード(Spartacus 本体): tick を起こす経路は 2 本、tick は常に Global", 40, 70, 640, 850, "#f5f5f5", "#666666")
a0=d19.box("印を付ける段階(16 章)は両モードで同じ: markViewDirty が 64|1024 を自分→根元(:5967-5978)、markAncestorsForTraversal が 8192、いずれも notify(source)(:18258)", 70, 110, 580, 48, *GREY, 10)
a1=d19.box("経路 A: zone.js が Angular zone のタスクを数える → マイクロタスクが 0 → NgZone.checkStable → onMicrotaskEmpty(17.3)\n印が付いていなくても発火する", 70, 178, 580, 56, *BLUE, 11)
a2=d19.box("NgZoneChangeDetectionScheduler: dirtyFlags |= 1; appRef._tick()(core.mjs:309-321)\nprovideZoneChangeDetection の ENVIRONMENT_INITIALIZER が initialize() を呼ぶ(core.mjs:363-373)", 70, 254, 580, 56, *ORANGE, 11)
b1=d19.box("経路 B(保険): notify(source) → shouldScheduleTick: Angular zone の中なら false(:18332)→ 経路 A に任せる\nzone の外(runOutsideAngular、外部ライブラリ)からの印だけ rAF / setTimeout(0) で予約(:18317-18323)", 70, 330, 580, 64, *GREY, 10)
b2=d19.box("tick(): zone モードでは dirtyFlags & 7(1|2|4)なら |= 1(:18345-18347)→ 経路 B の tick も Global", 70, 414, 580, 48, *GREY, 10)
c=d19.box("synchronizeOnce: useGlobalCheck && !zonelessEnabled → mode 0 Global(:12469)\nDefault(16 CheckAlways)の view は印が無くても評価(:5905)、OnPush は 64 でも評価(:5906)", 70, 482, 580, 56, *GREEN, 11)
d=d19.box("時刻: fetch 応答・Promise の続きはマイクロタスクが尽きた「その場」。クリックだけ eventCoalescing で次のフレーム(17.3 の表)", 70, 558, 580, 56, *YEL, 11)
for x,y in [(a0,a1),(a1,a2),(a2,b1),(b1,b2),(b2,c),(c,d)]: d19.edge(x,y)
d19.box("安定(isStable = PendingTasks が空 :12323-12325): ZoneStablePendingTask が zone のタスク数を PendingTasks に橋渡し(core.mjs:413-445)\n→ setTimeout / setInterval / 外部 SDK の Promise も SSR を待たせる。i18next の reloadInterval: false はその回避(i18next-http-backend.initializer.ts:66-68)", 70, 634, 580, 80, *RED, 10)
d19.text("根拠: core.mjs:299-325, 348-412, 413-445 / _debug_node-chunk.mjs:5900-5933, 12396-12401, 12460-12471, 18258-18360 / zone.js 0.16.3 bundles/zone.umd.min.js 約 39 KB / 17 章", 70, 734, 580, 60, 10)
gM=d19.group("zoneless(Angular 21 の既定): 残る経路は 1 本、tick は常に Targeted", 720, 70, 480, 850, "#f5f5f5", "#666666")
m1=d19.box("NgZone の実体は NoopNgZone(:2603-2623): run も runOutsideAngular もただ関数を呼ぶ\nonMicrotaskEmpty を発火する者がいない → 経路 A は存在しない", 740, 110, 440, 64, *BLUE, 11)
m2=d19.box("notify(source) → dirtyFlags(0 → 2 / 1〜5 → 4 / 12 → 16 / 13 → 2 / 他 → 8 :18262-18304)\nshouldScheduleTick の zone 判定は !zonelessEnabled で短絡 → 印の通知 = 予約", 740, 194, 440, 64, *ORANGE, 10)
m3=d19.box("予約 = requestAnimationFrame / setTimeout(0) の早い方(scheduleCallbackWithRafRace :2359-2384)= 次のフレーム\ntick 直後の続きだけ queueMicrotask(:18229-18257、連続 100 回でエラー 103 :18190)", 740, 278, 440, 72, *ORANGE, 10)
m4=d19.box("tick(): 1 を立てない。ApplicationRef.tick() も zoneless では立てない(:12397-12399)\n→ synchronizeOnce は mode 1 Targeted(:12469)。印の無い root view には入らない(:12466)", 740, 370, 440, 64, *GREEN, 10)
m5=d19.box("root に 1024 が届けば root の refreshView → 子は Global で辿る(:5816-5817)\n→ markForCheck / クリック / async パイプの印なら、評価範囲は zone モードと同じ", 740, 454, 440, 64, *GREEN, 10)
m6=d19.box("差が出るのは 2 つだけ:\n① 印がどこにも付かない → tick 自体が起きない(setTimeout / subscribe で普通のフィールドに代入、ngZone.run の中で印なし)\n② 8192 だけ(signal の set)→ 途中の Default の view は評価しない", 740, 538, 440, 84, *YEL, 10)
for x,y in [(m1,m2),(m2,m3),(m3,m4),(m4,m5),(m5,m6)]: d19.edge(x,y)
d19.box("安定: PendingTasks だけ。HttpClient の各リクエスト(_module-chunk.mjs:1456-1460, 1529-1531)、Router の遷移(_router-chunk.mjs:4667-4669)、PendingTasks.run(:2775-2797)、pendingUntilEvent\n→ タイマーは待たない。HttpClient を通らない非同期は待たれずに HTML が出る", 740, 642, 440, 90, *RED, 10)
d19.text("根拠: _effect-chunk2.mjs:2231-2260, 2359-2390, 2603-2623, 2767-2769, 2775-2797 / _debug_node-chunk.mjs:18205-18375, 18392-18414 / core.mjs:723, 2142 / @schematics/angular/application/schema.json:131-135", 740, 752, 440, 80, 10)
gR=d19.group("差分と Spartacus 2612 の現状", 1240, 70, 540, 850, "#fff7e6", "#d79b00")
d19.box("既定の決まり方: ZONELESS_ENABLED の工場は true(:2767-2769)。bootstrapApplication は provideZonelessChangeDetectionInternal() を provider の先頭に置く(core.mjs:2142)\nprovideZoneChangeDetection が ZONELESS_ENABLED: false と本物の NgZone で上書き(core.mjs:348-387)\n→ zone.js を読み込んでいても provider が無ければ zoneless で動く", 1260, 110, 500, 90, *GREY, 10)
d19.box("Spartacus の設定: app.config.ts:30 provideZoneChangeDetection({ eventCoalescing: true })、project.json:23 polyfills zone.js\nschematics は zoneless: false 固定(generate-default-workspace.ts:33)、docs は --zoneless=false(installation.md:24)\n移行 221121_7 に「provideZoneChangeDetection を app.module.ts へ移す」専用マイグレーション", 1260, 220, 500, 84, *BLUE, 10)
d19.box("集計(spec 除く): @Component 552 ファイル、OnPush 389(約 70%)、Default 約 160\nDefault で subscribe 64(購読直後に代入 26)、setTimeout 17(Default 4)、NgZone 注入 8、markForCheck 48、detectChanges 45", 1260, 324, 500, 64, *YEL, 10)
d19.box("zone に頼る 3 系統: ① Default + 購読内代入(cx-storefront の HostBinding、storefront.component.ts:86-87, 127-129, 194-196)\n② setTimeout で代入(base-message.component.ts:71 ほか)\n③ 外部 SDK を ngZone.run で包む(CDC gigya-raas.component.ts:98、SmartEdit :132、OPF global-functions 約 30 箇所)", 1260, 408, 500, 84, *ORANGE, 10)
d19.box("両モードで同じに動くもの: async パイプ(notify(4))、テンプレートのイベント、@Input、signal を読むテンプレート、ViewRef.detectChanges()(1024 + Global :6152-6155)、Query / Command と NgRx の値(async パイプ経由)", 1260, 512, 500, 64, *GREEN, 10)
d19.box("判断: 本体は zone モード前提で検証済み。顧客側で zoneless に切り替える構成はサポートの外\nカスタム実装は OnPush + async パイプ / signal で書き、購読内代入や外部コールバックは markForCheck か signal.set で終える。SSR で待たせたい非同期は HttpClient か PendingTasks.run\n→ zone モードでは「経路 A + 自分の印」、zoneless では「自分の印だけ」で評価され、結果が一致する", 1260, 596, 500, 100, *RED, 10)
d19.text("根拠: projects/storefrontapp/src/app/app.config.ts:30 / project.json:23 / core-libs/schematics/src/shared/utils/generate-default-workspace.ts:33 / migrations.json:93-96 / docs/migration/221121_7/migration.md:331-375 / core-libs/core/src/test.ts:28 / cx-api.service.ts:74 / opf-resource-loader.service.ts:237 / cx-common-engine.ts:20 / grep 集計は 20.7", 1260, 716, 500, 110, 10)
d20=D("20 状態管理の 2 つの作り方と変更検知の 2 つのモード")
d20.text("「signal か NgRx か」は状態の持ち方の問い、「zone か zoneless か」は描き直しの問い。左: Spartacus 本体の NgRx 経路。中: Angular 21 の signal 経路と 2 つを結ぶ橋。右: 2×2 の軸、本体の集計、カスタム実装での選び方。21 章", 40, 20, 1740, 30, 16, "fontStyle=1;")
gL=d20.group("NgRx + Observable(Spartacus 本体): 1 本の木、書き込みは Action、届け方は async パイプ", 40, 70, 640, 850, "#f5f5f5", "#666666")
n1=d20.box("OCC の JSON → Connector / Adapter(Normalizer が API の形を State の形に変える。5.2、15.2)", 70, 110, 580, 48, *BLUE, 11)
n2=d20.box("Effect: ofType(LOAD_PRODUCT) → bufferDebounceTime で同時の要求をまとめる → productConnector.getMany → LoadProductSuccess / Fail(product.effect.ts:34-57)\nwithdrawOn(contextChange$): 言語・通貨が変わったら途中の取得を捨てる(:55)", 70, 174, 580, 70, *ORANGE, 10)
n3=d20.box("Reducer: loaderReducer が { loading, error, success, value } を新しいオブジェクトで返す(loader.reducer.ts:39-60)\n商品詳細は entityScopedLoaderReducer<Product>(...) の 1 行(reducers/index.ts:31)= entities[code][scope] の辞書", 70, 260, 580, 70, *ORANGE, 10)
n4=d20.box("Store の木: StateWithProduct { product: { details, search, searchByCode, ... } }(product-state.ts:14, 22-33)。StoreModule.forFeature で枝を足す(product-store.module.ts:35)\nmeta reducer が ssrTransfer.keys の枝だけ TransferState に書く(state/reducers/index.ts:27-43、transfer-state.reducer.ts:18-35)", 70, 346, 580, 80, *GREY, 10)
n5=d20.box("Selector: createSelector の工場(code, scope)→ 引数の組ごとに memoized(product.selectors.ts:19-38)\npush 型: Store が変わるたびに走り、入力の参照が同じなら前の値(NgRx の仕様)", 70, 442, 580, 64, *PURP, 10)
n6=d20.box("Facade: store.pipe(select(...)) を Observable で返す(product.service.ts:55-59)\nProductLoadingService: shouldLoad$(!loading && !success && !error)のときだけ dispatch(product-loading.service.ts:102-132)= 取得済みなら取らない。using + shareReplay で購読者が何人でも 1 本(:139-142)", 70, 522, 580, 84, *GREEN, 10)
n7=d20.box("コンポーネント: Observable → async パイプ → markForCheck(16.3)。末端で toSignal に替えてもよい(21.6)", 70, 622, 580, 48, *BLUE, 11)
for x,y in [(n1,n2),(n2,n3),(n3,n4),(n4,n5),(n5,n6),(n6,n7)]: d20.edge(x,y)
d20.box("書き込みは dispatch(Action)だけ。Action の列がそのまま履歴(Redux DevTools、private.providers.ts:55、非 production)\n木が 1 本なので「全体のスナップショット」があり、SSR はそれを JSON にできる(cx-state)", 70, 690, 580, 64, *YEL, 10)
d20.text("根拠: core-libs/core/src/product/{facade,services,store}/ / state/utils/loader/loader.reducer.ts / state/reducers/index.ts / state/config/state-config.ts:24-35 / core/package.json:22-24(@ngrx 21.0.1)/ 5 章・15 章・19 章", 70, 770, 580, 60, 10)
gM=d20.group("Signal(Angular 21): 散らばった入れ物、書き込みは set、届け方は読み取り", 720, 70, 480, 850, "#f5f5f5", "#666666")
s1=d20.box("params = signal(...)(_effect-chunk2.mjs:2723-2736)。set / update で書く(_effect-chunk.mjs:365-379)。equal が同値と言えば何も起きない(:369)", 740, 110, 440, 60, *BLUE, 10)
s2=d20.box("resource / rxResource / httpResource(_resource-chunk.mjs:101-108、rxjs-interop.mjs:210-257、http.mjs:356-390)\neffect(loadEffect) が params を読む(:220, 286-320)。前回を AbortController で中断(:297-301)、pendingTasks.add() で SSR を待たせる(:298)", 740, 186, 440, 84, *ORANGE, 10)
s3=d20.box("loader / stream: HttpClient(または既存の Connector)を呼ぶ。rxResource は Observable を購読して最初の値を Promise にし、abort で unsubscribe", 740, 286, 440, 60, *ORANGE, 10)
s4=d20.box("state signal に { status, stream } を set(:315-320)。status / value / error / isLoading は computed(:117-119, 227-231)\n木は無い: resource を作った場所ごとに 1 つ。重複排除・まとめ取りは無し", 740, 362, 440, 72, *GREY, 10)
s5=d20.box("computed: 読まれたときに依存先の version を確かめて再計算(_effect-chunk.mjs:264-284)。pull 型。読まれなければ一度も計算しない(:288-293)", 740, 450, 440, 60, *PURP, 10)
s6=d20.box("テンプレートで value() と読む → その view の consumer が汚れる(18.3)。async パイプも markForCheck も不要", 740, 526, 440, 48, *BLUE, 11)
for x,y in [(s1,s2),(s2,s3),(s3,s4),(s4,s5),(s5,s6)]: d20.edge(x,y)
d20.box("2 つを結ぶ橋: toSignal(Observable → signal。呼んだ瞬間に subscribe、rxjs-interop.mjs:100-160)/ toObservable(signal → Observable。effect 経由なので set の直後には流れない :74-98)\n本体の signal 利用はすべてこの橋の先: listParams = signal → toObservable → switchMap(facade) → toSignal(subscription-list.component.ts:44-64)", 740, 594, 440, 110, *GREEN, 10)
d20.text("根拠: @angular/core 21.2.25 fesm2022/_effect-chunk.mjs:264-298, 340-379 / _effect-chunk2.mjs:2723-2736, 2884-2900 / _resource-chunk.mjs:68-108, 109-332 / rxjs-interop.mjs:74-160, 210-257 / @angular/common http.mjs:349-392", 740, 720, 440, 90, 10)
gR=d20.group("2 本の軸と Spartacus 2612 の現状", 1240, 70, 540, 850, "#fff7e6", "#d79b00")
d20.box("2×2(21.1): 縦 = 状態の持ち方、横 = 変更検知のモード\nNgRx + async × zone = Spartacus 本体 / NgRx + async × zoneless = 動く(notify(4))\nsignal × zone = 動く(zone の tick に乗る)/ signal × zoneless = Angular 21 新規アプリの既定\n→ 2 つの問いは独立。どちらの印も notify に入り、分岐は shouldScheduleTick(20 章)", 1260, 110, 500, 96, *GREY, 10)
d20.box("本体の NgRx: @ngrx/store 21.0.1(core/package.json:22-24)、StoreModule.forFeature 22、store ディレクトリ 23、createEffect 213、createSelector 264、Facade 79\nSSR 転送の既定は product / cms / site-context / site-theme の 4 枝。@ngrx/signals(SignalStore)は 0", 1260, 222, 500, 84, *BLUE, 10)
d20.box("本体の signal: 13 ファイル。signal( 17、computed( 13、toSignal( 6、effect( 3、toObservable( 1、model( 2\nresource / rxResource / httpResource / linkedSignal / input( は 0。すべて Facade の外側(コンポーネント・ディレクティブ 12 + インターセプタ 1)。Store・Effect・Selector・Facade の返り値に signal は無い", 1260, 322, 500, 84, *YEL, 10)
d20.box("差が出る所: 重複排除(Store 全体で 1 回 vs resource を作った場所ごと)/ まとめ取り(bufferDebounceTime vs 無し)/ SSR 転送(ssrTransfer vs httpResource の transfer cache のみ)/ 履歴(Action の列 vs 無し)/ 書き込みのコスト(新しい木 vs O(1))", 1260, 422, 500, 84, *ORANGE, 10)
d20.box("選び方(21.8): ① 本体が持つサーバー状態 → Facade + async か toSignal ② 自前のサーバー状態 → 15 章 Facade + 19 章 Query(NgRx の枝は DevTools・ssrTransfer・共有辞書が要るときだけ)③ 画面だけの状態 → signal ④ 画面をまたぐクライアント状態 → root サービスの signal\nFacade の返り値は Observable のまま。toSignal は末端で 1 回", 1260, 522, 500, 100, *GREEN, 10)
d20.box("バックエンドへの意味: API 契約は不変。resource を直接使うと同じ GET が複数回・途中で abort されたリクエストが増える。cx-state に載るのは NgRx の 4 枝だけ(Query・signal・resource は載らない)\n依頼書には機能ごとに状態の種類 ①〜④ を 1 行", 1260, 638, 500, 84, *RED, 10)
d20.text("根拠: core-libs/core/package.json:22-24 / product-store.module.ts:20-30 / cms-store.module.ts:25 / site-context-store.module.ts:24 / site-theme-store.module.ts:23 / private.providers.ts:55 / subscription-product-price.component.ts:33-51 / http-error-handler.interceptor.ts:46, 91 / docs/spa-bff-reference-implementation.md:1156-1177 / grep 集計は 21.7", 1260, 738, 500, 100, 10)
d21=D("21 カスタマイズの 7 段と 100 シナリオの分布")
d21.text("「〜を変えたい」はどの段で吸収できるか。左ほど安い。各段の件数は 100 シナリオ(22 章)を「いちばん浅く済む段」で数えたもの。段 0 と段 1 で 64 件", 40, 20, 1740, 30, 16, "fontStyle=1;")
tiers=[
 ("段 0  バックエンドのデータ・CMS だけ\n18 件", "フロントは変更なし\n#12 類似商品の見出し / #26 検索候補の件数 / #27 リストかグリッド / #36 クーポン / #51 マイアカウントのメニュー / #62 コンテンツページ / #68 404 / #71-72 言語・通貨", GREEN),
 ("段 1  フロントの設定値\n46 件", "provideConfig に 1 ブロック\n#21 一覧の件数 / #24 無限スクロール / #14・#25 fields / #20 maxAge / #41-44 チェックアウト / #61 商品 URL / #74 文言 / #81-83 レイアウト / #98 ssrTransfer", BLUE),
 ("段 2  見た目・アウトレット\n8 件", "SCSS・CSS 変数・provideOutlet\n#1 標準の見た目 / #28 カードへの差し込み / #38 カート行の置き換え / #78 ブランドカラー / #84-85 前後・置き換え / #90 スロットの CSS", YEL),
 ("段 3  コンポーネントの差し替え・追加\n15 件", "cmsComponents.<typeCode>.component\n#2 同じ typeCode で差し替え / #3 新 ItemType / #11 類似商品の件数 / #19 画像 / #31 ミニカート / #46 独自ステップ / #52 注文履歴の件数", ORANGE),
 ("段 4  変換\n3 件", "*_NORMALIZER / *_SERIALIZER\n#16 商品の独自項目 / #94 応答の変換 / #95 送信の変換", PURP),
 ("段 5  取得・ロジックの差し替え\n8 件", "Adapter / Facade / サービス / Interceptor\n#54 ログイン後の遷移 / #60 ユーザー固有 API / #65 meta / #92 別サーバー / #96 HTTP エラー / #100 Facade", GREY),
 ("BE  バックエンド実装が必要\n2 件", "フロントに設定が無い\n#22 並び順の選択肢 / #23 ファセットの表示数(Solr の設定)", RED),
]
prev=None
for i,(h,b,col) in enumerate(tiers):
    x=40+i*250
    t=d21.box(h, x, 80, 220, 60, *col, 12, "fontStyle=1;")
    d21.box(b, x, 160, 220, 150, *col, 10, "align=left;spacingLeft=6;verticalAlign=top;")
    if prev: d21.edge(prev,t)
    prev=t
d21.text("段の読み方: 「0 → 3」は段 0 で済むが、もっと変えたいなら段 3。バックエンドの欄に作業がある行は 53 件。ほとんどは CMS への配置・属性の公開・DTO への項目追加で、新しいエンドポイントが要るのは機能や取得先が新しいとき(#45・#59・#60・#92)だけ", 40, 325, 1720, 40, 12)
gP=d21.group("落とし穴: 設定がありそうで無いもの(22.12)", 40, 380, 1060, 420, "#fff2f2", "#b85450")
pit=[
 "maximumNumberProducts / displayProductTitles は定義だけで未使用(cms.model.ts:148-150)→ 類似商品の件数は段 3",
 "minPerFacet は定義だけ。移行ツールに「削除済み」(cms.model.ts:197)",
 "注文履歴の件数は private PAGE_SIZE = 5(order-history.component.ts:61)→ 差し替え",
 "guards は部品単位ではなく、ページのルートガードとして評価(cms-components.service.ts:253)",
 "参照タイプをカンマ区切りにすると Selector の完全一致で 0 件(product-references.selectors.ts:35)",
 "productSearch の fields から keywordRedirectUrl を消すと、検索語リダイレクトが黙って止まる",
 "数量の上限・ログイン後の遷移先には設定キーが無い(add-to-cart.component.ts:224、auth-redirect.service.ts:81)",
 "独自のチェックアウトステップは完了チェックを素通り(checkout-steps-set.guard.ts:106)",
 "a11yPrimaryColorContrast が有効だと --cx-color-primary が !important で上書き(root.scss:66-70)",
]
for i,t in enumerate(pit):
    d21.box(t, 60, 420+i*41, 1020, 34, *RED, 10, "align=left;spacingLeft=6;")
gU=d21.group("要件の会話での使い方(22.14)", 1140, 380, 620, 420, "#f5f5f5", "#666666")
use=[
 ("まず段を引く。「件数を変えたい」でも #11・#21・#39・#52 で段が違う", BLUE),
 ("段 0・段 1 はその場で試せる。CMS の属性を変える、provideConfig を 1 ブロック書く。動く画面を見せれば API の議論が要らない", GREEN),
 ("段 3 以上は「なぜ浅い段で済まないか」を 1 行書く。22.12 の根拠を添えると見積もりの理由になる", ORANGE),
 ("BE の欄は「新しい API」か「既存 API の中身(fields・DTO)」かを分けて依頼書に書く(11.8、12 章、14 章)", PURP),
]
for i,(t,col) in enumerate(use):
    d21.box(t, 1160, 420+i*90, 580, 76, *col, 11, "align=left;spacingLeft=6;")
d21.text("根拠: core/config/config-providers.ts:18, 55 / core/cms/config/cms-config.ts:61-130 / sf/cms-structure/outlet/outlet.model.ts:9-10 / core/product/connectors/product/converters.ts:11 / core/lazy-loading/facade-factory/facade-factory.ts:20 / 各行の根拠は 22 章の表(232 か所、全件照合済み)", 40, 810, 1720, 30, 10)
d22=D("22 カスタマイズの置き場所")
d22.text("書く中身より書く場所で失敗する。左: ng add が作る骨格。中: すぐ読まれる root の injector と、遅延ロードで作られる子の injector。右: 段ごとの置き場所。23 章", 40, 20, 1740, 30, 16, "fontStyle=1;")
gA=d22.group("アプリの骨格(ng add が作る)", 40, 70, 520, 770, "#f5f5f5", "#666666")
a1=d22.box("app.config.ts\nprovideHttpClient(withFetch(), withInterceptorsFromDi())\nprovideZoneChangeDetection / importProvidersFrom(AppModule)", 60, 110, 480, 66, *BLUE, 10)
a2=d22.box("app.module.ts\nStoreModule.forRoot / EffectsModule.forRoot / AppRoutingModule / SpartacusModule\n+ CustomModule(自作をここで読む)", 60, 196, 480, 66, *BLUE, 10)
a3=d22.box("spartacus/spartacus.module.ts\nBaseStorefrontModule + 機能モジュール + 設定モジュール", 60, 282, 480, 50, *BLUE, 10)
a4=d22.box("spartacus-configuration.module.ts\nアプリ全体の provideConfig(OCC・サイト・翻訳・レイアウト・features.level)", 60, 352, 230, 84, *GREEN, 10)
a5=d22.box("spartacus-features.module.ts\n使う機能の *FeatureModule を並べる", 310, 352, 230, 84, *GREEN, 10)
a6=d22.box("features/cart/cart-base-feature.module.ts(すぐ読む)\nCartBaseRootModule(設定・ルート・Facade の代理)\nfeatureModules: { cartBase: { module: () => import('./cart-base-wrapper.module') } }", 60, 456, 480, 80, *YEL, 10)
a7=d22.box("features/cart/cart-base-wrapper.module.ts(遅延ロード)\nimports: [CartBaseModule, ...拡張]\n← カートの Service / Facade / Normalizer の上書きはここ", 60, 556, 480, 80, *ORANGE, 10)
a8=d22.box("src/styles.scss(本体の SCSS を順番どおり)/ styles-config.scss(変数を先に)/ src/styles/cx-*.scss(部品ごとの上書き)", 60, 656, 480, 60, *PURP, 10)
for x,y in [(a1,a2),(a2,a3),(a3,a4),(a3,a5),(a5,a6)]: d22.edge(x,y)
d22.edge(a6,a7,"CMS に cartBase の部品が出たとき import()",dashed=True)
d22.text("根拠: core-libs/schematics/src/add-spartacus/__snapshots__/index_spec.ts.snap:24-108 / shared/utils/lib-utils.ts:320-326 / add-spartacus/index.ts:147-167 / projects/storefrontapp/src/app/spartacus/features/cart/cart-base-feature.module.ts:23-70, cart-base-wrapper.module.ts:22-25", 60, 730, 480, 80, 10)
gB=d22.group("2 層の injector: どこに provide すると効くか", 600, 70, 560, 770, "#f5f5f5", "#666666")
b1=d22.box("root の injector(起動時)\nprovideConfig のマージ先 / @spartacus/core・storefront のサービス(ProductService、ProductAdapter、PRODUCT_NORMALIZER)/ ActiveCartFacade の代理(facadeFactory)/ HTTP_INTERCEPTORS / HttpErrorHandler", 620, 110, 520, 110, *BLUE, 10)
b2=d22.box("子の injector(カートの部品が初めて出たとき)\nActiveCartFacade → ActiveCartService(facade-providers.ts:28-29)\nCART_NORMALIZER など、その機能の provider", 620, 300, 520, 90, *ORANGE, 10)
d22.edge(b1,b2,"代理が import() して本物を探す(facade-factory.ts:20)",dashed=True)
d22.box("✕ root に { provide: ActiveCartService, useClass: Mine }\n→ カートの中では子の provider が先に見つかる。黙って無視される", 620, 420, 250, 90, *RED, 10)
d22.box("○ wrapper に { provide: ActiveCartService, useClass: Mine }\n→ 子の injector の中で上書きされる", 890, 420, 250, 90, *GREEN, 10)
d22.box("✕ 遅延ロード側に routing / i18n / view の provideConfig\n→ 機能が読まれるまで値が無い", 620, 530, 250, 80, *RED, 10)
d22.box("○ cmsComponents や、その機能の Adapter だけが使う endpoints は wrapper でも可\n(迷ったら root。provideConfig は provideDefaultConfig に必ず勝つ)", 890, 530, 250, 80, *GREEN, 10)
d22.box("規則 1: アプリ全体で読む設定 → すぐ読まれる設定モジュール\n規則 2: 遅延ロードの機能のサービス → その機能の wrapper\n規則 3: core / storefront のサービス → root", 620, 630, 520, 80, *YEL, 11, "fontStyle=1;")
d22.text("根拠: fl/cart/base/core/facade/facade-providers.ts:28-29 / fl/cart/base/root/facade/active-cart.facade.ts:16, 46 / core/lazy-loading/facade-factory/facade-factory.ts:20 / core/config/config-providers.ts:18, 55 / core-libs/skills/skills/spartacus-developer/references/correct-injector.md, configuration.md, proxy-facade-pattern.md", 620, 730, 520, 80, 10)
gC=d22.group("段ごとの置き場所と書き方", 1200, 70, 560, 770, "#fff7e6", "#d79b00")
rows=[
 ("段 1 設定値: provideConfig({...})\n→ spartacus-configuration.module.ts か custom-config.module.ts(root)。配列は丸ごと書く。provideDefaultConfig は使わない", BLUE),
 ("段 2 見た目: src/styles/cx-*.scss(グローバル)。cx-* セレクタと --cx-* 変数を狙う。部品の styleUrls では子に届かない", PURP),
 ("段 2 アウトレット: provideOutlet({ id, position, component })(root)\n差し込んだ部品は ProductListItemContext.product$ / CartItemContext.item$ で文脈を受ける", PURP),
 ("段 3 差し替え: class Mine extends 本体の部品 + cmsComponents: { <typeCode>: { component: Mine } }\n写さず継承。private には触れないので、そこだけ自分で書く", ORANGE),
 ("段 4 変換: declare module で型を拡張 → Converter を実装 → { provide: *_NORMALIZER, useExisting, multi: true }\ncore の型は root、機能の型は wrapper", YEL),
 ("段 5 差し替え: { provide: 本体の Adapter / Service, useClass / useExisting: Mine }\ncore は root、カート等は wrapper。Facade は代理なので中の Service を替える", RED),
 ("確かめ方: ConfigurationService.unifiedConfig$ / OccEndpointsService.buildUrl / CmsService.getCurrentPage() / inject(CmsConfig).featureModules をログに出す", GREY),
]
for i,(t,col) in enumerate(rows):
    d22.box(t, 1220, 110+i*96, 520, 84, *col, 10, "align=left;spacingLeft=6;")
d23=D("23 バックエンドの 4 層とフロントの段")
d23.text("バックエンドの仕事は 4 層のどこまで降りるか。左: 層と置く拡張。中: CMS の属性が OCC でどんな形になるか(デモ実測)。右: フロントの段との対応とリリースの順番。24 章", 40, 20, 1740, 30, 16, "fontStyle=1;")
gL=d23.group("バックエンドの 4 層(拡張名は仮)", 40, 70, 560, 780, "#f5f5f5", "#666666")
l1=d23.box("中身: ImpEx / Backoffice(データ拡張)\n部品の作成・スロット配置([mode=append])・ContentPage・CMSUserGroupRestriction・商品参照・Solr・OAuth クライアント\nJava は書かない。22 章の段 0 はすべてここ", 60, 110, 520, 96, *GREEN, 10)
l2=d23.box("型: *-items.xml(mycore)\n既存型は autocreate=false generate=false で属性を足す\nCMS 部品は SimpleCMSComponent を継承。code = typeCode = cmsComponents のキー\n→ システム更新", 60, 226, 520, 96, *BLUE, 10)
l3=d23.box("変換: *-beans.xml(Data / WsDTO)+ Populator + modifyPopulatorList(myfacades / myocc)\nData と WsDTO の項目名を揃えると DataMapper が対応づける\nWsDTO の項目名 = フロントの fields に書く名前", 60, 342, 520, 96, *ORANGE, 10)
l4=d23.box("窓口: Controller(myocc、/occ/v2 に載る)\n@Controller + @RequestMapping(\"/{baseSiteId}/users/{userId}/...\")\n@Secured / @ApiBaseSiteIdAndUserIdParam / DataMapper.map(data, WsDTO, fields)\nfieldSetLevelMapping で BASIC / DEFAULT / FULL", 60, 458, 520, 110, *RED, 10)
for x,y in [(l2,l1),(l2,l3),(l3,l4)]: d23.edge(x,y)
d23.box("設定: local.properties / manifest\ncorsfilter.commercewebservices.allowedHeaders ⊇ フロントが送るヘッダー(X-Anonymous-Consents、Occ-Personalization-*、独自ヘッダー)\nOAuth: フロント既定 client_id = mobile_android_public / docs の例は mobile_android + secret → 揃える", 60, 588, 520, 100, *YEL, 10)
d23.text("根拠: SAP 公式サンプル opf(7cd4c67)beans.xml:801-803・spring.xml:348-351 / cxai-extn(311e1f0)CxaioccController.java:29-53・cxaiocc-web-spring.xml:14-26・extensioninfo.xml:13 / cxai-assist(c52062c)items.xml:13-20, 18-32 / cx-translate(dec6529)admin-component.impex:10-16 / Spartacus docs cors.md・installing 2205", 60, 700, 520, 120, 10)
gM=d23.group("CMS の属性は OCC でどう出るか(デモ実測 2026-10-30)", 640, 70, 520, 780, "#f5f5f5", "#666666")
shapes=[
 ("数値・真偽値 → 文字列\nmaximumNumberProducts: \"5\" / displayProductPrices: \"true\"", BLUE),
 ("列挙 → code の文字列\ntotalDisplay: \"SUBTOTAL\" / context: \"LANGUAGE\"", BLUE),
 ("ローカライズ文字列 → 要求した言語の文字列\ntitle: \"You may also like...\"", BLUE),
 ("メディア → オブジェクト / レスポンシブ → フォーマット名がキー\nmedia: { tablet, desktop, mobile, widescreen }", GREEN),
 ("参照 → ネストしたオブジェクト\nnavigationNode / lightboxBannerComponent", GREEN),
 ("部品のコレクション → uid を空白区切り\ncomponents: \"ProductDetailsTabComponent ProductSpecsTabComponent ...\"", ORANGE),
 ("商品のコレクション → 属性名が変わる\nproducts → productCodes: \"300938 358639 ...\"(フロントは split(' '))", ORANGE),
]
for i,(t,col) in enumerate(shapes):
    d23.box(t, 660, 110+i*74, 480, 62, *col, 10, "align=left;spacingLeft=6;")
d23.box("言えないこと: 独自の型の属性が追加実装なしで同じ形で出るか(公開資料で未確認)。コレクションは型ごとの変換があると考える\n→ 型を足したら最初に cms/components?componentIds=<uid> を叩いて形を確かめ、依頼書に書く", 660, 636, 480, 90, *RED, 10)
d23.text("根拠: デモ OCC cms/pages(ProductPage 1934793、homepage)/ core/occ/adapters/cms/converters/occ-cms-page-normalizer.ts:166 / sf/.../product-carousel.component.ts:74 / core/occ/occ-models/occ.models.ts:282, 287", 660, 740, 480, 70, 10)
gR=d23.group("フロントの段との対応とリリースの順番", 1200, 70, 560, 780, "#fff7e6", "#d79b00")
rows=[
 ("段 0(CMS の値・配置・ナビ・ページ・言語・通貨)→ 中身だけ", GREEN),
 ("段 3 新しい CMS 部品 → 型 + 中身(+ 24.5 の確認)", BLUE),
 ("段 1 + 4 商品・カート・注文に項目 → 型 + 変換", ORANGE),
 ("段 5 新しいリソース → 型 + 変換 + 窓口", RED),
 ("並び順・ファセット・検索語リダイレクト → Solr の ImpEx + 再インデックス", PURP),
 ("OAuth・CORS・独自ヘッダー → 設定", YEL),
]
for i,(t,col) in enumerate(rows):
    d23.box(t, 1220, 110+i*58, 520, 48, *col, 11, "align=left;spacingLeft=6;")
r1=d23.box("① バックエンドを出す(型・変換・窓口)。ImpEx は Staged → 同期 → Online", 1220, 470, 520, 50, *GREY, 11)
r2=d23.box("② curl で確かめる: cms/components / users/anonymous/cms/pages / products/{code}?fields=code,<項目>", 1220, 540, 520, 50, *GREY, 11)
r3=d23.box("③ フロント: fields に項目を足す、cmsComponents を登録、エンドポイントを足す", 1220, 610, 520, 50, *GREY, 11)
d23.edge(r1,r2); d23.edge(r2,r3)
d23.box("順番を逆にすると: fields に WsDTO に無い項目 → HTTP 400 Incorrect field(デモ実測)→ 商品の画面ごと出ない", 1220, 680, 520, 60, *RED, 11)
d23.text("根拠: デモ products/1934793?fields=code,noSuchField → 400 / core/occ/adapters/product/default-occ-product-config.ts:14-26 / core/occ/utils/occ-user-ids.ts:7-9", 1220, 760, 520, 60, 10)
d24=D("24 ビュー層の Java の行き先と責務の分け方")
d24.text("JSP やタグの裏で動いていた Java は、ヘッドレスでは呼ばれない。左: アクセラレータの 1 つの Web アプリ。中: ヘッドレスで残る通り道と、各処理の行き先。右: フロントとバックを決める 6 つの問い。25 章", 40, 20, 1740, 30, 16, "fontStyle=1;")
gA=d24.group("アクセラレータ(JSP): 1 つの Web アプリで完結", 40, 70, 520, 720, "#f5f5f5", "#666666")
a1=d24.box("ページコントローラ(addon / storefront の web/src)\n@RequireHardLogIn・@PreValidateCheckoutStep\nmodel.addAttribute(\"opfPaymentMethods\", facade...)  ← 緑の Facade を呼ぶ", 60, 110, 480, 80, *RED, 10)
a2=d24.box("BeforeViewHandler / Validator(web/src)\nビュー名の差し替え、metaRobots、パンくず、入力チェック", 60, 210, 480, 60, *RED, 10)
a3=d24.box("JSP / タグ / EL 関数\n${x.displayName}・spring:theme・fn:escapeXml\nycommerce:sanitizeHTML・<script> の直書き", 60, 290, 480, 80, *RED, 10)
a4=d24.box("Facade / Service(core・facades 拡張)\nOPFAcceleratorFacade.getActiveConfigurations()", 60, 470, 480, 60, *GREEN, 10)
a5=d24.box("HTML", 60, 400, 480, 40, *GREY, 11)
d24.edge(a1,a2); d24.edge(a2,a3); d24.edge(a3,a5)
d24.box("赤 = storefront の Web 拡張の中。ヘッドレスでは /occ/v2 の通り道に無いので一度も実行されない\n緑 = OCC の Controller からも呼べる", 60, 550, 480, 70, *YEL, 10)
d24.text("根拠: opf(7cd4c67)opfacceleratoraddon/extensioninfo.xml:16-19 / opfacceleratorcore/extensioninfo.xml:13-16 / OPFPaymentCheckoutStepController.java:76-99 / OPFAcceleratorAddonBeforeViewHandler.java:33-38 / opfPaymentMethodSelector.tag:2-89 / DefaultOPFAcceleratorFacade.java:157-162", 60, 640, 480, 100, 10)
gB=d24.group("ヘッドレス: 残る通り道と、各処理の行き先", 600, 70, 560, 720, "#f5f5f5", "#666666")
b1=d24.box("ブラウザ: Angular(Spartacus)\nURL(cxUrl)・文言(cxTranslate)・画像 URL・レイアウト・画面の状態\n写し: AuthGuard・CustomFormValidators・数量の上限", 620, 110, 520, 90, *BLUE, 10)
b2=d24.box("/occ/v2(commercewebservices + 自社の occ 拡張)\n本物: @Secured・入力の検証(400)・cart validate\nfields で選んだ WsDTO の項目", 620, 250, 520, 90, *ORANGE, 10)
b3=d24.box("Facade / Service(JSP 時代のものを使い回す)\n価格の formattedValue・合計・割引・在庫・検索", 620, 390, 520, 70, *GREEN, 10)
b4=d24.box("外部サービス(例: OPF)\nブラウザから OCC を経ずに、公開鍵で直接呼ぶ。カートのアクセスコードは OCC が発行", 620, 500, 520, 70, *PURP, 10)
d24.edge(b1,b2,"JSON"); d24.edge(b2,b3); d24.box("移行の第一原則: web/src に直接書いたロジックは、先に Facade へ下ろす(アクセラレータが動いたままできる)", 620, 600, 520, 60, *YEL, 11, "fontStyle=1;")
d24.text("根拠: integration-libs/opf/base/opf-api/adapters/opf-api-base.adapter.ts:65-79, 91-116 / opf-checkout-payments.component.html:1-3, 26, 60-64 / fl/cart/base/occ/config/default-occ-cart-config-factory.ts:31-32 / core/model/product.model.ts:70 / core/auth/user-auth/guards/auth.guard.ts:30-42 / sf/cms-components/content/paragraph/paragraph.component.ts:49-51", 620, 680, 520, 100, 10)
gC=d24.group("どちらに置くか: 上から順に当てる", 1200, 70, 560, 720, "#fff7e6", "#d79b00")
qs=[
 ("Q1 ブラウザで書き換えられたら困るか(価格・割引・在庫・権限)→ バック", RED),
 ("Q2 フロントに無いデータ・大きなデータが要るか(検索・並び順・ファセット)→ バック", RED),
 ("Q3 業務担当がデプロイなしで変えたいか(文章・配置・robots・表示条件)→ バック(CMS)", ORANGE),
 ("Q4 アプリや他システムでも同じ答えが要るか → バック(Facade)", ORANGE),
 ("Q5 見た目・言い回し・URL の形・画面の組み立てか → フロント", BLUE),
 ("Q6 画面の一時的な状態か(開閉・選択中・入力途中)→ フロント", BLUE),
]
prev=None
for i,(t,col) in enumerate(qs):
    q=d24.box(t, 1220, 110+i*80, 520, 60, *col, 11, "align=left;spacingLeft=6;")
    if prev: d24.edge(prev,q,"いいえ")
    prev=q
d24.box("両方に置くもの: ログイン要求・入力チェック・数量の上限・外部サービスの証明\n正はバック、フロントは写し(規則は依頼書でもらう)", 1220, 600, 520, 70, *GREEN, 11)
d24.box("✕ バックが「残り 3 点」や HTML 断片を返す / フロントが合計を計算し直す / フロントだけで権限を確かめる", 1220, 690, 520, 60, *RED, 10)
out='<mxfile host="app.diagrams.net" modified="2026-10-23T00:00:00.000Z" agent="gen_drawio.py" version="24.0.0" type="device">'+d1.xml()+d2.xml()+d3.xml()+d4.xml()+d5.xml()+d6.xml()+d7.xml()+d8.xml()+d9.xml()+d10.xml()+d11.xml()+d12.xml()+d13.xml()+d14.xml()+d15.xml()+d16.xml()+d17.xml()+d18.xml()+d19.xml()+d20.xml()+d21.xml()+d22.xml()+d23.xml()+d24.xml()+'</mxfile>'
import os,sys; out_path=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(__file__),'..','docs','diagrams','spartacus-architecture.drawio'); open(out_path,'w').write(out)
print("ok", len(out))
