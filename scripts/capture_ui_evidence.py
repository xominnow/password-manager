"""Render staged desktop UI captures with synthetic, in-memory fixture data.

Run from the project root: python -m scripts.capture_ui_evidence
No real vault, clipboard, Android secure-window flags or release APK is used.
The white canvas is a documented presentation setting for these previews.
"""

from pathlib import Path
import argparse
import subprocess
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screen", type=int, choices=range(1, 10))
    args = parser.parse_args()
    if args.screen is None:
        for number in range(1, 10):
            result = subprocess.run([sys.executable, "-m", "scripts.capture_ui_evidence", "--screen", str(number)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if result.returncode:
                raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
            print(f"Captured synthetic desktop screen {number}/9", flush=True)
        sys.exit(0)
    # Kivy also parses sys.argv; consume our capture argument before importing it.
    sys.argv[1:] = []

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import NoTransition

from app.ui.controller import VaultUiController
from app.ui.navigation import Routes, build_app_shell


OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "ui" / "screenshots"
DEMO_MASTER = "Synthetic Demo!729"
DEMO_KEY = "DemoOnly12345678"  # 16 public fixture characters, not an actual vault key.


class NoClipboard:
    """Never access the user's system clipboard during evidence capture."""

    def copy(self, _text):
        raise RuntimeError("Clipboard disabled for evidence capture")

    def paste(self):
        return ""

    def clear(self):
        pass


class EvidenceApp(App):
    title = "Lockbox desktop evidence — synthetic fixture"

    def build(self):
        OUTPUT.mkdir(parents=True, exist_ok=True)
        self.paths = []
        self.controller = VaultUiController(":memory:", NoClipboard())
        self.manager = build_app_shell(self.controller)
        self.manager.transition = NoTransition()
        Window.size = (480, 1040)
        Window.clearcolor = (1, 1, 1, 1)
        with self.manager.canvas.before:
            Color(1, 1, 1, 1)
            self.backdrop = Rectangle(pos=self.manager.pos, size=self.manager.size)
        self.manager.bind(pos=self.update_backdrop, size=self.update_backdrop)
        steps = [
            ("01-setup.png", self.show_setup),
            ("02-recovery-confirmation.png", self.show_confirmation),
            ("03-login.png", lambda: self.show(Routes.LOGIN)),
            ("04-vault.png", self.show_vault),
            ("05-credential.png", self.show_entry),
            ("06-detail.png", self.show_detail),
            ("07-generator.png", self.show_generator),
            ("08-recovery.png", lambda: self.show(Routes.RECOVERY)),
            ("09-new-master.png", lambda: self.show(Routes.NEW_MASTER)),
        ]
        # One capture per fresh process avoids graphics-cache interactions
        # between repeated framebuffer exports of shared label textures.
        selected = steps[self.capture_index]
        self.preparations = [prepare for _, prepare in steps[:self.capture_index]]
        self.steps = iter([selected])
        Clock.schedule_once(self.next_frame, 0.5)
        return self.manager

    def show(self, route):
        self.manager.current = route
        screen = self.manager.get_screen(route)
        screen.scroll.scroll_y = 1
        return screen

    def show_setup(self):
        self.show(Routes.SETUP)

    def update_backdrop(self, *_args):
        self.backdrop.pos = self.manager.pos
        self.backdrop.size = self.manager.size

    def show_confirmation(self):
        # Staged screen state: never expose the randomly generated real key.
        self.controller.setup(DEMO_MASTER)
        screen = self.manager.get_screen(Routes.SETUP)
        screen.recovery_key = DEMO_KEY
        screen.recovery_label.text = f"Save this recovery key now:\n{DEMO_KEY}"
        screen.copy_recovery_button.disabled = False
        screen.saved_button.disabled = False
        screen.create_button.disabled = True
        screen.status("Vault created. Save the recovery key, then sign in.")

    def show_vault(self):
        self.controller.login(DEMO_MASTER)
        self.entry_id = self.controller.create("Example App", "demo-user", "SyntheticOnly!729").entry_id
        self.controller.create("Bank Demo", "test-account", "SyntheticOnly!839")
        self.show(Routes.VAULT)

    def show_entry(self):
        screen = self.show(Routes.ENTRY)
        screen.app_name.text = "Example App"
        screen.username.text = "demo-user"
        screen.password.text = "SyntheticOnly!729"

    def show_detail(self):
        self.controller.current_entry_id = self.entry_id
        self.show(Routes.DETAIL)

    def show_generator(self):
        screen = self.show(Routes.GENERATOR)
        # Stable, public demonstration string replaces the generated fixture.
        screen.generated.text = "Demo7!Only8@Test9#Ke"
        screen.feedback.text = "Strong: Synthetic demonstration password."

    def next_frame(self, _dt):
        try:
            filename, prepare = next(self.steps)
        except StopIteration:
            self.stop()
            return
        for prior in self.preparations:
            prior()
        self.preparations = []
        prepare()
        Clock.schedule_once(lambda _: self.capture(filename), 0.6)

    def capture(self, filename):
        # Re-render the entire widget tree so a partial desktop-window repaint
        # cannot omit unchanged labels. These remain staged desktop UI renders.
        target = OUTPUT / (Path(filename).stem + "0001.png")
        self.manager.export_to_png(str(target))
        self.paths.append(filename)
        Clock.schedule_once(self.next_frame, 0.1)

    def on_stop(self):
        self.controller.close()


if __name__ == "__main__":
    app = EvidenceApp()
    app.capture_index = args.screen - 1
    app.run()
