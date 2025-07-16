import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class RuleService {
  private baseUrl = 'http://localhost:8000/api/rules'; // Match your Django viewset route

  constructor(private http: HttpClient) { }

  /**
   * GET /api/rules/list/
   * List all rules
   */
  getRules(page: number = 1, limit: number = 10): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/list/?page=${page}&limit=${limit}`);
  }

  /**
   * GET /api/rules/get/:id/
   * Retrieve a rule by ID
   */
  getRule(id: string): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/edit/${id}/`);
  }

  /**
   * POST /api/rules/create/
   * Create a new rule
   */
  createRule(data: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/create/`, data);
  }

  /**
   * PUT /api/rules/update/:id/
   * Update an existing rule
   */
  updateRule(id: string, data: any): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/update/${id}/`, data);
  }

  /**
   * DELETE /api/rules/delete/:id/
   * Delete a rule by ID
   */
  deleteRule(id: string): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}/delete/${id}/`);
  }

  getOptions(data:any={}): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/options/`,data);
  }

  getResource_list(data:any={}): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/resource_list/`,data);
  }
}
