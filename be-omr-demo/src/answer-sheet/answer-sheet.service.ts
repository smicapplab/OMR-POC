import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../database/database.service';
import { eq, like, or, asc, desc, sql } from 'drizzle-orm';
import { ListAnswerSheetDto } from './dto/list-answer-sheet.dto';
import { currentSchools, omrScans, students, previousSchools, studentAnswers } from '../../drizzle/schema';
import { PaginatedAnswerSheetResponse } from './interfaces/paginated-response.interface';
import { AnswerSheetListItem } from './interfaces/answer-sheet-list-item.interface';
import { AnswerSheetDetailResponse } from './interfaces/answer-sheet-detail-response-interface';

@Injectable()
export class AnswerSheetService {
    constructor(
        private readonly dbService: DatabaseService,
    ) { }

    async getPaginatedAnswerSheets(
        params: ListAnswerSheetDto,
    ): Promise<PaginatedAnswerSheetResponse> {
        const {
            page = 1,
            limit = 20,
            keyword,
            sortBy = 'created_at',
            sortOrder = 'desc',
        } = params;

        const offset = (page - 1) * limit;

        const db = this.dbService.db;

        const orderDirection = sortOrder.toLowerCase() === 'asc' ? 'asc' : 'desc';

        const baseQuery = db
            .select({
                scanId: omrScans.id,
                firstName: students.firstName,
                lastName: students.lastName,
                schoolId: currentSchools.schoolId,
                createdAt: omrScans.createdAt,
                studentsReviewRequired: sql<boolean>`coalesce(${students.reviewRequired}, false)`,
                currentSchoolsReviewRequired: sql<boolean>`coalesce(${currentSchools.reviewRequired}, false)`,
                previousSchoolsReviewRequired: sql<boolean>`coalesce(${previousSchools.reviewRequired}, false)`
            })
            .from(omrScans)
            .leftJoin(students, eq(students.scanId, omrScans.id))
            .leftJoin(currentSchools, eq(currentSchools.scanId, omrScans.id))
            .leftJoin(previousSchools, eq(previousSchools.scanId, omrScans.id));

        const keywordFilter = keyword
            ? or(
                like(students.firstName, `%${keyword}%`),
                like(students.lastName, `%${keyword}%`),
                // search by school_id (not school name)
                like(currentSchools.schoolId, `%${keyword}%`),
            )
            : undefined;

        const filteredQuery = keywordFilter ? baseQuery.where(keywordFilter) : baseQuery;

        const sortedQuery =
            sortBy === 'name'
                ? filteredQuery.orderBy(
                    orderDirection === 'asc'
                        ? asc(students.lastName)
                        : desc(students.lastName),
                    orderDirection === 'asc'
                        ? asc(students.firstName)
                        : desc(students.firstName),
                )
                : sortBy === 'school'
                    ? filteredQuery.orderBy(
                        orderDirection === 'asc'
                            ? asc(currentSchools.schoolId)
                            : desc(currentSchools.schoolId),
                    )
                    : filteredQuery.orderBy(
                        orderDirection === 'asc'
                            ? asc(omrScans.createdAt)
                            : desc(omrScans.createdAt),
                    );

        const rawData = await sortedQuery
            .limit(limit)
            .offset(offset);

        const data: AnswerSheetListItem[] = rawData.map((row) => ({
            ...row,
            createdAt: new Date(row.createdAt),
        }));

        // Total count (same joins + same filter)
        const totalBaseQuery = db
            .select({ total: sql<number>`count(*)` })
            .from(omrScans)
            .leftJoin(students, eq(students.scanId, omrScans.id))
            .leftJoin(currentSchools, eq(currentSchools.scanId, omrScans.id))
            .leftJoin(previousSchools, eq(previousSchools.scanId, omrScans.id));

        const totalResult = keywordFilter
            ? await totalBaseQuery.where(keywordFilter)
            : await totalBaseQuery;

        const total = Number(totalResult[0]?.total ?? 0);
        
        return {
            page,
            limit,
            total,
            totalPages: Math.ceil(total / limit),
            data,
        };
    }

    async getAnswerSheetById(scanId: number): Promise<AnswerSheetDetailResponse | null> {
        const db = this.dbService.db;

        // Base entities (skip rawJson explicitly)
        const baseResult = await db
            .select({
                omrScan: {
                    id: omrScans.id,
                    fileName: omrScans.fileName,
                    filePath: omrScans.filePath,
                    fileUrl: omrScans.fileUrl,
                    status: omrScans.status,
                    confidence: omrScans.confidence,
                    reviewRequired: omrScans.reviewRequired,
                    createdAt: omrScans.createdAt,
                },
                student: students,
                currentSchool: currentSchools,
                previousSchool: previousSchools,
            })
            .from(omrScans)
            .leftJoin(students, eq(students.scanId, omrScans.id))
            .leftJoin(currentSchools, eq(currentSchools.scanId, omrScans.id))
            .leftJoin(previousSchools, eq(previousSchools.scanId, omrScans.id))
            .where(eq(omrScans.id, scanId))
            .limit(1);

        if (!baseResult.length) {
            return null;
        }

        const baseRow = baseResult[0];

        // Fetch answers separately
        const answers = await db
            .select()
            .from(studentAnswers)
            .where(eq(studentAnswers.scanId, scanId));

        // Group answers by subject with score (count of isCorrect === true)
        const groupedAnswers: Record<
            string,
            { score: number; answers: typeof studentAnswers.$inferSelect[] }
        > = {};

        for (const ans of answers) {
            if (!groupedAnswers[ans.subject]) {
                groupedAnswers[ans.subject] = {
                    score: 0,
                    answers: [],
                };
            }

            groupedAnswers[ans.subject].answers.push(ans);

            if (ans.isCorrect === true) {
                groupedAnswers[ans.subject].score += 1;
            }
        }

        return {
            omrScan: {
                id: baseRow.omrScan.id,
                fileName: baseRow.omrScan.fileName ?? '',
                filePath: baseRow.omrScan.filePath ?? '',
                fileUrl: baseRow.omrScan.fileUrl ?? '',
                status: baseRow.omrScan.status,
                confidence: baseRow.omrScan.confidence,
                reviewRequired: baseRow.omrScan.reviewRequired,
                createdAt: new Date(baseRow.omrScan.createdAt),
            },
            student: baseRow.student,
            currentSchool: baseRow.currentSchool,
            previousSchool: baseRow.previousSchool,
            answers: groupedAnswers,
        };
    }
}
