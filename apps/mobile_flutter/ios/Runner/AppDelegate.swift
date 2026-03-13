import AVFoundation
import Flutter
import UIKit

private final class IOSMetronomeClickEngine {
  private let assetLookup: (String) -> String
  private let queue = DispatchQueue(label: "midichords.ios.metronome")
  private var activePlayers: [AVAudioPlayer] = []
  private lazy var metronomeURL: URL = {
    let resolved = assetLookup("assets/metronome.mp3")
    return Bundle.main.bundleURL.appendingPathComponent(resolved)
  }()
  private lazy var barAccentURL: URL = {
    let resolved = assetLookup("assets/metronome_bar_accent.mp3")
    return Bundle.main.bundleURL.appendingPathComponent(resolved)
  }()

  init?(assetLookup: @escaping (String) -> String) {
    self.assetLookup = assetLookup
    do {
      let session = AVAudioSession.sharedInstance()
      try session.setCategory(.playback, options: [.mixWithOthers])
      try session.setPreferredSampleRate(44_100)
      try session.setPreferredIOBufferDuration(0.0025)
      try session.setActive(true)
    } catch {
      return nil
    }
  }

  func playClick(level: Int, volume: Double) -> Bool {
    let safeLevel = max(0, min(2, level))
    let rate: Float
    let gainSeed: Float
    switch safeLevel {
    case 2:
      rate = 1.0
      gainSeed = 1.0
    case 1:
      rate = 1.42
      gainSeed = 0.86
    default:
      rate = 0.94
      gainSeed = 0.62
    }
    let gain = max(0.0, min(1.0, Float(volume) * gainSeed))
    do {
      let sourceURL = safeLevel == 2 ? barAccentURL : metronomeURL
      let player = try AVAudioPlayer(contentsOf: sourceURL)
      player.enableRate = true
      player.rate = rate
      player.volume = gain
      player.prepareToPlay()
      player.delegate = nil
      let ok = player.play()
      guard ok else {
        return false
      }
      queue.async {
        self.activePlayers.append(player)
        let cleanupDelay = max(0.25, player.duration / Double(rate) + 0.08)
        self.queue.asyncAfter(deadline: .now() + cleanupDelay) {
          self.activePlayers.removeAll { $0 === player || !$0.isPlaying }
        }
      }
      return true
    } catch {
      return false
    }
  }

  func prewarm() {
    queue.async {
      do {
        let player = try AVAudioPlayer(contentsOf: self.metronomeURL)
        player.enableRate = true
        player.volume = 0.0
        player.prepareToPlay()
        self.activePlayers.append(player)
        let accentPlayer = try AVAudioPlayer(contentsOf: self.barAccentURL)
        accentPlayer.enableRate = true
        accentPlayer.volume = 0.0
        accentPlayer.prepareToPlay()
        self.activePlayers.append(accentPlayer)
        self.queue.asyncAfter(deadline: .now() + 0.4) {
          self.activePlayers.removeAll { $0 === player || $0 === accentPlayer }
        }
      } catch {}
    }
  }
}

private final class IOSSynthFallbackEngine {
  private let engine = AVAudioEngine()
  private let mixer = AVAudioMixerNode()
  private let format: AVAudioFormat
  private var activeNodes: [AVAudioPlayerNode] = []
  private let queue = DispatchQueue(label: "midichords.ios.synth")

  init?() {
    guard let format = AVAudioFormat(standardFormatWithSampleRate: 44_100, channels: 1) else {
      return nil
    }
    self.format = format
    engine.attach(mixer)
    engine.connect(mixer, to: engine.mainMixerNode, format: format)
    engine.mainMixerNode.outputVolume = 1.0
    do {
      try engine.start()
    } catch {
      return nil
    }
  }

  func stopAll() {
    queue.sync {
      for node in activeNodes {
        node.stop()
        engine.detach(node)
      }
      activeNodes.removeAll()
    }
  }

  func playTone(midi: Int, instrument: String, durationMs: Int, volume: Double) -> Bool {
    playMixed(notes: [midi], instrument: instrument, durationMs: durationMs, volume: volume)
  }

  func playChord(notes: [Int], instrument: String, durationMs: Int, volume: Double) -> Bool {
    playMixed(notes: notes, instrument: instrument, durationMs: durationMs, volume: volume)
  }

