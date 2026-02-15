import { Card } from "@/components/ui/card";
import { TabsContent } from "@/components/ui/tabs";
import { formatLabel } from "@/lib/utils";
import { CurrentSchool, PreviousSchool, Student } from "@/types/answer-sheet";

export function StudentInfo({ student, currentSchool, previousSchool }: { student: Student | null, currentSchool: CurrentSchool | null, previousSchool: PreviousSchool | null }) {

    const normalizeSpecialClasses = (data: Student | null) => {
        if (!data) return null;

        let specialClasses = data.specialClasses;

        if (typeof specialClasses === "string") {
            try {
                const parsed = JSON.parse(specialClasses);
                if (Array.isArray(parsed)) {
                    specialClasses = parsed.join(", ");
                }
            } catch {
                // leave as is
            }
        }

        return { ...data, specialClasses };
    };

    const renderFieldGrid = <T extends object>(
        data: T,
        excluded: (keyof T)[]
    ) => {
        const keys = Object.keys(data) as (keyof T)[];

        return (
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 min-w-0">
                {keys
                    .filter((key) => !excluded.includes(key))
                    .map((key) => (
                        <div key={String(key)} className="flex flex-col">
                            <span className="text-xs text-muted-foreground uppercase tracking-wide">
                                {formatLabel(String(key))}
                            </span>
                            <span className="text-sm font-medium break-break-words">
                                {String(data[key] ?? "-")}
                            </span>
                        </div>
                    ))}
            </div>
        );
    };

    const transformedStudent = normalizeSpecialClasses(student);

    return (
        <TabsContent
            value="student-information"
            className="w-full h-full flex flex-col min-w-0"
        >
            <div className="w-full flex-1 min-w-0 overflow-auto">
                <Card className="w-full border border-gray-200 shadow-sm rounded-lg p-5">
                    {student && (
                        <div className="flex flex-col gap-6 min-w-0">

                            {/* Date of Birth (combined) */}
                            <div className="flex flex-col">
                                <span className="text-xs text-muted-foreground uppercase tracking-wide">
                                    Date of Birth
                                </span>
                                <span className="text-sm font-medium">
                                    {transformedStudent?.birthMonth && transformedStudent?.birthDay && transformedStudent?.birthYear
                                        ? (() => {
                                            const rawYear = transformedStudent.birthYear;
                                            let year = rawYear;

                                            if (rawYear.length === 2) {
                                                const twoDigit = Number(rawYear);
                                                const currentTwoDigit = new Date().getFullYear() % 100;
                                                year = twoDigit <= currentTwoDigit
                                                    ? `20${rawYear}`
                                                    : `19${rawYear}`;
                                            }

                                            return `${transformedStudent.birthMonth} ${transformedStudent.birthDay}, ${year}`;
                                        })()
                                        : "-"}
                                </span>
                            </div>

                            {transformedStudent && (
                                <>
                                    {/* Section 1 – Identity */}
                                    <div>
                                        <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">
                                            Identity
                                        </h3>
                                        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 min-w-0">
                                            {(
                                                [
                                                    "firstName",
                                                    "lastName",
                                                    "middleInitial",
                                                    "gender",
                                                    "lrn",
                                                ] as (keyof Student)[]
                                            ).map((key) => (
                                                <div key={String(key)} className="flex flex-col">
                                                    <span className="text-xs text-muted-foreground uppercase tracking-wide">
                                                        {formatLabel(String(key))}
                                                    </span>
                                                    <span className="text-sm font-medium break-break-break-words">
                                                        {String(transformedStudent[key] ?? "-")}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Section 2 – Program */}
                                    <div>
                                        <h3 className="text-sm font-semibold mb-3 mt-6 text-muted-foreground uppercase tracking-wide">
                                            Program
                                        </h3>
                                        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 min-w-0">
                                            {(
                                                [
                                                    "ssc",
                                                    "fourPs",
                                                    "specialClasses",
                                                ] as (keyof Student)[]
                                            ).map((key) => (
                                                <div key={String(key)} className="flex flex-col">
                                                    <span className="text-xs text-muted-foreground uppercase tracking-wide">
                                                        {formatLabel(String(key))}
                                                    </span>
                                                    <span className="text-sm font-medium break-break-words">
                                                        {String(transformedStudent[key] ?? "-")}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </>
                            )}
                        </div>
                    )}
                </Card>

                <Card className="w-full border border-gray-200 shadow-sm rounded-lg p-5 mt-5">
                    <h2
                        id="grade-6-heading"
                        className="text-base font-semibold mb-4"
                    >
                        Grade 6 – Previous School
                    </h2>
                    {previousSchool
                        ? renderFieldGrid(previousSchool, [
                            "id",
                            "scanId",
                            "reviewRequired",
                            "createdAt",
                        ])
                        : (
                            <div className="text-sm text-muted-foreground">
                                No previous school data available.
                            </div>
                        )}
                </Card>

                <Card className="w-full border border-gray-200 shadow-sm rounded-lg p-5 mt-5">
                    <h2
                        id="grade-7-heading"
                        className="text-base font-semibold mb-4"
                    >
                        Grade 7 – Current School
                    </h2>

                    {currentSchool
                        ? renderFieldGrid(currentSchool, [
                            "id",
                            "scanId",
                            "reviewRequired",
                            "createdAt",
                        ])
                        : (
                            <div className="text-sm text-muted-foreground">
                                No current school data available.
                            </div>
                        )}
                </Card>

            </div>
        </TabsContent>
    );
}