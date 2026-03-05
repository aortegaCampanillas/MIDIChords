import { listChordPatterns, listScalePatterns } from "../_lib/music.js";

export const onRequestGet = async ({ request }) => {
  const url = new URL(request.url);
  const language = (url.searchParams.get("language") || "es").toLowerCase() === "en" ? "en" : "es";
  return Response.json({
    chord_patterns: listChordPatterns(),
    scale_patterns: listScalePatterns(language),
  });
};

