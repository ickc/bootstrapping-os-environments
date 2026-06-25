{
  description = "My Darwin system flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-26.05-darwin";
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nix-darwin = {
      url = "github:LnL7/nix-darwin/nix-darwin-26.05";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    nix-homebrew.url = "github:zhaofengli/nix-homebrew";
    # nix-homebrew's declarative tap management:
    homebrew-core = {
      url = "github:homebrew/homebrew-core";
      flake = false;
    };
    homebrew-cask = {
      url = "github:homebrew/homebrew-cask";
      flake = false;
    };
  };

  outputs =
    inputs@{
      self,
      nixpkgs,
      nix-darwin,
      ...
    }:
    let
      mkHost =
        hostName: system: stateVersion:
        let
          pkgs-unstable = import inputs.nixpkgs-unstable {
            inherit system;
            config.allowUnfree = true;
          };
        in
        nix-darwin.lib.darwinSystem {
          inherit system;
          specialArgs = { inherit self inputs pkgs-unstable; };
          modules = [
            ./hosts/${hostName}.nix
            { system.stateVersion = stateVersion; }
          ];
        };
    in
    {
      # Build darwin flake using:
      # $ darwin-rebuild build --flake .#simple
      darwinConfigurations."simple" = mkHost "default" "aarch64-darwin" 4;
      darwinConfigurations.ickc-mba = mkHost "default" "aarch64-darwin" 4;
      darwinConfigurations.ickc-mbp-m1p = mkHost "default" "aarch64-darwin" 4;
      darwinConfigurations.ickc-mbp-m4p = mkHost "default" "aarch64-darwin" 5;
    };
}
