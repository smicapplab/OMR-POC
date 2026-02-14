export interface AnswerSheetListItem {
    scanId: number;
    firstName: string | null;
    lastName: string | null;
    schoolId: string | null;
    createdAt: Date;
    studentsReviewRequired: boolean;
    currentSchoolsReviewRequired: boolean;
    previousSchoolsReviewRequired: boolean;
}