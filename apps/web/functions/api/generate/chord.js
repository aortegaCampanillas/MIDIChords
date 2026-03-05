import { generateChord } from "../../_lib/music.js";

export const onRequestPost = async ({ request }) => {
  const body = await request.json().catch(() => ({}));
  const language = (body.language || "es").toLowerCase() === "en" ? "en" : "es";
  const preferFlat = String(body.accidental || "sharp").toLowerCase() === "flat";
  return Response.json(
    generateChord({
      rootPc: Number(body.root_pc) || 0,
      suffix: String(body.suffix || ""),
      inversion: Number(body.inversion) || 0,
      language,
      preferFlat,
    }),
  );
};

