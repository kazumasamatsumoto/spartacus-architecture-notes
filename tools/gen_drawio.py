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
h_b3=d5.box("B-3 新しい資源 API(8 章)\nユーザー固有 / 大きい / 他画面でも使う / 高頻度更新", 1110, 390, 530, 60, *ORANGE)
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
c1=d6.box("ライブラリ側  provideDefaultConfig(<CmsConfig>{ cmsComponents: { CMSParagraphComponent: {...} } })\n→ DefaultConfigChunk (InjectionToken, multi: true)   config-providers.ts:55-61", 890, 110, 700, 60, *YEL)
c2=d6.box("アプリ側  provideConfig({ cmsComponents: { MyPromoBannerComponent: {...} }, layoutSlots: {...} })\n→ ConfigChunk (InjectionToken, multi: true)   config-providers.ts:18-27", 890, 200, 700, 60, *GREEN)
c3=d6.box("遅延モジュール内の provideDefaultConfig / provideConfig\n→ ambientDefaultConfig / ambientConfig   configuration.service.ts:92-105", 890, 290, 700, 50, *GREY)
c4=d6.box("Config = deepMerge({}, DefaultConfig, ambientDefault, ambient, RootConfig)\nオブジェクトは再帰マージ・後勝ち、配列は丸ごと置換   config-tokens.ts:10-62 / deep-merge.ts:31-48", 890, 390, 700, 70, *ORANGE)
c5=d6.box("CmsConfig / LayoutConfig / OccConfig / RoutingConfig / StateConfig\n@Injectable({ providedIn: 'root', useExisting: Config })  = 同じ合成済み設定を型付きで覗く窓", 890, 500, 700, 60, *PURP)
c6=d6.box("利用側\nCmsComponentsService.getMapping(flexType) → cmsComponents[flexType]\nPageLayoutService → layoutSlots[template]\nOccEndpointsService.buildUrl → backend.occ.endpoints / baseUrl / prefix", 890, 600, 700, 90, *BLUE)
d6.edge(c1,c4,"",exit=(0.5,1),entry=(0.3,0)); d6.edge(c2,c4,"",exit=(0.5,1),entry=(0.5,0)); d6.edge(c3,c4,"",exit=(0.5,1),entry=(0.7,0)); d6.edge(c4,c5); d6.edge(c5,c6)
d6.text("結果: アプリの provideConfig は、ライブラリ既定の同じキーだけを置き換える(他のキーは既定のまま)。typeCode のマッピング追加・上書き、スロット追加、エンドポイント追加はすべてこの 1 つの仕組みで行う。", 890, 720, 700, 60, 12)

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

out='<mxfile host="app.diagrams.net" modified="2026-10-23T00:00:00.000Z" agent="gen_drawio.py" version="24.0.0" type="device">'+d1.xml()+d2.xml()+d3.xml()+d4.xml()+d5.xml()+d6.xml()+d7.xml()+'</mxfile>'
import os,sys; out_path=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(__file__),'..','docs','diagrams','spartacus-architecture.drawio'); open(out_path,'w').write(out)
print("ok", len(out))
