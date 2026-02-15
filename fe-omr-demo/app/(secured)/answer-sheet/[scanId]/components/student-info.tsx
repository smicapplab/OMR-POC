import { Card } from "@/components/ui/card";
import { TabsContent } from "@/components/ui/tabs";
import { formatLabel } from "@/lib/utils";
import { CurrentSchool, PreviousSchool, Student } from "@/types/answer-sheet";

export function StudentInfo({ student, currentSchool, previousSchool }: { student: Student | null, currentSchool: CurrentSchool | null, previousSchool: PreviousSchool | null }) {

    return (
        <TabsContent
            value="student-information"
            className="w-full h-full flex flex-col min-w-0"
        >
            <div className="w-full flex-1 min-w-0 overflow-auto">
                <Card className="w-full border border-gray-200 shadow-sm rounded-lg p-5">
                    {student && (
                        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">

                            {/* Date of Birth (combined) */}
                            <div className="flex flex-col">
                                <span className="text-xs text-muted-foreground uppercase tracking-wide">
                                    Date of Birth
                                </span>
                                <span className="text-sm font-medium">
                                    {student.birthMonth && student.birthDay && student.birthYear
                                        ? `${student.birthMonth} ${student.birthDay}, ${student.birthYear}`
                                        : "-"}
                                </span>
                            </div>

                            {Object.entries(student)
                                .filter(([key]) =>
                                    ![
                                        "id",
                                        "scanId",
                                        "reviewRequired",
                                        "createdAt",
                                        "birthMonth",
                                        "birthDay",
                                        "birthYear",
                                    ].includes(key)
                                )
                                .map(([key, value]) => {
                                    let displayValue = value ?? "-";

                                    if (key === "specialClasses" && typeof value === "string") {
                                        try {
                                            const parsed = JSON.parse(value);
                                            if (Array.isArray(parsed)) {
                                                displayValue = parsed.join(", ");
                                            }
                                        } catch {
                                            displayValue = value;
                                        }
                                    }



                                    return (
                                        <div key={key} className="flex flex-col">
                                            <span className="text-xs text-muted-foreground uppercase tracking-wide">
                                                {formatLabel(key)}
                                            </span>
                                            <span className="text-sm font-medium">
                                                {String(displayValue || "-")}
                                            </span>
                                        </div>
                                    );
                                })}
                        </div>
                    )}
                </Card>

                <Card className="w-full border border-gray-200 shadow-sm rounded-lg p-5 mt-5">
                    <h2 className="text-black">Grade 6</h2>
                    {previousSchool && (
                        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                            {Object.entries(previousSchool)
                                .filter(([key]) =>
                                    ![
                                        "id",
                                        "scanId",
                                        "reviewRequired",
                                        "createdAt",
                                    ].includes(key)
                                )
                                .map(([key, value]) => (
                                    <div key={key} className="flex flex-col">
                                        <span className="text-xs text-muted-foreground uppercase tracking-wide">
                                            {formatLabel(key)}
                                        </span>
                                        <span className="text-sm font-medium">
                                            {String(value ?? "-")}
                                        </span>
                                    </div>
                                ))}
                        </div>
                    )}
                </Card>

                <Card className="w-full border border-gray-200 shadow-sm rounded-lg p-5 mt-5">
                    <h2 className="text-black">Grade 7</h2>

                    {currentSchool && (
                        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
                            {Object.entries(currentSchool)
                                .filter(([key]) =>
                                    ![
                                        "id",
                                        "scanId",
                                        "reviewRequired",
                                        "createdAt",
                                    ].includes(key)
                                )
                                .map(([key, value]) => (
                                    <div key={key} className="flex flex-col">
                                        <span className="text-xs text-muted-foreground uppercase tracking-wide">
                                            {formatLabel(key)}
                                        </span>
                                        <span className="text-sm font-medium">
                                            {String(value ?? "-")}
                                        </span>
                                    </div>
                                ))}
                        </div>
                    )}
                </Card>

            </div>
        </TabsContent>
    );
}