# =============================
#   CLEAN PROJECT TREE SCRIPT
# =============================

$exclude = @(
    'venv','env','node_modules','.git','__pycache__',
    'dist','.vite','build','.mypy_cache','.pytest_cache',
    '*.egg-info','.DS_Store'
)

function Write-Tree {
    param($Path=".", $Prefix="")

    # Get items excluding unwanted folders
    $items = Get-ChildItem -LiteralPath $Path -Force | Where-Object {
        $name = $_.Name
        -not ($exclude -contains $name) -and
        -not ($exclude | Where-Object { $name -like $_ })
    }

    # Sort: folders first, then files
    $items = $items | Sort-Object { -not $_.PSIsContainer }, Name

    foreach ($item in $items) {
        # ASCII only: no fancy characters
        "$Prefix|-- $($item.Name)" | Out-File project_tree_clean.txt -Append

        if ($item.PSIsContainer) {
            Write-Tree -Path $item.FullName -Prefix ("$Prefix   ")
        }
    }
}

# Remove previous output
Remove-Item project_tree_clean.txt -ErrorAction SilentlyContinue

# Generate
Write-Tree

Write-Host ""
Write-Host "Done! Generated project_tree_clean.txt"
