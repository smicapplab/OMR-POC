import { sqliteTable, text, integer, real, index, uniqueIndex } from 'drizzle-orm/sqlite-core';
import { sql } from 'drizzle-orm';

export const users = sqliteTable('users', {
    id: integer('id').primaryKey({ autoIncrement: true }),

    email: text('email')
        .notNull()
        .unique(),

    passwordHash: text('password_hash')
        .notNull(),

    role: text('role', {
        enum: ['admin', 'user'],
    })
        .notNull()
        .default('user'),

    createdAt: text('created_at')
        .notNull()
        .default(sql`CURRENT_TIMESTAMP`),
});

export const omrScans = sqliteTable('omr_scan', {
    id: integer('id').primaryKey({ autoIncrement: true }),

    // File metadata
    fileName: text('file_name'),
    filePath: text('file_path'),
    fileUrl: text('file_url'),

    // Raw full JSON payload for entire scan
    rawJson: text('raw_json').notNull(),

    // Aggregate confidence (recommended: minimum confidence across sections)
    confidence: real('confidence'),

    // Aggregate review flag (true if ANY section.review_required === true)
    reviewRequired: integer('review_required', { mode: 'boolean' })
        .notNull()
        .default(false),

    createdAt: text('created_at')
        .notNull()
        .default(sql`CURRENT_TIMESTAMP`),
}, (table) => ({
    reviewIdx: index('idx_scan_review').on(table.reviewRequired),
    createdIdx: index('idx_scan_created').on(table.createdAt),
}));

export const students = sqliteTable('student', {
    id: integer('id').primaryKey({ autoIncrement: true }),

    scanId: integer('scan_id')
        .notNull()
        .references(() => omrScans.id, { onDelete: 'cascade' }),

    // Raw full JSON payload from OMR reader
    rawJson: text('raw_json').notNull(),

    // Flattened / queryable columns
    lastName: text('last_name'),
    firstName: text('first_name'),
    middleInitial: text('middle_initial'),

    birthMonth: text('birth_month'),
    birthDay: text('birth_day'),
    birthYear: text('birth_year'),

    ssc: text('ssc'),
    fourPs: text('four_ps'),
    gender: text('gender'),
    lrn: text('lrn'),

    // Multi-select special classes (stored as JSON string, read-only from OMR so shutup DB nazis :P)
    specialClasses: text('special_classes'),

    // Row-level review flag (true if ANY field.review_required === true)
    reviewRequired: integer('review_required', { mode: 'boolean' })
        .notNull()
        .default(false),

    createdAt: text('created_at')
        .notNull()
        .default(sql`CURRENT_TIMESTAMP`),
}, (table) => ({
    scanIdx: index('idx_student_scan').on(table.scanId),
    lrnIdx: index('idx_student_lrn').on(table.lrn),
}));

export const previousSchools = sqliteTable('previous_school', {
    id: integer('id').primaryKey({ autoIncrement: true }),

    scanId: integer('scan_id')
        .notNull()
        .references(() => omrScans.id, { onDelete: 'cascade' }),

    // Raw JSON payload from previous school OMR section
    rawJson: text('raw_json').notNull(),

    // Flattened / queryable fields
    schoolId: text('school_id'),

    mathGrade: text('math_grade'),
    englishGrade: text('english_grade'),
    scienceGrade: text('science_grade'),
    filipinoGrade: text('filipino_grade'),
    apGrade: text('ap_grade'),

    classSize: text('class_size'),
    schoolYear: text('school_year'),

    // Row-level review flag (true if ANY nested field.review_required === true)
    reviewRequired: integer('review_required', { mode: 'boolean' })
        .notNull()
        .default(false),

    createdAt: text('created_at')
        .notNull()
        .default(sql`CURRENT_TIMESTAMP`),
}, (table) => ({
    scanIdx: index('idx_prev_scan').on(table.scanId),
    reviewIdx: index('idx_prev_review').on(table.reviewRequired),
}));

export const currentSchools = sqliteTable('current_school', {
    id: integer('id').primaryKey({ autoIncrement: true }),

    scanId: integer('scan_id')
        .notNull()
        .references(() => omrScans.id, { onDelete: 'cascade' }),

    // Raw JSON payload from current school OMR section
    rawJson: text('raw_json').notNull(),

    // Flattened / queryable fields
    region: text('region'),
    division: text('division'),
    schoolId: text('school_id'),
    schoolType: text('school_type'),

    // Row-level review flag (true if ANY nested field.review_required === true)
    reviewRequired: integer('review_required', { mode: 'boolean' })
        .notNull()
        .default(false),

    createdAt: text('created_at')
        .notNull()
        .default(sql`CURRENT_TIMESTAMP`),
}, (table) => ({
    scanIdx: index('idx_curr_scan').on(table.scanId),
    reviewIdx: index('idx_curr_review').on(table.reviewRequired),
}));

export const studentAnswers = sqliteTable('student_answer', {
    id: integer('id').primaryKey({ autoIncrement: true }),

    scanId: integer('scan_id')
        .notNull()
        .references(() => omrScans.id, { onDelete: 'cascade' }),

    subject: text('subject').notNull(),
    questionNumber: integer('question_number').notNull(),

    answer: text('answer'),
    confidence: real('confidence'),

    // Per-question review flag
    reviewRequired: integer('review_required', { mode: 'boolean' })
        .notNull()
        .default(false),

    // Optional: raw JSON per question for forensic/debug
    rawJson: text('raw_json'),

    createdAt: text('created_at')
        .notNull()
        .default(sql`CURRENT_TIMESTAMP`),
}, (table) => ({
    scanIdx: index('idx_answer_scan').on(table.scanId),
    reviewIdx: index('idx_answer_review').on(table.reviewRequired),
    uniqueAnswer: uniqueIndex('uq_scan_subject_question')
        .on(table.scanId, table.subject, table.questionNumber),
}));

export const seedHistory = sqliteTable('seed_history', {
    id: integer('id').primaryKey({ autoIncrement: true }),

    name: text('name')
        .notNull()
        .unique(),

    executedAt: text('executed_at')
        .notNull()
        .default(sql`CURRENT_TIMESTAMP`),
});