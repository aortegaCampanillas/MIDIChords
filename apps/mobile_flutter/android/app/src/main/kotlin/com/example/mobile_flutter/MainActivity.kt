package com.example.mobile_flutter

import android.media.AudioAttributes
import android.media.SoundPool
import android.util.Log
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import kotlin.concurrent.thread
import kotlin.math.abs
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

private class AndroidNativeSampleEngine(private val activity: FlutterActivity) {
    private val tag = "MidiChordsAudio"
    private val attrs = AudioAttributes.Builder()
        .setUsage(AudioAttributes.USAGE_MEDIA)
        .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
        .build()
    private val soundPool = SoundPool.Builder()
        .setAudioAttributes(attrs)
        .setMaxStreams(24)
        .build()
    private val soundIds = mutableMapOf<String, Int>()
    private val loaded = mutableSetOf<Int>()

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
        soundPool.setOnLoadCompleteListener { _, sampleId, status ->
            if (status == 0) {
                synchronized(loaded) { loaded.add(sampleId) }
            }
        }
        preloadAll()
    }

    fun playSampleTone(midi: Int, instrument: String, durationMs: Int, volume: Float): Boolean {
        val bank = if (instrument == "guitar") guitarBank else pianoBank
        val safe = midi.coerceIn(21, 108)
        val sampleMidi = nearestSample(bank.keys, safe) ?: return false
        val path = bank[sampleMidi] ?: return false
        val semitones = safe - sampleMidi
        val rate = (2.0.pow(semitones / 12.0)).toFloat().coerceIn(0.5f, 2.0f)
        val ok = playAsset(path, volume.coerceIn(0f, 1f), rate, durationMs)
        if (ok) {
            Log.d(tag, "playSampleTone ok midi=$midi sample=$sampleMidi inst=$instrument")
        } else {
            Log.e(tag, "playSampleTone failed midi=$midi inst=$instrument")
        }
        return ok
    }

    fun playSampleChord(notes: List<Int>, instrument: String, durationMs: Int, volume: Float): Boolean {
        var playedAny = false
        for (midi in notes) {
            val ok = playSampleTone(midi, instrument, durationMs, volume)
            playedAny = playedAny || ok
        }
        if (playedAny) {
            Log.d(tag, "playSampleChord ok notes=${notes.joinToString(",")} inst=$instrument")
        } else {
            Log.e(tag, "playSampleChord failed notes=${notes.joinToString(",")} inst=$instrument")
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
            ensureLoaded(path)
        }
    }

    private fun ensureLoaded(path: String): Int? {
        synchronized(soundIds) {
            soundIds[path]?.let { return it }
            return try {
                val afd = activity.assets.openFd("flutter_assets/$path")
                val id = soundPool.load(afd, 1)
                afd.close()
                soundIds[path] = id
                id
            } catch (_: Throwable) {
                null
            }
        }
    }

    private fun playAsset(path: String, volume: Float, rate: Float, durationMs: Int): Boolean {
        val id = ensureLoaded(path) ?: return false
        var isReady = synchronized(loaded) { loaded.contains(id) }
        if (!isReady) {
            // Give SoundPool a brief window to finish async load on first touch.
            repeat(12) {
                try {
                    Thread.sleep(10)
                } catch (_: Throwable) {
                }
                isReady = synchronized(loaded) { loaded.contains(id) }
                if (isReady) return@repeat
            }
        }
        if (!isReady) return false
        val streamId = soundPool.play(id, volume, volume, 1, 0, rate.coerceIn(0.5f, 2.0f))
        if (streamId == 0) return false
        thread(name = "mc-stop-$streamId", isDaemon = true) {
            try {
                Thread.sleep(durationMs.toLong().coerceAtLeast(20L))
                soundPool.stop(streamId)
            } catch (_: Throwable) {
            }
        }
        return true
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
