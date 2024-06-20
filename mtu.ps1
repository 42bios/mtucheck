# IP address for MTU test (default is 1.1.1.1 if -IP parameter is not specified)
$ip = "1.1.1.1"

# Function to perform MTU test
function Test-MTU {
    param (
        [string]$TargetIP
    )

    $maxMTU = 10000  # Maximum size for MTU test
    $minMTU = 0      # Minimum size for MTU test
    $payloadSize = $maxMTU
    $doNotFragment = $true
    $timeout = 3000   # Timeout for response in milliseconds

    # Loop until maximum MTU size is converged upon
    while ($maxMTU -gt $minMTU) {
        if (Test-Connection -ComputerName $TargetIP -Count 1 -BufferSize $payloadSize -ErrorAction SilentlyContinue) {
            Write-Host "+ ICMP payload of $($payloadSize) bytes succeeded."
            $minMTU = $payloadSize
        } else {
            Write-Host "- ICMP payload of $($payloadSize) bytes failed.."
            $maxMTU = $payloadSize - 1
        }
        $payloadSize = [math]::Ceiling(($maxMTU + $minMTU) / 2.0)
    }

    # Calculate and display Path MTU
    Write-Host "Path MTU: $($minMTU + 28) bytes."
}

# Call the function to test MTU
Test-MTU -TargetIP $ip
