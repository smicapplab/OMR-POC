import Database from 'better-sqlite3';
import type { Database as SQLiteDatabase } from 'better-sqlite3';
import { drizzle, type BetterSQLite3Database } from 'drizzle-orm/better-sqlite3';
import * as bcrypt from 'bcrypt';
import * as path from 'path';
import * as schema from '../drizzle/schema';
import { users, seedHistory } from '../drizzle/schema';
import { eq } from 'drizzle-orm';

import * as fs from 'fs';
import * as dotenv from 'dotenv';

dotenv.config();

const SEED_NAME = 'users_v1';

async function seed(): Promise<void> {
    const rawPath = process.env.OMR_DB_PATH ?? '../omr.db';
    const dbPath = path.resolve(process.cwd(), rawPath);

    console.log('Using DB path:', dbPath);

    if (!fs.existsSync(dbPath)) {
        throw new Error(`Database file not found at: ${dbPath}`);
    }

    const sqlite: SQLiteDatabase = new Database(dbPath);
    console.log('Connected to SQLite database successfully.');

    const db: BetterSQLite3Database<typeof schema> = drizzle(sqlite, { schema });

    const alreadyExecuted = await db
        .select()
        .from(seedHistory)
        .where(eq(seedHistory.name, SEED_NAME));

    if (alreadyExecuted.length > 0) {
        console.log(`Seed ${SEED_NAME} already executed. Skipping.`);
        return;
    }

    const passwordHash: string = await bcrypt.hash('password', 10);

    await db.insert(users).values([
        {
            email: 'storrefranca@gmail.com',
            passwordHash,
            role: 'admin',
        },
        {
            email: 'aldrich.abrogena@dice205.com',
            passwordHash,
            role: 'admin',
        },
    ]);

    await db.insert(seedHistory).values({
        name: SEED_NAME,
    });

    console.log(`Seed ${SEED_NAME} executed successfully.`);
}

seed().catch((err: unknown) => {
    console.error('Seeding failed:', err);
    process.exit(1);
});