  private func playMixed(notes: [Int], instrument: String, durationMs: Int, volume: Double) -> Bool {
    let safeNotes = Array(Set(notes.map { min(108, max(21, $0)) })).sorted()
    guard !safeNotes.isEmpty else { return false }
    let seconds = max(0.08, min(2.6, Double(durationMs) / 1000.0))
    guard let buffer = buildBuffer(notes: safeNotes, seconds: seconds, instrument: instrument, gain: volume) else {
      return false
    }
    return queue.sync {
      if !engine.isRunning {
        do {
          try engine.start()
        } catch {
          return false
        }
      }
      let node = AVAudioPlayerNode()
      engine.attach(node)
      engine.connect(node, to: mixer, format: format)
      activeNodes.append(node)
      node.scheduleBuffer(buffer, at: nil, options: []) { [weak self, weak node] in
        guard let self, let node else { return }
        self.queue.async {
          node.stop()
          self.engine.detach(node)
          self.activeNodes.removeAll { $0 === node }
        }
      }
      node.play()
      return true
    }
  }

  private func buildBuffer(notes: [Int], seconds: Double, instrument: String, gain: Double) -> AVAudioPCMBuffer? {
    let frameCount = max(1, Int(format.sampleRate * seconds))
    guard let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: AVAudioFrameCount(frameCount)),
          let channel = buffer.floatChannelData?[0] else {
      return nil
    }
    buffer.frameLength = AVAudioFrameCount(frameCount)
    let isGuitar = instrument == "guitar"
    let attack = isGuitar ? 0.0045 : 0.010
    let decayBase = isGuitar ? 0.92 : 0.80
    let maxAmp = (isGuitar ? 0.54 : 0.50) * max(0.0, min(1.0, gain))
    let release = min(seconds * 0.18, isGuitar ? 0.040 : 0.028)
    let sampleRate = format.sampleRate
    let invCount = 1.0 / max(1.0, sqrt(Double(notes.count)))

    for i in 0..<frameCount {
      let t = Double(i) / sampleRate
      let decayFactor = pow(decayBase, t * (isGuitar ? 8.3 : 5.3))
      let fadeOut = (release <= 0 || t < seconds - release) ? 1.0 : max(0.0, min(1.0, (seconds - t) / release))
      let env = (t < attack ? (t / attack) : decayFactor) * fadeOut
      var mixed = 0.0
      for midi in notes {
        let freq = 440.0 * pow(2.0, Double(midi - 69) / 12.0)
        let pi2 = 2.0 * Double.pi
        let fundamental = sin(pi2 * freq * t) * (isGuitar ? 0.84 : 0.92)
        let harmonic2 = sin(pi2 * freq * 2.0 * t) * (isGuitar ? 0.24 : 0.20)
        let harmonic3 = sin(pi2 * freq * 3.0 * t) * (isGuitar ? 0.15 : 0.12)
        let harmonic4 = sin(pi2 * freq * 4.0 * t) * (isGuitar ? 0.08 : 0.06)
        let harmonic5 = sin(pi2 * freq * 5.0 * t) * (isGuitar ? 0.03 : 0.045)
        mixed += (fundamental + harmonic2 + harmonic3 + harmonic4 + harmonic5) * env * maxAmp * invCount
      }
      channel[i] = Float(max(-1.0, min(1.0, mixed)))
    }
    return buffer
  }
}

private final class IOSSampleInstrumentEngine {
  private struct ActiveVoice {
    let player: AVAudioPlayerNode
    let rate: AVAudioUnitVarispeed
  }

  private let engine = AVAudioEngine()
  private let mixer = AVAudioMixerNode()
  private let queue = DispatchQueue(label: "midichords.ios.samples")
  private let assetLookup: (String) -> String
  private var activeVoices: [ActiveVoice] = []
  private var sampleBuffers: [String: AVAudioPCMBuffer] = [:]

  private let pianoBank: [Int: String] = [
    48: "assets/samples/grand_piano/C3.mp3",
    52: "assets/samples/grand_piano/E3.mp3",
    55: "assets/samples/grand_piano/G3.mp3",
    60: "assets/samples/grand_piano/C4.mp3",
    64: "assets/samples/grand_piano/E4.mp3",
    67: "assets/samples/grand_piano/G4.mp3",
    72: "assets/samples/grand_piano/C5.mp3",
  ]

