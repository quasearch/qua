import { Subject } from 'rxjs/Subject';
import { Injectable } from '@angular/core';
import { Headers, Http, RequestOptions } from '@angular/http';
import { CanActivate, Router } from '@angular/router';

import { ErrorService } from '../services/error.service';

import { IResponse } from '../interfaces/response.interface';

import { URLS } from '../../environments/const';

@Injectable()
export class AuthService implements CanActivate {
  private isAuthSource = new Subject<boolean>();
  private headers: Headers;
  private options: RequestOptions;

  isAuth$ = this.isAuthSource.asObservable();

  isAuth: boolean;
  token: string;

  constructor(
    private http: Http,
    private router: Router,
    private errorService: ErrorService) {
      this.headers = new Headers({
        'Content-type': 'application/json'
      });
      this.options = new RequestOptions({
        headers: this.headers
      });
    }

  canActivate() {
    this.isAuth = this.checkAuth();
    if (!this.isAuth) {
      this.router.navigate(['auth']);
      return false;
    }
    return true;
  }

  auth(username: string, password: string): Promise<any> {
    let data: any  = {
      username,
      password
    };

    return this.http.post(URLS.auth, JSON.stringify(data), this.options)
      .toPromise()
      .then((response: any) => {
        return response.json() as IResponse;
      })
      .then((response: IResponse) => {
        if (!response.ok) {
          throw response.error;
        }
        this.token = response.response.token;
        this.isAuth = true;
        localStorage.setItem('token', response.response.token);
        return true;
      })
      .catch(this.handleError);
  }

  logout(): void {
    localStorage.removeItem('token');
    this.router.navigate(['/auth']);
  }

  checkAuth(): boolean {
    let token: string = localStorage.getItem('token');
    let isAuth: boolean = Boolean(token);
    this.isAuthSource.next(isAuth);
    return isAuth;
  }

  private handleError = (error) => {
    return this.errorService.handleError(error);
  }
}