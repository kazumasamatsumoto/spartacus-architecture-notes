// H7 Angular の標準: HTTP_INTERCEPTORS で、すべての HTTP の前後に処理を挟む
// (デモの OCC は CORS で content-type 以外のヘッダーを許していないので、ヘッダーは足さない)
import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, finalize } from 'rxjs';

@Injectable()
export class SampleTimingInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const start = performance.now();
    return next.handle(req).pipe(
      finalize(() => {
        const path = req.url.replace(/^https?:\/\/[^/]+/, '').split('?')[0];
        console.log(`[H7 interceptor] ${req.method} ${path} ${Math.round(performance.now() - start)}ms`);
      })
    );
  }
}
