(function initChordHelpCatalog(global) {
  "use strict";

// Mantiene la clasificación de AutoChords y añade dos grupos explícitos para
// las variantes alteradas propias de MIDIChords. Todos los sufijos del Worker
// deben aparecer una sola vez; el fallback de buildSelectors evita perder
// variantes futuras aunque todavía no estén clasificadas aquí.
const CHORD_VARIANT_GROUPS = [
  { labelKey: "chord_group_triads", suffixes: ["", "m", "dim", "aug", "sus2", "sus4", "5", "-5", "sus2sus4"] },
  { labelKey: "chord_group_sevenths", suffixes: ["7", "maj7", "m7", "mMaj7", "dim7", "m7b5", "maj7#5", "7sus4", "maj7b5", "m7#5"] },
  { labelKey: "chord_group_sixths", suffixes: ["6", "m6", "6add9", "m6add9"] },
  { labelKey: "chord_group_add", suffixes: ["add2", "add4", "add9", "madd9"] },
  { labelKey: "chord_group_altered_dominants", suffixes: ["7#5", "7b5", "7#9", "7b9", "7(#5,#9)", "7(#5,b9)", "7(b5,#9)", "7(b5,b9)"] },
  { labelKey: "chord_group_extensions", suffixes: ["9", "maj9", "m9", "11", "maj11", "m11", "13", "maj13", "m13", "mMaj9"] },
  { labelKey: "chord_group_altered_extensions", suffixes: ["9#5", "9b5", "11b9", "13b9", "13#11", "maj9#11", "maj13#11"] },
];

// Textos propios, resumidos y contrastados con el apartado «Teoría» de
// https://auto-chords.com/es/acordes/piano/mayor.html y sus páginas de variantes.
// La fórmula se separa del párrafo para que la ayuda sea fácil de consultar.
const CHORD_VARIANT_THEORY = {
  "": ["1 - 3 - 5", "El acorde mayor se construye apilando dos terceras: una tercera mayor (4 semitonos) seguida de una tercera menor (3 semitonos). Este apilamiento crea un intervalo de quinta justa (7 semitonos) entre la fundamental y la quinta.", "A major chord stacks two thirds: a major third (4 semitones) followed by a minor third (3 semitones). Together they form a perfect fifth (7 semitones) from the root."],
  "5": ["1 - 5", "El power chord contiene solo la fundamental y la quinta justa (7 semitonos). Al no tener tercera no es mayor ni menor: su sonido es abierto, neutro y potente, especialmente habitual en rock.", "A power chord contains only the root and perfect fifth (7 semitones). With no third it is neither major nor minor, giving it an open, neutral and powerful sound commonly used in rock."],
  "-5": ["1 - 3 - ♭5", "Parte de una tríada mayor y rebaja la quinta un semitono, convirtiéndola en quinta disminuida. El tritono entre fundamental y ♭5 rompe la estabilidad del acorde mayor y crea una tensión marcada.", "This chord starts from a major triad and lowers the fifth by one semitone. The tritone between the root and ♭5 removes the usual stability of the major chord and creates pronounced tension."],
  "m": ["1 - ♭3 - 5", "El acorde menor apila una tercera menor (3 semitonos) y una tercera mayor (4 semitonos). La tercera rebajada respecto al acorde mayor le da su color oscuro, mientras la quinta justa conserva la estabilidad.", "A minor chord stacks a minor third (3 semitones) and a major third (4 semitones). Lowering the third changes the major chord's brightness into a darker color while the perfect fifth retains stability."],
  "dim": ["1 - ♭3 - ♭5", "La tríada disminuida apila dos terceras menores. Su quinta disminuida forma un tritono con la fundamental, por lo que produce una sonoridad inestable que suele conducir hacia otro acorde.", "A diminished triad stacks two minor thirds. Its diminished fifth forms a tritone with the root, producing an unstable sound that usually leads toward another chord."],
  "aug": ["1 - 3 - ♯5", "La tríada aumentada apila dos terceras mayores. Al subir la quinta un semitono pierde la quinta justa y adquiere un carácter simétrico, expansivo y ambiguo que pide continuación.", "An augmented triad stacks two major thirds. Raising the fifth removes the perfect fifth and gives the chord a symmetrical, expansive and ambiguous quality that calls for continuation."],
  "sus2": ["1 - 2 - 5", "Sustituye la tercera por una segunda mayor. Sin tercera no define modo mayor o menor; la cercanía entre fundamental y segunda crea una suspensión abierta que suele resolver en la tercera.", "This chord replaces the third with a major second. Without a third it defines neither major nor minor; the close root-second interval creates an open suspension that often resolves to the third."],
  "sus4": ["1 - 4 - 5", "Sustituye la tercera por una cuarta justa. La cuarta queda a un tono de la quinta y genera una suspensión clara que, en la armonía tonal, suele descender hacia la tercera.", "This chord replaces the third with a perfect fourth. The fourth sits one whole tone below the fifth and creates a clear suspension that commonly resolves downward to the third."],
  "sus2sus4": ["1 - 2 - 4 - 5", "Combina segunda y cuarta suspendidas alrededor de la fundamental y la quinta. Al omitir la tercera mantiene un carácter modalmente ambiguo, amplio y rico en tensiones internas.", "This chord combines suspended seconds and fourths around the root and fifth. Omitting the third keeps it modally ambiguous, spacious and rich in internal tension."],
  "add2": ["1 - 2 - 3 - 5", "Añade la segunda mayor dentro de la tríada mayor sin retirar la tercera. La fricción de un tono entre 1-2 y 2-3 aporta brillo y densidad, manteniendo intacta la identidad mayor.", "This chord adds the major second inside a major triad without removing the third. The whole-tone motion through 1-2-3 adds brightness and density while preserving its major identity."],
  "add4": ["1 - 3 - 4 - 5", "Añade la cuarta justa a la tríada mayor sin sustituir la tercera. El semitono entre tercera y cuarta crea una tensión expresiva que convive con la estabilidad de la quinta.", "This chord adds a perfect fourth to the major triad without replacing the third. The semitone between the third and fourth creates expressive tension alongside the stable fifth."],
  "add9": ["1 - 3 - 5 - 9", "Es una tríada mayor con una novena mayor añadida, pero sin séptima. La separación de octava distingue la novena de add2 y ofrece un color abierto y luminoso muy usado en pop.", "This is a major triad with an added major ninth but no seventh. Placing it above the octave distinguishes it from add2 and gives an open, bright color widely used in pop."],
  "madd9": ["1 - ♭3 - 5 - 9", "Añade una novena mayor a la tríada menor sin incorporar séptima. La novena ilumina el color oscuro de la tercera menor y crea una sonoridad emotiva y espaciosa.", "This chord adds a major ninth to a minor triad without adding a seventh. The ninth brightens the darker minor third and creates an emotional, spacious sound."],
  "6": ["1 - 3 - 5 - 6", "Añade una sexta mayor a la tríada mayor. Es una alternativa suave al maj7: conserva el carácter estable del acorde mayor con un color cálido frecuente en jazz, swing y pop clásico.", "This chord adds a major sixth to a major triad. It is a gentle alternative to maj7, retaining major stability with a warm color common in jazz, swing and classic pop."],
  "6add9": ["1 - 3 - 5 - 6 - 9", "Combina una tríada mayor con sexta y novena mayores. Al no incluir séptima evita la tensión dominante y produce un acorde amplio, consonante y muy útil como tónica final.", "This chord combines a major triad with major sixth and ninth. With no seventh it avoids dominant tension and produces a broad, consonant chord often used as a final tonic."],
  "m6": ["1 - ♭3 - 5 - 6", "Añade una sexta mayor a la tríada menor. El contraste entre tercera menor y sexta mayor crea un color sofisticado, asociado al jazz menor, la bossa nova y ciertos finales melódicos.", "This chord adds a major sixth to a minor triad. The contrast between minor third and major sixth creates a sophisticated color associated with minor jazz, bossa nova and melodic endings."],
  "m6add9": ["1 - ♭3 - 5 - 6 - 9", "Extiende el acorde menor con sexta y novena mayores, sin séptima. Su mezcla de oscuridad y apertura produce una tónica menor rica, suave y especialmente característica del jazz.", "This chord extends a minor triad with major sixth and ninth, without a seventh. Its blend of darkness and openness creates a rich, gentle minor tonic especially characteristic of jazz."],
  "7": ["1 - 3 - 5 - ♭7", "Añade una séptima menor a la tríada mayor. El tritono entre tercera y séptima crea una fuerte tensión dominante que normalmente resuelve hacia un acorde situado una quinta por debajo.", "This chord adds a minor seventh to a major triad. The tritone between third and seventh creates strong dominant tension that normally resolves to a chord a fifth below."],
  "7sus4": ["1 - 4 - 5 - ♭7", "Sustituye la tercera del acorde dominante por la cuarta justa. Conserva la séptima menor, pero aplaza la definición mayor y la resolución habitual de la cuarta hacia la tercera.", "This chord replaces the third of a dominant seventh with a perfect fourth. It retains the minor seventh while delaying the major identity and the usual resolution of the fourth to the third."],
  "7#5": ["1 - 3 - ♯5 - ♭7", "Altera el acorde dominante elevando su quinta un semitono. Mantiene el tritono de tercera y séptima, mientras la quinta aumentada añade cromatismo y empuja con más fuerza hacia la resolución.", "This alteration raises the fifth of a dominant seventh by one semitone. It keeps the third-seventh tritone while the augmented fifth adds chromatic pull toward the resolution."],
  "7b5": ["1 - 3 - ♭5 - ♭7", "Rebaja la quinta del acorde dominante. La ♭5 añade otro tritono respecto a la fundamental y crea un color más áspero, útil para enlaces cromáticos y dominantes alterados.", "This chord lowers the fifth of a dominant seventh. The ♭5 adds another tritone against the root, creating a sharper color useful in chromatic movement and altered dominants."],
  "7#9": ["1 - 3 - 5 - ♭7 - ♯9", "Añade una novena aumentada al acorde de dominante. La convivencia de tercera mayor y ♯9 —enarmónica de una tercera menor— produce la característica tensión mayor-menor del acorde Hendrix.", "This chord adds a sharp ninth to a dominant seventh. The clash between the major third and ♯9—enharmonically a minor third—creates the characteristic major-minor tension of the Hendrix chord."],
  "7b9": ["1 - 3 - 5 - ♭7 - ♭9", "Añade una novena menor, situada un semitono sobre la fundamental. Esa fricción intensifica la función dominante y es habitual en tonalidades menores y en escalas dominante disminuida o frigia dominante.", "This chord adds a minor ninth one semitone above the root. That friction intensifies its dominant function and is common in minor keys and diminished-dominant or Phrygian-dominant contexts."],
  "7(#5,#9)": ["1 - 3 - ♯5 - ♭7 - ♯9", "Combina quinta y novena aumentadas sobre una séptima dominante. Las dos alteraciones aumentan la ambigüedad cromática y permiten varias resoluciones por semitono.", "This chord combines sharp fifth and sharp ninth over a dominant seventh. Both alterations increase chromatic ambiguity and provide several semitone resolutions."],
  "7(#5,b9)": ["1 - 3 - ♯5 - ♭7 - ♭9", "Combina quinta aumentada y novena menor. La ♭9 presiona contra la fundamental y la ♯5 abre una vía cromática adicional hacia el acorde de resolución.", "This chord combines an augmented fifth and minor ninth. The ♭9 presses against the root while the ♯5 adds another chromatic route into the resolving chord."],
  "7(b5,#9)": ["1 - 3 - ♭5 - ♭7 - ♯9", "Combina quinta disminuida y novena aumentada en un dominante muy alterado. Reúne varios tritonos y semitonos, por lo que su color es tenso y flexible en jazz.", "This heavily altered dominant combines a diminished fifth and sharp ninth. Its tritones and semitone relationships create a tense, flexible jazz color."],
  "7(b5,b9)": ["1 - 3 - ♭5 - ♭7 - ♭9", "Combina quinta y novena disminuidas. La concentración de tritonos y semitonos refuerza al máximo la inestabilidad dominante y favorece resoluciones cromáticas.", "This chord combines flat fifth and flat ninth. Its concentration of tritones and semitones strongly reinforces dominant instability and favors chromatic resolution."],
  "9": ["1 - 3 - 5 - ♭7 - 9", "Añade una novena mayor al acorde de séptima dominante. Conserva la tensión del tritono y suma un color más amplio, frecuente en jazz, blues, funk y soul.", "This chord adds a major ninth to a dominant seventh. It retains the tritone's tension while adding a broader color common in jazz, blues, funk and soul."],
  "9#5": ["1 - 3 - ♯5 - ♭7 - 9", "Es un acorde de novena dominante con la quinta aumentada. La novena aporta amplitud y la ♯5 intensifica el movimiento cromático hacia la resolución.", "This is a dominant ninth with an augmented fifth. The ninth adds breadth while the ♯5 intensifies chromatic movement toward the resolution."],
  "9b5": ["1 - 3 - ♭5 - ♭7 - 9", "Es un acorde de novena dominante con quinta disminuida. La novena suaviza parcialmente el color, pero la ♭5 mantiene una tensión incisiva y ambigua.", "This is a dominant ninth with a diminished fifth. The ninth partly softens the color while the ♭5 maintains incisive, ambiguous tension."],
  "11": ["1 - 3 - 5 - ♭7 - 9 - 11", "Extiende el acorde dominante hasta la undécima. La 11ª choca con la tercera mayor, por lo que en la práctica suele omitirse la tercera o separarse ambas notas en distintas octavas.", "This chord extends a dominant harmony to the eleventh. The 11th clashes with the major third, so performers often omit the third or separate both notes into different octaves."],
  "11b9": ["1 - 3 - 5 - ♭7 - ♭9 - 11", "Combina la amplitud de la undécima con la intensa fricción de la novena menor. Es un dominante complejo en el que suelen omitirse notas para lograr un voicing claro.", "This chord combines the breadth of an eleventh with the strong friction of a minor ninth. It is a complex dominant in which notes are often omitted to keep the voicing clear."],
  "13": ["1 - 3 - 5 - ♭7 - 9 - 13", "Extiende la séptima dominante hasta la decimotercera, equivalente a una sexta mayor sobre la octava. La 11ª suele omitirse para evitar su choque con la tercera.", "This chord extends a dominant seventh to the thirteenth, equivalent to a major sixth above the octave. The 11th is usually omitted to avoid its clash with the third."],
  "13b9": ["1 - 3 - 5 - ♭7 - ♭9 - 13", "Añade a la dominante una decimotercera mayor y una novena menor. El contraste entre ambas tensiones es típico del jazz y conduce con fuerza hacia acordes mayores o menores.", "This chord adds a major thirteenth and minor ninth to a dominant harmony. Their contrasting tensions are typical of jazz and resolve strongly to major or minor chords."],
  "13#11": ["1 - 3 - 5 - ♭7 - 9 - ♯11 - 13", "Combina novena, undécima aumentada y decimotercera sobre una dominante. La ♯11 evita el choque de la 11ª justa con la tercera y aporta un color lidio dominante.", "This dominant combines ninth, sharp eleventh and thirteenth. The ♯11 avoids the perfect 11th's clash with the major third and supplies a Lydian-dominant color."],
  "maj7": ["1 - 3 - 5 - 7", "Añade una séptima mayor a la tríada mayor. El semitono entre séptima y fundamental superior crea una tensión suave y refinada, sin la necesidad de resolución propia del acorde dominante.", "This chord adds a major seventh to a major triad. The semitone between the seventh and upper root creates gentle, refined tension without the dominant seventh's need to resolve."],
  "maj7#5": ["1 - 3 - ♯5 - 7", "Une una tríada aumentada con una séptima mayor. La simetría de las terceras mayores se combina con la tensión de la séptima para crear un color luminoso, inestable y cinematográfico.", "This chord joins an augmented triad with a major seventh. Its stacked major thirds combine with seventh tension to create a bright, unstable and cinematic color."],
  "maj7b5": ["1 - 3 - ♭5 - 7", "Rebaja la quinta de un maj7. El tritono fundamental-♭5 contrasta con la delicada séptima mayor y produce una sonoridad moderna y ambigua.", "This chord lowers the fifth of a maj7. The root-♭5 tritone contrasts with the delicate major seventh, producing a modern and ambiguous sound."],
  "maj9": ["1 - 3 - 5 - 7 - 9", "Añade una novena mayor al acorde maj7. Mantiene el carácter estable de tónica y lo amplía con una sonoridad aérea, cálida y muy habitual en jazz y soul.", "This chord adds a major ninth to maj7. It preserves a stable tonic character while expanding it into an airy, warm sonority common in jazz and soul."],
  "maj11": ["1 - 3 - 5 - 7 - 9 - 11", "Extiende el maj7 con novena y undécima. La 11ª justa roza con la tercera mayor, así que suele omitirse la tercera o abrirse mucho el voicing.", "This chord extends maj7 with a ninth and eleventh. The perfect 11th rubs against the major third, so the third is often omitted or the voicing spread widely."],
  "maj13": ["1 - 3 - 5 - 7 - 9 - 13", "Extiende el maj7 con novena y decimotercera. Suele prescindir de la 11ª para conservar claridad y ofrece una tónica mayor rica, suave y completa.", "This chord extends maj7 with ninth and thirteenth. The 11th is usually omitted for clarity, resulting in a rich, smooth and complete major tonic."],
  "maj9#11": ["1 - 3 - 5 - 7 - 9 - ♯11", "Añade novena y undécima aumentada al maj7. La ♯11 convive mejor con la tercera mayor que la 11ª justa y crea el color abierto característico del modo lidio.", "This chord adds a ninth and sharp eleventh to maj7. The ♯11 coexists more easily with the major third than a perfect 11th and creates the open color of the Lydian mode."],
  "maj13#11": ["1 - 3 - 5 - 7 - 9 - ♯11 - 13", "Reúne las extensiones superiores del acorde mayor con una 11ª aumentada. Es una tónica lidia muy completa, brillante y espaciosa, normalmente distribuida en un voicing abierto.", "This chord gathers the upper major extensions around a sharp eleventh. It is a full, bright and spacious Lydian tonic, normally distributed across an open voicing."],
  "m7": ["1 - ♭3 - 5 - ♭7", "Añade una séptima menor a la tríada menor. Su estructura es estable y flexible: funciona como tónica menor, como ii en tonalidades mayores y como base habitual de jazz, funk y soul.", "This chord adds a minor seventh to a minor triad. Its stable, flexible structure works as a minor tonic, as ii in major keys, and as a staple of jazz, funk and soul."],
  "m7#5": ["1 - ♭3 - ♯5 - ♭7", "Eleva la quinta del acorde m7. La quinta aumentada debilita la estabilidad de la tríada y genera un color raro y cromático, útil como acorde de paso.", "This chord raises the fifth of m7. The augmented fifth weakens triadic stability and creates an unusual chromatic color useful as a passing chord."],
  "m9": ["1 - ♭3 - 5 - ♭7 - 9", "Añade una novena mayor al m7. La extensión aporta luz y amplitud sin borrar el carácter menor, creando uno de los colores más suaves y expresivos del jazz.", "This chord adds a major ninth to m7. The extension brings light and breadth without erasing its minor character, creating one of jazz's smoothest and most expressive colors."],
  "m11": ["1 - ♭3 - 5 - ♭7 - 9 - 11", "Extiende el m9 con una undécima justa. A diferencia del acorde mayor, la 11ª no choca fuertemente con la tercera menor y forma un voicing modal amplio y natural.", "This chord extends m9 with a perfect eleventh. Unlike in a major chord, the 11th does not strongly clash with the minor third, creating a broad and natural modal voicing."],
  "m13": ["1 - ♭3 - 5 - ♭7 - 9 - 13", "Añade novena y decimotercera mayores al m7. La 13ª aporta un color dórico luminoso al fondo menor; la 11ª suele omitirse para mantener claridad.", "This chord adds major ninth and thirteenth to m7. The 13th supplies a bright Dorian color over the minor base; the 11th is commonly omitted for clarity."],
  "mMaj7": ["1 - ♭3 - 5 - 7", "Combina una tríada menor con una séptima mayor. El semitono entre séptima y fundamental superior crea un color oscuro y luminoso a la vez, propio de la menor armónica y del cine.", "This chord combines a minor triad with a major seventh. The semitone between seventh and upper root creates a simultaneously dark and bright color associated with harmonic minor and film music."],
  "mMaj9": ["1 - ♭3 - 5 - 7 - 9", "Añade una novena mayor al acorde menor con séptima mayor. Amplía su tensión misteriosa con una nota más abierta y cantable, frecuente en jazz moderno y música cinematográfica.", "This chord adds a major ninth to a minor-major seventh. It expands the chord's mysterious tension with a more open, singable note common in modern jazz and film music."],
  "dim7": ["1 - ♭3 - ♭5 - 𝄫7", "Apila tres terceras menores, dividiendo la octava simétricamente. Cada nota puede sentirse como fundamental y el acorde admite varias resoluciones por semitono, lo que lo hace muy útil para modular.", "This chord stacks three minor thirds and divides the octave symmetrically. Any note can act as a root, and several semitone resolutions make it especially useful for modulation."],
  "m7b5": ["1 - ♭3 - ♭5 - ♭7", "También llamado semidisminuido: es una tríada disminuida con séptima menor. Aparece de forma natural como ii en tonalidades menores y conduce habitualmente al dominante.", "Also called half-diminished, this is a diminished triad with a minor seventh. It occurs naturally as ii in minor keys and commonly leads to the dominant."],
};

const MAJOR_CHORD_INVERSION_THEORY = [
  ["Posición fundamental: la fundamental está en el bajo, seguida de la tercera y la quinta. Es la disposición más estable y directa del acorde, y la que expresa con mayor claridad su función tonal.", "Root position: the root is in the bass, followed by the third and fifth. This is the chord's most stable and direct arrangement, and the one that expresses its tonal function most clearly."],
  ["Primera inversión: la tercera pasa al bajo y la fundamental se desplaza a la voz superior. Produce una sonoridad más ligera y facilita movimientos suaves del bajo entre acordes cercanos.", "First inversion: the third moves to the bass and the root is displaced to the upper voice. This produces a lighter sound and enables smooth bass movement between nearby chords."],
  ["Segunda inversión: la quinta está en el bajo, con la fundamental y la tercera por encima. Su carácter es menos estable y suele utilizarse como acorde de paso, prolongación o preparación de una resolución.", "Second inversion: the fifth is in the bass, with the root and third above it. Its character is less stable, and it is often used as a passing chord, prolongation or preparation for a resolution."],
];

const CHORD_DEGREE_NAMES = {
  es: {
    "1": "la fundamental",
    "2": "la segunda mayor",
    "♭3": "la tercera menor",
    "3": "la tercera mayor",
    "4": "la cuarta justa",
    "♭5": "la quinta disminuida",
    "5": "la quinta justa",
    "♯5": "la quinta aumentada",
    "6": "la sexta mayor",
    "𝄫7": "la séptima disminuida",
    "♭7": "la séptima menor",
    "7": "la séptima mayor",
    "♭9": "la novena menor",
    "9": "la novena mayor",
    "♯9": "la novena aumentada",
    "11": "la undécima justa",
    "♯11": "la undécima aumentada",
    "13": "la decimotercera mayor",
  },
  en: {
    "1": "the root",
    "2": "the major second",
    "♭3": "the minor third",
    "3": "the major third",
    "4": "the perfect fourth",
    "♭5": "the diminished fifth",
    "5": "the perfect fifth",
    "♯5": "the augmented fifth",
    "6": "the major sixth",
    "𝄫7": "the diminished seventh",
    "♭7": "the minor seventh",
    "7": "the major seventh",
    "♭9": "the minor ninth",
    "9": "the major ninth",
    "♯9": "the augmented ninth",
    "11": "the perfect eleventh",
    "♯11": "the augmented eleventh",
    "13": "the major thirteenth",
  },
};

const CHORD_INVERSION_NAMES = {
  es: ["Posición fundamental", "Primera inversión", "Segunda inversión", "Tercera inversión", "Cuarta inversión", "Quinta inversión", "Sexta inversión"],
  en: ["Root position", "First inversion", "Second inversion", "Third inversion", "Fourth inversion", "Fifth inversion", "Sixth inversion"],
};

function naturalLanguageList(items, language) {
  if (items.length <= 1) return items[0] || "";
  const conjunction = language === "en" ? " and " : " y ";
  return `${items.slice(0, -1).join(", ")}${conjunction}${items[items.length - 1]}`;
}

function chordInversionTheory(formula, inversion, language) {
  const lang = language === "en" ? "en" : "es";
  const degrees = String(formula || "").split(" - ").filter(Boolean);
  const safeInversion = Math.max(0, Math.min(Number(inversion) || 0, degrees.length - 1));
  const inversionName = CHORD_INVERSION_NAMES[lang][safeInversion] || (lang === "en" ? `Inversion ${safeInversion}` : `Inversión ${safeInversion}`);
  if (safeInversion === 0) {
    return lang === "en"
      ? `${inversionName}: the root is in the bass and the remaining notes appear above it in formula order. This is the clearest reference position for recognizing the chord's structure.`
      : `${inversionName}: la fundamental está en el bajo y las demás notas aparecen por encima siguiendo el orden de la fórmula. Es la posición de referencia más clara para reconocer la estructura del acorde.`;
  }

  const degreeNames = CHORD_DEGREE_NAMES[lang];
  const bassDegree = degreeNames[degrees[safeInversion]] || degrees[safeInversion];
  const movedDegrees = degrees.slice(0, safeInversion).map((degree) => degreeNames[degree] || degree);
  const moved = naturalLanguageList(movedDegrees, lang);
  if (lang === "en") {
    return `${inversionName}: ${bassDegree} is in the bass. ${moved} ${movedDegrees.length === 1 ? "moves" : "move"} up one octave; the chord keeps the same notes, but its bass support and voice leading into nearby chords change.`;
  }
  return `${inversionName}: ${bassDegree} está en el bajo. ${moved} ${movedDegrees.length === 1 ? "se desplaza" : "se desplazan"} una octava hacia arriba; el acorde conserva las mismas notas, pero cambia su apoyo grave y el enlace con los acordes cercanos.`;
}


global.MidiChordsChordHelp = Object.freeze({
  CHORD_VARIANT_GROUPS,
  CHORD_VARIANT_THEORY,
  MAJOR_CHORD_INVERSION_THEORY,
  chordInversionTheory,
});
})(globalThis);
