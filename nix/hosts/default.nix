{ ... }:
{
  imports = [
    ../modules/common.nix
    ../modules/shell.nix
    ../modules/homebrew.nix
  ];

  system.primaryUser = "kolen";
}
