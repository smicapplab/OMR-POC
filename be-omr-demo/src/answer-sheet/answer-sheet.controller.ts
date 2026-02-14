import { Controller, Get, Query, Param, ParseIntPipe, UseGuards } from '@nestjs/common';
import { AnswerSheetService } from './answer-sheet.service';
import { ListAnswerSheetDto } from './dto/list-answer-sheet.dto';
import { PaginatedAnswerSheetResponse } from './interfaces/paginated-response.interface';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';

@Controller('answer-sheet')
export class AnswerSheetController {
    constructor(private readonly answerSheetService: AnswerSheetService) { }

    @UseGuards(JwtAuthGuard)
    @Get()
    async listAnswerSheets(
        @Query() query: ListAnswerSheetDto,
    ): Promise<PaginatedAnswerSheetResponse> {
        return await this.answerSheetService.getPaginatedAnswerSheets(query);
    }

    @UseGuards(JwtAuthGuard)
    @Get(':id')
    async getAnswerSheetById(
        @Param('id', ParseIntPipe) id: number,
    ) {
        return this.answerSheetService.getAnswerSheetById(id);
    }
    
}
