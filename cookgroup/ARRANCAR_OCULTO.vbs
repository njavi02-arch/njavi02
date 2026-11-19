' Arranca ARRANCAR.bat sin ventana (lo usa la tarea programada de INSTALAR_AUTOARRANQUE.bat)
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
CreateObject("WScript.Shell").Run "cmd /c """ & dir & "\ARRANCAR.bat""", 0, False
