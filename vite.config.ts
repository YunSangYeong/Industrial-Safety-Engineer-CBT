import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({ plugins: [react()], base: "/Industrial-Safety-Engineer-CBT/", build: { rollupOptions: { output: { manualChunks: { questions: ["./src/data/questions.json"] } } } } });
