"use client";
/* eslint-disable @next/next/no-img-element */

import React, { useState, useRef, useEffect } from "react";

export function ZoomableImage({ src }: { src: string | null }) {
    const [scale, setScale] = useState(1);
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isDragging, setIsDragging] = useState(false);

    const containerRef = useRef<HTMLDivElement | null>(null);
    const startRef = useRef({ x: 0, y: 0 });
    const imgRef = useRef<HTMLImageElement | null>(null);

    const zoomIn = () => setScale((s) => Math.min(s + 0.2, 5));
    const zoomOut = () => setScale((s) => Math.max(s - 0.2, 0.05));
    const reset = () => {
        setScale(1);
        setPosition({ x: 0, y: 0 });
    };

    useEffect(() => {
        function fitToWidth() {
            if (!containerRef.current || !imgRef.current) return;

            const containerWidth = containerRef.current.clientWidth;
            const imageWidth = imgRef.current.naturalWidth;

            if (!imageWidth) return;

            const fitScale = containerWidth / imageWidth;
            setScale(fitScale);
            setPosition({ x: 0, y: 0 });
        }

        fitToWidth();
        window.addEventListener("resize", fitToWidth);

        return () => {
            window.removeEventListener("resize", fitToWidth);
        };
    }, [src]);

    const handleMouseDown = (e: React.MouseEvent) => {
        setIsDragging(true);
        startRef.current = {
            x: e.clientX - position.x,
            y: e.clientY - position.y,
        };
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!isDragging) return;
        setPosition({
            x: e.clientX - startRef.current.x,
            y: e.clientY - startRef.current.y,
        });
    };

    const handleMouseUp = () => setIsDragging(false);

    if (!src) {
        return (
            <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                No image available
            </div>
        );
    }

    return (
        <div
            ref={containerRef}
            className="relative h-full w-full overflow-hidden bg-muted/20"
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
        >
            {/* Floating Controls */}
            <div className="absolute top-4 right-4 z-10 bg-background/90 backdrop-blur shadow-md rounded-md p-2 flex items-center gap-2">
                <button
                    onClick={zoomOut}
                    className="px-2 py-1 text-sm border rounded hover:bg-muted"
                >
                    -
                </button>
                <span className="text-xs w-12 text-center">
                    {(scale * 100).toFixed(0)}%
                </span>
                <button
                    onClick={zoomIn}
                    className="px-2 py-1 text-sm border rounded hover:bg-muted"
                >
                    +
                </button>
                <button
                    onClick={reset}
                    className="px-2 py-1 text-xs border rounded hover:bg-muted"
                >
                    Reset
                </button>
            </div>

            {/* Image Layer */}
            <div
                className="absolute top-0 left-0 cursor-grab active:cursor-grabbing"
                style={{
                    transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
                    transformOrigin: "top left",
                }}
                onMouseDown={handleMouseDown}
            >
                <img
                    ref={imgRef}
                    src={src}
                    alt="OMR Scan"
                    className="max-w-none select-none"
                    draggable={false}
                />
            </div>
        </div>
    );
}
