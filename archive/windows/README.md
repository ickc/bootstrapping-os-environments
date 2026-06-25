# Install

Open Microsoft Store once and update softwares there to ensure the account is authenticated. (And login Microsoft account beforehand.)

Open Terminal with administrator rights to minimize the amount of interaction needed. (Note the security implications.)

```powershell
winget import --import-file winget.json
```

# Tips

Use [winstall](https://winstall.app/) to discover and generates the JSON.
And then run `task sort` to cleanup.

If hash doesn't match, you could override it by

```powershell
# open terminal without adminstrative rights...
# https://stackoverflow.com/a/76828240
winget settings --enable InstallerHashOverride
winget install -i -e PACKAGE --ignore-security-hash
```
