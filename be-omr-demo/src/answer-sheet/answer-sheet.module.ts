import { Module } from '@nestjs/common';
import { AnswerSheetController } from './answer-sheet.controller';
import { AnswerSheetService } from './answer-sheet.service';
import { DatabaseService } from '../database/database.service';
import { AuthModule } from '../auth/auth.module';

@Module({
  imports: [AuthModule],
  controllers: [AnswerSheetController],
  providers: [AnswerSheetService, DatabaseService]
})

export class AnswerSheetModule {}
