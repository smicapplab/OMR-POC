import type { Config } from 'drizzle-kit';

export default {
    schema: './drizzle/schema.ts',
    out: './drizzle/migrations',
    dialect: 'sqlite',
    dbCredentials: {
        url: process.env.OMR_DB_PATH ?? '../omr.db',
    },
} satisfies Config;