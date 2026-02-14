"use client";

import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { AnswerSheetDetailResponse } from "@/types/answer-sheet";
import { useLoading } from "@/app/context/LoadingContext";
import { ZoomableImage } from "./components/zoomable-image";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

export default function AnswerSheet() {
    const params = useParams();
    const scanIdParam = params?.scanId as string;
    const { setIsLoading } = useLoading();
    const router = useRouter();

    const [data, setData] = useState<AnswerSheetDetailResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!scanIdParam) return;

        const scanId = Number(scanIdParam);
        if (isNaN(scanId)) {
            setError("Invalid scanId");
            setIsLoading(false);
            return;
        }

        async function fetchData() {
            setIsLoading(true);
            try {
                const res = await fetch(`/api/answer-sheet/${scanId}`, {
                    method: "GET",
                });

                if (res.status === 404) {
                    setData(null);
                    return;
                }

                if (!res.ok) {
                    throw new Error("Failed to fetch answer sheet");
                }

                const json: AnswerSheetDetailResponse | null = await res.json();

                if (!json) {
                    setData(null);
                    return;
                }

                setData(json);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Unexpected error");
            } finally {
                setIsLoading(false);
            }
        }

        fetchData();
    }, [scanIdParam, setIsLoading]);

    if (error) return <div className="p-4 text-red-500">{error}</div>;
    if (!data) {
        return (
            <div className="flex h-full items-center justify-center">
                <div className="text-center">
                    <h2 className="text-xl font-semibold">Answer Sheet Not Found</h2>
                    <p className="text-sm text-muted-foreground mt-2">
                        The requested scan could not be located or may have been removed.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col">
            <Separator className="my-1"/>
            <ResizablePanelGroup orientation="horizontal" className="flex-1 min-h-0">
                <ResizablePanel defaultSize={60} className="px-5">
                    <div className="flex items-center mb-4">
                        <Button variant="ghost"
                            onClick={() => router.push("/dashboard")}
                            className="px-3 py-1.5 text-sm hover:bg-muted flex items-center gap-5"
                        >
                            <ArrowLeft />
                        </Button>

                        <h1 className="font-bold text-xl">
                            {data.student?.firstName} {data.student?.lastName}
                        </h1>
                    </div>
                    <Separator />
                    <pre className="p-4 text-xs overflow-auto">
                        {JSON.stringify(data.omrScan, null, 2)}
                    </pre>
                </ResizablePanel>

                <ResizableHandle withHandle />

                <ResizablePanel defaultSize={40} className="px-5">
                    {data.omrScan.fileUrl}
                    <ZoomableImage src={data.omrScan.fileUrl} />
                </ResizablePanel>
            </ResizablePanelGroup>
        </div>
    );
}