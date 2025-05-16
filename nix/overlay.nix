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
                pyglet = pyfinal.buildPythonPackage {
                  inherit (pyprev.pyglet) pname;
                  version = "1.5.31";

                  src = pyfinal.fetchPypi {
                    inherit (pyfinal.pyglet) pname version;
                    sha256 = "sha256-9oQTVku+w4DkgViY/vD7ekpJTcP4cYv78oziqAJjTIg=";
                    format = "wheel";
                    dist = "py3";
                    python = "py3";
                  };
                  format = "wheel";
                };
              };
            };
          })
        ];
      };
    };
}
