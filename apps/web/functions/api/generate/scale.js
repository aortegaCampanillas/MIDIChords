import { generateScale } from "../../_lib/music.js";

export const onRequestPost = async ({ request }) => {
  const body = await request.json().catch(() => ({}));
  const language = (body.language || "es").toLowerCase() === "en" ? "en" : "es";
  const preferFlat = String(body.accidental || "sharp").toLowerCase() === "flat";
  return Response.json(
    generateScale({
      tonicPc: Number(body.tonic_pc) || 0,
      patternName: String(body.pattern_name || "Ionian"),
      language,
      preferFlat,
    }),
  );
};

