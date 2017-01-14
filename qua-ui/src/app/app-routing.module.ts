import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { SearchResultComponent } from './search-result/search-result.component';
import { SearchQuestionComponent } from './search-question/search-question.component';
import { SearchAddComponent } from './search-add/search-add.component';
import { AuthComponent } from './auth/auth.component';
import { SearchCategoryComponent } from './search-category/search-category.component';

import { AuthService } from './auth.service';

const routes: Routes = [
  {
    path: '',
    redirectTo: '/search',
    pathMatch: 'full'
  },
  {
    path: 'search',
    component:
    SearchResultComponent,
    canActivate: [AuthService]
  },
  {
    path: 'questions/:id',
    component: SearchQuestionComponent,
    canActivate: [AuthService]
  },
  {
    path: 'category',
    component: SearchCategoryComponent,
    canActivate: [AuthService]
  },
  {
    path: 'add',
    component: SearchAddComponent,
    canActivate: [AuthService]
  },
  {
    path: 'auth',
    component: AuthComponent
  }
];
@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
