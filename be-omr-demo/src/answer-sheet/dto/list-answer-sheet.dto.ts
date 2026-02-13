import { Transform } from 'class-transformer';
import { IsIn, IsInt, IsOptional, IsString, Min } from 'class-validator';

export class ListAnswerSheetDto {
    @IsOptional()
    @Transform(({ value }: { value: unknown }) => typeof value === 'string' ? parseInt(value, 10) : value)
    @IsInt()
    @Min(1)
    page: number = 1;

    @IsOptional()
    @Transform(({ value }: { value: unknown }) => typeof value === 'string' ? parseInt(value, 10) : value)
    @IsInt()
    @Min(1)
    limit: number = 20;

    @IsOptional()
    @IsString()
    keyword?: string;

    @IsOptional()
    @IsIn(['name', 'school', 'created_at'])
    sortBy: 'name' | 'school' | 'created_at' = 'created_at';

    @IsOptional()
    @IsIn(['asc', 'desc'])
    sortOrder: 'asc' | 'desc' = 'desc';
}