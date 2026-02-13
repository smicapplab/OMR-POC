import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { DatabaseModule } from './database/database.module';
import { AuthModule } from './auth/auth.module';
import { ConfigModule } from '@nestjs/config';
import { ServeStaticModule } from '@nestjs/serve-static';
import { join } from 'path';
import { AnswerSheetModule } from './answer-sheet/answer-sheet.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    ServeStaticModule.forRoot({
      rootPath: join(process.cwd(), '..', 'bucket'),
      serveRoot: '/bucket',
    }),
    DatabaseModule,
    AuthModule,
    AnswerSheetModule
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule { }
