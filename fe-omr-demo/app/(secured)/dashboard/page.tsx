"use client";

import { useEffect, useState, useCallback, useTransition } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";

interface PaginatedAnswerSheetResponse {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    data: AnswerSheetListItem[];
}

interface AnswerSheetListItem {
    scanId: number;
    firstName: string | null;
    lastName: string | null;
    schoolId: string | null;
    createdAt: Date;
    studentsReviewRequired: boolean;
    currentSchoolsReviewRequired: boolean;
    previousSchoolsReviewRequired: boolean;
}

export default function Dashboard() {
    const [data, setData] = useState<PaginatedAnswerSheetResponse | null>(null);
    const [keyword, setKeyword] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);
    const [page, setPage] = useState<number>(1);
    const [sortBy, setSortBy] = useState<"name" | "school" | "created_at">("created_at");
    const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
    const [, startTransition] = useTransition();

    const fetchData = useCallback(async (search?: string, pageNumber?: number) => {
        setLoading(true);

        const params = new URLSearchParams({
            page: String(pageNumber ?? page),
            limit: "10",
            sortBy,
            sortOrder,
        });

        if (search && search.trim().length > 0) {
            params.append("keyword", search.trim());
        }

        const res = await fetch(`/api/answer-sheet?${params.toString()}`);

        if (!res.ok) {
            setData(null);
            setLoading(false);
            return;
        }

        const text = await res.text();
        const json = text ? (JSON.parse(text) as PaginatedAnswerSheetResponse) : null;
        setData(json);

        if (pageNumber) {
            setPage(pageNumber);
        }

        setLoading(false);
    }, [page, sortBy, sortOrder]);

    useEffect(() => {
        startTransition(() => {
            void fetchData(undefined, 1);
        });
    }, [fetchData, startTransition]);

    return (
        <div className="p-6 space-y-6">
            {/* Search Section */}
            <div className="flex items-center gap-2">
                <Input
                    placeholder="Search by name or school..."
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") {
                            fetchData(keyword);
                        }
                    }}
                />
                <Button
                    onClick={() => fetchData(keyword)}
                    disabled={loading}
                >
                    {loading ? "Searching..." : "Search"}
                </Button>
                <Button
                    variant="outline"
                    onClick={() => {
                        setKeyword("");
                        fetchData("");
                    }}
                >
                    Reset
                </Button>
            </div>

            {/* Table Output */}
            {data && (
                <div className="space-y-4">
                    <div className="border rounded-md">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="text-center">ID</TableHead>
                                    <TableHead
                                        className="text-center cursor-pointer select-none"
                                        onClick={() => {
                                            setSortBy("name");
                                            setSortOrder(sortOrder === "asc" ? "desc" : "asc");
                                        }}
                                    >
                                        <div className="flex items-center justify-center gap-1">
                                            Name
                                            {sortBy === "name" ? (
                                                sortOrder === "asc" ? (
                                                    <ArrowUp className="h-4 w-4" />
                                                ) : (
                                                    <ArrowDown className="h-4 w-4" />
                                                )
                                            ) : (
                                                <ArrowUpDown className="h-4 w-4 opacity-40" />
                                            )}
                                        </div>
                                    </TableHead>
                                    <TableHead
                                        className="text-center cursor-pointer select-none"
                                        onClick={() => {
                                            setSortBy("school");
                                            setSortOrder(sortOrder === "asc" ? "desc" : "asc");
                                        }}
                                    >
                                        <div className="flex items-center justify-center gap-1">
                                            School ID
                                            {sortBy === "school" ? (
                                                sortOrder === "asc" ? (
                                                    <ArrowUp className="h-4 w-4" />
                                                ) : (
                                                    <ArrowDown className="h-4 w-4" />
                                                )
                                            ) : (
                                                <ArrowUpDown className="h-4 w-4 opacity-40" />
                                            )}
                                        </div>
                                    </TableHead>
                                    <TableHead
                                        className="text-center cursor-pointer select-none"
                                        onClick={() => {
                                            setSortBy("created_at");
                                            setSortOrder(sortOrder === "asc" ? "desc" : "asc");
                                        }}
                                    >
                                        <div className="flex items-center justify-center gap-1">
                                            Created
                                            {sortBy === "created_at" ? (
                                                sortOrder === "asc" ? (
                                                    <ArrowUp className="h-4 w-4" />
                                                ) : (
                                                    <ArrowDown className="h-4 w-4" />
                                                )
                                            ) : (
                                                <ArrowUpDown className="h-4 w-4 opacity-40" />
                                            )}
                                        </div>
                                    </TableHead>
                                    <TableHead className="text-center">Student Review</TableHead>
                                    <TableHead className="text-center">Grade 6 Review</TableHead>
                                    <TableHead className="text-center">Grade 7 Flags</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {data.data.map((item) => (
                                    <TableRow key={item.scanId}>
                                        <TableCell>{item.scanId}</TableCell>
                                        <TableCell>
                                            {item.firstName ?? ""} {item.lastName ?? ""}
                                        </TableCell>
                                        <TableCell className="text-center">{item.schoolId ?? "-"}</TableCell>
                                        <TableCell className="text-center">
                                            {new Date(item.createdAt).toLocaleString()}
                                        </TableCell>
                                        <TableCell className="text-center">
                                            {item.studentsReviewRequired ? (
                                                <Badge variant="destructive">Yes</Badge>
                                            ) : (
                                                <Badge variant="secondary">No</Badge>
                                            )}
                                        </TableCell>
                                        <TableCell className="text-center">
                                            {item.currentSchoolsReviewRequired ? (
                                                <Badge variant="destructive">Yes</Badge>
                                            ) : (
                                                <Badge variant="secondary">No</Badge>
                                            )}
                                        </TableCell>
                                        <TableCell className="text-center">
                                            {item.previousSchoolsReviewRequired ? (
                                                <Badge variant="destructive">Yes</Badge>
                                            ) : (
                                                <Badge variant="secondary">No</Badge>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>

                    {/* Pagination */}
                    <div className="flex items-center justify-between">
                        <div className="text-sm text-muted-foreground">
                            Page {data.page} of {data.totalPages} • Total {data.total}
                        </div>

                        <div className="flex gap-2">
                            <Button
                                variant="outline"
                                disabled={page <= 1 || loading}
                                onClick={() => fetchData(keyword, page - 1)}
                            >
                                Previous
                            </Button>
                            <Button
                                variant="outline"
                                disabled={page >= data.totalPages || loading}
                                onClick={() => fetchData(keyword, page + 1)}
                            >
                                Next
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
