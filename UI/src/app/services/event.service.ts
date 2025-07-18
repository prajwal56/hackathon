import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})


export class EventService {
  private baseUrl = 'http://10.0.4.203:9090/event'; // Match your Django viewset route

  constructor(private http: HttpClient) { }

  getEvent_list(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/event_list/`);
  }

  get_event_rca(data:any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/get_event_rca/`, data);
  }

  executeCustomCommands(data: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/execute_custom_commands/`, data);
  }

  get_event_rca_list(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/get_event_chart/`,{});
  }

  get_rule_donut_chart(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/get_rule_donut_chart/`,{});
  }
  generateEvent(payload: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/generate_event/`, payload);
  }
  markResolved(eventId: {}): Observable<any> {
    return this.http.post(`${this.baseUrl}/mark_resolved/`, { event_id: eventId });
  }
  clearAIMemory(): Observable<any> {
    return this.http.post(`${this.baseUrl}/clear_ai_memory/`, {});
  }
}

