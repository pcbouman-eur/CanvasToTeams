# You can use the following in a privileged Teams installation to install the required thing
# Install-Module MicrosoftTeams -AllowPrerelease -RequiredVersion "1.1.3-preview"

Import-Module MicrosoftTeams

$maxAttempts = 2

$inputfile = Read-Host -Prompt 'Input the name of the .json file that contains students registrations'
$data = Get-Content $inputfile | ConvertFrom-Json -AsHashtable

$groupid = Read-Host -Prompt 'Please enter the Group ID of the team you want to add users to'

$role = Read-Host -Prompt "Do you want to add users as an owner? (type 'yes' if positive)"

$errorfile = Read-Host -Prompt 'To which file shoulds errors be written?'

Connect-MicrosoftTeams

foreach ($section in $data.keys) {
    foreach ($user in $data[$section]) {
		# I am using a loop here, because sometimes a request fails. This way the script is more robust
		$attempt = 0
		do {
			$attempt = $attempt + 1
			try {
				Add-TeamUser -GroupId $groupid -User $user
				Add-TeamChannelUser -GroupId $groupid -DisplayName $section -User $user
				if ($role -eq 'yes') {
					Add-TeamChannelUser -GroupId $groupid -DisplayName $section -User $user -Role Owner
				}
				Write-Host "User $user was succesfully added to $section"
				$attempt = $maxAttempts
			}
			catch {
				if ($attempt -eq $maxAttempts ) {
					Add-Content -Path $errorfile -Value "Error adding $user to $section"
					Add-Content -Path $errorfile -Value $_
					Write-Host "An error occurred while adding $user to $section"
				}
				else {
					Write-Host "An error occurred. Retrying..."
				}			
			}	
		} While ($attempt -lt $maxAttempts)
    }
}

