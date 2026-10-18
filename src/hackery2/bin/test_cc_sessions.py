"""Regression tests for session selection and live display filters."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import cc_sessions as sessions


class SessionViewsTest(unittest.TestCase):
	def setUp(self):
		self.temp = tempfile.TemporaryDirectory()
		self.addCleanup(self.temp.cleanup)
		self.sdir = Path(self.temp.name)
		self.records = [
			self.record("prompt", None, "user", "Explain this"),
			self.record("mixed", "prompt", "assistant", [
				{"type": "text", "text": "Here is an answer"},
				{"type": "thinking", "thinking": "PRIVATE_REASONING"},
				{"type": "tool_use", "name": "Read", "input": {"path": "TOOL_INPUT"}},
			]),
			self.record("result", "mixed", "user", [
				{"type": "tool_result", "content": "TOOL_OUTPUT"},
			]),
			self.record("answer", "result", "assistant", "Final answer"),
			{"uuid": "progress", "parentUuid": "answer", "type": "progress"},
		]
		self.write("alpha-one", self.records)
		self.write("alpha-two", [self.record("other", None, "user", "Other session")])
		# A fork copies the original prefix, then appends its own prompt.
		self.write("fork", self.records + [
			self.record("fork-prompt", "answer", "user", "Try a different approach"),
		])

	def record(self, uuid, parent, role, content):
		return {"uuid": uuid, "parentUuid": parent, "type": role,
			"timestamp": "2026-01-01T00:00:00Z", "sessionId": "alpha-one",
			"message": {"role": role, "content": content}}

	def write(self, sid, records):
		with (self.sdir / f"{sid}.jsonl").open("w") as output:
			for rec in records:
				output.write(json.dumps({**rec, "sessionId": sid}) + "\n")

	def test_id_selection_and_errors(self):
		self.assertEqual(sessions.session_files(self.sdir, "alpha-o")[0].stem, "alpha-one")
		for prefix, reason in (("alpha", "ambiguous"), ("missing", "no matching")):
			with self.assertRaisesRegex(ValueError, reason):
				sessions.session_files(self.sdir, prefix)
		self.assertEqual(len(sessions.load_sessions(self.sdir, "fork")), 1)
		graph = sessions.analyze_graph(self.sdir, session_id="fork")
		self.assertEqual(set(graph["nodes"]), {"prompt", "fork-prompt"})
		self.assertEqual(graph["pof"]("fork-prompt"), "prompt")
		self.assertEqual(graph["leaf_sid"]("prompt"), "fork")

	def test_conversation_filters_mixed_blocks_and_reconnects_parents(self):
		graph = sessions.analyze_graph(self.sdir, session_id="alpha-one", view="conversation")
		self.assertEqual(set(graph["nodes"]), {"prompt", "mixed", "answer"})
		self.assertEqual(graph["pof"]("answer"), "mixed")
		self.assertEqual(graph["nodes"]["mixed"]["message"]["content"],
			[{"type": "text", "text": "Here is an answer"}])
		html = sessions.build_html(self.sdir, session_id="alpha-one", view="conversation")
		self.assertIn("prompts + answers", html)
		self.assertNotIn("PRIVATE_REASONING", html)
		self.assertNotIn("TOOL_INPUT", html)
		self.assertNotIn("TOOL_OUTPUT", html)

	def test_everything_and_thinking(self):
		for thinking in (False, True):
			graph = sessions.analyze_graph(self.sdir, session_id="alpha-one",
				view="all", thinking=thinking)
			self.assertEqual(set(graph["nodes"]), {"prompt", "mixed", "result", "answer"})
			html = sessions.build_html(self.sdir, full=True,
				session_id="alpha-one", thinking=thinking)
			self.assertIn("TOOL_INPUT", html)
			self.assertIn("TOOL_OUTPUT", html)
			self.assertEqual("PRIVATE_REASONING" in html, thinking)

	def test_cli_id_in_dump_list_and_tree(self):
		for mode in ([], ["--list"], ["--tree"]):
			output = io.StringIO()
			with patch.object(sessions, "resolve_sessions_dir", return_value=self.sdir), \
				patch("sys.argv", ["cc_sessions", "--id", "alpha-o"] + mode), \
				contextlib.redirect_stdout(output):
				self.assertEqual(sessions.main(), 0)
			self.assertNotIn("Other session", output.getvalue())
			self.assertNotIn("alpha-two", output.getvalue())

	def test_serve_requests_apply_defaults_and_interactive_filters(self):
		requests = []

		def request(handler_class, path):
			handler = object.__new__(handler_class)
			handler.path = path
			handler.wfile = io.BytesIO()
			status = []
			handler.send_response = lambda code: status.append(code)
			handler.send_error = lambda code, *args: status.append(code)
			handler.send_header = lambda *args: None
			handler.end_headers = lambda: None
			handler.do_GET()
			requests.append((status[0], handler.wfile.getvalue().decode()))

		class FakeServer:
			server_address = ("127.0.0.1", 8000)

			def __init__(server, address, handler):
				server.handler = handler

			def serve_forever(server):
				for path in (
					"/", "/msg/mixed",
					"/?view=conversation&id=alpha-one&filters=1",
					"/msg/mixed?view=conversation&id=alpha-one&filters=1",
					"/msg/mixed?view=all&id=alpha-one&filters=1",
					"/msg/other?view=all&id=alpha-one",
					"/?view=invalid", "/?id=alpha",
					"/?view=prompts&id=&filters=1",
				):
					request(server.handler, path)
				raise KeyboardInterrupt

			def server_close(server):
				pass

		with patch("http.server.HTTPServer", FakeServer), \
			patch("webbrowser.open"), contextlib.redirect_stdout(io.StringIO()):
			self.assertEqual(sessions.serve_html(self.sdir, full=True,
				session_id="alpha-one", thinking=True), 0)
		self.assertIn('value="all" selected', requests[0][1])
		self.assertIn('value="alpha-one" selected', requests[0][1])
		self.assertIn("PRIVATE_REASONING", requests[1][1])
		self.assertIn('value="conversation" selected', requests[2][1])
		self.assertNotIn("TOOL_INPUT", requests[2][1])
		self.assertEqual([b["type"] for b in json.loads(requests[3][1])["blocks"]], ["text"])
		self.assertNotIn("PRIVATE_REASONING", requests[4][1])
		self.assertEqual([status for status, _ in requests[5:8]], [404, 400, 400])
		self.assertIn("Other session", requests[8][1])

	def test_empty_live_view_keeps_controls(self):
		self.write("tools-only", [self.record("tool", None, "assistant", [
			{"type": "tool_use", "name": "Read", "input": {}},
		])])
		html = sessions.build_html(self.sdir, embed=False, session_id="tools-only")
		self.assertIn('id="filters"', html)
		self.assertIn("No messages match", html)

	def test_selected_html_and_git_export(self):
		out = self.sdir / "selected.html"
		with contextlib.redirect_stdout(io.StringIO()):
			self.assertEqual(sessions.print_html(self.sdir, out_path=str(out),
				session_id="fork", view="conversation"), 0)
			self.assertEqual(sessions.export_git(self.sdir,
				str(self.sdir / "export"), session_id="fork"), 0)
		self.assertIn("Try a different approach", out.read_text())
		self.assertNotIn("Other session", out.read_text())
		commits = subprocess.run(["git", "-C", str(self.sdir / "export"),
			"rev-list", "--count", "--all"], capture_output=True, text=True, check=True)
		self.assertEqual(commits.stdout.strip(), "2")


if __name__ == "__main__":
	unittest.main()
