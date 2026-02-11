import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';
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

export const seedHistory = sqliteTable('seed_history', {
    id: integer('id').primaryKey({ autoIncrement: true }),

    name: text('name')
        .notNull()
        .unique(),

    executedAt: text('executed_at')
        .notNull()
        .default(sql`CURRENT_TIMESTAMP`),
});