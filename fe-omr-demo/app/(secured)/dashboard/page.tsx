"use client";

import { useEffect, useState } from "react";

interface PaginatedAnswerSheetResponse {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  data: AnswerSheetListItem[];
}

interface AnswerSheetListItem {
    scanId: number;
    firstName: string | null;
    lastName: string | null;
    schoolId: string | null;
    createdAt: Date;
    studentsReviewRequired: boolean;
    currentSchoolsReviewRequired: boolean;
    previousSchoolsReviewRequired: boolean;
}

export default function Dashboard() {
    const [data, setData] = useState<PaginatedAnswerSheetResponse | null>(null);

    useEffect(() => {
        fetch("/api/answer-sheet?page=1&limit=10")
            .then(res => res.json())
            .then(setData);
    }, []);


    return (
        <div className="">
            <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
    );
}
