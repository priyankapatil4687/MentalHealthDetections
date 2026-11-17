param([string]$Docx, [string]$Pdf)
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
  $d = $w.Documents.Open($Docx)
  $d.Repaginate()
  $null = $d.Fields.Update()
  foreach ($t in $d.TablesOfContents) { $t.Update() }; foreach ($t in $d.TablesOfFigures) { $t.Update() }
  $null = $d.Fields.Update()
  foreach ($t in $d.TablesOfContents) { $t.Update() }; foreach ($t in $d.TablesOfFigures) { $t.Update() }
  $d.Repaginate()
  $d.Save()
  $d.ExportAsFixedFormat($Pdf, 17)
  "pages: " + $d.ComputeStatistics(2)
  $d.Close(0)
} finally { $w.Quit() }

