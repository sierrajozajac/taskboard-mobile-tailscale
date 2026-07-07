' serve-hidden.vbs - launch the TaskBoard API with no console window.
'
' Self-locating: it resolves paths relative to its own folder (the api/ dir),
' so it works wherever the repo lives. A shortcut to this file in the Windows
' Startup folder makes the API auto-start at logon. Run it directly to start
' the server by hand.
'
' Binds to 0.0.0.0 so the API is reachable over Tailscale / the LAN.
' Runs through a hidden cmd so uvicorn's stdout/stderr are redirected to
' api.log -- without valid output handles, uvicorn's logging kills pythonw.

Dim q : q = Chr(34)   ' a double-quote character

Set fso = CreateObject("Scripting.FileSystemObject")
apiDir  = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = apiDir & "\.venv\Scripts\pythonw.exe"
logFile = apiDir & "\api.log"

Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = apiDir   ' so sqlite tasks.db resolves next to the app

cmd = "cmd /c " & q & q & pythonw & q & _
      " -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > " & _
      q & logFile & q & " 2>&1" & q

sh.Run cmd, 0, False   ' 0 = hidden window, False = don't wait
