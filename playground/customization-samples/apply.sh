#!/usr/bin/env bash
# SAP/spartacus のクローンの projects/storefrontapp にサンプルを組み込む。
# usage: apply.sh <spartacus のクローン>
set -euo pipefail
SRC=$(cd "$(dirname "$0")" && pwd)/samples
APP=$1/projects/storefrontapp/src
rm -rf "$APP/app/samples"; cp -R "$SRC" "$APP/app/samples"
grep -q SamplesModule "$APP/app/app.module.ts" || {
  sed -i.bak "s#^import { SpartacusModule } from './spartacus/spartacus.module';#&\nimport { SamplesModule } from './samples/samples.module';#" "$APP/app/app.module.ts"
  sed -i.bak "s#^    SpartacusModule,#&\n    SamplesModule,#" "$APP/app/app.module.ts"
  # デモアプリは AppModule 自身の providers(privateProviders)で product の paths を決めている。
  # モジュール自身の providers は imports のモジュールより後に並ぶので、SamplesModule の設定は負ける。
  # H2 の設定だけは AppModule の providers の最後にも足す
  sed -i.bak "s#^import { SamplesModule } from './samples/samples.module';#&\nimport { sampleConfigProviders } from './samples/h2-config.providers';#" "$APP/app/app.module.ts"
  sed -i.bak "s#providers: \[privateProviders\]#providers: [privateProviders, sampleConfigProviders]#" "$APP/app/app.module.ts"
  rm "$APP/app/app.module.ts.bak"
}
grep -q h3-theme "$APP/styles.scss" || printf "\n@import 'app/samples/h3-theme';\n" >> "$APP/styles.scss"
echo "applied. 起動: cd $1 && CX_BASE_URL=<OCC の URL> npm start"
