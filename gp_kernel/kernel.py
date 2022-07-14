from ipykernel.kernelbase import Kernel
from pexpect import EOF, TIMEOUT, spawn
from tempfile import NamedTemporaryFile

from os import path, fpathconf, fsync
import re
import signal
import traceback

from codecs import open


def readfile(filename):
    with open(filename, encoding="utf-8") as f:
        return f.read()


__version__ = readfile(path.join(path.dirname(__file__), "VERSION"))
version_pat = re.compile(r"version (\d+(\.\d+)+)")


class GPKernel(Kernel):
    implementation = "gp_kernel"
    implementation_version = __version__
    _prompt = ">PEXPECT_PROMPT<"

    language_info = {
        "name": "gp",
        "codemirror_mode": "c",
        "mimetype": "text/x-gp",
        "file_extension": ".g",
    }

    def debug(self, message):
        return
        self.send_response(
            self.iopub_socket,
            "stream",
            {
                "name": "stdout",
                "text": f"DEBUG: {message}\n",
            },
        )

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        # sets child, banner, language_info, language_version

        self._start_gp()

    def _start_gp(self):
        # Signal handlers are inherited by forked processes, and we can't easily
        # reset it from the subprocess. Since kernelapp ignores SIGINT except in
        # message handlers, we need to temporarily reset the SIGINT handler here
        # so that gp and its children are interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            gp = spawn(
                f"gp -D prompt='{self._prompt}' -D breakloop=0 -D colors='no,no,no,no,no,no,no' -D readline=0",
                echo=False,
                encoding="utf-8",
                maxread=4194304,
                ignore_sighup=True,
                codec_errors="ignore",
            )
            gp.expect_exact(self._prompt)
            banner = gp.before
            self.child = gp
        finally:
            signal.signal(signal.SIGINT, sig)

        self.max_input_line_size = 255
        lang_version = re.search(r" GP/PARI CALCULATOR Version (\d*.\d*.\d*)", banner).group(1)
        self.banner = "GP kernel connected to GP " + lang_version
        self.language_info["version"] = lang_version
        self.language_version = lang_version


    def do_execute(
        self, code, silent, store_history=True, user_expressions=None, allow_stdin=False
    ):
        code = code.rstrip()

        if not code.lstrip():
            return {
                "status": "ok",
                "execution_count": self.execution_count,
                "payload": [],
                "user_expressions": {},
            }


        interrupted = False

        read_characters = [0]
        def wait_for_output(read_characters, filename=None):
            # this function will *modify* the read_characters[0]
            # handle error messages with filename
            # output output initially on intervals of 0.5 seconds
            # If no output is received, the interval slowly increases to 30 seconds over 5 min
            initial_counter = counter = 10
            initial_timeout = timeout = 0.1

            while True:
                v = self.child.expect_exact([self._prompt, TIMEOUT], timeout=timeout)

                # something in output
                if not silent and len(self.child.before) > read_characters[0]:
                    output = self.child.before[read_characters[0]:]

                    if filename:
                        match = re.search(r'  \*\*\*   at top-level: read\(".+\n  \*\*\*\s+\^-+\s+\n  \*\*\*\s+in function read:', output)
                        self.debug(repr(output))
                        if match:
                            begin, end = match.span()
                            # hide the fact that we read a temporary file
                            output = output[0:begin] + '  ***   at top-level:    ' + output[end:]

                    if output:
                        self.send_response(
                            self.iopub_socket,
                            "stream",
                            {
                                "name": "stdout",
                                "text": output,
                            },
                        )
                    read_characters[0] = len(self.child.before)
                    counter = initial_counter
                    timeout = initial_timeout
                counter -= 1
                # increase timeout after default_counter attempts of processing line
                if counter <= 0:
                    # timeout = min(30, 2 * timeout)
                    counter = initial_counter
                if v == 0:
                    # finished waiting for output
                    return

        append_to_output = ""

        self.debug("before try")
        self.debug(f"{len(code)} {self.max_input_line_size}")
        try:
            # if the code block is long write it into a file and load it in gp
            # this takes about as the same time as sending a single line, and thus
            # we check the length of the whole code block
            # WARNING: the more obvious workaround of splitting each long line into
            # several small escaped lines, doesn't work, as we hit other system limits.
            # For example, I wasn't able to send a line longer that 2^16 character.
            if len(code) > self.max_input_line_size:
                # send the line via a temporary file
                with NamedTemporaryFile("w+t") as tmpfile:

                    self.debug(tmpfile.name)
                    tmpfile.write(code)
                    tmpfile.flush()
                    fsync(tmpfile.fileno())
                    self.child.sendline(f'read("{tmpfile.name}");')
                    wait_for_output(read_characters, tmpfile.name)
            else:
                self.child.sendline(code)
                wait_for_output(read_characters)
        except KeyboardInterrupt:
            self.debug("KeyboardInterrupt")
            self.child.sendintr()
            interrupted = True
            wait_for_output(read_characters)
            append_to_output = "Interrupted"
        except EOF:
            self.debug("EOF")
            append_to_output = "Restarting GP"
            self._start_gp()
        self.debug("end of try block")

        if not silent:
            # Send standard output
            self.send_response(
                self.iopub_socket,
                "stream",
                {
                    "name": "stdout",
                    "text": self.child.before[read_characters[0]:] + append_to_output,
                },
            )

        if interrupted:
            return {"status": "abort", "execution_count": self.execution_count}

        return {
            "status": "ok",
            "execution_count": self.execution_count,
            "payload": [],
            "user_expressions": {},
        }

    def do_complete(self, code, cursor_pos):
        default = {
            "matches": [],
            "cursor_start": 0,
            "cursor_end": cursor_pos,
            "metadata": dict(),
            "status": "ok",
        }
        return default

        #FIXME: not sure how to do this yet


        # optimizing to not send everything
        token = code[:cursor_pos]
        for sep in ["\n", ";", " "]:  # we just need the last chunk
            token = token.rpartition(sep)[-1]
        if not token:
            return default
        token_escaped = token.replace('"', r"\"")
        self.child.sendline(f'Completion("{token_escaped}", {len(token)});')
        self.child.expect_exact(self._prompt)
        if self.child.before == "DIE\n":
            self.log.error(
                f'Failed to complete, gp did not like our call:  Completion("{token_escaped}", {len(token)});'
            )
            return default
        matches = self.child.before.splitlines()
        try:
            # how many matches
            matches_len = int(matches[0])
            if matches_len == 0:
                return default
            # The range of text that should be replaced by the above matches when a completion is accepted.
            # typically cursor_end is the same as cursor_pos in the request.
            cursor_start = cursor_pos - len(token) + int(matches[1])
            cursor_end = cursor_pos - len(token) + int(matches[1]) + int(matches[2])
            matches = matches[3:]
            assert matches_len == len(matches)
        except Exception:
            self.log.error("Failed to complete: \n" + traceback.format_exc())
            return default

        return {
            "matches": matches,
            "cursor_start": cursor_start,
            "cursor_end": cursor_end,
            "metadata": dict(),
            "status": "ok",
        }
