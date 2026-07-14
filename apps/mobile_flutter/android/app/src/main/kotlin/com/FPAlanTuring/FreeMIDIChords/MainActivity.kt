package com.FPAlanTuring.FreeMIDIChords

import android.media.AudioAttributes
import android.media.AudioDeviceInfo
import android.media.AudioFormat
import android.media.AudioManager
import android.media.AudioTrack
import android.media.MediaCodec
import android.media.MediaExtractor
import android.media.MediaFormat
import android.os.Build
import android.util.Log
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.concurrent.thread
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min
import kotlin.math.pow

class MainActivity : FlutterActivity() {
    private val channelName = "midichords/platform"
    private val nativeAudio by lazy { AndroidNativeSampleEngine(this) }

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, channelName)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "playAndroidSynthTone" -> result.success(handlePlayTone(call))
                    "playAndroidSynthChord" -> result.success(handlePlayChord(call))
                    "playAndroidMetronomeClick" -> result.success(handlePlayMetronome(call))
                    else -> result.notImplemented()
                }
            }
    }

    private fun handlePlayTone(call: MethodCall): Boolean {
        val midi = (call.argument<Number>("midi")?.toInt() ?: 60).coerceIn(21, 108)
        val instrument = call.argument<String>("instrument") ?: "piano"
        val durationMs = (call.argument<Number>("durationMs")?.toInt() ?: 500).coerceIn(80, 2600)
        val volume = (call.argument<Number>("volume")?.toDouble() ?: 0.8).coerceIn(0.0, 1.0)
        return nativeAudio.playSampleTone(midi, instrument, durationMs, volume.toFloat())
    }

    private fun handlePlayChord(call: MethodCall): Boolean {
        val raw = call.argument<List<Number>>("notes") ?: emptyList()
        val notes = raw.map { it.toInt().coerceIn(21, 108) }.distinct().take(8)
        if (notes.isEmpty()) return false
        val instrument = call.argument<String>("instrument") ?: "piano"
        val durationMs = (call.argument<Number>("durationMs")?.toInt() ?: 500).coerceIn(80, 2600)
        val volume = (call.argument<Number>("volume")?.toDouble() ?: 0.8).coerceIn(0.0, 1.0)
        return nativeAudio.playSampleChord(notes, instrument, durationMs, volume.toFloat())
    }

    private fun handlePlayMetronome(call: MethodCall): Boolean {
        val level = (call.argument<Number>("level")?.toInt() ?: 0).coerceIn(0, 2)
        val durationMs = (call.argument<Number>("durationMs")?.toInt() ?: 55).coerceIn(20, 180)
        val volume = (call.argument<Number>("volume")?.toDouble() ?: 0.75).coerceIn(0.0, 1.0)
        return nativeAudio.playMetronome(level, durationMs, volume.toFloat())
    }
}

/** Un sample de audio ya decodificado a PCM 16-bit estéreo, listo para reproducir con AudioTrack. */
private class DecodedSample(val pcm: ShortArray, val sampleRate: Int, val channels: Int)

/**
 * Motor de audio nativo Android. Usa AudioTrack (en vez de SoundPool) porque es la única API
 * que permite fijar el dispositivo de salida por pista con setPreferredDevice(): con un
 * dispositivo MIDI-USB conectado (p.ej. un piano Roland expuesto también como interfaz de
 * audio USB), Android reenruta STREAM_MUSIC automáticamente hacia el USB, igual que haría con
 * unos auriculares USB-C — silenciando o distorsionando el sonido de síntesis local aunque el
 * usuario tenga seleccionada la salida "Audio" en la app. SoundPool no expone forma alguna de
 * evitar ese reenrutamiento; AudioTrack sí.
 */
private class AndroidNativeSampleEngine(private val activity: FlutterActivity) {
    private val tag = "MidiChordsAudio"
    private val decoded = mutableMapOf<String, DecodedSample>()
    private val decodeLock = Object()

