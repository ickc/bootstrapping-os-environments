{ ... }:
{
  programs.bash = {
    enable = true;
    completion.enable = true;
  };
  # Create /etc/zshrc that loads the nix-darwin environment.
  programs.zsh = {
    enable = true;
    enableBashCompletion = false;
    enableCompletion = false;
    enableFzfCompletion = true;
    enableFzfHistory = true;
    promptInit = "";
  };
}