  private let guitarBank: [Int: String] = [
    40: "assets/samples/guitar_nylon/E2.mp3",
    45: "assets/samples/guitar_nylon/A2.mp3",
    50: "assets/samples/guitar_nylon/D3.mp3",
    52: "assets/samples/guitar_nylon/E3.mp3",
    55: "assets/samples/guitar_nylon/G3.mp3",
    59: "assets/samples/guitar_nylon/B3.mp3",
    64: "assets/samples/guitar_nylon/E4.mp3",
  ]

  init?(assetLookup: @escaping (String) -> String) {
    self.assetLookup = assetLookup
    engine.attach(mixer)
    engine.connect(mixer, to: engine.mainMixerNode, format: nil)
    engine.mainMixerNode.outputVolume = 1.0
    do {
      let session = AVAudioSession.sharedInstance()
      try session.setCategory(.playback, options: [.mixWithOthers])
      try session.setPreferredSampleRate(44_100)
      try session.setPreferredIOBufferDuration(0.0029)
      try session.setActive(true)
      engine.prepare()
      try engine.start()
    } catch {
      return nil
    }
  }

  func prewarm() {
    let assets = Array(Set(Array(pianoBank.values) + Array(guitarBank.values)))
    queue.async {
      for asset in assets {
        _ = self.loadBuffer(assetPath: asset)
      }
    }
  }

  func stopAll() {
    queue.sync {
      for voice in activeVoices {
        voice.player.stop()
        voice.rate.bypass = true
        engine.detach(voice.player)
        engine.detach(voice.rate)
      }
      activeVoices.removeAll()
    }
  }

  func playTone(midi: Int, instrument: String, durationMs: Int, volume: Double) -> Bool {
    playNotes([midi], instrument: instrument, durationMs: durationMs, volume: volume)
  }

  func playChord(notes: [Int], instrument: String, durationMs: Int, volume: Double) -> Bool {
    playNotes(notes, instrument: instrument, durationMs: durationMs, volume: volume)
  }

  private func playNotes(_ notes: [Int], instrument: String, durationMs: Int, volume: Double) -> Bool {
    let safeNotes = Array(Set(notes.map { min(108, max(21, $0)) })).sorted()
    guard !safeNotes.isEmpty else { return false }
    let rawDuration = Double(durationMs) / 1000.0
    let duration = max(0.08, min(2.6, rawDuration))
    let clampedVolume = max(0.0, min(1.0, volume))
    let noteCount = max(1, safeNotes.count)
    let voiceVolume = Float(clampedVolume) / sqrt(Float(noteCount))

    return queue.sync {
      if !engine.isRunning {
        do {
          try engine.start()
        } catch {
          return false
        }
      }

      var createdVoices: [ActiveVoice] = []
      for midi in safeNotes {
        guard let voice = makeVoice(midi: midi, instrument: instrument, volume: voiceVolume) else {
          for created in createdVoices {
            created.player.stop()
            engine.detach(created.player)
            engine.detach(created.rate)
          }
          return false
        }
        createdVoices.append(voice)
      }

      activeVoices.append(contentsOf: createdVoices)
      for voice in createdVoices {
        voice.player.play()
      }

      queue.asyncAfter(deadline: .now() + duration) { [weak self] in
        guard let self else { return }
        self.stopVoices(createdVoices)
      }
      return true
    }
  }

  private func makeVoice(midi: Int, instrument: String, volume: Float) -> ActiveVoice? {
    let bank = instrument == "guitar" ? guitarBank : pianoBank
    let safe = midi
    guard let sampleMidi = bank.keys.min(by: { abs($0 - safe) < abs($1 - safe) }),
          let assetPath = bank[sampleMidi],
          let sourceBuffer = loadBuffer(assetPath: assetPath)
    else {
      return nil
    }

    let semitones = safe - sampleMidi
    let rate = Float(max(0.5, min(2.0, pow(2.0, Double(semitones) / 12.0))))
    let player = AVAudioPlayerNode()
    let varispeed = AVAudioUnitVarispeed()
    varispeed.rate = rate
    varispeed.bypass = false
    player.volume = volume

    engine.attach(player)
    engine.attach(varispeed)
    engine.connect(player, to: varispeed, format: sourceBuffer.format)
    engine.connect(varispeed, to: mixer, format: sourceBuffer.format)
    player.scheduleBuffer(sourceBuffer, at: nil, options: [])
    return ActiveVoice(player: player, rate: varispeed)
  }

