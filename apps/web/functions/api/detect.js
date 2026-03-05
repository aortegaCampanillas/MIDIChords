import { detectChord } from "../_lib/music.js";

export const onRequestPost = async ({ request }) => {
  const body = await request.json().catch(() => ({}));
  const language = (body.language || "es").toLowerCase() === "en" ? "en" : "es";
  const preferFlat = String(body.accidental || "sharp").toLowerCase() === "flat";
  const notes = Array.isArray(body.notes) ? body.notes : [];
  return Response.json(detectChord({ notes, language, preferFlat }));
};

