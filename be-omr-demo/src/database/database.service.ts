import { Injectable, OnModuleDestroy, Logger } from '@nestjs/common';
import Database from 'better-sqlite3';
import { drizzle, BetterSQLite3Database } from 'drizzle-orm/better-sqlite3';
import * as path from 'path';
import * as schema from '../../drizzle/schema';

export type AppDatabase = BetterSQLite3Database<typeof schema>;

@Injectable()
export class DatabaseService implements OnModuleDestroy {
    private readonly logger = new Logger(DatabaseService.name);
    private readonly sqlite: InstanceType<typeof Database>;
    private readonly _db: AppDatabase;

    constructor() {
        const rawPath =
            process.env.OMR_DB_PATH ??
            path.resolve(process.cwd(), '..', 'omr.db');

        const dbPath = path.isAbsolute(rawPath)
            ? rawPath
            : path.resolve(process.cwd(), rawPath);

        this.logger.log(`Using SQLite DB at: ${dbPath}`);

        this.sqlite = new Database(dbPath, { timeout: 5000 });

        this.sqlite.pragma('journal_mode = WAL');
        this.sqlite.pragma('synchronous = NORMAL');
        this.sqlite.pragma('foreign_keys = ON');
        this.sqlite.pragma('busy_timeout = 5000');

        this._db = drizzle(this.sqlite, { schema }) as AppDatabase;
    }

    get db(): AppDatabase {
        return this._db;
    }

    all(query: Parameters<AppDatabase['all']>[0]): unknown[] {
        return this._db.all(query);
    }

    get(query: Parameters<AppDatabase['get']>[0]) {
        return this._db.get(query);
    }

    run(query: Parameters<AppDatabase['run']>[0]) {
        return this._db.run(query);
    }

    isHealthy(): boolean {
        try {
            this.sqlite.prepare('SELECT 1').get();
            return true;
        } catch {
            return false;
        }
    }

    onModuleDestroy() {
        try {
            this.sqlite.pragma('wal_checkpoint(TRUNCATE)');
        } catch (e: unknown) {
            const message = e instanceof Error ? e.message : String(e);
            const stack = e instanceof Error ? e.stack : undefined;
            this.logger.warn(`WAL checkpoint failed on shutdown: ${message}`, stack);
        } finally {
            this.sqlite.close();
        }
    }
}