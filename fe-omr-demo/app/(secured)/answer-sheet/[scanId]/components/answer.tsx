import { Card } from "@/components/ui/card";
import { TabsContent } from "@/components/ui/tabs";
import { useMemo } from "react";
import type { StudentAnswer } from "@/types/answer-sheet";

export function Answers({ answers }: {
    answers: Record<
        string,
        {
            score: number;
            answers: StudentAnswer[];
        }
    > | null
}) {

    const subjects = useMemo(() => {
        return answers ? Object.keys(answers) : [];
    }, [answers]);

    const { maxQuestions, normalized } = useMemo(() => {
        if (!answers || subjects.length === 0) {
            return { maxQuestions: 0, normalized: {} as Record<string, Record<number, StudentAnswer>> };
        }

        const maxQuestions = Math.max(
            ...subjects.map((s) => answers[s].answers.length)
        );

        const normalized: Record<string, Record<number, StudentAnswer>> = {};

        subjects.forEach((subject) => {
            normalized[subject] = {};

            answers[subject].answers
                .slice()
                .sort((a, b) => a.questionNumber - b.questionNumber)
                .forEach((ans) => {
                    normalized[subject][ans.questionNumber] = ans;
                });
        });

        return { maxQuestions, normalized };
    }, [answers, subjects]);

    if (!answers) {
        return (
            <TabsContent
                value="answers"
                className="w-full h-full flex flex-col min-w-0"
            >
                <div className="flex items-center justify-center h-full text-muted-foreground">
                    No answers available
                </div>
            </TabsContent>
        );
    }


    return (
        <TabsContent
            value="answers"
            className="w-full h-full flex flex-col min-w-0"
        >
            <div className="w-full flex-1 min-w-0 overflow-auto space-y-6">

                {/* Legend */}
                <div className="flex flex-wrap gap-4 text-xs">
                    <div className="flex items-center gap-2">
                        <span className="w-3 h-3 bg-red-100 border border-red-300"></span>
                        <span>Incorrect Answer</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-amber-600">⚠</span>
                        <span>Requires Manual Review</span>
                    </div>
                </div>
                <Card className="p-4 border border-gray-200 shadow-sm overflow-auto">
                    <div className="min-w-max">
                        <table className="w-full text-sm border-collapse border border-gray-200">
                            <thead className="sticky top-0 bg-background z-10">
                                <tr className="border-b">
                                    <th className="text-left p-2 border-r border-gray-200">Question #</th>
                                    {subjects.map((subject) => (
                                        <th
                                            key={subject}
                                            className="text-center p-2 capitalize border-r border-gray-200"
                                        >
                                            {subject.length <= 3
                                                ? subject.toUpperCase()
                                                : subject.charAt(0).toUpperCase() + subject.slice(1)}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {Array.from({ length: maxQuestions }).map((_, idx) => {
                                    const questionNumber = idx + 1;

                                    return (
                                        <tr key={questionNumber} className="border-b">
                                            <td className="p-2 font-medium border-r border-gray-200">
                                                {questionNumber}
                                            </td>

                                            {subjects.map((subject) => {
                                                const answer = normalized[subject][questionNumber];

                                                if (!answer) {
                                                    return (
                                                        <td key={subject} className="p-2 text-center border-r border-gray-200">
                                                            -
                                                        </td>
                                                    );
                                                }

                                                const isCorrect = answer.isCorrect;
                                                const needsReview = answer.reviewRequired;

                                                const cellColor = !isCorrect
                                                    ? "bg-red-100 text-red-700"
                                                    : "";

                                                return (
                                                    <td
                                                        key={subject}
                                                        className={`p-2 text-center border-r border-gray-200 ${cellColor}`}
                                                    >
                                                        <div className="flex items-center justify-center gap-1">
                                                            <span>{answer.answer}</span>
                                                            {needsReview && (
                                                                <span className="text-xs text-amber-600">
                                                                    ⚠
                                                                </span>
                                                            )}
                                                        </div>
                                                    </td>
                                                );
                                            })}
                                        </tr>
                                    );
                                })}
                                {/* Score Row */}
                                <tr className="bg-muted/40 font-semibold">
                                    <td className="p-2 border-r border-gray-200">
                                        Score
                                    </td>
                                    {subjects.map((subject) => {
                                        const total = answers[subject].answers.length;
                                        const score = answers[subject].score;

                                        return (
                                            <td
                                                key={subject}
                                                className="p-2 text-center border-r border-gray-200"
                                            >
                                                {(() => {
                                                    const percentage = total > 0
                                                        ? Math.round((score / total) * 100)
                                                        : 0;
                                                    return `${score} (${percentage}%)`;
                                                })()}
                                            </td>
                                        );
                                    })}
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </Card>
            </div>
        </TabsContent>
    );
}