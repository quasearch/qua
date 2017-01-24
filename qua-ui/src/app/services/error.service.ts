import { Subject } from 'rxjs/Subject';
import { Injectable } from '@angular/core';

import { IError } from '../interfaces/error.interface';
import { IResponse } from '../interfaces/response.interface';

@Injectable()
export class ErrorService {
  private error = new Subject<IError>();

  error$ = this.error.asObservable();

  constructor() { }

  viewError(err: IError) {
    console.dir(err);
    console.error(err);
    this.error.next(err);
  }

  handleError(response: any) {
    let error;
    if (response.status !== 500) {
      let res = response.json() as IResponse;
      if (!res.ok) {
        error = res.error;
      }
    } else {
      error = new Error('Extenral error');
      error.response = response;
    }
    return Promise.reject(error);
  }
}