    private val pianoBank = mapOf(
        48 to "assets/samples/grand_piano/C3.mp3",
        52 to "assets/samples/grand_piano/E3.mp3",
        55 to "assets/samples/grand_piano/G3.mp3",
        60 to "assets/samples/grand_piano/C4.mp3",
        64 to "assets/samples/grand_piano/E4.mp3",
        67 to "assets/samples/grand_piano/G4.mp3",
        72 to "assets/samples/grand_piano/C5.mp3",
    )
    private val guitarBank = mapOf(
        40 to "assets/samples/guitar_nylon/E2.mp3",
        45 to "assets/samples/guitar_nylon/A2.mp3",
        50 to "assets/samples/guitar_nylon/D3.mp3",
        52 to "assets/samples/guitar_nylon/E3.mp3",
        55 to "assets/samples/guitar_nylon/G3.mp3",
        59 to "assets/samples/guitar_nylon/B3.mp3",
        64 to "assets/samples/guitar_nylon/E4.mp3",
    )
    private val metronomePath = "assets/metronome.mp3"

    init {
        thread(name = "mc-preload", isDaemon = true) { preloadAll() }
    }

    fun playSampleTone(midi: Int, instrument: String, durationMs: Int, volume: Float): Boolean {
        val bank = if (instrument == "guitar") guitarBank else pianoBank
        val safe = midi.coerceIn(21, 108)
        val sampleMidi = nearestSample(bank.keys, safe) ?: return false
        val path = bank[sampleMidi] ?: return false
        val semitones = safe - sampleMidi
        // El límite 0.5x-2.0x venía de SoundPool (que sí tenía ese tope de
        // hardware); con el resample manual por AudioTrack no aplica, y
        // recortarlo hacía que todas las notas por encima de C6 (dos
        // octavas sobre la muestra más aguda, C5) o por debajo de A0/D2
        // sonaran todas exactamente igual entre sí en vez de con su propio
        // tono. El rango cubre el peor caso real (MIDI 21-108 contra
        // cualquier muestra del banco) sin recortar.
        val rate = (2.0.pow(semitones / 12.0)).toFloat().coerceIn(0.18f, 13.0f)
        val ok = playAsset(path, volume.coerceIn(0f, 1f), rate, durationMs)
        if (ok) {
            Log.d(tag, "playSampleTone ok midi=$midi sample=$sampleMidi inst=$instrument")
        } else {
            Log.e(tag, "playSampleTone failed midi=$midi inst=$instrument")
        }
        return ok
    }

    fun playSampleChord(notes: List<Int>, instrument: String, durationMs: Int, volume: Float): Boolean {
        val bank = if (instrument == "guitar") guitarBank else pianoBank
        val midis = notes.map { it.coerceIn(21, 108) }.distinct()
        if (midis.isEmpty()) return false
        val paths = midis.mapNotNull { midi ->
            val sampleMidi = nearestSample(bank.keys, midi) ?: return@mapNotNull null
            bank[sampleMidi]
        }.toSet()
        for (path in paths) {
            if (ensureDecoded(path) == null) return false
        }
        var playedAny = false
        for (midi in midis) {
            val ok = playSampleTone(midi, instrument, durationMs, volume)
            playedAny = playedAny || ok
        }
        if (playedAny) {
            Log.d(tag, "playSampleChord ok notes=${midis.joinToString(",")} inst=$instrument")
        } else {
            Log.e(tag, "playSampleChord failed notes=${midis.joinToString(",")} inst=$instrument")
        }
        return playedAny
    }

    fun playMetronome(level: Int, durationMs: Int, volume: Float): Boolean {
        val rate = when (level) {
            2 -> 1.68f
            1 -> 1.24f
            else -> 0.94f
        }
        val gain = when (level) {
            2 -> 1.0f
            1 -> 0.86f
            else -> 0.68f
        } * volume.coerceIn(0f, 1f)
        val ok = playAsset(metronomePath, gain.coerceIn(0f, 1f), rate, durationMs)
        if (ok) {
            Log.d(tag, "playMetronome ok level=$level")
        } else {
            Log.e(tag, "playMetronome failed level=$level")
        }
        return ok
    }

    private fun preloadAll() {
        val all = mutableSetOf<String>()
        all.addAll(pianoBank.values)
        all.addAll(guitarBank.values)
        all.add(metronomePath)
        for (path in all) {
            ensureDecoded(path)
        }
    }

    private fun ensureDecoded(path: String): DecodedSample? {
        synchronized(decodeLock) {
            decoded[path]?.let { return it }
            val sample = try {
                decodeMp3Asset(path)
            } catch (t: Throwable) {
                Log.e(tag, "decode failed for $path: $t")
                null
            } ?: return null
            decoded[path] = sample
            return sample
        }
    }

