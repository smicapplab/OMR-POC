"use client";

import { LoginForm } from "@/components/login-form";
import Image from "next/image";

export default function Home() {

  return (
    <div className="grid min-h-svh lg:grid-cols-2">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <Image
          src="/icon.png"
          alt="Logo"
          width={40}
          height={20}
          priority
        />
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-md">
            <LoginForm />
          </div>
        </div>
      </div>
      <div
        className="relative hidden lg:block bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: "url('/login-bg.jpg')" }}
      >
      </div>
    </div>
  );
}
