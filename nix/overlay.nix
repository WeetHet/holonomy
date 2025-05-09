{ inputs, ... }:
{
  perSystem =
    { system, ... }:
    {
      _module.args.pyproject-nix = inputs.pyproject-nix;
      _module.args.pkgs = import inputs.nixpkgs {
        inherit system;
        overlays = [
          (self: super: {
            python3 = super.python3.override {
              packageOverrides = pyfinal: pyprev: {
                bezier = pyfinal.callPackage ./bezier.nix { };
              };
            };
          })
        ];
      };
    };
}
