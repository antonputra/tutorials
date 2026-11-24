"""The words every step uses, so the hand-written agent and the framework agents get the same request."""

# The agent's instructions say who it is and nothing else: no tools are named, so the first request, which
# offers none, reads true. They stay these 131 characters from the first request to the last.
# (Until the afternoon of 21 Nov 2026 they ended with "Read the real data with your tools. Never guess.",
# 49 characters more: the wiring run's request sizes include them.)
SYSTEM = ("You are the payables agent of Juniper Market, a grocery store in Bend, Oregon. "
          "You check supplier invoices against purchase orders.")
QUESTION = "Is invoice 1042 from Cascade Packaging correct? Check it against its purchase order."
PAYMENT_RUN = ("Do the Friday payment run for invoices due 2026-11-27. Check every invoice against its purchase order. "
               "Schedule the payment when it matches. Put it on hold with the reason when it does not.")
# Only with MEMORY_FIRM=1, for a small model that does not follow the library's own memory guidelines.
MEMORY_FIRM = ("Your memory is the file /memories/AGENTS.md. When you are told to remember something, add it to that file "
               "with write_file or edit_file, at exactly that path, and nowhere else. Then say what you saved.")
