import 'rxjs/add/operator/switchMap';
import { Component, OnInit, OnDestroy, ViewChild  } from '@angular/core';
import { ActivatedRoute, Params, Router, NavigationExtras } from '@angular/router';

import { MarkdownComponent } from '../markdown/markdown.component';

import { QuestionService } from '../question.service';
import { CategoryService } from '../category.service';

import { IQuestion, INewQuestion, ICategories, IAnswer } from '../question.interface';
import { ICategory } from '../category.interface';

@Component({
  selector: 'app-search-add',
  templateUrl: './search-add.component.html',
  styleUrls: ['./search-add.component.less']
})
export class SearchAddComponent implements OnInit, OnDestroy {
  @ViewChild(MarkdownComponent) private mde: MarkdownComponent;

  question: IQuestion | INewQuestion;
  allCategories: ICategories[];
  isReply: boolean = false;
  sfHide: boolean = true;
  title: string = '';
  keywords: string[] = [];
  keyword: string;
  categories: ICategories[] = [];
  answer: any = {
    raw: ''
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private questionService: QuestionService,
    private categoryService: CategoryService
  ) {  }

  onSubmit(): void {
    this.answer = { raw: this.mde.getValue() };
    if (this.isReply) {
      this.edit(this.question['id']);
    } else {
      this.add();
    }
  }

  edit(id: number) {
    let data: INewQuestion = {
      title: this.title,
      categories: this.categories,
      keywords: this.keywords
    };
    if (this.answer.raw) {
      data.answer = this.answer;
    }
    this.questionService.editQuestion(id, data)
      .then((que: IQuestion) => {
        this.router.navigate([`questions/${que.id}`]);
      });
  }

  add() {
    let data: INewQuestion = {
      title: this.title,
      categories: this.categories,
      keywords: this.keywords,
    };
    if (this.answer.raw) {
      data.answer = this.answer;
    }
    this.questionService.addQuestion(data)
      .then((que: IQuestion) => {
        this.router.navigate([`questions/${que.id}`]);
      });
  }

  getCategories() {
    this.categoryService.getCategories()
      .then((categories: ICategory[]) => {
        this.allCategories = categories;
      });
  }

  addCategory(index: number) {
    this.categories.push({
      id: this.allCategories[index].id,
      name: this.allCategories[index].name
    });
  }

  delCategory(index: number) {
    this.categories.splice(index, 1);
  }

  addKeyword() {
    console.log(this.keyword);
    if (this.keyword) {
      this.keywords.push(this.keyword);
    }
  }

  delKeyword(index: number) {
    this.keywords.splice(index, 1);
  }

  ngOnInit() {
    let question = this.questionService.question;
    if (question && !question['new']) {
      this.title = question.title || this.title;
      this.keywords = question.keywords.slice() || this.keywords;
      this.categories = question.categories.slice() || this.categories;
      this.answer = question.answer ? Object.assign(question.answer) : this.answer;
      this.isReply = question.reply;
      this.question = question;
    } else if (question) {
      this.title = question.title || this.title;
    }
    this.getCategories();
  }

  ngOnDestroy() {
    this.questionService.question = null;
  }
}