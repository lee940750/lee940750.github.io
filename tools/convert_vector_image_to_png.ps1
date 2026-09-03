param(
  [Parameter(Mandatory = $true)]
  [string]$InputPath,

  [Parameter(Mandatory = $true)]
  [string]$OutputPath
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

$Image = [System.Drawing.Image]::FromFile($InputPath)
try {
  $Bitmap = New-Object System.Drawing.Bitmap $Image.Width, $Image.Height
  $Graphics = [System.Drawing.Graphics]::FromImage($Bitmap)
  try {
    $Graphics.Clear([System.Drawing.Color]::White)
    $Graphics.DrawImage($Image, 0, 0, $Image.Width, $Image.Height)
    $Bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
  }
  finally {
    $Graphics.Dispose()
    $Bitmap.Dispose()
  }
}
finally {
  $Image.Dispose()
}
