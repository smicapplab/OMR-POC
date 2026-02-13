import { students, currentSchools, previousSchools, studentAnswers } from '../../../drizzle/schema';

export interface AnswerSheetDetailResponse {
    omrScan: {
        id: number;
        fileName: string;
        filePath: string;
        fileUrl: string;
        status: string;
        confidence: number | null;
        reviewRequired: boolean;
        createdAt: Date;
    };
    student: typeof students.$inferSelect | null;
    currentSchool: typeof currentSchools.$inferSelect | null;
    previousSchool: typeof previousSchools.$inferSelect | null;
    answers: Record<
        string,
        {
            score: number;
            answers: (typeof studentAnswers.$inferSelect)[];
        }
    >;
}