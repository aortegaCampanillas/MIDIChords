import Flutter
import UIKit

@main
@objc class AppDelegate: FlutterAppDelegate {
  private var platformChannel: FlutterMethodChannel?

  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    GeneratedPluginRegistrant.register(with: self)
    if let registrar = self.registrar(forPlugin: "MIDIChordsPlatform") {
      let channel = FlutterMethodChannel(
        name: "midichords/platform",
        binaryMessenger: registrar.messenger()
      )
      channel.setMethodCallHandler { call, result in
        switch call.method {
        case "isIosSimulator":
          #if targetEnvironment(simulator)
            result(true)
          #else
            result(false)
          #endif
        default:
          result(FlutterMethodNotImplemented)
        }
      }
      platformChannel = channel
    }
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
