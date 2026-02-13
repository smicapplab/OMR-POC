import { Controller, Get, Query, Param, ParseIntPipe } from '@nestjs/common';
import { AnswerSheetService } from './answer-sheet.service';
import { ListAnswerSheetDto } from './dto/list-answer-sheet.dto';
import { PaginatedAnswerSheetResponse } from './interfaces/paginated-response.interface';

@Controller('answer-sheet')
export class AnswerSheetController {
    constructor(private readonly answerSheetService: AnswerSheetService) { }

    @Get()
    async listAnswerSheets(
        @Query() query: ListAnswerSheetDto,
    ): Promise<PaginatedAnswerSheetResponse> {
        return await this.answerSheetService.getPaginatedAnswerSheets(query);
    }

    @Get(':id')
    async getAnswerSheetById(
        @Param('id', ParseIntPipe) id: number,
    ) {
        return this.answerSheetService.getAnswerSheetById(id);
    }
    
}