    private fun decodeMp3Asset(path: String): DecodedSample? {
        val afd = activity.assets.openFd("flutter_assets/$path")
        val extractor = MediaExtractor()
        extractor.setDataSource(afd.fileDescriptor, afd.startOffset, afd.length)
        afd.close()
        if (extractor.trackCount == 0) return null
        val format = extractor.getTrackFormat(0)
        val mime = format.getString(MediaFormat.KEY_MIME) ?: return null
        extractor.selectTrack(0)
        val sampleRate = format.getInteger(MediaFormat.KEY_SAMPLE_RATE)
        val channels = format.getInteger(MediaFormat.KEY_CHANNEL_COUNT)

        val codec = MediaCodec.createDecoderByType(mime)
        codec.configure(format, null, null, 0)
        codec.start()

        val pcmOut = ArrayList<Short>(sampleRate * channels)
        val bufferInfo = MediaCodec.BufferInfo()
        var sawInputEos = false
        var sawOutputEos = false

        while (!sawOutputEos) {
            if (!sawInputEos) {
                val inIndex = codec.dequeueInputBuffer(10_000)
                if (inIndex >= 0) {
                    val inBuffer = codec.getInputBuffer(inIndex) ?: continue
                    val sampleSize = extractor.readSampleData(inBuffer, 0)
                    if (sampleSize < 0) {
                        codec.queueInputBuffer(inIndex, 0, 0, 0, MediaCodec.BUFFER_FLAG_END_OF_STREAM)
                        sawInputEos = true
                    } else {
                        codec.queueInputBuffer(inIndex, 0, sampleSize, extractor.sampleTime, 0)
                        extractor.advance()
                    }
                }
            }
            val outIndex = codec.dequeueOutputBuffer(bufferInfo, 10_000)
            if (outIndex >= 0) {
                val outBuffer = codec.getOutputBuffer(outIndex)
                if (outBuffer != null && bufferInfo.size > 0) {
                    outBuffer.order(ByteOrder.LITTLE_ENDIAN)
                    outBuffer.position(bufferInfo.offset)
                    outBuffer.limit(bufferInfo.offset + bufferInfo.size)
                    val shortBuf = outBuffer.asShortBuffer()
                    val chunk = ShortArray(shortBuf.remaining())
                    shortBuf.get(chunk)
                    pcmOut.ensureCapacity(pcmOut.size + chunk.size)
                    for (s in chunk) pcmOut.add(s)
                }
                codec.releaseOutputBuffer(outIndex, false)
                if (bufferInfo.flags and MediaCodec.BUFFER_FLAG_END_OF_STREAM != 0) {
                    sawOutputEos = true
                }
            }
        }
        codec.stop()
        codec.release()
        extractor.release()

        return DecodedSample(pcmOut.toShortArray(), sampleRate, channels)
    }

    /**
     * Cambia el pitch reescalando el propio buffer PCM (resample simple por interpolación
     * lineal) y ajustando la longitud resultante — evita depender de PlaybackParams (que en
     * algunos dispositivos ignora el pitch al usar STREAM_MUSIC con AudioTrack en modo estático).
     */
    private fun resamplePitch(pcm: ShortArray, channels: Int, rate: Float): ShortArray {
        if (rate == 1.0f || pcm.isEmpty()) return pcm
        val framesIn = pcm.size / channels
        val framesOut = max(1, (framesIn / rate).toInt())
        val out = ShortArray(framesOut * channels)
        for (frameOut in 0 until framesOut) {
            val srcPos = frameOut * rate
            val frameA = min(framesIn - 1, srcPos.toInt())
            val frameB = min(framesIn - 1, frameA + 1)
            val t = srcPos - frameA
            for (ch in 0 until channels) {
                val a = pcm[frameA * channels + ch]
                val b = pcm[frameB * channels + ch]
                out[frameOut * channels + ch] = (a + (b - a) * t).toInt().toShort()
            }
        }
        return out
    }

