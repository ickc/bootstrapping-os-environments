{ pkgs, pkgs-unstable, self, ... }:
{
  # nixpkgs.config.allowUnfree = true;
  environment.systemPackages = import ./systemPackages.nix { inherit pkgs pkgs-unstable; };
  homebrew = {
    enable = true;
    onActivation.cleanup = "zap";
    masApps = import ./darwin/masApps.nix;
    brews = import ./darwin/brews.nix;
    casks = import ./darwin/casks.nix;
  };

  nix.settings = {
    download-buffer-size = 256 * 1024 * 1024;
    # Necessary for using flakes on this system.
    experimental-features = "nix-command flakes";
    trusted-users = [
      "root"
      "@admin"
    ];
  };

  security.pam.services.sudo_local.touchIdAuth = true;

  # Set Git commit hash for darwin-version.
  system.configurationRevision = self.rev or self.dirtyRev or null;

  system.defaults = {
    LaunchServices.LSQuarantine = false;
    NSGlobalDomain = {
      AppleInterfaceStyle = "Dark";
      AppleInterfaceStyleSwitchesAutomatically = false;
      AppleMeasurementUnits = "Centimeters";
      AppleMetricUnits = 1;
      AppleShowAllExtensions = true;
      AppleShowAllFiles = true;
      AppleTemperatureUnit = "Celsius";
      AppleWindowTabbingMode = "always";
      NSAutomaticCapitalizationEnabled = false;
      NSAutomaticDashSubstitutionEnabled = false;
      NSAutomaticPeriodSubstitutionEnabled = false;
      NSAutomaticQuoteSubstitutionEnabled = true;
      NSAutomaticSpellingCorrectionEnabled = false;
      "com.apple.mouse.tapBehavior" = 1;
      "com.apple.sound.beep.feedback" = 0;
      "com.apple.trackpad.enableSecondaryClick" = true;
      "com.apple.trackpad.forceClick" = true;
    };
    SoftwareUpdate.AutomaticallyInstallMacOSUpdates = true;
    dock = {
      autohide = true;
      minimize-to-application = true;
      mru-spaces = false;
      show-recents = false;
      wvous-bl-corner = 5;
      wvous-tl-corner = 10;
    };
    finder = {
      AppleShowAllExtensions = true;
      AppleShowAllFiles = true;
      FXDefaultSearchScope = "SCcf";
      FXEnableExtensionChangeWarning = false;
      FXPreferredViewStyle = "clmv";
      QuitMenuItem = true;
      ShowPathbar = true;
      _FXShowPosixPathInTitle = false;
    };
    loginwindow = {
      DisableConsoleAccess = false;
      GuestEnabled = false;
      PowerOffDisabledWhileLoggedIn = true;
      RestartDisabledWhileLoggedIn = true;
      ShutDownDisabledWhileLoggedIn = true;
    };
    magicmouse.MouseButtonMode = "TwoButton";
    menuExtraClock = {
      ShowAMPM = true;
      ShowDate = 1;
      ShowDayOfWeek = true;
    };
    screensaver = {
      askForPassword = true;
      askForPasswordDelay = 5;
    };
    spaces.spans-displays = false;
    trackpad = {
      ActuationStrength = 0;
      Clicking = true;
      TrackpadRightClick = true;
      TrackpadThreeFingerDrag = true;
      TrackpadThreeFingerTapGesture = 0;
    };
  };
}
