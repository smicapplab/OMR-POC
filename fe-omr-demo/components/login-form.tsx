"use client";

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { signIn } from "next-auth/react";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { useLoading } from "@/app/context/LoadingContext";
import { useRouter } from "next/navigation";

export function LoginForm() {
    const [email, setEmail] = useState("storrefranca@gmail.com");
    const [password, setPassword] = useState("password");
    const [showPassword, setShowPassword] = useState(false);
    const { setIsLoading } = useLoading();
    const { toast } = useToast();
    const router = useRouter();

    const handleSubmit = async () => {
        if (!email || !password) {
            toast({
                title: "Missing fields",
                description: "Please enter both email and password.",
                variant: "destructive",
            });
            return;
        }

        setIsLoading(true);
        try {
            const result = await signIn("credentials", {
                redirect: false,
                email,
                password,
            });

            if (result?.error) {
                toast({
                    title: "Login failed",
                    description:
                        "We could not sign you in using your email and password. Please try again.",
                    variant: "destructive",
                });
            } else {
                toast({
                    title: "Login successful",
                    description: "Redirecting to your Dashboard...",
                    variant: "success",
                });

                router.push("/dashboard");
            }
        } catch {
            toast({
                title: "Login failed",
                description:
                    "We could not sign you in using your email and password. Please try again.",
                variant: "destructive",
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={cn("flex flex-col gap-6 border p-10 rounded-xl shadow")}>
            <FieldGroup>
                <div className="flex flex-col items-center gap-1 text-center text-yellow-600">
                    <h1 className="text-2xl font-bold">Welcome Back</h1>
                    <p className="text-muted-foreground text-sm text-balance">
                        Enter your email below to login to your account
                    </p>
                </div>
                <Field>
                    <FieldLabel htmlFor="email">Email</FieldLabel>
                    <Input id="email" type="email" placeholder="me@external-email.com" value={email} required onChange={(e) => setEmail(e.target.value)} />
                </Field>
                <Field>
                    <div className="flex items-center">
                        <FieldLabel htmlFor="password">Password</FieldLabel>
                        {/* <a
                            href="/forgot-password"
                            className="ml-auto text-sm underline-offset-4 hover:underline"
                        >
                            Forgot your password?
                        </a> */}
                    </div>
                    <div className="relative w-full">
                        <Input
                            id="password"
                            type={showPassword ? "text" : "password"}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="pr-10"
                        />
                        <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute inset-y-0 right-3 flex items-center text-muted-foreground"
                        >
                            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                        </button>
                    </div>
                </Field>
                <Field>
                    <Button type="button" className="bg-blue-900" onClick={() => handleSubmit()}>Login</Button>
                </Field>
            </FieldGroup>
        </div>
    )
}
