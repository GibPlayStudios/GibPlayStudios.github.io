// swift-tools-version: 5.9
import Foundation
import PackageDescription

// Exports Bitz pixel art for gibplay.com with the app's own renderer.
// BITZ_SRC points at a read-only copy of the Bitz repository (see README.md);
// the default assumes both repositories sit side by side.
let bitz = ProcessInfo.processInfo.environment["BITZ_SRC"] ?? "../../../Bitz"
// A path dependency is identified by its folder name.
let bitzIdentity = URL(fileURLWithPath: bitz).lastPathComponent

let package = Package(
    name: "bitz-art",
    platforms: [.macOS(.v13)],
    dependencies: [.package(path: bitz)],
    targets: [
        .executableTarget(name: "bitz-art", dependencies: [.product(name: "BitzCore", package: bitzIdentity)],
                          path: "Sources")
    ]
)
