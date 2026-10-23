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

out='<mxfile host="app.diagrams.net" modified="2026-10-23T00:00:00.000Z" agent="gen_drawio.py" version="24.0.0" type="device">'+d1.xml()+d2.xml()+d3.xml()+d4.xml()+d5.xml()+'</mxfile>'
import os,sys; out_path=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(__file__),'..','docs','diagrams','spartacus-architecture.drawio'); open(out_path,'w').write(out)
print("ok", len(out))
