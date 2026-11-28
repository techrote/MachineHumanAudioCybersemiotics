"""Verify exact native upstream Git blob identities without network access."""
import hashlib
import pathlib
import sys

LOCK = (
    {"host.hpp": "f2c4057bd8cbbf94972b628b0e33e6fa39a7e64a", "escape_release.hpp": "2f1b50daad0b896aa4a8dbec3cfaa866d1dd686b", "orbit.hpp": "2e3d4bf0adb5fe3eccd53ce0320b745242584d85", "phase_routes.hpp": "0552694c270917bce16c2d20f14ed2a13645fb30", "sustain.hpp": "c55b93a588ca48c5fe9c0c40e292c3b526b00022"},
    {"bank_host.hpp": "340f967fb1094e443570373d1d600165b23caa9c", "bank_budget.hpp": "6040c9e5e1e4ae44d5dcf8593702e96de41f9ce2", "harmonic_bank.hpp": "c63a7ba3222f5549b1a940db4076975f29157adb", "band_input.hpp": "df548d771b8ef5d548796f0ba44ee815d72d6f8b", "resonator.hpp": "7ee4b814f6466a1434286efdecef75ecba0640df"},
    {"shuttle.hpp": "4c45b32ccfdd7963c32cce34381c161dd306696f", "shuttle_control.hpp": "56e9dc8690da8074e5a52703bec23b0f8306fca3", "shuttle_host_state.hpp": "b0737a09225b78148eb46113a98e36929770719a"},
)


def main(argv):
    if len(argv) != 3:
        raise ValueError("Expected ORBIT_DIR BANK_DIR SHUTTLE_DIR")
    for directory, files in zip(argv, LOCK):
        for name, expected in files.items():
            path = pathlib.Path(directory) / name
            raw = path.read_bytes()
            actual = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
            if actual != expected:
                raise ValueError(f"{path}: expected {expected}, got {actual}")
    print("CHAIN_SOURCE_PASS headers=13")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except (ValueError, OSError) as exc:
        sys.exit(str(exc))