    private fun applyVolumeAndFade(pcm: ShortArray, volume: Float, durationMs: Int, sampleRate: Int, channels: Int): ShortArray {
        val framesTotal = pcm.size / channels
        val framesWanted = min(framesTotal, ((durationMs / 1000.0) * sampleRate).toInt().coerceAtLeast(1))
        val fadeFrames = min(framesWanted, (sampleRate * 0.02).toInt().coerceAtLeast(1))
        val out = ShortArray(framesWanted * channels)
        for (frame in 0 until framesWanted) {
            var gain = volume
            val tailStart = framesWanted - fadeFrames
            if (frame >= tailStart) {
                gain *= (framesWanted - frame).toFloat() / fadeFrames
            }
            for (ch in 0 until channels) {
                val v = pcm[frame * channels + ch] * gain
                out[frame * channels + ch] = v.coerceIn(-32768f, 32767f).toInt().toShort()
            }
        }
        return out
    }

    @Volatile private var cachedSpeaker: AudioDeviceInfo? = null
    @Volatile private var speakerLookedUp = false

    private fun builtInSpeaker(): AudioDeviceInfo? {
        if (speakerLookedUp) return cachedSpeaker
        try {
            val audioManager = activity.getSystemService(AudioManager::class.java)
            cachedSpeaker = audioManager?.getDevices(AudioManager.GET_DEVICES_OUTPUTS)?.firstOrNull {
                it.type == AudioDeviceInfo.TYPE_BUILTIN_SPEAKER
            }
        } catch (_: Throwable) {
        }
        speakerLookedUp = true
        return cachedSpeaker
    }

    /**
     * playAsset se llama en el hilo del MethodChannel: debe volver rápido para no introducir
     * lag perceptible al tocar teclas seguidas. El resample/fade (coste de CPU) se hace en un
     * hilo aparte; solo el AudioTrack.play() de una pista silenciosa "placeholder" ocurre síncrono
     * para devolver cuanto antes, y el audio real llega en cuanto el hilo de fondo termina.
     */
    private fun playAsset(path: String, volume: Float, rate: Float, durationMs: Int): Boolean {
        val sample = ensureDecoded(path) ?: return false
        thread(name = "mc-play", isDaemon = true) {
            try {
                playDecodedSample(sample, volume, rate, durationMs)
            } catch (_: Throwable) {
            }
        }
        return true
    }

    private fun playDecodedSample(sample: DecodedSample, volume: Float, rate: Float, durationMs: Int) {
        val pitched = resamplePitch(sample.pcm, sample.channels, rate)
        val finalPcm = applyVolumeAndFade(pitched, volume, durationMs, sample.sampleRate, sample.channels)
        if (finalPcm.isEmpty()) return

        val channelConfig = if (sample.channels >= 2) {
            AudioFormat.CHANNEL_OUT_STEREO
        } else {
            AudioFormat.CHANNEL_OUT_MONO
        }
        val minBufBytes = AudioTrack.getMinBufferSize(
            sample.sampleRate,
            channelConfig,
            AudioFormat.ENCODING_PCM_16BIT,
        )
        val bufBytes = max(minBufBytes, finalPcm.size * 2)

        val track = AudioTrack.Builder()
            .setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_MEDIA)
                    .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                    .build(),
            )
            .setAudioFormat(
                AudioFormat.Builder()
                    .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                    .setSampleRate(sample.sampleRate)
                    .setChannelMask(channelConfig)
                    .build(),
            )
            .setBufferSizeInBytes(bufBytes)
            .setTransferMode(AudioTrack.MODE_STATIC)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            builtInSpeaker()?.let { track.preferredDevice = it }
        }

        track.write(finalPcm, 0, finalPcm.size)
        track.play()

        val playMs = (finalPcm.size.toLong() / sample.channels) * 1000L / sample.sampleRate
        try {
            Thread.sleep(playMs + 60L)
        } catch (_: Throwable) {
        }
        try {
            track.stop()
        } catch (_: Throwable) {
        }
        try {
            track.release()
        } catch (_: Throwable) {
        }
    }

    private fun nearestSample(candidates: Set<Int>, midi: Int): Int? {
        if (candidates.isEmpty()) return null
        var best: Int? = null
        var bestDist = Int.MAX_VALUE
        for (c in candidates) {
            val d = abs(c - midi)
            if (d < bestDist) {
                bestDist = d
                best = c
            }
        }
        return best
    }
}
