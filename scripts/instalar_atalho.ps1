# Script automatizado para criar o atalho invisível (modo EXE) na Área de Trabalho

$DesktopPath = [Environment]::GetFolderPath("Desktop")
$WshShell = New-Object -comObject WScript.Shell

$ShortcutPath = "$DesktopPath\Kyros Leads.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)

# Usamos pythonw em vez de python para esconder totalmente o terminal preto.
$Shortcut.TargetPath = "pythonw.exe"

# O diretório atual onde o script está rodando (pasta prospeccao-vendas)
$CurrentDir = Get-Location
$Shortcut.Arguments = "$CurrentDir\kyros_app.py"
$Shortcut.WorkingDirectory = "$CurrentDir"

# Salva o atalho
$Shortcut.Save()

Write-Host "✅ Atalho 'Kyros Leads' criado com sucesso na Área de Trabalho!"
Write-Host "Pode fechar esta janela."
Start-Sleep -Seconds 3
