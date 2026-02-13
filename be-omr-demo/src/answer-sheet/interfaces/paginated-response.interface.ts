import { AnswerSheetListItem } from "./answer-sheet-list-item.interface";

export interface PaginatedAnswerSheetResponse {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  data: AnswerSheetListItem[];
}