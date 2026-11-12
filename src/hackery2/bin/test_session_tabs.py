"""Check list validation and argument preservation through SSH/shell/tmux."""

import contextlib
import io
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import session_tabs as tabs


class SessionTabsTest(unittest.TestCase):
	def test_defaults_and_overrides(self):
		entry = tabs.normalize("claude:existing-session", tabs.DEFAULT_HOST, tabs.DEFAULT_CWD)
		self.assertEqual(entry["host"], "dev4-3")
		self.assertEqual(entry["tmux"], "existing-session")
		override = tabs.normalize({"tool": "codex", "session": "x", "host": "other",
		                           "cwd": "/srv/work", "tmux": "running"}, "default", "/default")
		self.assertEqual(override["host"], "other")
		self.assertEqual(override["cwd"], "/srv/work")
		self.assertEqual(override["tmux"], "running")

	def test_invalid_entries(self):
		for entry in ("x", "other:x", "codex:", "codex:--last", None,
		              {"tool": "codex", "session": "x", "cwd": None},
		              {"tool": "codex", "session": "x", "host": "-oProxyCommand=x"},
		              {"tool": "codex", "session": "x", "tmux": "a.b"},
		              {"tool": "codex", "session": "x", "directory": "/typo"},
		              "claude:x\ny"):
			with self.subTest(entry=entry), self.assertRaises(ValueError):
				tabs.normalize(entry, tabs.DEFAULT_HOST, tabs.DEFAULT_CWD)

	def test_sanitized_names_do_not_collide(self):
		self.assertNotEqual(tabs.tmux_name("a.b"), tabs.tmux_name("a:b"))
		self.assertEqual(tabs.tmux_name("a.b"), tabs.tmux_name("a.b"))
		self.assertNotRegex(tabs.tmux_name("named session:1.2"), r"[ .:]")

	def test_arguments_survive_shells_without_execution(self):
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			capture = root / "capture.json"
			stub = '#!/usr/bin/python3\nimport json, os, sys\nopen(os.environ["CAPTURE"], "w").write(json.dumps(sys.argv[1:]))\n'
			for executable in ("tmux", "claude", "codex"):
				path = root / executable
				path.write_text(stub)
				path.chmod(0o755)
			env = {**os.environ, "PATH": directory + os.pathsep + os.environ["PATH"],
			       "HOME": directory, "CAPTURE": str(capture)}
			name = "a 'quoted' name; $(touch INJECTED) `touch ALSO_INJECTED` $HOME"
			cwd = "~/project's space/$(touch INJECTED)"
			for tool in ("claude", "codex"):
				entry = tabs.normalize({"tool": tool, "session": name, "cwd": cwd}, "remote", "unused")
				ssh = tabs.session_command(entry)
				self.assertEqual(ssh[:4], ["ssh", "-t", "--", "remote"])
				# SSH's remote command is interpreted by the user's shell first.
				for shell in ("sh", "fish"):
					if not shutil.which(shell):
						continue
					subprocess.run([shell, "-c", ssh[-1]], env=env, cwd=directory, check=True,
					               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					tmux = json.loads(capture.read_text())
					self.assertEqual(tmux[:4], ["new-session", "-A", "-s", entry["tmux"]])
					self.assertEqual(tmux[4:6], ["-c", directory + "/" + cwd[2:]])
					# tmux in turn executes its shell-command as a single string.
					subprocess.run([shell, "-c", tmux[-1]], env=env, cwd=directory, check=True)
					self.assertEqual(json.loads(capture.read_text()),
					                 ["resume" if tool == "codex" else "--resume", name])
			self.assertFalse((root / "INJECTED").exists())
			self.assertFalse((root / "ALSO_INJECTED").exists())

	def test_cli_file_overrides_dedup_and_local(self):
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory) / "sessions.json"
			path.write_text(json.dumps(["claude:x", "claude:x",
			                           {"tool": "codex", "session": "y", "host": "local", "cwd": "/tmp"}]))
			output = io.StringIO()
			with contextlib.redirect_stdout(output), patch.object(tabs, "dbus_call") as launch:
				self.assertEqual(tabs.main(["--dry-run", "--host", "other", "-f", str(path)]), 0)
				launch.assert_not_called()
			lines = output.getvalue().splitlines()
			self.assertEqual(len(lines), 2)
			remote, local = map(shlex.split, lines)
			self.assertIn("other", remote)
			self.assertEqual(local[:2], ["sh", "-c"])

	def test_validate_all_before_launch(self):
		for args in (["claude:x", "invalid"], ["claude:x", "codex:x"], []):
			with self.subTest(args=args), patch.object(tabs, "dbus_call") as launch:
				with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
					tabs.main(args)
				self.assertEqual(error.exception.code, 2)
				launch.assert_not_called()

	def test_all_entries_use_one_selected_window(self):
		with patch.object(tabs, "select_window", return_value=(":1.78", "/Windows/3")) as select, \
		     patch.object(tabs, "open_tab") as launch:
			self.assertEqual(tabs.main(["codex:a", "claude:b"]), 0)
			select.assert_called_once_with(None, None)
			self.assertEqual(launch.call_count, 2)
			for call in launch.call_args_list:
				self.assertEqual(call.args[1:], (":1.78", "/Windows/3"))

	def test_find_callers_window_among_many(self):
		with patch.dict(os.environ, {"KONSOLE_DBUS_SERVICE": ":1.78", "KONSOLE_DBUS_SESSION": "/Sessions/42"}, clear=True), \
		     patch.object(tabs, "dbus_call", side_effect=["/Windows/1\n/Windows/3\n/Sessions/42", "1\n2", "41\n42"]):
			self.assertEqual(tabs.select_window(), (":1.78", "/Windows/3"))

	def test_explicit_window(self):
		with patch.dict(os.environ, {}, clear=True), \
		     patch.object(tabs, "dbus_call", return_value="/Windows/1\n/Windows/3") as call:
			self.assertEqual(tabs.select_window(":1.78", "3"), (":1.78", "/Windows/3"))
			call.assert_called_once_with(":1.78")

	def test_ambiguous_window_does_not_launch(self):
		with patch.dict(os.environ, {"KONSOLE_DBUS_SERVICE": ":1.78"}, clear=True), \
		     patch.object(tabs, "dbus_call", return_value="/Windows/1\n/Windows/3") as call:
			with self.assertRaisesRegex(RuntimeError, "--konsole-window"):
				tabs.select_window()
			call.assert_called_once_with(":1.78")

	def test_create_tab_and_address_only_returned_session(self):
		entry = tabs.normalize("codex:a", "remote", "/project")
		with patch.object(tabs, "dbus_call", side_effect=["99", "", "", ""]) as call:
			self.assertEqual(tabs.open_tab(entry, ":1.78", "/Windows/3"), "99")
			self.assertEqual(call.call_args_list[0].args,
			                 (":1.78", "/Windows/3", "org.kde.konsole.Window.newSession"))
			for item in call.call_args_list[1:]:
				self.assertEqual(item.args[:2], (":1.78", "/Sessions/99"))
			self.assertEqual(call.call_args_list[-1].args[2:],
			                 ("org.kde.konsole.Session.runCommand", shlex.join(tabs.session_command(entry))))

	def test_launch_failure_is_reported(self):
		with patch.object(tabs, "select_window", side_effect=RuntimeError("D-Bus unavailable")), \
		     patch.object(tabs.subprocess, "Popen") as launch:
			with contextlib.redirect_stderr(io.StringIO()) as error:
				self.assertEqual(tabs.main(["codex:a"]), 1)
			self.assertIn("D-Bus unavailable", error.getvalue())
			launch.assert_not_called()


if __name__ == "__main__":
	unittest.main()
