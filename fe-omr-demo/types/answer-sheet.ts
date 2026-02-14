export interface OmrScan {
    id: number;
    fileName: string | null;
    filePath: string | null;
    fileUrl: string | null;
    status: string;
    confidence: number | null;
    reviewRequired: boolean;
    createdAt: string;
}

export interface StudentAnswer {
    id: number;
    scanId: number;
    subject: string;
    questionNumber: number;
    answer: string | null;
    confidence: number | null;
    reviewRequired: boolean;
    isCorrect: boolean;
    createdAt: string;
}

export interface Student {
    id: number;
    scanId: number;
    lastName: string | null;
    firstName: string | null;
    middleInitial: string | null;
    birthMonth: string | null;
    birthDay: string | null;
    birthYear: string | null;
    ssc: string | null;
    fourPs: string | null;
    gender: string | null;
    lrn: string | null;
    specialClasses: string | null;
    reviewRequired: boolean;
    createdAt: string;
}

export interface CurrentSchool {
    id: number;
    scanId: number;
    region: string | null;
    division: string | null;
    schoolId: string | null;
    schoolType: string | null;
    reviewRequired: boolean;
    createdAt: string;
}

export interface PreviousSchool {
    id: number;
    scanId: number;
    schoolId: string | null;
    mathGrade: string | null;
    englishGrade: string | null;
    scienceGrade: string | null;
    filipinoGrade: string | null;
    apGrade: string | null;
    classSize: string | null;
    schoolYear: string | null;
    reviewRequired: boolean;
    createdAt: string;
}

export interface AnswerSheetDetailResponse {
    omrScan: OmrScan;
    student: Student | null;
    currentSchool: CurrentSchool | null;
    previousSchool: PreviousSchool | null;
    answers: Record<
        string,
        {
            score: number;
            answers: StudentAnswer[];
        }
    >;
}