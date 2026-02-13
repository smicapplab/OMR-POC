import { Module } from '@nestjs/common';
import { AnswerSheetController } from './answer-sheet.controller';
import { AnswerSheetService } from './answer-sheet.service';
import { DatabaseService } from '../database/database.service';

@Module({
  controllers: [AnswerSheetController],
  providers: [AnswerSheetService, DatabaseService]
})

export class AnswerSheetModule {}