  private func stopVoices(_ voices: [ActiveVoice]) {
    queue.async {
      for voice in voices {
        voice.player.stop()
        self.engine.detach(voice.player)
        self.engine.detach(voice.rate)
      }
      self.activeVoices.removeAll { active in
        voices.contains { $0.player === active.player }
      }
    }
  }

  private func loadBuffer(assetPath: String) -> AVAudioPCMBuffer? {
    if let cached = sampleBuffers[assetPath] {
      return cached
    }

    let resolved = assetLookup(assetPath)
    let url = Bundle.main.bundleURL.appendingPathComponent(resolved)
    guard let file = try? AVAudioFile(forReading: url) else {
      return nil
    }
    let frameCount = AVAudioFrameCount(file.length)
    guard let buffer = AVAudioPCMBuffer(pcmFormat: file.processingFormat, frameCapacity: frameCount) else {
      return nil
    }
    do {
      try file.read(into: buffer)
      sampleBuffers[assetPath] = buffer
      return buffer
    } catch {
      return nil
    }
  }
}

@main
@objc class AppDelegate: FlutterAppDelegate {
  private var platformChannel: FlutterMethodChannel?
  private var sampleEngine: IOSSampleInstrumentEngine?
  private let synthFallback = IOSSynthFallbackEngine()
  private var metronomeClickEngine: IOSMetronomeClickEngine?

  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    GeneratedPluginRegistrant.register(with: self)
    if let registrar = self.registrar(forPlugin: "MIDIChordsPlatform") {
      sampleEngine = IOSSampleInstrumentEngine(assetLookup: { asset in
        registrar.lookupKey(forAsset: asset)
      })
      metronomeClickEngine = IOSMetronomeClickEngine(assetLookup: { asset in
        registrar.lookupKey(forAsset: asset)
      })
      sampleEngine?.prewarm()
      metronomeClickEngine?.prewarm()
      let channel = FlutterMethodChannel(
        name: "midichords/platform",
        binaryMessenger: registrar.messenger()
      )
      channel.setMethodCallHandler { [weak self] call, result in
        guard let self else {
          result(false)
          return
        }
        switch call.method {
        case "isIosSimulator":
          #if targetEnvironment(simulator)
            result(true)
          #else
            result(false)
          #endif
        case "playIosSynthTone":
          guard
            let args = call.arguments as? [String: Any],
            let midi = args["midi"] as? NSNumber,
            let instrument = args["instrument"] as? String,
            let durationMs = args["durationMs"] as? NSNumber,
            let volume = args["volume"] as? NSNumber
          else {
            result(false)
            return
          }
          let ok = self.sampleEngine?.playTone(
            midi: midi.intValue,
            instrument: instrument,
            durationMs: durationMs.intValue,
            volume: volume.doubleValue
          ) ?? false
          if ok {
            result(true)
            return
          }
          result(self.synthFallback?.playTone(
            midi: midi.intValue,
            instrument: instrument,
            durationMs: durationMs.intValue,
            volume: volume.doubleValue
          ) ?? false)
        case "playIosSynthChord":
          guard
            let args = call.arguments as? [String: Any],
            let notes = args["notes"] as? [NSNumber],
            let instrument = args["instrument"] as? String,
            let durationMs = args["durationMs"] as? NSNumber,
            let volume = args["volume"] as? NSNumber
          else {
            result(false)
            return
          }
          let noteValues = notes.map(\.intValue)
          let ok = self.sampleEngine?.playChord(
            notes: noteValues,
            instrument: instrument,
            durationMs: durationMs.intValue,
            volume: volume.doubleValue
          ) ?? false
          if ok {
            result(true)
            return
          }
          result(self.synthFallback?.playChord(
            notes: noteValues,
            instrument: instrument,
            durationMs: durationMs.intValue,
            volume: volume.doubleValue
          ) ?? false)
        case "stopIosSynth":
          self.sampleEngine?.stopAll()
          self.synthFallback?.stopAll()
          result(true)
        case "playIosMetronomeClick":
          guard
            let args = call.arguments as? [String: Any],
            let level = args["level"] as? NSNumber,
            let volume = args["volume"] as? NSNumber
          else {
            result(false)
            return
          }
          let ok = self.metronomeClickEngine?.playClick(
            level: level.intValue,
            volume: min(1.0, max(0.0, volume.doubleValue))
          ) ?? false
          result(ok)
        default:
          result(FlutterMethodNotImplemented)
        }
      }
      platformChannel = channel
    }
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
