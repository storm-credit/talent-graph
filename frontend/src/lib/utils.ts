import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function fitColor(score: number): string {
  if (score >= 0.7) return "text-emerald-400";
  if (score >= 0.4) return "text-amber-400";
  return "text-red-400";
}

export function fitBg(score: number): string {
  if (score >= 0.7) return "bg-emerald-500/20 border-emerald-500/30";
  if (score >= 0.4) return "bg-amber-500/20 border-amber-500/30";
  return "bg-red-500/20 border-red-500/30";
}

export function burnoutColor(risk: number): string {
  if (risk < 0.3) return "text-emerald-400";
  if (risk <= 0.6) return "text-amber-400";
  return "text-red-400";
}

export function burnoutBg(risk: number): string {
  if (risk < 0.3) return "bg-emerald-500/20";
  if (risk <= 0.6) return "bg-amber-500/20";
  return "bg-red-500/20";
}

export function ratingColor(rating: string): string {
  switch (rating) {
    case "exceptional":
      return "text-emerald-400";
    case "exceeds":
      return "text-emerald-300";
    case "meets":
      return "text-zinc-300";
    case "below":
      return "text-amber-400";
    case "unsatisfactory":
      return "text-red-400";
    default:
      return "text-zinc-400";
  }
}
