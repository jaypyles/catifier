import { fetch } from "@/lib/utils";

export async function getPreviousImages() {
  const data = await fetch<{ images: string[] }>("/images");
  return data?.images;
}
