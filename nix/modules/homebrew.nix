{ inputs, ... }:
{
  imports = [
    # https://github.com/zhaofengli/nix-homebrew/issues/5#issuecomment-2412587886
    (
      { config, ... }:
      {
        homebrew.taps = builtins.attrNames config.nix-homebrew.taps;
      }
    )
    inputs.nix-homebrew.darwinModules.nix-homebrew
  ];

  nix-homebrew = {
    # Install Homebrew under the default prefix
    enable = true;
    enableRosetta = false;
    user = "kolen";
    # Optional: Declarative tap management
    taps = {
      "homebrew/homebrew-core" = inputs.homebrew-core;
      "homebrew/homebrew-cask" = inputs.homebrew-cask;
    };
    # Automatically migrate existing Homebrew installations
    autoMigrate = true;
    # With mutableTaps disabled, taps can no longer be added imperatively with `brew tap`.
    mutableTaps = false;
  };
}
