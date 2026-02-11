import { Injectable, UnauthorizedException } from '@nestjs/common';
import { DatabaseService } from '../database/database.service';
import { JwtService } from '@nestjs/jwt';
import { eq } from 'drizzle-orm';
import * as bcrypt from 'bcrypt';
import { users } from '../../drizzle/schema';
import { JwtPayload } from './types/jwt-payload.type';

@Injectable()
export class AuthService {


    constructor(
        private readonly dbService: DatabaseService,
        private readonly jwtService: JwtService,
    ) {

        console.log(process.env.JWT_SECRET)

    }

    async validateUser(email: string, password: string) {
        console.log({ email, password })
        const db = this.dbService.db;

        console.log(db)

        const result: (typeof users.$inferSelect)[] = await db
            .select()
            .from(users)
            .where(eq(users.email, email));

        const user = result[0];

        if (!user) throw new UnauthorizedException('Invalid credentials');

        const isMatch = await bcrypt.compare(password, user.passwordHash);
        if (!isMatch) throw new UnauthorizedException('Invalid credentials');

        return user;
    }

    async login(email: string, password: string) {
        const user = await this.validateUser(email, password);

        const payload: JwtPayload = {
            sub: user.id,
            email: user.email,
            role: user.role,
        };

        return {
            accessToken: await this.jwtService.signAsync(payload),
        };
    }
}
